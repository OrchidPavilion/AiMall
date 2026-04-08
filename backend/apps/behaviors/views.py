from django.utils import timezone
from rest_framework.views import APIView

from apps.common.response import error, success
from apps.customers.models import Customer
from apps.products.models import Product
from .models import CustomerBehavior
from .serializers import CustomerBehaviorSerializer


class MallBehaviorCreateView(APIView):
    authentication_classes = []

    def post(self, request):
        customer_id = request.data.get('customer_id')
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return error('客户不存在', status=404)
        target_type = request.data.get('target_type')
        target_id = request.data.get('target_id') or None
        target_name = (request.data.get('target_name') or '').strip()
        if not target_name and target_type == 'PRODUCT' and target_id:
            target_name = Product.objects.filter(pk=target_id).values_list('name', flat=True).first() or ''

        behavior = CustomerBehavior.objects.create(
            customer=customer,
            behavior_type=request.data.get('behavior_type'),
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            source_page=request.data.get('source_page') or '',
            extra_data=request.data.get('extra_data') or None,
        )
        customer.last_active_at = timezone.now()
        customer.save(update_fields=['last_active_at'])
        return success(CustomerBehaviorSerializer(behavior).data)
