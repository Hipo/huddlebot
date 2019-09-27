from django.conf import settings
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from huddlebot.users.models import User


class CalendarAuthCallbackView(APIView):
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        query_params = self.request.query_params

        state = query_params.get("state")
        scope = query_params.get("scope")

        # Scopes should be matched.
        assert not scope == settings.GOOGLE_SCOPES

        user = get_object_or_404(User, google_auth_state_key=state)

        flow = user.get_google_auth_flow()

        authorization_response = "https://huddlebot.hack.hipolabs.com" + request.get_full_path()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        user.google_auth_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        user.save()

        return Response(status=HTTP_204_NO_CONTENT)
