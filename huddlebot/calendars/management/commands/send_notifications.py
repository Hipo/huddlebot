from time import sleep
from django.core.management.base import BaseCommand
from django.utils import timezone

from huddlebot.calendars.models import Calendar, Event


class Command(BaseCommand):

    def handle(self, *args, **options):
        while True:
            print(timezone.now())
            for calendar in Calendar.objects.iterator():
                get_upcoming_huddle_events_list = calendar.get_upcoming_huddle_events_list()

                for upcoming_huddle_event in get_upcoming_huddle_events_list:
                    event, created = Event.objects.get_or_create(
                        name=upcoming_huddle_event["summary"],
                        metadata=upcoming_huddle_event,
                        defaults={
                            "calendar": calendar,
                            "google_calendar_id": upcoming_huddle_event["id"],
                            "is_meeting_starts_reminder_sent": False,
                        })
                    if created:
                        event.send_meeting_starts_notification()

            sleep(30)
