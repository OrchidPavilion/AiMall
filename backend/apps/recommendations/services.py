from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from decimal import Decimal
from time import perf_counter
from uuid import uuid4

import numpy as np
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone

from apps.behaviors.models import CustomerBehavior
from apps.carts.models import CartItem
from apps.categories.models import ProductCategory
from apps.customers.models import Customer
from apps.products.models import Product
from .models import RecommendationSetting, UserRecommendation

DEFAULT_BEHAVIOR_WEIGHTS = {
    "SEARCH": 1.0,
    "CLICK_CATEGORY": 1.0,
    "VIEW_PRODUCT": 2.0,
    "ADD_TO_CART": 4.0,
    "PURCHASE": 6.0,
}

ALGORITHM_LABELS = {
    "USER_CF": "基于用户的协同过滤算法",
    "ITEM_CF": "基于物品的协同过滤算法",
    "ALS": "基于交替最小二乘的矩阵分解算法",
}

SEARCH_EXPANSION_LIMIT = 8
CATEGORY_EXPANSION_LIMIT = 8
SEARCH_DECAY_FACTORS = (1.0, 0.88, 0.76, 0.64, 0.52, 0.4, 0.28, 0.16)
CATEGORY_DECAY_FACTORS = (1.0, 0.92, 0.84, 0.76, 0.68, 0.6, 0.52, 0.44)

THESIS_SAMPLE_CUSTOMER_PREFIX = "论文样本用户"
THESIS_SAMPLE_CUSTOMER_HOBBY = "推荐系统论文实验样本"
THESIS_SAMPLE_CUSTOMER_ADDRESS = "AUTO_GENERATED_RECOMMENDATION_THESIS_SAMPLE"
THESIS_SAMPLE_EXTRA_FLAG = "thesis_generated_sample"


def get_recommendation_setting() -> RecommendationSetting:
    obj, _ = RecommendationSetting.objects.get_or_create(
        singleton_key="default",
        defaults={"behavior_weights": DEFAULT_BEHAVIOR_WEIGHTS},
    )
    merged_weights = dict(DEFAULT_BEHAVIOR_WEIGHTS)
    merged_weights.update({k: v for k, v in (obj.behavior_weights or {}).items() if k in DEFAULT_BEHAVIOR_WEIGHTS})
    if obj.behavior_weights != merged_weights:
        obj.behavior_weights = merged_weights
        obj.save(update_fields=["behavior_weights", "updated_at"])
    return obj


def _weights_from_setting(setting: RecommendationSetting | None = None):
    setting = setting or get_recommendation_setting()
    merged = dict(DEFAULT_BEHAVIOR_WEIGHTS)
    merged.update({k: float(v) for k, v in (setting.behavior_weights or {}).items() if k in DEFAULT_BEHAVIOR_WEIGHTS})
    return merged


@dataclass
class InteractionDataset:
    user_ids: list[int]
    item_ids: list[int]
    user_index: dict[int, int]
    item_index: dict[int, int]
    matrix: np.ndarray  # train weights
    train_items_by_user: dict[int, set[int]]
    test_items_by_user: dict[int, set[int]]
    item_popularity: dict[int, float]
    user_names: dict[int, str]
    item_names: dict[int, str]
    data_summary: dict


def _real_behaviors_queryset():
    # 真实行为口径：默认排除实验回放生成的模拟行为
    return (
        CustomerBehavior.objects.exclude(source_page="EXPERIMENT_REPLAY")
        .exclude(customer__name__startswith="实验用户")
    )


def _product_behaviors_queryset():
    return (
        _real_behaviors_queryset().filter(target_type="PRODUCT", target_id__isnull=False)
        .select_related("customer")
        .order_by("customer_id", "created_at", "id")
    )


def _keyword_product_ids(keyword: str, cache: dict[str, list[int]]) -> list[int]:
    normalized = (keyword or "").strip()
    if not normalized:
        return []
    if normalized in cache:
        return cache[normalized]
    ids = list(
        Product.objects.filter(status="ON_SHELF")
        .filter(
            Q(name__icontains=normalized)
            | Q(subtitle__icontains=normalized)
            | Q(summary__icontains=normalized)
            | Q(category__name__icontains=normalized)
        )
        .order_by("-sales_count", "-view_count", "-sort", "-id")
        .values_list("id", flat=True)[:SEARCH_EXPANSION_LIMIT]
    )
    cache[normalized] = ids
    return ids


def _category_product_ids(category_id: int | None, cache: dict[int, list[int]]) -> list[int]:
    if not category_id:
        return []
    if category_id in cache:
        return cache[category_id]
    ids = list(
        Product.objects.filter(status="ON_SHELF")
        .filter(Q(category_id=category_id) | Q(category__parent_id=category_id) | Q(category__parent__parent_id=category_id))
        .order_by("-sales_count", "-view_count", "-sort", "-id")
        .values_list("id", flat=True)[:CATEGORY_EXPANSION_LIMIT]
    )
    cache[category_id] = ids
    return ids


def _normalize_product_ids(values) -> list[int]:
    if values is None:
        return []
    if not isinstance(values, (list, tuple, set)):
        values = [values]
    result: list[int] = []
    for value in values:
        try:
            pid = int(value)
        except (TypeError, ValueError):
            continue
        if pid > 0:
            result.append(pid)
    return result


def _purchase_product_ids(row: dict) -> list[int]:
    target_id = row.get("target_id")
    if target_id:
        return [int(target_id)]
    extra = row.get("extra_data") or {}
    return _normalize_product_ids(extra.get("item_ids") or extra.get("product_ids"))


def _weighted_targets(product_ids: list[int], base_weight: float, decay_factors: tuple[float, ...]) -> list[tuple[int, float]]:
    rows: list[tuple[int, float]] = []
    seen: set[int] = set()
    for idx, product_id in enumerate(product_ids):
        if product_id in seen:
            continue
        seen.add(product_id)
        factor = decay_factors[min(idx, len(decay_factors) - 1)] if decay_factors else 1.0
        rows.append((int(product_id), round(base_weight * factor, 6)))
    return rows


