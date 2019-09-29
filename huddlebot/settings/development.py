from huddlebot.settings.base import *  # noqa

SECRET_KEY = '#oe1a+pj48ckyaz^r^j@1e=s8m#$mi3keg&i5db9s4pa823k13'

DEBUG = True

SERVER_URL = "http://localhost:8000"

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '9e7706c6.ngrok.io',
]

INSTALLED_APPS = INSTALLED_APPS + [
    # Development Modules
    'django_extensions',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': "huddlebot",
        'USER': "huddlebot",
        'PASSWORD': "password",
        'HOST': "postgres",
        'PORT': '5432',
    }
}
