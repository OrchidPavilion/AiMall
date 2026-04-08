from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView

from apps.common.permissions import IsAdminToken
from apps.common.response import error, success
from apps.products.models import Product
from .models import ProductCategory
from .serializers import ProductCategorySerializer, ProductCategoryTreeSerializer


def _build_tree():
    roots = ProductCategory.objects.filter(parent__isnull=True).prefetch_related('children__children').order_by('sort', 'id')
    return ProductCategoryTreeSerializer(roots, many=True).data


class AdminCategoryTreeView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request):
        qs = ProductCategory.objects.annotate(product_count=Count('products')).order_by('sort', 'id')
        by_parent = {}
        for c in qs:
            by_parent.setdefault(c.parent_id, []).append(c)

        def build(node):
            data = ProductCategorySerializer(node).data
            data['children'] = [build(x) for x in by_parent.get(node.id, [])]
            return data

        data = [build(x) for x in by_parent.get(None, [])]
        return success(data)

    def post(self, request):
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return success(ProductCategorySerializer(obj).data)
        return error(str(serializer.errors), status=400)


class AdminCategoryDetailView(APIView):
    permission_classes = [IsAdminToken]

    def put(self, request, pk):
        try:
            obj = ProductCategory.objects.get(pk=pk)
        except ProductCategory.DoesNotExist:
            return error('分类不存在', status=404)
        serializer = ProductCategorySerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            return success(ProductCategorySerializer(obj).data)
        return error(str(serializer.errors), status=400)

    def delete(self, request, pk):
        try:
            obj = ProductCategory.objects.get(pk=pk)
        except ProductCategory.DoesNotExist:
            return error('分类不存在', status=404)
        if obj.children.exists():
            return error('存在子分类，不能删除', status=400)
        if Product.objects.filter(category=obj).exists():
            return error('存在关联商品，不能删除', status=400)
        obj.delete()
        return success(True)


class MallCategoryTreeView(APIView):
    authentication_classes = []

    def get(self, request):
        return success(_build_tree())
