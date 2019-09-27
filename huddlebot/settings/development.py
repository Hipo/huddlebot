from huddlebot.settings.base import *  # noqa

from urllib import parse
import redis

SECRET_KEY = '#oe1a+pj48ckyaz^r^j@1e=s8m#$mi3keg&i5db9s4pa823k13'

DEBUG = True

SERVER_URL = "http://localhost:8000"

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '2841fd20.ngrok.io',
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

# Redis
REDIS_HOST = "redis"
REDIS_PORT = '6379'
REDIS_DB = 0
REDIS_CONNECTION = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Celery
CELERY_REDIS_DB = 1
CELERY_BROKER_URL = 'redis://{redis_host}:{redis_port}/{db}'.format(redis_host=REDIS_HOST, redis_port=REDIS_PORT, db=CELERY_REDIS_DB)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TIMEZONE = 'UTC'

# Django Core
HIPO_DJANGO_CORE_SETTINGS = {
    "FLOWER": {
        "BASE_URL": "http://flower:5555",
        "USERNAME": "hello",
        "PASSWORD": "huddlebot"
    }
}