def _expand_behavior_targets(row: dict, weight: float, keyword_cache: dict[str, list[int]], category_cache: dict[int, list[int]]) -> list[tuple[int, float]]:
    behavior_type = row.get("behavior_type")
    target_type = row.get("target_type")
    target_id = row.get("target_id")
    target_name = row.get("target_name") or ""

    if target_type == "PRODUCT" and target_id:
        return [(int(target_id), round(weight, 6))]
    if behavior_type == "PURCHASE":
        return [(pid, round(weight, 6)) for pid in _purchase_product_ids(row)]
    if behavior_type == "SEARCH":
        return _weighted_targets(_keyword_product_ids(target_name, keyword_cache), weight, SEARCH_DECAY_FACTORS)
    if behavior_type == "CLICK_CATEGORY":
        try:
            category_id = int(target_id) if target_id else None
        except (TypeError, ValueError):
            category_id = None
        return _weighted_targets(_category_product_ids(category_id, category_cache), weight, CATEGORY_DECAY_FACTORS)
    return []


def build_interaction_dataset(setting: RecommendationSetting | None = None, for_experiment: bool = False) -> InteractionDataset:
    weights = _weights_from_setting(setting)
    rows = list(
        _real_behaviors_queryset().values(
            "customer_id",
            "behavior_type",
            "target_type",
            "target_id",
            "target_name",
            "created_at",
            "extra_data",
            "customer__name",
        )
    )

    agg = {}
    behavior_type_counter = Counter()
    all_behavior_counter = Counter(_real_behaviors_queryset().values_list("behavior_type", flat=True))
    product_event_count = 0  # 纳入建模权重后的商品行为数（受行为权重配置影响）
    product_event_total_count = 0  # 真实商品行为总数（不受权重过滤影响）
    keyword_cache: dict[str, list[int]] = {}
    category_cache: dict[int, list[int]] = {}
    for r in rows:
        bt = r["behavior_type"]
        if r.get("target_type") == "PRODUCT" and r.get("target_id"):
            product_event_total_count += 1
        if bt not in weights:
            continue
        w = float(weights.get(bt, 0) or 0)
        if w <= 0:
            continue
        expanded_targets = _expand_behavior_targets(r, w, keyword_cache, category_cache)
        if not expanded_targets:
            continue
        product_event_count += 1
        behavior_type_counter[bt] += 1
        for product_id, weighted_value in expanded_targets:
            key = (int(r["customer_id"]), int(product_id))
            cur = agg.get(key)
            if cur is None:
                agg[key] = {
                    "weight": weighted_value,
                    "last_at": r["created_at"],
                    "events": [(bt, r["created_at"])],
                }
            else:
                cur["weight"] += weighted_value
                if r["created_at"] > cur["last_at"]:
                    cur["last_at"] = r["created_at"]
                cur["events"].append((bt, r["created_at"]))

    if not agg:
        return InteractionDataset([], [], {}, {}, np.zeros((0, 0)), {}, {}, {}, {}, {}, {
            "total_behaviors": _real_behaviors_queryset().count(),
            "product_behaviors": 0,
            "model_product_behaviors": 0,
            "interactions": 0,
            "active_users": 0,
            "active_products": 0,
            "sparsity": 1.0,
            "behavior_type_distribution": dict(all_behavior_counter),
            "product_behavior_distribution": dict(behavior_type_counter),
            "data_scope": "REAL_ONLY",
        })

    user_ids = sorted({u for u, _ in agg.keys()})
    candidate_item_ids = sorted({i for _, i in agg.keys()})
    valid_item_ids = set(Product.objects.filter(id__in=candidate_item_ids, status="ON_SHELF").values_list("id", flat=True))
    item_ids = sorted(valid_item_ids)
    user_index = {u: idx for idx, u in enumerate(user_ids)}
    item_index = {i: idx for idx, i in enumerate(item_ids)}

    n_users, n_items = len(user_ids), len(item_ids)
    full = np.zeros((n_users, n_items), dtype=np.float64)
    train = np.zeros((n_users, n_items), dtype=np.float64)
    train_items_by_user = defaultdict(set)
    test_items_by_user = defaultdict(set)

    user_item_rows = defaultdict(list)
    for (u, i), v in agg.items():
        if i not in item_index:
            continue
        user_item_rows[u].append((i, v["weight"], v["last_at"]))

    for u, lst in user_item_rows.items():
        uidx = user_index[u]
        lst.sort(key=lambda x: x[2])
        test_count = 0
        if for_experiment and len(lst) >= 2:
            test_count = max(1, int(round(len(lst) * 0.2)))
            test_count = min(test_count, len(lst) - 1)
        test_items = {item for item, _, _ in lst[-test_count:]} if test_count else set()
        for item_id, weight, _ in lst:
            iidx = item_index[item_id]
            full[uidx, iidx] = float(weight)
            if item_id in test_items:
                test_items_by_user[u].add(item_id)
            else:
                train[uidx, iidx] = float(weight)
                train_items_by_user[u].add(item_id)
        if for_experiment and not train_items_by_user[u] and test_items_by_user[u]:
            # 保证训练集非空：将最早一个测试样本回退到训练集
            rollback = next(iter(test_items_by_user[u]))
            test_items_by_user[u].remove(rollback)
            train_items_by_user[u].add(rollback)
            iidx = item_index[rollback]
            train[uidx, iidx] = full[uidx, iidx]

    item_popularity = {item_ids[i]: float(train[:, i].sum()) for i in range(n_items)}
    user_names = dict(Customer.objects.filter(id__in=user_ids).values_list("id", "name"))
    item_names = dict(Product.objects.filter(id__in=item_ids).values_list("id", "name"))

    interactions = int(np.count_nonzero(full))
    total_cells = max(n_users * n_items, 1)
    data_summary = {
        "total_behaviors": _real_behaviors_queryset().count(),
        "product_behaviors": product_event_total_count,
        "model_product_behaviors": product_event_count,
        "interactions": interactions,
        "active_users": int(sum(1 for u in user_ids if np.count_nonzero(full[user_index[u]]) > 0)),
        "active_products": int(sum(1 for i in item_ids if np.count_nonzero(full[:, item_index[i]]) > 0)),
        "sparsity": round(1 - interactions / total_cells, 6),
        "behavior_type_distribution": dict(all_behavior_counter),
        "product_behavior_distribution": dict(behavior_type_counter),
        "data_scope": "REAL_ONLY",
    }
    return InteractionDataset(
        user_ids=user_ids,
        item_ids=item_ids,
        user_index=user_index,
        item_index=item_index,
        matrix=train if for_experiment else full,
        train_items_by_user=dict(train_items_by_user),
        test_items_by_user=dict(test_items_by_user),
        item_popularity=item_popularity,
        user_names=user_names,
        item_names=item_names,
        data_summary=data_summary,
    )


