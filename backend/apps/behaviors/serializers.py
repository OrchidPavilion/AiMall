from rest_framework import serializers

from apps.products.models import Product
from .models import CustomerBehavior


class CustomerBehaviorSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    type = serializers.CharField(source="behavior_type", read_only=True)
    description = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    relatedProductId = serializers.SerializerMethodField()
    behaviorTypeLabel = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomerBehavior
        fields = [
            "id",
            "customer",
            "customer_name",
            "behavior_type",
            "type",
            "target_type",
            "target_id",
            "target_name",
            "source_page",
            "extra_data",
            "created_at",
            "createdAt",
            "description",
            "relatedProductId",
            "behaviorTypeLabel",
        ]

    def get_description(self, obj):
        target_name = self.get_target_name(obj)
        if obj.behavior_type == "PURCHASE":
            names = []
            total_amount = None
            if isinstance(obj.extra_data, dict):
                names = [str(x) for x in (obj.extra_data.get("item_names") or []) if str(x).strip()]
                total_amount = obj.extra_data.get("total_amount")
            if not names and target_name:
                names = [x.strip() for x in str(target_name).split("、") if x.strip()]
            names_text = "、".join(names) if names else (target_name or "商品")
            if total_amount is not None:
                try:
                    amount_text = f"{(float(total_amount) / 100):.2f}"
                except Exception:
                    amount_text = str(total_amount)
                return f"购买了{names_text}商品，总价格为{amount_text}元"
            return f"购买了{names_text}商品"
        mapping = {
            "SEARCH": f"搜索了 {target_name}",
            "CLICK_CATEGORY": f"点击了分类 {target_name}",
            "VIEW_PRODUCT": f"点击了商品详情 {target_name}",
            "ADD_TO_CART": f"将 {target_name} 加入购物车",
        }
        return mapping.get(obj.behavior_type, target_name or "执行了操作")

    def get_relatedProductId(self, obj):
        return obj.target_id if obj.target_type == "PRODUCT" else None

    def get_behaviorTypeLabel(self, obj):
        return {
            "SEARCH": "搜索",
            "CLICK_CATEGORY": "点击分类",
            "VIEW_PRODUCT": "浏览商品详情",
            "ADD_TO_CART": "加入购物车",
            "PURCHASE": "购买",
        }.get(obj.behavior_type, obj.behavior_type or "未知")

    def get_target_name(self, obj):
        if obj.target_name:
            return obj.target_name
        if obj.target_type == "PRODUCT" and obj.target_id:
            return Product.objects.filter(pk=obj.target_id).values_list("name", flat=True).first() or f"商品#{obj.target_id}"
        if obj.target_type == "CATEGORY" and obj.target_id:
            return f"分类#{obj.target_id}"
        return obj.target_name or ""
