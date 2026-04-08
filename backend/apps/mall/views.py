from rest_framework.views import APIView

from apps.categories.models import ProductCategory
from apps.categories.serializers import ProductCategoryTreeSerializer
from apps.common.response import success
from apps.products.models import Product
from apps.products.serializers import ProductSummarySerializer


class MallHomeView(APIView):
    authentication_classes = []

    def get(self, request):
        categories = ProductCategory.objects.filter(parent__isnull=True).prefetch_related('children__children').order_by('sort', 'id')
        random_products = Product.objects.filter(status='ON_SHELF').order_by('id')[:20]
        return success(
            {
                'categories': ProductCategoryTreeSerializer(categories, many=True).data,
                'random_products': ProductSummarySerializer(random_products, many=True).data,
            }
        )
