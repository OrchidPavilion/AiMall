from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from django.conf import settings

from .models import RecommendationExperimentRun


def _ensure_dir(exp: RecommendationExperimentRun) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(settings.MEDIA_ROOT) / "recommendation_exports" / f"exp_{exp.id}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _write_metrics_csv(exp: RecommendationExperimentRun, out_dir: Path) -> Path:
    path = out_dir / "metrics_summary.csv"
    metrics = exp.metrics_summary or {}
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "algorithm_label", "k", "recall", "precision", "ndcg", "hit_rate", "coverage", "train_cost_ms", "infer_cost_ms"])
        for alg, payload in metrics.items():
            label = payload.get("label", alg)
            train_cost_ms = payload.get("train_cost_ms", 0)
            infer_cost_ms = payload.get("infer_cost_ms", 0)
            for k, m in (payload.get("metrics_by_k") or {}).items():
                writer.writerow([
                    alg, label, k,
                    m.get("recall", 0), m.get("precision", 0), m.get("ndcg", 0),
                    m.get("hit_rate", 0), m.get("coverage", 0),
                    train_cost_ms, infer_cost_ms,
                ])
    return path


def _write_samples_csv(exp: RecommendationExperimentRun, out_dir: Path) -> Path:
    path = out_dir / "sample_recommendations.csv"
    samples = exp.sample_recommendations or {}
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "customer_id", "customer_name", "truth_items", "rank", "product_name", "score", "reason"])
        for alg, rows in samples.items():
            for row in rows or []:
                truth_items = " | ".join(row.get("truth_items") or [])
                for rank, rec in enumerate(row.get("recommendations") or [], start=1):
                    writer.writerow([
                        alg,
                        row.get("customer_id"),
                        row.get("customer_name"),
                        truth_items,
                        rank,
                        rec.get("product_name"),
                        rec.get("score"),
                        rec.get("reason"),
                    ])
    return path


def _write_json_snapshots(exp: RecommendationExperimentRun, out_dir: Path):
    p1 = out_dir / "data_summary.json"
    p2 = out_dir / "chart_payload.json"
    p3 = out_dir / "config_snapshot.json"
    p1.write_text(json.dumps(exp.data_summary or {}, ensure_ascii=False, indent=2), encoding="utf-8")
    p2.write_text(json.dumps(exp.chart_payload or {}, ensure_ascii=False, indent=2), encoding="utf-8")
    p3.write_text(json.dumps(exp.config_snapshot or {}, ensure_ascii=False, indent=2), encoding="utf-8")
    return [p1, p2, p3]