def _cosine_rows(M: np.ndarray) -> np.ndarray:
    if M.size == 0:
        return M
    norms = np.linalg.norm(M, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    X = M / norms
    return X @ X.T


def _fit_user_cf(dataset: InteractionDataset, neighbor_k: int = 10):
    sim = _cosine_rows(dataset.matrix)
    np.fill_diagonal(sim, 0)
    return {"sim": sim, "neighbor_k": int(neighbor_k)}


def _recommend_user_cf(dataset: InteractionDataset, model, customer_id: int, top_n: int):
    if customer_id not in dataset.user_index:
        return []
    uidx = dataset.user_index[customer_id]
    M = dataset.matrix
    sim = model["sim"][uidx].copy()
    if sim.size == 0:
        return []
    k = min(model["neighbor_k"], sim.shape[0])
    if k <= 0:
        return []
    idx = np.argpartition(sim, -k)[-k:]
    idx = idx[np.argsort(sim[idx])[::-1]]
    scores = np.zeros(M.shape[1], dtype=np.float64)
    denom = float(np.sum(np.abs(sim[idx]))) or 1.0
    for nidx in idx:
        if sim[nidx] <= 0:
            continue
        scores += sim[nidx] * M[nidx]
    scores = scores / denom
    seen = dataset.train_items_by_user.get(customer_id, set())
    for item_id in seen:
        scores[dataset.item_index[item_id]] = -1
    ranked = np.argsort(scores)[::-1]
    out = []
    neighbor_users = [dataset.user_ids[i] for i in idx if sim[i] > 0][:3]
    neighbor_names = [dataset.user_names.get(x, f"用户{x}") for x in neighbor_users]
    for iidx in ranked:
        if len(out) >= top_n:
            break
        if scores[iidx] <= 0:
            continue
        item_id = dataset.item_ids[iidx]
        out.append((item_id, float(scores[iidx]), f"与您相似的用户（{'、'.join(neighbor_names) or '相似用户'}）偏好该商品"))
    return out


def _fit_item_cf(dataset: InteractionDataset, neighbor_k: int = 10):
    M = dataset.matrix
    if M.size == 0:
        return {"item_sim": np.zeros((0, 0)), "neighbor_k": int(neighbor_k)}
    item_vecs = M.T
    norms = np.linalg.norm(item_vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    X = item_vecs / norms
    sim = X @ X.T
    np.fill_diagonal(sim, 0)
    return {"item_sim": sim, "neighbor_k": int(neighbor_k)}


def _recommend_item_cf(dataset: InteractionDataset, model, customer_id: int, top_n: int):
    if customer_id not in dataset.user_index:
        return []
    uidx = dataset.user_index[customer_id]
    user_vec = dataset.matrix[uidx]
    seen_indices = np.where(user_vec > 0)[0]
    if seen_indices.size == 0:
        return []
    sim = model["item_sim"]
    scores = np.zeros(sim.shape[0], dtype=np.float64)
    for iidx in seen_indices:
        scores += user_vec[iidx] * sim[iidx]
    scores[seen_indices] = -1
    ranked = np.argsort(scores)[::-1]
    out = []
    for cand_idx in ranked:
        if len(out) >= top_n:
            break
        if scores[cand_idx] <= 0:
            continue
        contrib = []
        for src_idx in seen_indices:
            s = float(sim[cand_idx, src_idx])
            if s > 0:
                contrib.append((s * float(user_vec[src_idx]), src_idx))
        contrib.sort(reverse=True)
        reason_items = [dataset.item_names.get(dataset.item_ids[i], str(dataset.item_ids[i])) for _, i in contrib[:2]]
        reason = f"与您已浏览/加购的商品（{'、'.join(reason_items) or '历史商品'}）相似"
        out.append((dataset.item_ids[cand_idx], float(scores[cand_idx]), reason))
    return out


def _fit_als_implicit(dataset: InteractionDataset, factors=12, iterations=8, reg=0.1, alpha=20):
    R = dataset.matrix
    n_users, n_items = R.shape
    if n_users == 0 or n_items == 0:
        return {"X": np.zeros((0, factors)), "Y": np.zeros((0, factors))}
    rng = np.random.default_rng(20260223)
    X = rng.normal(0, 0.1, size=(n_users, factors))
    Y = rng.normal(0, 0.1, size=(n_items, factors))
    I = np.eye(factors)

    P = (R > 0).astype(np.float64)
    C = 1.0 + alpha * R

    for _ in range(iterations):
        YtY = Y.T @ Y
        for u in range(n_users):
            cu = C[u]
            pu = P[u]
            idx = np.where(cu > 1.0)[0]
            if idx.size == 0:
                continue
            Y_u = Y[idx]
            Cu_minus_I = np.diag(cu[idx] - 1.0)
            A = YtY + Y_u.T @ Cu_minus_I @ Y_u + reg * I
            b = (Y[idx].T @ (cu[idx] * pu[idx]))
            X[u] = np.linalg.solve(A, b)

        XtX = X.T @ X
        for i in range(n_items):
            ci = C[:, i]
            pi = P[:, i]
            idx = np.where(ci > 1.0)[0]
            if idx.size == 0:
                continue
            X_i = X[idx]
            Ci_minus_I = np.diag(ci[idx] - 1.0)
            A = XtX + X_i.T @ Ci_minus_I @ X_i + reg * I
            b = X[idx].T @ (ci[idx] * pi[idx])
            Y[i] = np.linalg.solve(A, b)
    return {"X": X, "Y": Y}


def _recommend_als(dataset: InteractionDataset, model, customer_id: int, top_n: int):
    if customer_id not in dataset.user_index:
        return []
    uidx = dataset.user_index[customer_id]
    X = model["X"]
    Y = model["Y"]
    if X.size == 0 or Y.size == 0:
        return []
    scores = X[uidx] @ Y.T
    seen = dataset.train_items_by_user.get(customer_id, set())
    seen_indices = set()
    for item_id in seen:
        idx = dataset.item_index.get(item_id)
        if idx is None:
            continue
        seen_indices.add(idx)
        # 使用极小值作为内部屏蔽占位，避免误被展示
        scores[idx] = -1e12
    ranked = np.argsort(scores)[::-1]
    out = []
    for iidx in ranked:
        if len(out) >= top_n:
            break
        if iidx in seen_indices:
            continue
        score = float(scores[iidx])
        if score <= 0:
            continue
        item_id = dataset.item_ids[iidx]
        out.append((item_id, score, "基于隐式反馈矩阵分解的潜在兴趣匹配"))
    return out


def _popular_fallback(dataset: InteractionDataset, customer_id: int, top_n: int):
    seen = dataset.train_items_by_user.get(customer_id, set())
    ranked = sorted(dataset.item_ids, key=lambda x: (dataset.item_popularity.get(x, 0), x), reverse=True)
    out = []
    for item_id in ranked:
        if item_id in seen:
            continue
        out.append((item_id, float(dataset.item_popularity.get(item_id, 0)), "基于热度补齐（数据不足）"))
        if len(out) >= top_n:
            break
    return out


def fit_algorithm(dataset: InteractionDataset, algorithm: str, setting: RecommendationSetting | None = None):
    setting = setting or get_recommendation_setting()
    if algorithm == "USER_CF":
        return _fit_user_cf(dataset, neighbor_k=int(setting.neighbor_k or 10))
    if algorithm == "ITEM_CF":
        return _fit_item_cf(dataset, neighbor_k=int(setting.neighbor_k or 10))
    if algorithm == "ALS":
        return _fit_als_implicit(
            dataset,
            factors=int(setting.als_factors or 12),
            iterations=int(setting.als_iterations or 8),
            reg=float(setting.als_regularization or 0.1),
            alpha=int(setting.als_alpha or 20),
        )
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def recommend_for_customer_by_algorithm(customer_id: int, algorithm: str, top_n=10, exclude_ids=None, setting: RecommendationSetting | None = None, allow_fallback: bool = True):
    setting = setting or get_recommendation_setting()
    dataset = build_interaction_dataset(setting=setting, for_experiment=False)
    if dataset.matrix.size == 0:
        return []
    top_n = max(int(top_n or 10), 1)
    model = fit_algorithm(dataset, algorithm, setting)
    if algorithm == "USER_CF":
        rows = _recommend_user_cf(dataset, model, customer_id, top_n + len(exclude_ids or []))
    elif algorithm == "ITEM_CF":
        rows = _recommend_item_cf(dataset, model, customer_id, top_n + len(exclude_ids or []))
    else:
        rows = _recommend_als(dataset, model, customer_id, top_n + len(exclude_ids or []))
    if not rows and allow_fallback:
        rows = _popular_fallback(dataset, customer_id, top_n + len(exclude_ids or []))
    exclude_set = {int(x) for x in (exclude_ids or []) if str(x).isdigit()}
    filtered = [(pid, s, r) for pid, s, r in rows if pid not in exclude_set][:top_n]
    return filtered


def build_recommendations_for_customer(customer, limit=None, exclude_ids=None, persist=False, allow_fallback: bool = True):
    setting = get_recommendation_setting()
    alg = setting.online_algorithm or "ALS"
    limit = int(limit or setting.top_n or 10)
    rows = recommend_for_customer_by_algorithm(customer.id, alg, top_n=limit, exclude_ids=exclude_ids, setting=setting, allow_fallback=allow_fallback)
    products = {p.id: p for p in Product.objects.filter(id__in=[x[0] for x in rows], status="ON_SHELF")}
    ordered = [(products[pid], round(float(score), 4), reason) for pid, score, reason in rows if pid in products]

    if persist:
        batch_no = uuid4().hex[:16]
        UserRecommendation.objects.filter(customer=customer).delete()
        UserRecommendation.objects.bulk_create(
            [
                UserRecommendation(
                    customer=customer,
                    product=p,
                    score=Decimal(str(score)),
                    reason=f"[{ALGORITHM_LABELS.get(alg, alg)}] {reason}"[:255],
                    batch_no=batch_no,
                )
                for p, score, reason in ordered
            ]
        )
    return ordered


def get_customer_algorithm_compare(customer_id: int, top_n=5):
    setting = get_recommendation_setting()
    result = {}
    for alg in ("USER_CF", "ITEM_CF", "ALS"):
        rows = recommend_for_customer_by_algorithm(customer_id, alg, top_n=top_n, setting=setting, allow_fallback=False)
        result[alg] = rows
    return result


def _evaluate_topk(recs: list[int], truth: set[int], k: int):
    topk = recs[:k]
    if not truth:
        return {"hit": 0, "precision": 0.0, "recall": 0.0, "ndcg": 0.0}
    hits = [1 if x in truth else 0 for x in topk]
    hit = 1 if any(hits) else 0
    precision = sum(hits) / max(k, 1)
    recall = sum(hits) / max(len(truth), 1)
    dcg = sum(h / np.log2(idx + 2) for idx, h in enumerate(hits))
    ideal_len = min(len(truth), k)
    idcg = sum(1 / np.log2(idx + 2) for idx in range(ideal_len)) if ideal_len > 0 else 1.0
    ndcg = dcg / idcg if idcg else 0.0
    return {"hit": hit, "precision": precision, "recall": recall, "ndcg": ndcg}


def _fit_with_overrides(dataset: InteractionDataset, algorithm: str, setting: RecommendationSetting, overrides: dict | None = None):
    overrides = overrides or {}
    if algorithm == "USER_CF":
        return _fit_user_cf(dataset, neighbor_k=int(overrides.get("neighbor_k", setting.neighbor_k or 10)))
    if algorithm == "ITEM_CF":
        return _fit_item_cf(dataset, neighbor_k=int(overrides.get("neighbor_k", setting.neighbor_k or 10)))
    if algorithm == "ALS":
        return _fit_als_implicit(
            dataset,
            factors=int(overrides.get("als_factors", setting.als_factors or 12)),
            iterations=int(overrides.get("als_iterations", setting.als_iterations or 8)),
            reg=float(overrides.get("als_regularization", setting.als_regularization or 0.1)),
            alpha=int(overrides.get("als_alpha", setting.als_alpha or 20)),
        )
    raise ValueError(algorithm)


def _recommend_with_model(dataset: InteractionDataset, algorithm: str, model, uid: int, top_n: int):
    if algorithm == "USER_CF":
        return _recommend_user_cf(dataset, model, uid, top_n)
    if algorithm == "ITEM_CF":
        return _recommend_item_cf(dataset, model, uid, top_n)
    return _recommend_als(dataset, model, uid, top_n)


def _evaluate_algorithm_on_dataset(dataset: InteractionDataset, setting: RecommendationSetting, algorithm: str, top_ks: tuple[int, ...], eligible_users: list[int], overrides: dict | None = None):
    if not eligible_users:
        return None
    max_k = max(top_ks)
    t0 = perf_counter()
    model = _fit_with_overrides(dataset, algorithm, setting, overrides)
    train_cost_ms = round((perf_counter() - t0) * 1000, 2)

    t1 = perf_counter()
    metric_acc = {k: {"precision": 0.0, "recall": 0.0, "ndcg": 0.0, "hit_rate": 0.0} for k in top_ks}
    rec_item_union = set()
    user_count = 0
    for uid in eligible_users:
        rec_rows = _recommend_with_model(dataset, algorithm, model, uid, max_k)
        rec_ids = [x[0] for x in rec_rows]
        user_count += 1
        truth = dataset.test_items_by_user.get(uid, set())
        rec_item_union.update(rec_ids[:max_k])
        for k in top_ks:
            m = _evaluate_topk(rec_ids, truth, k)
            metric_acc[k]["precision"] += m["precision"]
            metric_acc[k]["recall"] += m["recall"]
            metric_acc[k]["ndcg"] += m["ndcg"]
            metric_acc[k]["hit_rate"] += m["hit"]
    infer_cost_ms = round((perf_counter() - t1) * 1000, 2)
    if user_count == 0:
        return None
    metrics_k = {}
    for k in top_ks:
        metrics_k[str(k)] = {
            "precision": round(metric_acc[k]["precision"] / user_count, 4),
            "recall": round(metric_acc[k]["recall"] / user_count, 4),
            "ndcg": round(metric_acc[k]["ndcg"] / user_count, 4),
            "hit_rate": round(metric_acc[k]["hit_rate"] / user_count, 4),
            "coverage": round(len(rec_item_union) / max(len(dataset.item_ids), 1), 4),
        }
    return {
        "label": ALGORITHM_LABELS[algorithm],
        "users_evaluated": user_count,
        "train_cost_ms": train_cost_ms,
        "infer_cost_ms": infer_cost_ms,
        "metrics_by_k": metrics_k,
    }


def _sample_dataset_by_ratio(dataset: InteractionDataset, ratio: float, seed: int = 20260223) -> InteractionDataset:
    ratio = float(max(min(ratio, 1.0), 0.1))
    M = dataset.matrix.copy()
    rng = np.random.default_rng(seed + int(ratio * 1000))
    new_train = {}
    for uid in dataset.user_ids:
        uidx = dataset.user_index[uid]
        item_ids = list(dataset.train_items_by_user.get(uid, set()))
        if len(item_ids) <= 1:
            new_train[uid] = set(item_ids)
            continue
        keep_n = max(1, int(round(len(item_ids) * ratio)))
        keep_idx = rng.choice(len(item_ids), size=keep_n, replace=False)
        keep_items = {item_ids[int(i)] for i in np.atleast_1d(keep_idx)}
        new_train[uid] = keep_items
        for item_id in item_ids:
            if item_id not in keep_items:
                M[uidx, dataset.item_index[item_id]] = 0.0
    item_pop = {item_id: float(M[:, idx].sum()) for item_id, idx in dataset.item_index.items()}
    ds2 = replace(dataset, matrix=M, train_items_by_user=new_train, item_popularity=item_pop)
    ds2.data_summary = dict(dataset.data_summary)
    ds2.data_summary["train_behavior_ratio"] = ratio
    return ds2


def run_experiment(top_ks=(5, 10, 20), sample_users=5):
    setting = get_recommendation_setting()
    dataset = build_interaction_dataset(setting=setting, for_experiment=True)
    top_ks = tuple(sorted(set(int(k) for k in top_ks if int(k) > 0)))
    max_k = max(top_ks) if top_ks else 10

    eligible_users = [
        uid for uid in dataset.user_ids
        if dataset.train_items_by_user.get(uid) and dataset.test_items_by_user.get(uid)
    ]
    if len(eligible_users) < 2 or dataset.matrix.shape[1] < 3:
        return {
            "ok": False,
            "message": "可用于实验的真实行为数据不足，请先增加用户浏览/加购行为后再运行实验",
            "data_summary": dataset.data_summary,
        }

    metrics_summary = {}
    chart_payload = {
        "metricCharts": [],
        "behaviorDistribution": dataset.data_summary.get("behavior_type_distribution", {}),
        "productBehaviorDistribution": dataset.data_summary.get("product_behavior_distribution", {}),
    }
    sample_recommendations = {}

    for alg in ("USER_CF", "ITEM_CF", "ALS"):
        result_metrics = _evaluate_algorithm_on_dataset(dataset, setting, alg, top_ks, eligible_users)
        if not result_metrics:
            continue
        metrics_summary[alg] = result_metrics

        model = _fit_with_overrides(dataset, alg, setting)

        sample_rows = []
        for uid in eligible_users[:sample_users]:
            rec_rows = _recommend_with_model(dataset, alg, model, uid, 5)
            sample_rows.append({
                "customer_id": uid,
                "customer_name": dataset.user_names.get(uid, f"用户{uid}"),
                "truth_items": [dataset.item_names.get(i, str(i)) for i in list(dataset.test_items_by_user.get(uid, set()))[:3]],
                "recommendations": [
                    {"product_id": pid, "product_name": dataset.item_names.get(pid, str(pid)), "score": round(float(score), 4), "reason": reason}
                    for pid, score, reason in rec_rows[:5]
                ],
            })
        sample_recommendations[alg] = sample_rows

    metrics_to_plot = ["recall", "precision", "ndcg", "hit_rate", "coverage"]
    for metric in metrics_to_plot:
        values = []
        for alg in ("USER_CF", "ITEM_CF", "ALS"):
            if alg not in metrics_summary:
                continue
            k10 = metrics_summary[alg]["metrics_by_k"].get("10") or next(iter(metrics_summary[alg]["metrics_by_k"].values()))
            values.append({"algorithm": alg, "label": ALGORITHM_LABELS[alg], "value": k10.get(metric, 0)})
        chart_payload["metricCharts"].append({"metric": metric, "k": 10, "values": values})

    chart_payload["timeChart"] = [
        {
            "algorithm": alg,
            "label": metrics_summary[alg]["label"],
            "train_cost_ms": metrics_summary[alg]["train_cost_ms"],
            "infer_cost_ms": metrics_summary[alg]["infer_cost_ms"],
        }
        for alg in ("USER_CF", "ITEM_CF", "ALS") if alg in metrics_summary
    ]

    # 参数敏感性：邻域算法的 neighbor_k、ALS 的 factors 对 Recall/NDCG 的影响
    param_top_ks = (10,)
    chart_payload["parameterSensitivityCharts"] = []
    for alg in ("USER_CF", "ITEM_CF"):
        xs = [5, 10, 20, 40]
        rows = []
        for metric in ("recall", "ndcg"):
            y = []
            for x in xs:
                r = _evaluate_algorithm_on_dataset(dataset, setting, alg, param_top_ks, eligible_users, overrides={"neighbor_k": x})
                y.append(float((((r or {}).get("metrics_by_k") or {}).get("10") or {}).get(metric, 0)))
            rows.append({"algorithm": alg, "label": ALGORITHM_LABELS[alg], "metric": metric, "x_label": "neighbor_k", "xs": xs, "ys": y})
        chart_payload["parameterSensitivityCharts"].append({"algorithm": alg, "label": ALGORITHM_LABELS[alg], "x_label": "neighbor_k", "series": rows})
    xs = [8, 12, 16, 24]
    rows = []
    for metric in ("recall", "ndcg"):
        y = []
        for x in xs:
            r = _evaluate_algorithm_on_dataset(dataset, setting, "ALS", param_top_ks, eligible_users, overrides={"als_factors": x})
            y.append(float((((r or {}).get("metrics_by_k") or {}).get("10") or {}).get(metric, 0)))
        rows.append({"algorithm": "ALS", "label": ALGORITHM_LABELS["ALS"], "metric": metric, "x_label": "als_factors", "xs": xs, "ys": y})
    chart_payload["parameterSensitivityCharts"].append({"algorithm": "ALS", "label": ALGORITHM_LABELS["ALS"], "x_label": "als_factors", "series": rows})

    # 数据规模影响：采样训练行为比例对指标的影响（同测试集）
    scale_ratios = [0.4, 0.6, 0.8, 1.0]
    chart_payload["dataScaleCharts"] = []
    for metric in ("recall", "ndcg"):
        series = []
        for alg in ("USER_CF", "ITEM_CF", "ALS"):
            ys = []
            for ratio in scale_ratios:
                sampled = _sample_dataset_by_ratio(dataset, ratio)
                elig = [uid for uid in eligible_users if sampled.train_items_by_user.get(uid)]
                r = _evaluate_algorithm_on_dataset(sampled, setting, alg, (10,), elig)
                ys.append(float((((r or {}).get("metrics_by_k") or {}).get("10") or {}).get(metric, 0)))
            series.append({"algorithm": alg, "label": ALGORITHM_LABELS[alg], "metric": metric, "xs": scale_ratios, "ys": ys})
        chart_payload["dataScaleCharts"].append({"metric": metric, "x_label": "train_behavior_ratio", "series": series})

    return {
        "ok": True,
        "message": "实验完成",
        "data_summary": dataset.data_summary,
        "metrics_summary": metrics_summary,
        "chart_payload": chart_payload,
        "sample_recommendations": sample_recommendations,
    }


def get_data_analysis_overview():
    ds = build_interaction_dataset(for_experiment=False)
    real_behaviors = _real_behaviors_queryset()
    top_customers = (
        real_behaviors.values("customer_id", "customer__name")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:10]
    )
    top_products = (
        real_behaviors.filter(target_type="PRODUCT", target_id__isnull=False)
        .values("target_id", "target_name")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:10]
    )
    return {
        "data_summary": ds.data_summary,
        "top_customers": [{"customer_id": x["customer_id"], "customer_name": x["customer__name"] or f"用户{x['customer_id']}", "count": x["cnt"]} for x in top_customers],
        "top_products": [{"product_id": x["target_id"], "product_name": x["target_name"] or f"商品{x['target_id']}", "count": x["cnt"]} for x in top_products],
        "setting": {
            "online_algorithm": get_recommendation_setting().online_algorithm,
            "algorithm_label": ALGORITHM_LABELS.get(get_recommendation_setting().online_algorithm, get_recommendation_setting().online_algorithm),
        },
        "data_scope": "REAL_ONLY",
        "generated_at": timezone.now().isoformat(),
    }


