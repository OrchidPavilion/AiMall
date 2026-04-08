from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.CharField(source="product.main_image", read_only=True)
    spec_name = serializers.CharField(source="sku.spec_name_text", read_only=True)
    unit_price = serializers.IntegerField(source="sku.price", read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "customer",
            "product",
            "sku",
            "quantity",
            "checked",
            "product_name",
            "product_image",
            "spec_name",
            "unit_price",
            "line_total",
            "created_at",
            "updated_at",
        ]

    def get_line_total(self, obj):
        return (obj.sku.price or 0) * (obj.quantity or 0)
