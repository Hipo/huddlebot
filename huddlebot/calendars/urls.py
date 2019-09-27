from django.urls import path

from huddlebot.calendars.views import CalendarAuthCallbackView

urlpatterns = [
    path(r'calendars/auth-callback/', CalendarAuthCallbackView.as_view(), name='auth-callback'),
]