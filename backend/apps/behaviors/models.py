from django.db import models


class CustomerBehavior(models.Model):
    TYPE_CHOICES = [
        ("SEARCH", "搜索"),
        ("CLICK_CATEGORY", "点击分类"),
        ("VIEW_PRODUCT", "查看商品"),
        ("ADD_TO_CART", "加入购物车"),
        ("PURCHASE", "购买"),
    ]
    TARGET_CHOICES = [
        ("KEYWORD", "关键词"),
        ("CATEGORY", "分类"),
        ("PRODUCT", "商品"),
    ]

    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="behaviors")
    behavior_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    target_type = models.CharField(max_length=32, choices=TARGET_CHOICES)
    target_id = models.BigIntegerField(null=True, blank=True)
    target_name = models.CharField(max_length=255, blank=True, default="")
    source_page = models.CharField(max_length=50, blank=True, default="")
    extra_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["customer", "-created_at"], name="idx_behavior_cust_time"),
            models.Index(fields=["behavior_type", "-created_at"], name="idx_behavior_type_time"),
        ]
