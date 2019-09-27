from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from hipo_django_core.models import AbstractBaseModel
from hipo_django_core.utils import generate_unique_id

from huddlebot.users.managers import UserManager


def generate_string_unique_id():
    return str(generate_unique_id())


class User(PermissionsMixin, AbstractBaseModel, AbstractBaseUser):
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    username = models.CharField(default=generate_string_unique_id, unique=True, max_length=255)

    is_staff = models.BooleanField(default=False, help_text=_("Only staff users can access Django Admin."))

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_google_calendar_service(self):
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', settings.GOOGLE_SCOPES)
        credentials = flow.run_console()
        service = build("calendar", "v3", credentials=credentials)

        return service

    def get_google_calendar_auth_url(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',
            settings.GOOGLE_SCOPES,
            redirect_uri='https://huddlebot.hack.hipolabs.com/calendars/callback'
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url

    def get_credentials(self):
        from google.oauth2.credentials import Credentials
        return Credentials(self.raw_google_crendetials)
