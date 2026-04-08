import os
import random
import uuid

from django.conf import settings
from django.db.models import Q
from rest_framework.views import APIView

from apps.common.permissions import IsAdminToken
from apps.common.response import error, success
from .models import Product, ProductSku
from .serializers import ProductAdminWriteSerializer, ProductDetailSerializer, ProductSummarySerializer


def _page_response(request, queryset, serializer_cls):
    page = max(int(request.query_params.get('page', 1) or 1), 1)
    page_size = max(min(int(request.query_params.get('page_size', 20) or 20), 100), 1)
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    rows = queryset[start:end]
    return success({
        'list': serializer_cls(rows, many=True).data,
        'page': page,
        'page_size': page_size,
        'total': total,
    })


class AdminProductListView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request):
        qs = Product.objects.select_related('category').all().order_by('-id')
        keyword = (request.query_params.get('keyword') or '').strip()
        category_id = request.query_params.get('category_id') or request.query_params.get('categoryId')
        status = request.query_params.get('status')
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if status:
            qs = qs.filter(status=status)
        return _page_response(request, qs, ProductSummarySerializer)

    def post(self, request):
        serializer = ProductAdminWriteSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return success(ProductDetailSerializer(product).data)
        return error(str(serializer.errors), status=400)


class AdminProductDetailView(APIView):
    permission_classes = [IsAdminToken]

    def get_object(self, pk):
        return Product.objects.select_related('category').prefetch_related('skus', 'images').filter(pk=pk).first()

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return error('商品不存在', status=404)
        return success(ProductDetailSerializer(obj).data)

    def put(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return error('商品不存在', status=404)
        serializer = ProductAdminWriteSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            return success(ProductDetailSerializer(obj).data)
        return error(str(serializer.errors), status=400)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return error('商品不存在', status=404)
        obj.delete()
        return success(True)


class AdminProductStatusView(APIView):
    permission_classes = [IsAdminToken]

    def post(self, request, pk):
        status_val = request.data.get('status')
        if status_val not in {'DRAFT', 'ON_SHELF', 'OFF_SHELF'}:
            return error('状态不合法', status=400)
        updated = Product.objects.filter(pk=pk).update(status=status_val)
        if not updated:
            return error('商品不存在', status=404)
        return success(True)


class AdminProductUploadView(APIView):
    permission_classes = [IsAdminToken]

    def post(self, request):
        f = request.FILES.get('file')
        if not f:
            return error('未上传文件', status=400)
        ext = os.path.splitext(f.name)[1] or '.jpg'
        filename = f"{uuid.uuid4().hex}{ext}"
        folder = settings.MEDIA_ROOT / 'uploads' / 'products'
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / filename
        with open(path, 'wb+') as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        url = f"{settings.MEDIA_URL}uploads/products/{filename}"
        return success({'url': url, 'name': f.name})


class MallProductListView(APIView):
    authentication_classes = []

    def get(self, request):
        qs = Product.objects.select_related('category').filter(status='ON_SHELF').order_by('-id')
        keyword = (request.query_params.get('keyword') or '').strip()
        category_id = request.query_params.get('category_id')
        if keyword:
            qs = qs.filter(name__icontains=keyword)
        if category_id:
            qs = qs.filter(Q(category_id=category_id) | Q(category__parent_id=category_id) | Q(category__parent__parent_id=category_id))
        return _page_response(request, qs, ProductSummarySerializer)


class MallProductRandomView(APIView):
    authentication_classes = []

    def get(self, request):
        size = max(min(int(request.query_params.get('size', 20) or 20), 100), 1)
        cursor = max(int(request.query_params.get('cursor', 0) or 0), 0)
        seed = int(request.query_params.get('seed', 0) or 0)
        qs = Product.objects.select_related('category').filter(status='ON_SHELF').order_by('id')
        items = list(qs)
        rnd = random.Random(seed or 20260223)
        rnd.shuffle(items)
        total = len(items)
        rows = items[cursor:cursor + size]
        next_cursor = cursor + len(rows)
        return success({'list': ProductSummarySerializer(rows, many=True).data, 'cursor': next_cursor, 'has_more': next_cursor < total})


class MallProductDetailView(APIView):
    authentication_classes = []

    def get(self, request, pk):
        obj = Product.objects.select_related('category').prefetch_related('skus', 'images').filter(pk=pk, status='ON_SHELF').first()
        if not obj:
            return error('商品不存在', status=404)
        Product.objects.filter(pk=obj.pk).update(view_count=obj.view_count + 1)
        obj.refresh_from_db()
        return success(ProductDetailSerializer(obj).data)
