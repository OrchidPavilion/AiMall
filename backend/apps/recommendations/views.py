from collections import defaultdict
import shutil
from pathlib import Path

from rest_framework.views import APIView
from django.db.models import Q
from django.conf import settings

from apps.common.permissions import IsAdminToken
from apps.common.response import error, success
from apps.behaviors.models import CustomerBehavior
from apps.carts.models import CartItem
from apps.customers.models import Customer
from apps.products.models import Product
from apps.products.serializers import ProductSummarySerializer
from .models import UserRecommendation, RecommendationExperimentRun
from .serializers import (
    UserRecommendationSerializer,
    RecommendationSettingSerializer,
    RecommendationExperimentRunSerializer,
)
from .exporters import export_experiment_artifacts
from .services import (
    build_recommendations_for_customer,
    get_recommendation_setting,
    ALGORITHM_LABELS,
    get_customer_algorithm_compare,
    run_experiment,
    get_data_analysis_overview,
    generate_experiment_behavior_replay,
    generate_recommendation_experiment_sample_data,
    reset_recommendation_workspace,
)


class AdminRecommendationListView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request):
        keyword = (request.query_params.get('keyword') or '').strip()
        customer_id = request.query_params.get('customer_id')
        qs = UserRecommendation.objects.select_related('customer', 'product').all()
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if keyword:
            qs = qs.filter(Q(customer__name__icontains=keyword) | Q(customer__phone__icontains=keyword))
        rows = UserRecommendationSerializer(qs.order_by('customer_id', '-score'), many=True).data
        grouped = defaultdict(lambda: {"products": []})
        for r in rows:
            item = grouped[r['customer']]
            item.update({
                'customerId': r['customer'],
                'customerName': r['customer_name'],
                'phone': r['phone'],
                'score': max(item.get('score', 0), float(r['score'])),
                'reason': r['reason'],
                'generatedAt': r['generated_at'],
            })
            item['products'].append(r['product_name'])
        return success(list(grouped.values()))


class AdminRecommendationRefreshView(APIView):
    permission_classes = [IsAdminToken]

    def post(self, request):
        customer_id = request.data.get('customer_id')
        if customer_id:
            customers = Customer.objects.filter(pk=customer_id)
        else:
            customers = Customer.objects.all()[:100]
        for customer in customers:
            build_recommendations_for_customer(customer, persist=True)
        return success(True, '推荐刷新成功')


class AdminRecommendationSettingView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request):
        setting = get_recommendation_setting()
        return success(RecommendationSettingSerializer(setting).data)

    def put(self, request):
        setting = get_recommendation_setting()
        serializer = RecommendationSettingSerializer(setting, data=request.data, partial=True)
        if not serializer.is_valid():
            return error(str(serializer.errors), status=400)
        obj = serializer.save()
        return success(RecommendationSettingSerializer(obj).data, "设置已更新")


class AdminRecommendationDataAnalysisView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request):
        return success(get_data_analysis_overview())


class AdminRecommendationExperimentRunView(APIView):
    permission_classes = [IsAdminToken]

    def post(self, request):
        top_ks = request.data.get("top_ks") or [5, 10, 20]
        result = run_experiment(top_ks=top_ks)
        run = RecommendationExperimentRun.objects.create(
            name=request.data.get("name") or "推荐算法对比实验",
            status="SUCCESS" if result.get("ok") else "FAILED",
            message=result.get("message", ""),
            config_snapshot={
                "top_ks": top_ks,
                "setting": RecommendationSettingSerializer(get_recommendation_setting()).data,
            },
            data_summary=result.get("data_summary") or {},
            metrics_summary=result.get("metrics_summary") or {},
            chart_payload=result.get("chart_payload") or {},
            sample_recommendations=result.get("sample_recommendations") or {},
        )
        payload = RecommendationExperimentRunSerializer(run).data
        payload["ok"] = bool(result.get("ok"))
        return success(payload, result.get("message", "实验已执行"))

    def get(self, request):
        qs = RecommendationExperimentRun.objects.all()[:30]
        return success(RecommendationExperimentRunSerializer(qs, many=True).data)

    def delete(self, request):
        deleted = RecommendationExperimentRun.objects.count()
        RecommendationExperimentRun.objects.all().delete()
        export_root = Path(settings.MEDIA_ROOT) / "recommendation_exports"
        if export_root.exists():
            shutil.rmtree(export_root, ignore_errors=True)
        return success({"deleted": deleted}, "实验记录已清空")


