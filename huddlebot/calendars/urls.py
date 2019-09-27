from django.urls import path

from huddlebot.calendars.views import CalendarAuthCallbackView

urlpatterns = [
    path(r'auth-callback/', CalendarAuthCallbackView.as_view(), name='auth-callback'),
]