from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView

from apps.behaviors.models import CustomerBehavior
from apps.behaviors.serializers import CustomerBehaviorSerializer
from apps.common.permissions import IsAdminToken
from apps.common.response import error, success
from .models import Customer
from .serializers import CustomerSerializer, MallLoginSerializer, MallRegisterSerializer


def _page(request, qs):
    page = max(int(request.query_params.get('page', 1) or 1), 1)
    page_size = max(min(int(request.query_params.get('page_size', 20) or 20), 100), 1)
    total = qs.count()
    rows = qs[(page-1)*page_size: page*page_size]
    return success({'list': CustomerSerializer(rows, many=True).data, 'page': page, 'page_size': page_size, 'total': total})


class AdminCustomerListView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request):
        qs = Customer.objects.all().order_by('-id')
        keyword = (request.query_params.get('keyword') or '').strip()
        if keyword:
            qs = qs.filter(Q(name__icontains=keyword) | Q(phone__icontains=keyword))
        return _page(request, qs)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return success(CustomerSerializer(obj).data)
        return error(str(serializer.errors), status=400)


class AdminCustomerDetailView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request, pk):
        obj = Customer.objects.filter(pk=pk).first()
        if not obj:
            return error('客户不存在', status=404)
        return success(CustomerSerializer(obj).data)

    def put(self, request, pk):
        obj = Customer.objects.filter(pk=pk).first()
        if not obj:
            return error('客户不存在', status=404)
        serializer = CustomerSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            return success(CustomerSerializer(obj).data)
        return error(str(serializer.errors), status=400)

    def delete(self, request, pk):
        obj = Customer.objects.filter(pk=pk).first()
        if not obj:
            return error('客户不存在', status=404)
        obj.delete()
        return success(True)


class AdminCustomerBehaviorsView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request, pk):
        rows = CustomerBehavior.objects.filter(customer_id=pk).select_related('customer').order_by('-created_at')[:100]
        return success(CustomerBehaviorSerializer(rows, many=True).data)


class MallAuthRegisterView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = MallRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error(str(serializer.errors), status=400)
        customer = serializer.save()
        return success(
            {
                "customer_id": customer.id,
                "user": CustomerSerializer(customer).data,
            },
            "注册成功",
        )


class MallAuthLoginView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = MallLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error(str(serializer.errors), status=400)
        phone = serializer.validated_data["phone"]
        password = serializer.validated_data["password"]
        customer = Customer.objects.filter(phone=phone).first()
        if not customer or not customer.verify_password(password):
            return error("手机号或密码错误", status=401)
        customer.last_active_at = timezone.now()
        customer.save(update_fields=["last_active_at", "updated_at"])
        return success({"customer_id": customer.id, "user": CustomerSerializer(customer).data}, "登录成功")


class MallAuthProfileView(APIView):
    authentication_classes = []

    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        if not customer_id:
            return error("缺少customer_id", status=400)
        customer = Customer.objects.filter(pk=customer_id).first()
        if not customer:
            return error("用户不存在", status=404)
        return success(CustomerSerializer(customer).data)
