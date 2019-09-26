# Huddlebot

## Development

- Install Docker.
- Run `./tools/run_development.sh`
- Ask for `hipo_django_core` package.
- Inside the container, `python manage.py migrate` (If you need database modifications)
- Inside the container, `python manage.py createsuperuser` (If you need a super user)
- Inside the container, `python manage.py runserver 0:8000`

