from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from operator import itemgetter

import slack


class SlackWorkspace(models.Model):
    access_token = models.CharField(max_length=255)
    team_name = models.CharField(max_length=255)
    team_id = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Slack Workspace"
        verbose_name_plural = "Slack Workspaces"

    def __str__(self):
        return f"{self.team_name}"
    
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
