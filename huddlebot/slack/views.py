from django.conf import settings
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from huddlebot.slack.models import SlackWorkspace, SlackChannel

import json
import pprint
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
        workspace.update_team_info()
        
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

        message = None

        if command == SLACK_COMMAND_AUTHENTICATE:
            #TODO: Generate Google authentication link and append
            message = 'Follow this link to authenticate your Google Calendar account: '
        elif command == SLACK_COMMAND_CONFIGURE:
            #TODO: Generate list of calendars and ask user to select one or more
            channel = workspace.channels.get(channel_id=channel_id)
            block_message = "Pick the calendars you would like to track"
            
            payload = [
                {
                    "type": "section",
                    "block_id": "calendar-picker",
                    "text": {
                        "type": "mrkdwn",
                        "text": block_message
                    },
                    "accessory": {
                        "action_id": "pick-calendars",
                        "type": "multi_external_select",
                        "min_query_length": 1,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select calendars"
                        },
                    }
                }
            ]
            
            channel.send_message(message, blocks=payload)
        elif command == SLACK_COMMAND_SHOW_EVENTS:
            #TODO: Display upcoming events
            channel = workspace.channels.get(channel_id=channel_id)
            
            channel.send_question_message("Would you like to create meeting notes?")
        elif command == SLACK_COMMAND_UPDATE_CHANNELS:
            workspace.update_channels()
            
            message = 'OK, all done! I have updated your channels.'

        if message:
            return JsonResponse({
                'text': message,
            })
        else:
            return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class SlackInteractiveView(View):
    """
    Handles incoming interactive calls from Slack
    """
    def post(self, request):
        payload = json.loads(request.POST.get('payload'))
        team_id = payload.get('team', {}).get('id')
        
        try:
            workspace = SlackWorkspace.objects.get(team_id=team_id)
        except:
            return HttpResponse(status=403)
        
        user_id = payload.get('user', {}).get('id')
        channel_id = payload.get('channel', {}).get('id')
        actions = payload.get('actions', [])
        
        if len(actions) == 0:
            return HttpResponse(status=403)

        action = actions[0]
        
        if action.get("action_id") == "pick-calendars":
            calendar_ids = []
            
            for selected_option in action.get("selected_options", []):
                calendar_ids.append(selected_option.get("value"))
            
            #TODO: Save new calendars list
            pprint.pprint(calendar_ids)
        elif action.get("value") == "meeting-notes-yes":
            channel = workspace.channels.get(channel_id=channel_id)

            #TODO: Find actual meeting and create notes with that title
            channel.create_file("Meeting on Friday, Sept 27, 2019")
        
        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class SlackLoadMenuView(View):
    """
    Handles incoming interactive calls from Slack
    """
    def post(self, request):
        payload = json.loads(request.POST.get('payload'))
        pprint.pprint(payload)
        team_id = payload.get('team', {}).get('id')
        
        try:
            workspace = SlackWorkspace.objects.get(team_id=team_id)
        except:
            return HttpResponse(status=403)
        
        user_id = payload.get('user', {}).get('id')
        channel_id = payload.get('channel', {}).get('id')

        #TODO: Get list of calendars and build options
        
        return JsonResponse({
            'options': [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Personal"
                    },
                    "value": "123456"
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "Business"
                    },
                    "value": "654321"
                },
            ],
        })
