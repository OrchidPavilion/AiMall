from unittest.mock import patch

import numpy as np
from django.test import TestCase

from apps.behaviors.models import CustomerBehavior
from apps.categories.models import ProductCategory
from apps.customers.models import Customer
from apps.products.models import Product
from .models import RecommendationSetting
from .services import (
    InteractionDataset,
    _evaluate_algorithm_on_dataset,
    build_recommendations_for_customer,
    build_interaction_dataset,
    clear_generated_thesis_sample_data,
    generate_thesis_experiment_sample_data,
    get_recommendation_setting,
    recommend_for_customer_by_algorithm,
    THESIS_SAMPLE_CUSTOMER_ADDRESS,
    THESIS_SAMPLE_CUSTOMER_HOBBY,
    THESIS_SAMPLE_CUSTOMER_PREFIX,
)


class RecommendationServiceTests(TestCase):
    def create_customer(self, suffix: str) -> Customer:
        return Customer.objects.create(
            name=f"客户{suffix}",
            phone=f"1390000{suffix:0>4}",
        )

    def create_category(self, name: str, parent: ProductCategory | None = None) -> ProductCategory:
        return ProductCategory.objects.create(name=name, parent=parent)

    def create_product(
        self,
        name: str,
        category: ProductCategory,
        *,
        sales_count: int = 0,
        view_count: int = 0,
        sort: int = 0,
    ) -> Product:
        return Product.objects.create(
            category=category,
            name=name,
            subtitle=f"{name} 副标题",
            summary=f"{name} 商品简介",
            main_image=f"https://example.com/{name}.png",
            default_spec_name="默认规格",
            default_price=19900,
            sales_count=sales_count,
            view_count=view_count,
            sort=sort,
            status="ON_SHELF",
        )

    def create_behavior(self, customer: Customer, **kwargs) -> CustomerBehavior:
        payload = {
            "customer": customer,
            "behavior_type": "VIEW_PRODUCT",
            "target_type": "PRODUCT",
            "source_page": "TEST",
        }
        payload.update(kwargs)
        return CustomerBehavior.objects.create(**payload)

    def test_build_interaction_dataset_models_search_category_and_purchase_behaviors(self):
        category = self.create_category("手机")
        product_a = self.create_product("手机A", category, sales_count=30, view_count=20)
        product_b = self.create_product("手机B", category, sales_count=20, view_count=10)
        product_c = self.create_product("手机C", category, sales_count=10, view_count=5)
        customer = self.create_customer("1")

        self.create_behavior(
            customer,
            behavior_type="SEARCH",
            target_type="KEYWORD",
            target_name="手机",
            target_id=None,
        )
        self.create_behavior(
            customer,
            behavior_type="CLICK_CATEGORY",
            target_type="CATEGORY",
            target_id=category.id,
            target_name=category.name,
        )
        self.create_behavior(
            customer,
            behavior_type="PURCHASE",
            target_type="PRODUCT",
            target_id=None,
            target_name=product_c.name,
            extra_data={"item_ids": [product_c.id]},
            source_page="CART",
        )

        dataset = build_interaction_dataset(setting=get_recommendation_setting(), for_experiment=False)

        self.assertIn(customer.id, dataset.user_ids)
        self.assertEqual(dataset.train_items_by_user[customer.id], {product_a.id, product_b.id, product_c.id})
        self.assertEqual(dataset.data_summary["model_product_behaviors"], 3)
        self.assertEqual(dataset.data_summary["product_behavior_distribution"]["SEARCH"], 1)
        self.assertEqual(dataset.data_summary["product_behavior_distribution"]["CLICK_CATEGORY"], 1)
        self.assertEqual(dataset.data_summary["product_behavior_distribution"]["PURCHASE"], 1)

    def test_search_and_category_behaviors_can_drive_algorithmic_recommendations(self):
        phone_category = self.create_category("电脑")
        accessory_category = self.create_category("配件")
        anchor_product = self.create_product("Laptop Pro", phone_category, sales_count=10, view_count=20)
        candidate_product = self.create_product("Wireless Mouse", accessory_category, sales_count=8, view_count=12)

        similar_customer = self.create_customer("2")
        target_customer = self.create_customer("3")

        self.create_behavior(similar_customer, target_id=anchor_product.id, target_name=anchor_product.name)
        self.create_behavior(similar_customer, target_id=candidate_product.id, target_name=candidate_product.name)
        self.create_behavior(
            target_customer,
            behavior_type="SEARCH",
            target_type="KEYWORD",
            target_name="Laptop Pro",
            target_id=None,
        )
        self.create_behavior(
            target_customer,
            behavior_type="CLICK_CATEGORY",
            target_type="CATEGORY",
            target_id=phone_category.id,
            target_name=phone_category.name,
        )

        rows = recommend_for_customer_by_algorithm(
            target_customer.id,
            "USER_CF",
            top_n=3,
            setting=get_recommendation_setting(),
            allow_fallback=False,
        )

        self.assertTrue(rows)
        self.assertEqual(rows[0][0], candidate_product.id)

    def test_evaluate_algorithm_does_not_fallback_to_popularity(self):
        dataset = InteractionDataset(
            user_ids=[1],
            item_ids=[101, 102],
            user_index={1: 0},
            item_index={101: 0, 102: 1},
            matrix=np.array([[1.0, 0.0]], dtype=np.float64),
            train_items_by_user={1: {101}},
            test_items_by_user={1: {102}},
            item_popularity={101: 1.0, 102: 0.0},
            user_names={1: "测试用户"},
            item_names={101: "商品A", 102: "商品B"},
            data_summary={},
        )
        setting = RecommendationSetting(
            online_algorithm="USER_CF",
            top_n=10,
            neighbor_k=10,
            als_factors=12,
            als_iterations=8,
            als_alpha=20,
            als_regularization=0.1,
            behavior_weights={},
        )

        with patch("apps.recommendations.services._fit_with_overrides", return_value=object()), patch(
            "apps.recommendations.services._recommend_with_model", return_value=[]
        ), patch("apps.recommendations.services._popular_fallback") as popular_fallback:
            result = _evaluate_algorithm_on_dataset(dataset, setting, "USER_CF", (1, 2), [1])

        popular_fallback.assert_not_called()
        self.assertIsNotNone(result)
        self.assertEqual(result["users_evaluated"], 1)
        self.assertEqual(result["metrics_by_k"]["1"]["precision"], 0.0)
        self.assertEqual(result["metrics_by_k"]["1"]["recall"], 0.0)
        self.assertEqual(result["metrics_by_k"]["1"]["ndcg"], 0.0)
        self.assertEqual(result["metrics_by_k"]["1"]["hit_rate"], 0.0)
        self.assertEqual(result["metrics_by_k"]["1"]["coverage"], 0.0)

    def test_mall_recommendations_respect_top_n_setting_even_when_client_requests_more(self):
        category = self.create_category("数码")
        anchor_product = self.create_product("锚点商品", category, sales_count=10, view_count=10)
        rec_a = self.create_product("推荐商品A", category, sales_count=9, view_count=9)
        rec_b = self.create_product("推荐商品B", category, sales_count=8, view_count=8)
        rec_c = self.create_product("推荐商品C", category, sales_count=7, view_count=7)

        target_customer = self.create_customer("4")
        neighbor_a = self.create_customer("5")
        neighbor_b = self.create_customer("6")
        neighbor_c = self.create_customer("7")

        self.create_behavior(target_customer, target_id=anchor_product.id, target_name=anchor_product.name)

        self.create_behavior(neighbor_a, target_id=anchor_product.id, target_name=anchor_product.name)
        self.create_behavior(neighbor_a, target_id=rec_a.id, target_name=rec_a.name)
        self.create_behavior(neighbor_b, target_id=anchor_product.id, target_name=anchor_product.name)
        self.create_behavior(neighbor_b, target_id=rec_b.id, target_name=rec_b.name)
        self.create_behavior(neighbor_c, target_id=anchor_product.id, target_name=anchor_product.name)
        self.create_behavior(neighbor_c, target_id=rec_c.id, target_name=rec_c.name)

        setting = get_recommendation_setting()
        setting.online_algorithm = "USER_CF"
        setting.top_n = 2
        setting.save(update_fields=["online_algorithm", "top_n", "updated_at"])

        response_default = self.client.get("/api/v1/mall/recommendations", {"customer_id": target_customer.id})
        payload_default = response_default.json()
        self.assertEqual(response_default.status_code, 200)
        self.assertEqual(payload_default["code"], 0)
        self.assertEqual(len(payload_default["data"]), 2)

        response_large = self.client.get(
            "/api/v1/mall/recommendations",
            {"customer_id": target_customer.id, "size": 20},
        )
        payload_large = response_large.json()
        self.assertEqual(response_large.status_code, 200)
        self.assertEqual(payload_large["code"], 0)
        self.assertEqual(len(payload_large["data"]), 2)

    def test_build_recommendations_uses_online_algorithm_setting(self):
        customer = self.create_customer("8")
        setting = get_recommendation_setting()
        setting.online_algorithm = "ITEM_CF"
        setting.save(update_fields=["online_algorithm", "updated_at"])

        with patch("apps.recommendations.services.recommend_for_customer_by_algorithm", return_value=[]) as mocked:
            build_recommendations_for_customer(customer, persist=False)

        self.assertEqual(mocked.call_args.args[1], "ITEM_CF")

    def test_generated_thesis_sample_data_can_be_regenerated_cleanly(self):
        category_a = self.create_category("户外")
        category_b = self.create_category("家居")
        for index in range(10):
            self.create_product(f"户外商品{index}", category_a, sales_count=20 - index, view_count=10 + index)
            self.create_product(f"家居商品{index}", category_b, sales_count=30 - index, view_count=5 + index)

        first = generate_thesis_experiment_sample_data(
            target_customers=4,
            actions_per_customer=14,
            seed=1234,
            clear_existing_generated=True,
            clear_all_behaviors=False,
        )
        self.assertTrue(first["ok"])
        self.assertEqual(first["customer_count"], 4)
        self.assertGreater(first["created_behaviors"], 0)

        generated_customers = Customer.objects.filter(
            name__startswith=THESIS_SAMPLE_CUSTOMER_PREFIX,
            hobby=THESIS_SAMPLE_CUSTOMER_HOBBY,
            address=THESIS_SAMPLE_CUSTOMER_ADDRESS,
        )
        self.assertEqual(generated_customers.count(), 4)
        first_behavior_count = CustomerBehavior.objects.filter(customer__in=generated_customers).count()
        self.assertEqual(first_behavior_count, first["created_behaviors"])

        second = generate_thesis_experiment_sample_data(
            target_customers=4,
            actions_per_customer=14,
            seed=1234,
            clear_existing_generated=True,
            clear_all_behaviors=False,
        )
        self.assertTrue(second["ok"])
        generated_customers = Customer.objects.filter(
            name__startswith=THESIS_SAMPLE_CUSTOMER_PREFIX,
            hobby=THESIS_SAMPLE_CUSTOMER_HOBBY,
            address=THESIS_SAMPLE_CUSTOMER_ADDRESS,
        )
        self.assertEqual(generated_customers.count(), 4)
        second_behavior_count = CustomerBehavior.objects.filter(customer__in=generated_customers).count()
        self.assertEqual(second_behavior_count, second["created_behaviors"])
        self.assertEqual(second_behavior_count, first_behavior_count)

        cleared = clear_generated_thesis_sample_data()
        self.assertEqual(cleared["generated_customers_deleted"], 4)
        self.assertFalse(
            Customer.objects.filter(
                name__startswith=THESIS_SAMPLE_CUSTOMER_PREFIX,
                hobby=THESIS_SAMPLE_CUSTOMER_HOBBY,
                address=THESIS_SAMPLE_CUSTOMER_ADDRESS,
            ).exists()
        )
