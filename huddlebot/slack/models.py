from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from operator import itemgetter

import slack


class SlackWorkspace(models.Model):
    access_token = models.CharField(max_length=255)
    team_name = models.CharField(max_length=255)
    team_id = models.CharField(max_length=255, unique=True)
    team_domain = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Slack Workspace"
        verbose_name_plural = "Slack Workspaces"

    def __str__(self):
        return f"{self.team_name}"
    
    def update_team_info(self):
        """
        Update team information
        """
        client = slack.WebClient(token=self.access_token)
        response = client.team_info()
        team_domain = response.get("team", {}).get("domain")
        
        self.team_domain = team_domain
        self.save()
    
    def update_channels(self):
        """
        Fetch all channels from Slack and create them
        """
        client = slack.WebClient(token=self.access_token)
        response = client.conversations_list(
            exclude_archived="true",
            limit=500,
        )

        channels = [SlackChannel(
            workspace=self,
            name=c.get("name"),
            channel_id=c.get("id")
        ) for c in sorted(response.get('channels', []), key=itemgetter('name'))]
        
        SlackChannel.objects.bulk_create(channels, ignore_conflicts=True)


class SlackChannel(models.Model):
    workspace = models.ForeignKey("SlackWorkspace", related_name="channels", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Channel"
        verbose_name_plural = "Channels"
        unique_together = ('workspace', 'channel_id')

    def __str__(self):
        return f"{self.workspace.team_name} - {self.name}"
    
    def send_question_message(self, message):
        """
        Sends a Yes/No question Slack message to this channel
        """
        payload = [
            {
    			"type": "section",
    			"text": {
    				"type": "mrkdwn",
    				"text": message,
    			}
    		},
            {
    			"type": "actions",
    			"elements": [
    				{
    					"type": "button",
    					"text": {
    						"type": "plain_text",
    						"emoji": True,
    						"text": "Yes"
    					},
    					"style": "primary",
    					"value": "meeting-notes-yes"
    				},
    				{
    					"type": "button",
    					"text": {
    						"type": "plain_text",
    						"emoji": True,
    						"text": "No"
    					},
    					"style": "danger",
    					"value": "meeting-notes-no"
    				}
    			]
    		}
        ]
        
        self.send_message(message, blocks=payload)
    
    def send_ephemeral_message(self, user_id, message, blocks=None):
        """
        Sends an ephemeral Slack message to the user
        """
        client = slack.WebClient(token=self.workspace.access_token)

        response = client.chat_postEphemeral(
            channel=self.channel_id,
            user=user_id,
            text=message,
            blocks=blocks
        )
    
    def send_message(self, message, blocks=None):
        """
        Sends a Slack message to this channel
        """
        client = slack.WebClient(token=self.workspace.access_token)

        response = client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            blocks=blocks,
            link_names=True
        )

    def create_file(self, title):
        """
        Creates empty editable text file in channel
        """
        client = slack.WebClient(token=self.workspace.access_token)

        response = client.files_upload(
            channels=self.channel_id,
            content=title,
            filetype="txt",
            title=title
        )
