from django.urls import path

from huddlebot.calendars.views import CalendarOuthCallbackView, CalendarAuthCallbackSuccessView

urlpatterns = [
    path(r'auth-callback/', CalendarOuthCallbackView.as_view(), name='auth-callback'),
    path(r'auth-callback/success/', CalendarAuthCallbackSuccessView.as_view(), name='auth-callback-success'),
]