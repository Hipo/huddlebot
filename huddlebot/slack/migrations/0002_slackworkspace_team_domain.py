# Generated by Django 2.2.4 on 2019-09-27 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slack', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='slackworkspace',
            name='team_domain',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