def _generated_thesis_customer_queryset():
    return Customer.objects.filter(
        name__startswith=THESIS_SAMPLE_CUSTOMER_PREFIX,
        hobby=THESIS_SAMPLE_CUSTOMER_HOBBY,
        address=THESIS_SAMPLE_CUSTOMER_ADDRESS,
    )


def reset_recommendation_workspace(
    *,
    clear_behaviors: bool = True,
    clear_carts: bool = True,
    clear_recommendations: bool = True,
    clear_generated_customers: bool = False,
):
    behavior_deleted = 0
    cart_deleted = 0
    recommendation_deleted = 0
    generated_customer_deleted = 0
    if clear_behaviors:
        behavior_deleted = CustomerBehavior.objects.count()
        CustomerBehavior.objects.all().delete()
    if clear_carts:
        cart_deleted = CartItem.objects.count()
        CartItem.objects.all().delete()
    if clear_recommendations:
        recommendation_deleted = UserRecommendation.objects.count()
        UserRecommendation.objects.all().delete()
    if clear_generated_customers:
        generated_customer_deleted = _generated_thesis_customer_queryset().count()
        _generated_thesis_customer_queryset().delete()
    return {
        "behaviors_deleted": behavior_deleted,
        "cart_items_deleted": cart_deleted,
        "recommendations_deleted": recommendation_deleted,
        "generated_customers_deleted": generated_customer_deleted,
    }


