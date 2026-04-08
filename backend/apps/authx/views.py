from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.permissions import IsAdminToken
from apps.common.response import error, success


class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "").strip()
        if username == "admin" and password == "123456":
            return success(
                {
                    "token": getattr(settings, "AIMALL_ADMIN_TOKEN", "dev-admin-token"),
                    "user": {"username": "admin", "nickname": "管理员"},
                }
            )
        return error("账号或密码错误", status=401)


class AdminProfileView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request):
        return success({"username": "admin", "nickname": "管理员"})


class AdminLogoutView(APIView):
    permission_classes = [IsAdminToken]

    def post(self, request):
        return success(True)
