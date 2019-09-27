import google.oauth2.credentials
import google_auth_oauthlib.flow

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
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

    google_auth_credentials = JSONField(blank=True, default=dict)
    google_auth_state_key = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_google_auth_flow(self):
        if self.google_auth_state_key:
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                client_secrets_file=settings.GOOGLE_SECRET_FILE_PATH,
                scopes=settings.GOOGLE_SCOPES,
                state=self.google_auth_state_key,
            )

        else:
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                client_secrets_file=settings.GOOGLE_SECRET_FILE_PATH,
                scopes=settings.GOOGLE_SCOPES,
            )

        flow.redirect_uri = 'https://huddlebot.hack.hipolabs.com/calendars/auth-callback'
        return flow

    def get_google_auth_credentials(self):
        credentials = google.oauth2.credentials.Credentials(
            self.google_auth_credentials["token"],
            refresh_token=self.google_auth_credentials["refresh_token"],
            token_uri=self.google_auth_credentials["token_uri"],
            client_id=self.google_auth_credentials["client_id"],
            client_secret=self.google_auth_credentials["client_secret"],
            scopes=self.google_auth_credentials["scopes"]
        )

        return credentials

    def get_google_calendar_service(self):
        service = build("calendar", "v3", credentials=self.get_google_auth_credentials())
        return service

    def get_google_calendar_auth_url(self):
        flow = self.get_google_auth_flow()

        auth_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true',
            prompt='consent',
        )

        self.google_auth_state_key = state
        self.save(update_fields=["google_auth_state_key"])

        return auth_url