def clear_generated_thesis_sample_data(*, clear_carts: bool = True, clear_recommendations: bool = True):
    generated_customer_ids = list(_generated_thesis_customer_queryset().values_list("id", flat=True))
    if not generated_customer_ids:
        return {
            "behaviors_deleted": 0,
            "cart_items_deleted": 0,
            "recommendations_deleted": 0,
            "generated_customers_deleted": 0,
        }
    behavior_qs = CustomerBehavior.objects.filter(customer_id__in=generated_customer_ids)
    cart_qs = CartItem.objects.filter(customer_id__in=generated_customer_ids)
    recommendation_qs = UserRecommendation.objects.filter(customer_id__in=generated_customer_ids)
    behavior_deleted = behavior_qs.count()
    cart_deleted = cart_qs.count() if clear_carts else 0
    recommendation_deleted = recommendation_qs.count() if clear_recommendations else 0
    customers_deleted = _generated_thesis_customer_queryset().count()
    behavior_qs.delete()
    if clear_carts:
        cart_qs.delete()
    if clear_recommendations:
        recommendation_qs.delete()
    _generated_thesis_customer_queryset().delete()
    return {
        "behaviors_deleted": behavior_deleted,
        "cart_items_deleted": cart_deleted,
        "recommendations_deleted": recommendation_deleted,
        "generated_customers_deleted": customers_deleted,
    }


