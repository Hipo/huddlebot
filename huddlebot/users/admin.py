from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from huddlebot.users.forms import UserChangeForm, UserCreationForm
from huddlebot.users.models import User


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        ("Credentials", {"fields": ("id", "email", "first_name", "last_name", "password", "creation_datetime")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser")}),
    )
    readonly_fields = ("id", "creation_datetime",)
    list_display = ("id", "first_name", "last_name", "email")
    list_filter = ("is_staff", "is_superuser",)
    search_fields = ("id", "email", "first_name", "last_name")
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ('-creation_datetime',)

    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')
            }
        ),
    )


admin.site.register(User, UserAdmin)
