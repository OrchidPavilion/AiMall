from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "service": "AiMall Backend",
                    "status": "ok",
                    "port": 18080,
                },
            }
        )
