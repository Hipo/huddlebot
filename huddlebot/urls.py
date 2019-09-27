from django.contrib import admin
from django.urls import path

from django.conf.urls import url
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^slack/', include(('huddlebot.slack.urls', 'slack'), namespace='slack')),
    url(r'^calendars/', include(('huddlebot.calendars.urls', 'calendars'), namespace='calendars')),
    url(r'^', include('hipo_django_core.urls')),
]
