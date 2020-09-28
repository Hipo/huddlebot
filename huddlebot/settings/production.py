from huddlebot.settings.base import *  # noqa

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SECRET_KEY = secrets.SECRET_KEY

DEBUG = False

SERVER_URL = "http://huddlebot.hack.hipolabs.com"

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'huddlebot.hack.hipolabs.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': "huddlebot",
        'USER': "huddlebot",
        'PASSWORD': secrets.POSTGRES_PASSWORD,
        'HOST': "hackdb.cmq91upkqjfq.us-east-1.rds.amazonaws.com",
        'PORT': '5432',
    }
}

sentry_sdk.init(
    dsn=secrets.SENTRY_DSN,
    integrations=[DjangoIntegration()]
)
