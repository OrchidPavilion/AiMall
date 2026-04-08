from django.db import transaction
from rest_framework.views import APIView

from apps.common.response import error, success
from apps.customers.models import Customer
from apps.products.models import ProductSku
from .models import CartItem
from .serializers import CartItemSerializer


class MallCartItemsView(APIView):
    authentication_classes = []

    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return error('缺少customer_id', status=400)
        rows = CartItem.objects.filter(customer_id=customer_id).select_related('product', 'sku').order_by('-updated_at')
        return success(CartItemSerializer(rows, many=True).data)

    @transaction.atomic
    def post(self, request):
        customer_id = request.data.get('customer_id')
        sku_id = request.data.get('sku_id')
        qty = max(int(request.data.get('quantity') or 1), 1)
        try:
            customer = Customer.objects.get(pk=customer_id)
            sku = ProductSku.objects.select_related('product').get(pk=sku_id)
        except (Customer.DoesNotExist, ProductSku.DoesNotExist):
            return error('客户或SKU不存在', status=404)
        item, created = CartItem.objects.select_for_update().get_or_create(
            customer=customer,
            sku=sku,
            defaults={'product': sku.product, 'quantity': qty, 'checked': True},
        )
        if not created:
            item.quantity += qty
            item.product = sku.product
            item.save()
        return success(CartItemSerializer(item).data)


class MallCartItemDetailView(APIView):
    authentication_classes = []

    def put(self, request, pk):
        item = CartItem.objects.filter(pk=pk).select_related('product', 'sku').first()
        if not item:
            return error('购物车项不存在', status=404)
        if 'quantity' in request.data:
            item.quantity = max(int(request.data.get('quantity') or 1), 1)
        if 'checked' in request.data:
            item.checked = bool(request.data.get('checked'))
        item.save()
        return success(CartItemSerializer(item).data)

    def delete(self, request, pk):
        item = CartItem.objects.filter(pk=pk).first()
        if not item:
            return error('购物车项不存在', status=404)
        item.delete()
        return success(True)


class MallCartSettlementPreviewView(APIView):
    authentication_classes = []

    def post(self, request):
        customer_id = request.data.get('customer_id')
        ids = request.data.get('item_ids') or []
        qs = CartItem.objects.filter(customer_id=customer_id, checked=True).select_related('sku')
        if ids:
            qs = qs.filter(id__in=ids)
        total = sum((i.sku.price or 0) * i.quantity for i in qs)
        return success({'total_amount': total, 'item_count': qs.count(), 'message': '结算预览（V1占位）'})
