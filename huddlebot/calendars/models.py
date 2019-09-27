from datetime import timedelta, datetime

from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

from django.db import models
from hipo_django_core.models import AbstractBaseModel


class Calendar(AbstractBaseModel):
    user = models.ForeignKey("users.User", related_name="calendars", on_delete=models.CASCADE)
    google_calendar_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('Calendar')
        verbose_name_plural = _('Calendars')
        unique_together = (("user", "google_calendar_id"), )

    def __str__(self):
        return f"{self.name} - {self.user}"

    @classmethod
    def get_google_calendar_list_of_user(cls, user):
        service = user.get_google_calendar_service()
        response = service.calendarList().list().execute()
        calendar_list = [{"name": item["summary"], "id": item["id"]} for item in response["items"]]

        return calendar_list

    def get_upcoming_events_list(self, limit=10):
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        two_minutes_later = (datetime.utcnow() + timedelta(minutes=2)).isoformat() + 'Z'  # 'Z' indicates UTC time

        service = self.user.get_google_calendar_service()

        response = service.events().list(
            calendarId=self.google_calendar_id,
            timeMin=now,
            timeMax=two_minutes_later,
            maxResults=limit,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return response["items"]

    def get_upcoming_huddle_events_list(self):
        upcoming_events = self.get_upcoming_events_list()
        upcoming_huddle_events_list = []

        for upcoming_event in upcoming_events:
            if "hangoutLink" in upcoming_event.keys() or ("description" in upcoming_event.keys() and "zoom.us/j/" in upcoming_event["description"]):
                upcoming_huddle_events_list.append(upcoming_event)

        return upcoming_huddle_events_list


class Event(AbstractBaseModel):
    HUDDLE_TYPE_ZOOM = "zoom"
    HUDDLE_TYPE_HANGOUTS = "hangouts"

    calendar = models.ForeignKey("calendars.Calendar", related_name="events", on_delete=models.CASCADE)
    google_calendar_id = models.CharField(max_length=255)

    name = models.CharField(max_length=255)
    metadata = JSONField(blank=True, default=dict)

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

    @property
    def is_zoom_huddle(self):
        return "description" in self.metadata.keys() and "zoom.us" in self.metadata["description"]

    @property
    def is_hangout_huddle(self):
        return "hangoutLink" in self.metadata.keys()

    def get_huddle_link(self):
        import re

        if self.is_zoom_huddle:
            return re.search("(?P<url>https?://[^\s]+)", self.metadata["description"]).group("url")
        elif self.is_hangout_huddle:
            return self.metadata["hangoutLink"]

    def get_slack_channels_to_notify(self):
        try:
            channels_of_user = self.calendar.user.slack_workspace.channels.all()

            location = self.metadata["location"]
            location = location.replace(" ", "")
            location = location.replace(",", "")
            channel_list = location.split("#")

            # Remove empty data.
            channel_list = list(filter(None, channel_list))

            channels = []
            for channel_item in channel_list:
                if "/" in channel_item:
                    workspace_domain, channel_name = channel_item.split("/")
                    slack_channel = channels_of_user.filter(workspace__team_domain=workspace_domain, name=channel_name).first()
                else:
                    channel_name = channel_item
                    slack_channel = channels_of_user.filter(name=channel_name).first()

                channels.append(slack_channel)
        except:
            return []

        return channels

    def send_meeting_starts_notification(self):
        channels_to_notify = self.get_slack_channels_to_notify()

        for channel in channels_to_notify:
            name = self.name if self.name else "Huddle"
            # message = f"{name} is going to start. {self.get_huddle_link()} https://media.giphy.com/media/3o7TKUM3IgJBX2as9O/giphy.gif"
            message = f"{name} is going to start. {self.get_huddle_link()}"

            channel.send_message(message)
            print(f"Notification for {self} is sent to {channel}")

        self.is_meeting_starts_reminder_sent = True
        self.save(update_fields=["is_meeting_starts_reminder_sent"])
