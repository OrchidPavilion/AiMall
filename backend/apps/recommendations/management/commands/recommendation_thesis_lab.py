import json

from django.core.management.base import BaseCommand, CommandError

from apps.recommendations.models import RecommendationExperimentRun
from apps.recommendations.serializers import RecommendationSettingSerializer
from apps.recommendations.services import (
    build_interaction_dataset,
    generate_thesis_experiment_sample_data,
    get_recommendation_setting,
    run_experiment,
    verify_online_algorithm_switch,
)


class Command(BaseCommand):
    help = "清空并重建论文实验样本，验证线上推荐算法切换，并执行三算法实验。"

    def add_arguments(self, parser):
        parser.add_argument("--customers", type=int, default=60, help="生成的论文样本用户数")
        parser.add_argument("--actions", type=int, default=60, help="每个论文样本用户生成的行为数")
        parser.add_argument("--total-behaviors", type=int, default=None, help="生成精确总行为数，并随机分配到各用户")
        parser.add_argument("--seed", type=int, default=20260408, help="随机种子，保证可重复")
        parser.add_argument(
            "--clear-all-behaviors",
            action="store_true",
            help="先清空全库行为/购物车/推荐，再生成论文实验样本",
        )
        parser.add_argument(
            "--clear-all-customers",
            action="store_true",
            help="先清空全库客户信息及其行为/购物车/推荐，再生成论文实验样本",
        )
        parser.add_argument(
            "--product-only-behaviors",
            action="store_true",
            help="生成的行为全部指向具体商品，适合论文中的用户-商品访问记录实验",
        )
        parser.add_argument(
            "--skip-seed",
            action="store_true",
            help="跳过样本生成，只做算法切换验证与实验运行",
        )
        parser.add_argument(
            "--skip-experiment",
            action="store_true",
            help="跳过三算法实验，只做样本生成与线上算法切换验证",
        )
        parser.add_argument("--probe-top-n", type=int, default=5, help="验证线上算法切换时查看前N条推荐")
        parser.add_argument("--experiment-name", default="论文三算法对比实验", help="保存实验记录时使用的名称")

    def handle(self, *args, **options):
        payload = {
            "seed_result": None,
            "dataset_summary": None,
            "algorithm_switch_verification": None,
            "experiment_result": None,
            "saved_experiment_id": None,
        }

        if not options["skip_seed"]:
            seed_result = generate_thesis_experiment_sample_data(
                target_customers=options["customers"],
                actions_per_customer=options["actions"],
                total_behaviors=options["total_behaviors"],
                seed=options["seed"],
                clear_existing_generated=True,
                clear_all_behaviors=options["clear_all_behaviors"],
                clear_all_customers=options["clear_all_customers"],
                product_only_behaviors=options["product_only_behaviors"],
            )
            if not seed_result.get("ok"):
                raise CommandError(seed_result.get("message") or "论文实验样本生成失败")
            payload["seed_result"] = seed_result

        payload["dataset_summary"] = build_interaction_dataset(for_experiment=False).data_summary

        verify_result = verify_online_algorithm_switch(top_n=options["probe_top_n"])
        if not verify_result.get("ok"):
            raise CommandError(verify_result.get("message") or "线上推荐算法切换验证失败")
        payload["algorithm_switch_verification"] = verify_result

        if not options["skip_experiment"]:
            experiment_result = run_experiment(top_ks=(5, 10, 20))
            payload["experiment_result"] = experiment_result
            run = RecommendationExperimentRun.objects.create(
                name=options["experiment_name"],
                status="SUCCESS" if experiment_result.get("ok") else "FAILED",
                message=experiment_result.get("message", ""),
                config_snapshot={
                    "seed": options["seed"],
                    "customers": options["customers"],
                    "actions": options["actions"],
                    "total_behaviors": options["total_behaviors"],
                    "product_only_behaviors": options["product_only_behaviors"],
                    "setting": RecommendationSettingSerializer(get_recommendation_setting()).data,
                },
                data_summary=experiment_result.get("data_summary") or {},
                metrics_summary=experiment_result.get("metrics_summary") or {},
                chart_payload=experiment_result.get("chart_payload") or {},
                sample_recommendations=experiment_result.get("sample_recommendations") or {},
            )
            payload["saved_experiment_id"] = run.id

        self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, default=float))
