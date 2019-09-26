from __future__ import absolute_import, unicode_literals
from datetime import timedelta

from celery import Celery
from django.conf import settings

app = Celery()

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

CELERYBEAT_SCHEDULE = {
    # Celerybeat controller
    'celerybeat_controller': {
        'task': 'hipo_django_core.tasks.celerybeat_controller',
        'schedule': timedelta(minutes=1),
    },
}

app.conf.update(
    CELERYBEAT_SCHEDULE=CELERYBEAT_SCHEDULE
)