class AdminRecommendationBehaviorReplayView(APIView):
    permission_classes = [IsAdminToken]

    def post(self, request):
        target_customers = int(request.data.get("target_customers") or 24)
        actions_per_customer = int(request.data.get("actions_per_customer") or 40)
        seed = int(request.data.get("seed") or 20260408)
        clear_all_behaviors = str(request.data.get("clear_all_behaviors", "1")) != "0"
        result = generate_recommendation_experiment_sample_data(
            target_customers=target_customers,
            actions_per_customer=actions_per_customer,
            seed=seed,
            clear_existing_generated=True,
            clear_all_behaviors=clear_all_behaviors,
        )
        return success(result, result.get("message", "已完成"))


class AdminRecommendationBehaviorResetView(APIView):
    permission_classes = [IsAdminToken]

    def delete(self, request):
        clear_carts = str(request.query_params.get("clear_carts", "1")) != "0"
        clear_recommendations = str(request.query_params.get("clear_recommendations", "1")) != "0"
        reset_summary = reset_recommendation_workspace(
            clear_behaviors=True,
            clear_carts=clear_carts,
            clear_recommendations=clear_recommendations,
            clear_generated_customers=True,
        )
        return success(
            {
                **reset_summary,
            },
            "行为轨迹已清空",
        )


class AdminRecommendationExperimentDetailView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request, pk):
        obj = RecommendationExperimentRun.objects.filter(pk=pk).first()
        if not obj:
            return error("实验结果不存在", status=404)
        return success(RecommendationExperimentRunSerializer(obj).data)


class AdminRecommendationExperimentExportView(APIView):
    permission_classes = [IsAdminToken]

    def post(self, request, pk):
        obj = RecommendationExperimentRun.objects.filter(pk=pk).first()
        if not obj:
            return error("实验结果不存在", status=404)
        base_url = request.build_absolute_uri("/").rstrip("/")
        data = export_experiment_artifacts(obj, base_url=base_url)
        return success(data, "实验材料导出成功")


class AdminCustomerRecommendationCompareView(APIView):
    permission_classes = [IsAdminToken]

    def get(self, request, pk):
        customer = Customer.objects.filter(pk=pk).first()
        if not customer:
            return error("客户不存在", status=404)
        top_n = max(min(int(request.query_params.get("top_n", 5) or 5), 20), 1)
        compare = get_customer_algorithm_compare(customer.id, top_n=top_n)
        products = {}
        for alg_rows in compare.values():
            for pid, _, _ in alg_rows:
                products.setdefault(pid, None)
        if products:
            for p in Product.objects.filter(id__in=products.keys()):
                products[p.id] = p
        payload = {}
        for alg, alg_rows in compare.items():
            positive_scores = [float(score) for _, score, _ in alg_rows if float(score) > 0]
            min_score = min(positive_scores) if positive_scores else 0.0
            max_score = max(positive_scores) if positive_scores else 0.0
            def normalize_score(raw: float) -> float:
                raw = float(raw)
                if raw <= 0:
                    return 0.0
                if max_score <= min_score:
                    return 100.0
                return round((raw - min_score) / (max_score - min_score) * 100, 2)
            payload[alg] = {
                "algorithm": alg,
                "label": ALGORITHM_LABELS.get(alg, alg),
                "items": [
                    dict(
                        ProductSummarySerializer(products[pid]).data,
                        score=round(float(score), 4),  # 原始分数（算法内部尺度）
                        score_normalized=normalize_score(float(score)),  # 归一化分数（0-100，便于展示）
                        reason=reason,
                    )
                    for pid, score, reason in alg_rows
                    if products.get(pid)
                ],
            }
        return success({
            "customer": {"id": customer.id, "name": customer.name, "phone": customer.phone},
            "algorithms": payload,
        })


class MallRecommendationListView(APIView):
    authentication_classes = []

    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return error('缺少customer_id', status=400)
        setting = get_recommendation_setting()
        setting_top_n = max(int(setting.top_n or 10), 1)
        raw_size = request.query_params.get('size')
        try:
            requested_size = int(raw_size) if raw_size not in (None, '') else setting_top_n
        except (TypeError, ValueError):
            return error('size参数格式错误', status=400)
        size = max(min(requested_size, setting_top_n), 1)
        exclude_ids = [x for x in (request.query_params.get('exclude_ids') or '').split(',') if x]
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return error('客户不存在', status=404)
        results = build_recommendations_for_customer(customer, limit=size, exclude_ids=exclude_ids, persist=False)
        data = []
        for p, score, reason in results:
            row = ProductSummarySerializer(p).data
            row['score'] = score
            row['reason'] = reason
            data.append(row)
        return success(data)