def _root_category_for_product(product: Product):
    root = product.category
    while getattr(root, "parent_id", None):
        root = root.parent
    return root


def generate_thesis_experiment_sample_data(
    *,
    target_customers: int = 60,
    actions_per_customer: int = 60,
    seed: int = 20260408,
    clear_existing_generated: bool = True,
    clear_all_behaviors: bool = False,
):
    if target_customers < 3:
        return {"ok": False, "message": "样本用户数量至少需要3个"}
    if actions_per_customer < 12:
        return {"ok": False, "message": "每个用户行为数至少需要12条"}

    reset_summary = None
    if clear_all_behaviors:
        reset_summary = reset_recommendation_workspace(
            clear_behaviors=True,
            clear_carts=True,
            clear_recommendations=True,
            clear_generated_customers=True,
        )
    elif clear_existing_generated:
        reset_summary = clear_generated_thesis_sample_data(clear_carts=True, clear_recommendations=True)

    products = list(
        Product.objects.filter(status="ON_SHELF")
        .select_related("category", "category__parent", "category__parent__parent")
        .order_by("-sales_count", "-view_count", "-sort", "-id")
    )
    if len(products) < 20:
        return {"ok": False, "message": "上架商品数量不足，至少需要20个商品才能生成论文实验样本"}

    by_root: dict[int, list[Product]] = defaultdict(list)
    by_leaf: dict[int, list[Product]] = defaultdict(list)
    root_categories: dict[int, ProductCategory] = {}
    for product in products:
        root = _root_category_for_product(product)
        root_categories[root.id] = root
        by_root[root.id].append(product)
        by_leaf[product.category_id].append(product)
    available_root_ids = [root_id for root_id, rows in by_root.items() if rows]
    if len(available_root_ids) < 2:
        return {"ok": False, "message": "商品一级分类过少，无法构建有区分度的论文实验样本"}

    rng = np.random.default_rng(seed)
    now = timezone.now()
    batch_no = uuid4().hex[:12]
    behavior_rows: list[CustomerBehavior] = []
    type_counter = Counter()
    generated_customers: list[Customer] = []

    def create_customer(index: int) -> Customer:
        customer = Customer(
            name=f"{THESIS_SAMPLE_CUSTOMER_PREFIX}{index:03d}",
            phone=f"1888{index:07d}",
            age=int(rng.integers(20, 46)),
            hobby=THESIS_SAMPLE_CUSTOMER_HOBBY,
            address=THESIS_SAMPLE_CUSTOMER_ADDRESS,
            last_active_at=now,
        )
        customer.set_password("123456")
        customer.save()
        generated_customers.append(customer)
        return customer

    def push_behavior(customer: Customer, payload: dict, current_time):
        behavior_rows.append(CustomerBehavior(customer=customer, created_at=current_time, **payload))
        type_counter[payload["behavior_type"]] += 1
        return current_time + timezone.timedelta(minutes=int(rng.integers(2, 15)), seconds=int(rng.integers(0, 59)))

    for idx in range(1, target_customers + 1):
        customer = create_customer(idx)
        preferred_roots = list(rng.choice(available_root_ids, size=min(2, len(available_root_ids)), replace=False))
        current_time = now - timezone.timedelta(days=int(rng.integers(10, 31)), hours=int(rng.integers(0, 23)))
        behaviors_created = 0
        while behaviors_created < actions_per_customer:
            root_id = preferred_roots[int(rng.integers(0, len(preferred_roots)))]
            product_pool = by_root.get(root_id) or products
            current_time = push_behavior(
                customer,
                {
                    "behavior_type": "SEARCH",
                    "target_type": "KEYWORD",
                    "target_name": root_categories[root_id].name,
                    "source_page": "HOME",
                    "extra_data": {
                        THESIS_SAMPLE_EXTRA_FLAG: True,
                        "batch_no": batch_no,
                        "seed": seed,
                    },
                },
                current_time,
            )
            behaviors_created += 1
            if behaviors_created >= actions_per_customer:
                break

            category_product = product_pool[int(rng.integers(0, len(product_pool)))]
            current_time = push_behavior(
                customer,
                {
                    "behavior_type": "CLICK_CATEGORY",
                    "target_type": "CATEGORY",
                    "target_id": category_product.category_id,
                    "target_name": category_product.category.name,
                    "source_page": "HOME",
                    "extra_data": {
                        THESIS_SAMPLE_EXTRA_FLAG: True,
                        "batch_no": batch_no,
                        "seed": seed,
                    },
                },
                current_time,
            )
            behaviors_created += 1

            session_view_count = max(2, min(int(rng.integers(3, 7)), actions_per_customer - behaviors_created))
            session_products = list(rng.choice(product_pool, size=session_view_count, replace=len(product_pool) < session_view_count))
            cart_candidates: list[Product] = []
            for product in session_products:
                current_time = push_behavior(
                    customer,
                    {
                        "behavior_type": "VIEW_PRODUCT",
                        "target_type": "PRODUCT",
                        "target_id": product.id,
                        "target_name": product.name,
                        "source_page": "PRODUCT_DETAIL" if rng.random() > 0.5 else "PRODUCT_LIST",
                        "extra_data": {
                            THESIS_SAMPLE_EXTRA_FLAG: True,
                            "batch_no": batch_no,
                            "seed": seed,
                        },
                    },
                    current_time,
                )
                behaviors_created += 1
                if rng.random() < 0.38 and behaviors_created < actions_per_customer:
                    cart_candidates.append(product)
                    current_time = push_behavior(
                        customer,
                        {
                            "behavior_type": "ADD_TO_CART",
                            "target_type": "PRODUCT",
                            "target_id": product.id,
                            "target_name": product.name,
                            "source_page": "PRODUCT_DETAIL",
                            "extra_data": {
                                THESIS_SAMPLE_EXTRA_FLAG: True,
                                "batch_no": batch_no,
                                "seed": seed,
                            },
                        },
                        current_time,
                    )
                    behaviors_created += 1
                if behaviors_created >= actions_per_customer:
                    break

            if cart_candidates and rng.random() < 0.32 and behaviors_created < actions_per_customer:
                purchase_count = min(len(cart_candidates), max(1, int(rng.integers(1, min(4, len(cart_candidates) + 1)))))
                purchase_products = cart_candidates[:purchase_count]
                item_ids = [product.id for product in purchase_products]
                item_names = [product.name for product in purchase_products]
                current_time = push_behavior(
                    customer,
                    {
                        "behavior_type": "PURCHASE",
                        "target_type": "PRODUCT",
                        "target_id": item_ids[0] if len(item_ids) == 1 else None,
                        "target_name": "、".join(item_names),
                        "source_page": "CART",
                        "extra_data": {
                            THESIS_SAMPLE_EXTRA_FLAG: True,
                            "batch_no": batch_no,
                            "seed": seed,
                            "item_ids": item_ids,
                            "item_names": item_names,
                            "item_count": len(item_ids),
                            "total_amount": sum(int(product.default_price or 0) for product in purchase_products),
                        },
                    },
                    current_time,
                )
                behaviors_created += 1

    if behavior_rows:
        CustomerBehavior.objects.bulk_create(behavior_rows, batch_size=500)

    return {
        "ok": True,
        "message": "论文实验样本已生成",
        "batch_no": batch_no,
        "seed": seed,
        "customer_count": len(generated_customers),
        "created_behaviors": len(behavior_rows),
        "behavior_distribution": dict(type_counter),
        "reset_summary": reset_summary or {},
    }


