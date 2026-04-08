from rest_framework import serializers

from .models import UserRecommendation, RecommendationSetting, RecommendationExperimentRun


class UserRecommendationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    phone = serializers.CharField(source="customer.phone", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = UserRecommendation
        fields = [
            "id",
            "customer",
            "customer_name",
            "phone",
            "product",
            "product_name",
            "score",
            "reason",
            "batch_no",
            "generated_at",
        ]


class RecommendationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationSetting
        fields = [
            "online_algorithm",
            "behavior_weights",
            "top_n",
            "neighbor_k",
            "als_factors",
            "als_regularization",
            "als_iterations",
            "als_alpha",
            "updated_at",
        ]


class RecommendationExperimentRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationExperimentRun
        fields = [
            "id",
            "name",
            "status",
            "message",
            "config_snapshot",
            "data_summary",
            "metrics_summary",
            "chart_payload",
            "sample_recommendations",
            "created_at",
        ]
