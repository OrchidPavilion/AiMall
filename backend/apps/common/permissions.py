from django.conf import settings
from rest_framework.permissions import BasePermission


class IsAdminToken(BasePermission):
    def has_permission(self, request, view):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return False
        token = auth.split(" ", 1)[1].strip()
        expected = getattr(settings, "AIMALL_ADMIN_TOKEN", "dev-admin-token")
        return token == expected
