from django.utils.translation import ugettext_lazy as _

from django.db import models
from hipo_django_core.models import AbstractBaseModel


class Calendar(AbstractBaseModel):
    user = models.ForeignKey("users.User", related_name="calendars", on_delete=models.CASCADE)
    google_calendar_id = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('Calendar')
        verbose_name_plural = _('Calendars')

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_google_calendar_list_of_user(cls, user):
        service = user.get_google_calendar_service()

        response = service.calendarList().list().execute()
        calendar_list = [{"name": item["summary"], "id": item["id"]} for item in response["items"]]

        return calendar_list

    def get_upcoming_events(self, limit=10):
        import datetime
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        service = self.user.get_google_calendar_service()

        response = service.events().list(calendarId=self.google_calendar_id, timeMin=now, maxResults=limit, singleEvents=True, orderBy='startTime').execute()

        return response


class Event(AbstractBaseModel):
    calendar = models.ForeignKey("calendars.Calendar", related_name="events", on_delete=models.CASCADE)
    google_calendar_id = models.CharField(max_length=255)

    name = models.CharField(max_length=255)
    start_datetime = models.DateTimeField(verbose_name=_("Starts at"))
    end_datetime = models.DateTimeField(verbose_name=_("Ends at"))

    # Pre Flags
    is_meeting_starts_reminder_sent = models.BooleanField(default=False)

    # Post Flags
    is_meeting_note_reminder_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        unique_together = (("calendar", "google_calendar_id"), )

    def __str__(self):
        return f"{self.name}"
