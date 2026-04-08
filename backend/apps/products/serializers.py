from rest_framework import serializers

from apps.categories.models import ProductCategory
from .models import Product, ProductImage, ProductSku


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "sort"]


class ProductSkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSku
        fields = [
            "id",
            "sku_code",
            "spec_values",
            "spec_name_text",
            "price",
            "stock",
            "image_url",
            "is_default",
            "status",
        ]


class ProductAdminWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(source="category", queryset=ProductCategory.objects.all())
    skus = ProductSkuSerializer(many=True, required=False)
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "subtitle",
            "category_id",
            "main_image",
            "default_spec_name",
            "default_price",
            "sales_count",
            "view_count",
            "status",
            "sort",
            "summary",
            "detail_content",
            "skus",
            "images",
        ]

    def create(self, validated_data):
        skus = validated_data.pop("skus", [])
        images = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)
        self._sync_children(product, skus, images)
        return product

    def update(self, instance, validated_data):
        skus = validated_data.pop("skus", None)
        images = validated_data.pop("images", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if skus is not None or images is not None:
            self._sync_children(instance, skus or [], images or [])
        return instance

    def _sync_children(self, product, skus, images):
        product.skus.all().delete()
        product.images.all().delete()
        created_skus = []
        for i, sku in enumerate(skus or []):
            created_skus.append(ProductSku.objects.create(product=product, **sku))
        for img in images or []:
            ProductImage.objects.create(product=product, **img)
        if created_skus:
            default_sku = next((s for s in created_skus if s.is_default), created_skus[0])
            product.default_price = default_sku.price
            product.default_spec_name = default_sku.spec_name_text or product.default_spec_name or "默认规格"
            product.save(update_fields=["default_price", "default_spec_name", "updated_at"])


class ProductSummarySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_id = serializers.IntegerField(source="category.id", read_only=True)
    price = serializers.SerializerMethodField()
    sales = serializers.IntegerField(source="sales_count", read_only=True)
    views = serializers.IntegerField(source="view_count", read_only=True)
    image = serializers.CharField(source="main_image", read_only=True)
    default_spec = serializers.CharField(source="default_spec_name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category_name",
            "category_id",
            "image",
            "default_spec",
            "price",
            "sales",
            "views",
            "status",
            "created_at",
        ]

    def get_price(self, obj):
        return round((obj.default_price or 0) / 100, 2)


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    skus = ProductSkuSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "subtitle",
            "category",
            "category_name",
            "main_image",
            "default_spec_name",
            "default_price",
            "sales_count",
            "view_count",
            "status",
            "sort",
            "summary",
            "detail_content",
            "skus",
            "images",
            "created_at",
            "updated_at",
        ]
