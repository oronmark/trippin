from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from trippin import tr_db


class OronView(APIView):
    def get(self, request) -> Response:
        loc = tr_db.Location.objects.first()
        print('asfsaf')
        return Response({"status": "success", "data": 'bla_data'}, status=status.HTTP_200_OK)