def verify_online_algorithm_switch(*, customer_id: int | None = None, top_n: int = 5):
    setting = get_recommendation_setting()
    original_algorithm = setting.online_algorithm or "ALS"
    dataset = build_interaction_dataset(setting=setting, for_experiment=False)
    if not dataset.user_ids:
        return {"ok": False, "message": "当前没有可用于验证的行为数据"}

    probe_customer_id = customer_id
    if probe_customer_id is None:
        ranked_users = sorted(
            dataset.user_ids,
            key=lambda uid: (len(dataset.train_items_by_user.get(uid, set())), uid),
            reverse=True,
        )
        probe_customer_id = ranked_users[0] if ranked_users else None
    if not probe_customer_id:
        return {"ok": False, "message": "未找到可用于验证的用户"}
    probe_customer = Customer.objects.filter(pk=probe_customer_id).first()
    if not probe_customer:
        return {"ok": False, "message": "验证用户不存在"}

    result = {
        "ok": True,
        "message": "线上推荐算法开关验证完成",
        "probe_customer": {
            "id": probe_customer.id,
            "name": probe_customer.name,
            "phone": probe_customer.phone,
        },
        "algorithms": {},
    }
    try:
        for algorithm in ("USER_CF", "ITEM_CF", "ALS"):
            setting.online_algorithm = algorithm
            setting.save(update_fields=["online_algorithm", "updated_at"])
            rows = build_recommendations_for_customer(
                probe_customer,
                limit=top_n,
                persist=False,
                allow_fallback=False,
            )
            result["algorithms"][algorithm] = [
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "score": round(float(score), 4),
                    "reason": reason,
                }
                for product, score, reason in rows
            ]
    finally:
        setting.online_algorithm = original_algorithm
        setting.save(update_fields=["online_algorithm", "updated_at"])
    result["distinct_output_count"] = len(
        {
            tuple((row["product_id"], row["reason"]) for row in rows)
            for rows in result["algorithms"].values()
        }
    )
    return result


