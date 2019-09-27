from django.urls import path

from huddlebot.slack.views import SlackOAuthView, SlackCommandView, SlackInteractiveView, SlackLoadMenuView


urlpatterns = [
    path(r'oauth/', SlackOAuthView.as_view(), name='slack-oauth'),
    path(r'command/', SlackCommandView.as_view(), name='slack-command'),
    path(r'interactive/', SlackInteractiveView.as_view(), name='slack-interactive'),
    path(r'load-menu/', SlackLoadMenuView.as_view(), name='slack-load-menu'),
]
