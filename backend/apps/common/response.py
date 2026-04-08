from rest_framework.response import Response


def success(data=None, message="success"):
    return Response({"code": 0, "message": message, "data": data})


def error(message="error", code=1, status=400):
    return Response({"code": code, "message": message, "data": None}, status=status)
