from rest_framework import serializers

from .models import ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        source="parent", queryset=ProductCategory.objects.all(), allow_null=True, required=False
    )
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "parent_id",
            "level",
            "icon",
            "sort",
            "enabled",
            "product_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["level", "created_at", "updated_at"]

    def get_product_count(self, obj):
        if getattr(obj, "product_count", None) is not None:
            return obj.product_count
        return obj.products.count() if hasattr(obj, "products") else 0


class ProductCategoryTreeSerializer(ProductCategorySerializer):
    children = serializers.SerializerMethodField()

    class Meta(ProductCategorySerializer.Meta):
        fields = ProductCategorySerializer.Meta.fields + ["children"]

    def get_children(self, obj):
        qs = obj.children.all().order_by("sort", "id")
        return ProductCategoryTreeSerializer(qs, many=True).data
