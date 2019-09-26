from django.urls import path

from huddlebot.slack.views import SlackOAuthView, SlackCommandView


urlpatterns = [
    path(r'oauth/', SlackOAuthView.as_view(), name='slack-oauth'),
    path(r'command/', SlackCommandView.as_view(), name='slack-command'),
]