def _save_bar_chart(title: str, x_labels: list[str], values: list[float], out_path: Path, y_label: str = "Value"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(9, 4.8), dpi=140)
    ax = fig.add_subplot(111)
    colors = ["#3b82f6", "#0ea5e9", "#22c55e", "#f59e0b", "#ef4444"]
    bars = ax.bar(x_labels, values, color=colors[: len(values)])
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{v:.4f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def _save_double_bar_chart(title: str, labels: list[str], v1: list[float], v2: list[float], out_path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.arange(len(labels))
    width = 0.36
    fig = plt.figure(figsize=(10, 5), dpi=140)
    ax = fig.add_subplot(111)
    b1 = ax.bar(x - width / 2, v1, width, label="train_cost_ms", color="#2563eb")
    b2 = ax.bar(x + width / 2, v2, width, label="infer_cost_ms", color="#16a34a")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title(title)
    ax.set_ylabel("Milliseconds")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    for bars in [b1, b2]:
        for b in bars:
            h = float(b.get_height())
            ax.text(b.get_x() + b.get_width() / 2, h, f"{h:.2f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def _save_multi_line_chart(title: str, x_values: list[int], series_rows: list[dict], out_path: Path, y_label: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(8.8, 5), dpi=140)
    ax = fig.add_subplot(111)
    colors = {"USER_CF": "#2563eb", "ITEM_CF": "#16a34a", "ALS": "#f59e0b"}
    for row in series_rows:
        alg = row.get("algorithm")
        ys = row.get("values") or []
        ax.plot(x_values, ys, marker="o", linewidth=2, label=row.get("label", alg), color=colors.get(alg))
    ax.set_title(title)
    ax.set_xlabel("K")
    ax.set_ylabel(y_label)
    ax.grid(True, linestyle="--", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def _algorithm_analysis_plain_text(exp: RecommendationExperimentRun) -> str:
    ms = exp.metrics_summary or {}
    algs = list(ms.keys())
    if not algs:
        return "本次实验未产生有效算法指标，请先补充行为数据后重新运行实验。"
    def m(alg, metric, k="10"):
        return float((((ms.get(alg) or {}).get("metrics_by_k") or {}).get(k) or {}).get(metric, 0))
    def label(alg):
        return (ms.get(alg) or {}).get("label", alg)
    best_recall = max(algs, key=lambda a: m(a, "recall"))
    best_ndcg = max(algs, key=lambda a: m(a, "ndcg"))
    best_cov = max(algs, key=lambda a: m(a, "coverage"))
    fastest_train = min(algs, key=lambda a: float((ms.get(a) or {}).get("train_cost_ms", 0)))
    fastest_infer = min(algs, key=lambda a: float((ms.get(a) or {}).get("infer_cost_ms", 0)))
    return "\n".join([
        "【算法分析（白话版）】",
        "本次实验是在同一份真实行为数据快照上完成，因此三种算法结果可以直接横向比较。",
        f"Recall@10 最好的是 {label(best_recall)}（{m(best_recall, 'recall'):.4f}），说明它更擅长把用户可能喜欢的商品“找全”。",
        f"NDCG@10 最好的是 {label(best_ndcg)}（{m(best_ndcg, 'ndcg'):.4f}），说明它把更相关商品排在前面的能力更强。",
        f"Coverage@10 最好的是 {label(best_cov)}（{m(best_cov, 'coverage'):.4f}），说明它覆盖到的商品更广，不容易只推荐少数热门商品。",
        f"训练耗时最短的是 {label(fastest_train)}（{float((ms.get(fastest_train) or {}).get('train_cost_ms', 0)):.2f}ms），推理耗时最短的是 {label(fastest_infer)}（{float((ms.get(fastest_infer) or {}).get('infer_cost_ms', 0)):.2f}ms）。",
        "如果论文强调可解释性与界面展示，可重点分析 UserCF/ItemCF；如果强调隐式反馈稀疏场景下的稳定性与综合效果，可重点分析 ALS。",
    ])


def _write_png_charts(exp: RecommendationExperimentRun, out_dir: Path) -> list[Path]:
    chart_payload = exp.chart_payload or {}
    out_paths: list[Path] = []
    for chart in chart_payload.get("metricCharts") or []:
        metric = str(chart.get("metric") or "metric")
        rows = chart.get("values") or []
        labels = [r.get("algorithm") or r.get("label") for r in rows]
        values = [float(r.get("value") or 0) for r in rows]
        path = out_dir / f"{metric}_k{chart.get('k', 10)}.png"
        _save_bar_chart(f"{metric.upper()}@{chart.get('k', 10)} Comparison", labels, values, path, y_label=metric.upper())
        out_paths.append(path)
    time_rows = chart_payload.get("timeChart") or []
    if time_rows:
        labels = [r.get("algorithm") or r.get("label") for r in time_rows]
        train_vals = [float(r.get("train_cost_ms") or 0) for r in time_rows]
        infer_vals = [float(r.get("infer_cost_ms") or 0) for r in time_rows]
        path = out_dir / "time_cost_compare.png"
        _save_double_bar_chart("Training vs Inference Cost", labels, train_vals, infer_vals, path)
        out_paths.append(path)

    metrics_summary = exp.metrics_summary or {}
    metric_names = ["recall", "precision", "ndcg", "hit_rate", "coverage"]
    k_set = set()
    for payload in metrics_summary.values():
        for k in (payload.get("metrics_by_k") or {}).keys():
            try:
                k_set.add(int(k))
            except Exception:
                pass
    ks = sorted(k_set)
    if ks:
        for metric in metric_names:
            series_rows = []
            for alg, payload in metrics_summary.items():
                row = {"algorithm": alg, "label": alg, "values": []}
                for k in ks:
                    row["values"].append(float(((payload.get("metrics_by_k") or {}).get(str(k)) or {}).get(metric, 0)))
                series_rows.append(row)
            path = out_dir / f"{metric}_curve_by_k.png"
            _save_multi_line_chart(f"{metric.upper()} vs K", ks, series_rows, path, y_label=metric.upper())
            out_paths.append(path)

    for g in chart_payload.get("parameterSensitivityCharts") or []:
        for s in g.get("series") or []:
            xs = [int(x) for x in (s.get("xs") or [])]
            ys = [float(y) for y in (s.get("ys") or [])]
            if not xs or not ys:
                continue
            path = out_dir / f"param_{g.get('algorithm','alg').lower()}_{s.get('metric','metric')}.png"
            _save_multi_line_chart(
                f"{g.get('algorithm')} {str(s.get('metric','')).upper()} Sensitivity ({g.get('x_label')})",
                xs,
                [{"algorithm": g.get("algorithm"), "label": g.get("algorithm"), "values": ys}],
                path,
                y_label=str(s.get("metric", "")).upper(),
            )
            out_paths.append(path)

    for g in chart_payload.get("dataScaleCharts") or []:
        xs = [int(round(float(x) * 100)) for x in ((g.get("series") or [{}])[0].get("xs") or [])]
        if not xs:
            continue
        series_rows = []
        for s in g.get("series") or []:
            series_rows.append({
                "algorithm": s.get("algorithm"),
                "label": s.get("algorithm"),
                "values": [float(y) for y in (s.get("ys") or [])],
            })
        path = out_dir / f"data_scale_{g.get('metric','metric')}.png"
        _save_multi_line_chart(
            f"Train Behavior Ratio vs {str(g.get('metric','')).upper()}@10",
            xs,
            series_rows,
            path,
            y_label=str(g.get("metric", "")).upper(),
        )
        out_paths.append(path)

    for key, filename in [("behaviorDistribution", "behavior_distribution.png"), ("productBehaviorDistribution", "product_behavior_distribution.png")]:
        dist = chart_payload.get(key) or {}
        if dist:
            labels = list(dist.keys())
            values = [float(dist[k]) for k in labels]
            path = out_dir / filename
            _save_bar_chart(key, labels, values, path, y_label="Count")
            out_paths.append(path)
    return out_paths


def _compose_chapter4_text(exp: RecommendationExperimentRun) -> str:
    ds = exp.data_summary or {}
    ms = exp.metrics_summary or {}
    if not ms:
        return (
            "## 第4章 实验设计与分析（自动草稿）\n\n"
            "本次实验未生成有效指标结果，主要原因是用户行为数据不足，无法完成训练集/测试集切分。"
            "建议先通过系统真实操作或实验行为回放补充浏览、加购等行为后重新运行实验。"
        )

    def metric_at(alg: str, metric: str, k: str = "10"):
        m = (((ms.get(alg) or {}).get("metrics_by_k") or {}).get(k) or {})
        return float(m.get(metric, 0))

    algs = [a for a in ("USER_CF", "ITEM_CF", "ALS") if a in ms]
    best_recall_alg = max(algs, key=lambda a: metric_at(a, "recall", "10"))
    best_ndcg_alg = max(algs, key=lambda a: metric_at(a, "ndcg", "10"))
    best_cov_alg = max(algs, key=lambda a: metric_at(a, "coverage", "10"))

    lines = []
    lines.append("## 第4章 实验设计与分析（自动草稿）")
    lines.append("")
    lines.append("### 4.1 实验数据与设置")
    lines.append(
        f"本实验基于 AiMall 电商系统的真实行为轨迹表（CustomerBehavior）构建隐式反馈数据集。"
        f"实验样本统计如下：总行为数 {ds.get('total_behaviors', 0)}，商品行为数 {ds.get('product_behaviors', 0)}，"
        f"用户-商品交互数 {ds.get('interactions', 0)}，活跃用户数 {ds.get('active_users', 0)}，"
        f"活跃商品数 {ds.get('active_products', 0)}，数据稀疏度 {ds.get('sparsity', 0)}。"
    )
    cfg = exp.config_snapshot or {}
    top_ks = (cfg.get("top_ks") or [5, 10, 20])
    lines.append(
        f"实验在同一数据快照上并行比较基于用户的协同过滤（UserCF）、基于物品的协同过滤（ItemCF）与 "
        f"基于交替最小二乘的矩阵分解算法（ALS），评价指标包括 Recall@K、Precision@K、NDCG@K、HitRate@K 与 Coverage@K（K={top_ks}）。"
    )
    lines.append("")
    lines.append("### 4.2 实验结果对比")
    for alg in algs:
        payload = ms.get(alg) or {}
        label = payload.get("label", alg)
        m10 = (payload.get("metrics_by_k") or {}).get("10") or next(iter((payload.get("metrics_by_k") or {}).values()), {})
        lines.append(
            f"- {label}：Recall@10={m10.get('recall', 0)}, Precision@10={m10.get('precision', 0)}, "
            f"NDCG@10={m10.get('ndcg', 0)}, HitRate@10={m10.get('hit_rate', 0)}, Coverage@10={m10.get('coverage', 0)}，"
            f"训练耗时={payload.get('train_cost_ms', 0)}ms，推理耗时={payload.get('infer_cost_ms', 0)}ms。"
        )
    lines.append("")
    lines.append("### 4.3 结果分析")
    lines.append(
        f"从实验结果看，在当前隐式反馈数据条件下，{(ms.get(best_recall_alg) or {}).get('label', best_recall_alg)} "
        f"在 Recall@10 指标上表现最佳；{(ms.get(best_ndcg_alg) or {}).get('label', best_ndcg_alg)} 在 NDCG@10 指标上表现最佳；"
        f"{(ms.get(best_cov_alg) or {}).get('label', best_cov_alg)} 在 Coverage@10 指标上表现最佳。"
    )
    lines.append(
        "总体上，邻域方法（UserCF、ItemCF）具有较强的可解释性，便于在系统界面中给出“相似用户/相似商品”的推荐原因；"
        "ALS 通过隐式反馈矩阵分解学习潜在兴趣，在数据稀疏场景下通常具有较好的稳定性与泛化能力。"
    )
    lines.append(
        "实验图表表明，不同协同过滤算法在召回率、排序质量、覆盖率和计算开销方面存在明显差异，这与论文中对三类模型适用场景的分析基本一致。"
    )
    lines.append("")
    lines.append("### 4.4 小结")
    lines.append(
        "本实验在 AiMall 电商平台真实行为日志基础上完成了三种协同过滤算法的对比验证，说明协同过滤方法能够在隐式反馈电商场景下实现有效推荐。"
        "后续可进一步引入购买行为、收藏行为以及更多用户特征，提升实验数据质量与模型效果。"
    )
    return "\n".join(lines)


def export_experiment_artifacts(exp: RecommendationExperimentRun, base_url: str = "") -> dict:
    out_dir = _ensure_dir(exp)
    files = []

    metrics_csv = _write_metrics_csv(exp, out_dir)
    samples_csv = _write_samples_csv(exp, out_dir)
    files.extend([metrics_csv, samples_csv])
    files.extend(_write_json_snapshots(exp, out_dir))
    files.extend(_write_png_charts(exp, out_dir))

    chapter_text = _compose_chapter4_text(exp)
    chapter_md = out_dir / "chapter4_experiment_analysis_auto.md"
    chapter_txt = out_dir / "chapter4_experiment_analysis_auto.txt"
    algo_txt = out_dir / "algorithm_analysis_plain_language.txt"
    chapter_md.write_text(chapter_text, encoding="utf-8")
    chapter_txt.write_text(chapter_text, encoding="utf-8")
    algo_txt.write_text(_algorithm_analysis_plain_text(exp), encoding="utf-8")
    files.extend([chapter_md, chapter_txt, algo_txt])

    rel_prefix = Path(settings.MEDIA_ROOT)
    file_items = []
    for p in files:
        rel = p.relative_to(rel_prefix).as_posix()
        url = f"{settings.MEDIA_URL.rstrip('/')}/{rel}"
        if base_url:
            url = f"{base_url.rstrip('/')}{url}"
        file_items.append({"name": p.name, "path": str(p), "url": url})

    return {
        "export_dir": str(out_dir),
        "files": file_items,
        "chapter_text": chapter_text,
    }
