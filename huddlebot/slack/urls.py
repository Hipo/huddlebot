from django.urls import path

from huddlebot.slack.views import SlackOAuthView


urlpatterns = [
    path(r'oauth/', SlackOAuthView.as_view(), name='slack-oauth'),
]
