from django.db import models


class UserRecommendation(models.Model):
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="recommendations")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="recommended_to")
    score = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    reason = models.CharField(max_length=255, blank=True, default="")
    batch_no = models.CharField(max_length=64)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at", "-score", "id"]


class RecommendationSetting(models.Model):
    ALGORITHM_CHOICES = [
        ("USER_CF", "基于用户的协同过滤"),
        ("ITEM_CF", "基于物品的协同过滤"),
        ("ALS", "交替最小二乘矩阵分解"),
    ]

    singleton_key = models.CharField(max_length=32, unique=True, default="default")
    online_algorithm = models.CharField(max_length=20, choices=ALGORITHM_CHOICES, default="ALS")
    behavior_weights = models.JSONField(default=dict, blank=True)
    top_n = models.PositiveIntegerField(default=10)
    neighbor_k = models.PositiveIntegerField(default=10)
    als_factors = models.PositiveIntegerField(default=12)
    als_regularization = models.DecimalField(max_digits=6, decimal_places=4, default=0.1000)
    als_iterations = models.PositiveIntegerField(default=8)
    als_alpha = models.PositiveIntegerField(default=20)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RecommendationExperimentRun(models.Model):
    STATUS_CHOICES = [
        ("SUCCESS", "成功"),
        ("FAILED", "失败"),
    ]
    name = models.CharField(max_length=100, default="实验")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SUCCESS")
    message = models.CharField(max_length=255, blank=True, default="")
    config_snapshot = models.JSONField(default=dict, blank=True)
    data_summary = models.JSONField(default=dict, blank=True)
    metrics_summary = models.JSONField(default=dict, blank=True)
    chart_payload = models.JSONField(default=dict, blank=True)
    sample_recommendations = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
