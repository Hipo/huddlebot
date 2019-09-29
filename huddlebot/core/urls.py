from django.urls import path

from huddlebot.core.views import HomepageView


urlpatterns = [
    path(r'', HomepageView.as_view(), name='homepage'),
]
