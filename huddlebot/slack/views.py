from django.conf import settings
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from huddlebot.slack.models import SlackWorkspace, SlackChannel

import requests
import slack


SLACK_OAUTH_URL = "https://slack.com/api/oauth.access"
SLACK_OAUTH_SCOPES = "channels:read,chat:write:bot,commands,files:write:user,team:read"

SLACK_COMMAND_AUTHENTICATE = 'authenticate'
SLACK_COMMAND_CONFIGURE = 'configure'
SLACK_COMMAND_UPDATE_CHANNELS = 'update_channels'
SLACK_COMMAND_SHOW_EVENTS = 'show_events'

ALLOWED_COMMANDS = [
    SLACK_COMMAND_SHOW_EVENTS,
    SLACK_COMMAND_UPDATE_CHANNELS,
    SLACK_COMMAND_CONFIGURE,
    SLACK_COMMAND_AUTHENTICATE,
]


class SlackOAuthView(View):
    """
    Authenticates the workspace, saves or updates internal list of channels
    """
    def get(self, request):
        auth_code = request.GET.get('code')
        
        if not auth_code:
            return render(request, 'slack/authenticate.html', {
                'client_id': settings.SLACK_CLIENT_ID,
                'oauth_scope': SLACK_OAUTH_SCOPES,
            })
        
        response = requests.get(SLACK_OAUTH_URL, params={
            'client_id': settings.SLACK_CLIENT_ID,
            'client_secret': settings.SLACK_CLIENT_SECRET,
            'code': auth_code,
        }).json()
    
        access_token = response.get('access_token')
        team_name = response.get('team_name')
        team_id = response.get('team_id')
        
        if not access_token or not team_id:
            return render(request, 'slack/authenticate.html', {
                'client_id': settings.SLACK_CLIENT_ID,
                'oauth_scope': SLACK_OAUTH_SCOPES,
            })
        
        workspace, created = SlackWorkspace.objects.update_or_create(
            team_id=team_id,
            defaults={
                'access_token': access_token,
                'team_name': team_name,
            }
        )
        
        workspace.update_channels()
        
        return render(request, 'slack/success.html')


@method_decorator(csrf_exempt, name='dispatch')
class SlackCommandView(View):
    """
    Handles incoming commands from Slack
    """
    def post(self, request):
        command = request.POST.get('text').strip()
        team_id = request.POST.get('team_id')
        user_id = request.POST.get('user_id')
        channel_id = request.POST.get('channel_id')
        
        if command not in ALLOWED_COMMANDS:
            return JsonResponse({
                'response_type': 'ephemeral',
                'text': "Sorry, I don't know this command. Please try one of the allowed commands."
            })

        try:
            workspace = SlackWorkspace.objects.get(team_id=team_id)
        except:
            return JsonResponse({
                'response_type': 'ephemeral',
                'text': "Your workspace doesn't seem to be setup, please install Huddlebot first."
            })

        message = ''

        if command == SLACK_COMMAND_AUTHENTICATE:
            #TODO: Generate Google authentication link and append
            message = 'Follow this link to authenticate your Google Calendar account: '
        elif command == SLACK_COMMAND_CONFIGURE:
            #TODO: Generate list of calendars and ask user to select one or more
            channel = workspace.channels.get(channel_id=channel_id)
            channel.create_file("Meeting on Friday, Sept 27, 2019")
        elif command == SLACK_COMMAND_SHOW_EVENTS:
            #TODO: Display upcoming events
            pass
        elif command == SLACK_COMMAND_UPDATE_CHANNELS:
            workspace.update_channels()
            
            message = 'OK, all done! I have updated your channels.'

        if message:
            return JsonResponse({
                'text': message,
            })
        else:
            return HttpResponse(status=200)