def generate_experiment_behavior_replay(target_customers=24, actions_per_customer=40):
    # 基于真实商品和真实行为表生成实验行为轨迹，便于快速产出论文图表
    now = timezone.now()
    customers = list(Customer.objects.all().order_by("id"))
    while len(customers) < target_customers:
        idx = len(customers) + 1
        phone = f"1890000{idx:04d}"[-11:]
        if Customer.objects.filter(phone=phone).exists():
            idx += 1
            phone = f"1890000{idx:04d}"[-11:]
        c = Customer(name=f"实验用户{idx:02d}", phone=phone, hobby="电商浏览", address="实验数据")
        c.set_password("123456")
        c.save()
        customers.append(c)
    customers = customers[:target_customers]

    products = list(Product.objects.filter(status="ON_SHELF").select_related("category", "category__parent", "category__parent__parent"))
    if len(products) < 20:
        return {"ok": False, "message": "商品数量不足，无法生成实验行为轨迹"}

    by_leaf = defaultdict(list)
    by_l1 = defaultdict(list)
    for p in products:
        by_leaf[p.category_id].append(p)
        root = p.category
        while getattr(root, "parent_id", None):
            root = root.parent
        by_l1[root.id].append(p)
    categories = {c.id: c for c in ProductCategory.objects.filter(id__in=list(by_leaf.keys()) + list(by_l1.keys()))}

    created = 0
    for idx, customer in enumerate(customers):
        pref_l1_ids = list(by_l1.keys())
        if not pref_l1_ids:
            continue
        pref_l1 = pref_l1_ids[idx % len(pref_l1_ids)]
        candidate_pool = by_l1[pref_l1][:]
        if len(candidate_pool) < 10:
            candidate_pool = products[:]
        rng = np.random.default_rng(20260223 + customer.id)
        chosen = [candidate_pool[int(x)] for x in rng.integers(0, len(candidate_pool), size=max(actions_per_customer // 2, 10))]
        base_time = now - timezone.timedelta(days=int(idx % 7) + 1)

        keyword = categories.get(pref_l1).name if categories.get(pref_l1) else "商品"
        CustomerBehavior.objects.create(
            customer=customer,
            behavior_type="SEARCH",
            target_type="KEYWORD",
            target_name=keyword,
            source_page="EXPERIMENT_REPLAY",
            extra_data={"is_simulated": True, "replay_type": "EXPERIMENT"},
            created_at=base_time,
        )
        created += 1

        cat = categories.get(pref_l1)
        if cat:
            CustomerBehavior.objects.create(
                customer=customer,
                behavior_type="CLICK_CATEGORY",
                target_type="CATEGORY",
                target_id=cat.id,
                target_name=cat.name,
                source_page="EXPERIMENT_REPLAY",
                extra_data={"is_simulated": True, "replay_type": "EXPERIMENT"},
                created_at=base_time + timezone.timedelta(minutes=1),
            )
            created += 1

        for step, p in enumerate(chosen, start=1):
            t = base_time + timezone.timedelta(minutes=step * 3)
            CustomerBehavior.objects.create(
                customer=customer,
                behavior_type="VIEW_PRODUCT",
                target_type="PRODUCT",
                target_id=p.id,
                target_name=p.name,
                source_page="EXPERIMENT_REPLAY",
                extra_data={"is_simulated": True, "replay_type": "EXPERIMENT", "origin_page": ("PRODUCT_LIST" if step % 2 else "HOME")},
                created_at=t,
            )
            created += 1
            if step % 3 == 0:
                CustomerBehavior.objects.create(
                    customer=customer,
                    behavior_type="ADD_TO_CART",
                    target_type="PRODUCT",
                    target_id=p.id,
                    target_name=p.name,
                    source_page="EXPERIMENT_REPLAY",
                    extra_data={"is_simulated": True, "replay_type": "EXPERIMENT", "origin_page": "PRODUCT_DETAIL"},
                    created_at=t + timezone.timedelta(seconds=20),
                )
                created += 1

    return {"ok": True, "message": "实验行为回放已生成", "created_behaviors": created, "customer_count": len(customers)}
