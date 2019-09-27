from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView


class CalendarAuthCallbackView(APIView):
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        import pdb; pdb.set_trace()
        return Response(status=HTTP_204_NO_CONTENT)
