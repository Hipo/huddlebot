from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from huddlebot.calendars.admin import CalendarInline
from huddlebot.users.forms import UserChangeForm, UserCreationForm
from huddlebot.users.models import User


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        ("Credentials", {"fields": (
            "id", "email", "name", "password", "creation_datetime",
        )}),
        ("Google Auth", {"fields": ("google_auth_credentials", "google_auth_state_key")}),
        ("Slack", {"fields": ("slack_user_id", "slack_workspace")}),

        ("Permissions", {"fields": ("is_staff", "is_superuser")}),
    )
    readonly_fields = ("id", "creation_datetime",)
    list_display = ("id", "name", "email")
    list_filter = ("is_staff", "is_superuser",)
    search_fields = ("id", "email", "name")
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ('-creation_datetime',)
    raw_id_fields = ("slack_workspace", )
    inlines = [CalendarInline, ]

    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ('email', 'name', 'password1', 'password2')
            }
        ),
    )


admin.site.register(User, UserAdmin)
