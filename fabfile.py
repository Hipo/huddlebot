from contextlib import contextmanager as _contextmanager
from fabric.api import cd, env, prefix, run, settings, sudo, puts

import time

env.user = 'ubuntu'
env.forward_agent = True
env.gateway = 'ubuntu@tunnel.hipolabs.com'


class FabricException(Exception):
    pass


def msg(text):
    puts('\n\n------------------[ ' + text + ' ]------------------')


@_contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield


def deploy_app(branch, deploying_to_first_server, with_smoke_test):
    """
    Deploys appropriate branch with docker.
    """
    directory = '/huddlebot'
    assert deploying_to_first_server in ["yes", "no"]
    assert with_smoke_test in ["yes", "no"]

    docker_cmd = 'CONTAINER_UID=$(id -u) CONTAINER_GID=$(id -g) docker-compose -f docker-compose.yml -f docker-compose.{branch}.yml'.format(branch=branch)

    with cd(directory):
        run('GIT_SSH_COMMAND="ssh -i ~/.ssh/huddlebot_github_backend_id_rsa" git reset --hard')
        run('GIT_SSH_COMMAND="ssh -i ~/.ssh/huddlebot_github_backend_id_rsa" git fetch')
        run('GIT_SSH_COMMAND="ssh -i ~/.ssh/huddlebot_github_backend_id_rsa" git checkout %s' % branch)
        run('GIT_SSH_COMMAND="ssh -i ~/.ssh/huddlebot_github_backend_id_rsa" git pull origin %s' % branch)

        run("{docker_cmd} stop --timeout 60".format(docker_cmd=docker_cmd))
        run("{docker_cmd} rm --force".format(docker_cmd=docker_cmd))
        run("{docker_cmd} up --remove-orphans --build --no-start".format(docker_cmd=docker_cmd))

        # If we deploy to multiple servers and this is the first one, run migrate and collectstatic.
        # Otherwise don't run since they do the same operation.
        if deploying_to_first_server == 'yes':
            sudo('{docker_cmd} run huddlebot ./manage.py migrate --no-input'.format(docker_cmd=docker_cmd))

        # Start
        sudo('{docker_cmd} start huddlebot rapid7 notification_sender'.format(docker_cmd=docker_cmd))

        sudo("ln -sfn /huddlebot/conf/rapid7_{branch}_rsyslog.conf /etc/rsyslog.d/rapid7.conf".format(branch=branch))
        sudo("service rsyslog restart")

        if with_smoke_test == "yes":
            # allow to warm up for gunicorn
            time.sleep(15)
            print("now doing some smoke tests")
            try:
                run('http-checks -c conf/check_urls.yml')
            except Exception:
                sudo('{docker_cmd} stop huddlebot'.format(docker_cmd=docker_cmd))
                raise


def collectstatic(branch):
    """
    we run this as a seperate task after deploy task,
    so we dont have to wait until collectstatic runs.
    """
    directory = '/huddlebot'
    docker_cmd = 'CONTAINER_UID=$(id -u) CONTAINER_GID=$(id -g) docker-compose -f docker-compose.yml -f docker-compose.{branch}.yml'.format(branch=branch)

    delay = 5
    max_attempts = 3
    attempts = 0
    keep_trying = True  # Becomes False when collectstatic was successful
    with cd(directory):
        while keep_trying:
            try:
                sudo('{docker_cmd} run huddlebot ./manage.py collectstatic --no-input'.format(docker_cmd=docker_cmd))
                keep_trying = False
            except FabricException as e:  # Very likely a connection error
                attempts += 1
                run('echo "collectstatic failed %d times, retrying in %d seconds..."' % (attempts, delay))
                if attempts >= max_attempts:
                    raise e
                time.sleep(delay)
