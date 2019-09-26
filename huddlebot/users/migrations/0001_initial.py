# Generated by Django 2.2.4 on 2019-09-26 10:36

from django.db import migrations, models
import hipo_django_core.models
import hipo_django_core.utils
import huddlebot.users.managers
import huddlebot.users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.BigIntegerField(default=hipo_django_core.utils.generate_unique_id, editable=False, primary_key=True, serialize=False)),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(blank=True, max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('username', models.CharField(default=huddlebot.users.models.generate_string_unique_id, max_length=255, unique=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Only staff users can access Django Admin.')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            bases=(hipo_django_core.models.LogEntryMixin, models.Model),
            managers=[
                ('objects', huddlebot.users.managers.UserManager()),
            ],
        ),
    ]
