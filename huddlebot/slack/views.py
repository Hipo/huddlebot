from django.conf import settings
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from huddlebot.slack.models import SlackWorkspace, SlackChannel

import requests
import slack


SLACK_OAUTH_URL = "https://slack.com/api/oauth.access"
SLACK_OAUTH_SCOPES = "channels:read,chat:write:bot"


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
