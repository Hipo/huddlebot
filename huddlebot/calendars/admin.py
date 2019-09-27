from django.contrib import admin

from huddlebot.calendars.models import Calendar, Event
from django.utils.translation import ugettext_lazy as _


class CalendarInline(admin.TabularInline):
    verbose_name_plural = _("Calendars")
    model = Calendar
    fields = ("name", "google_calendar_id")
    show_change_link = True
    can_delete = True
    extra = 0


admin.site.register(Event)
