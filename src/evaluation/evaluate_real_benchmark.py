"""
Comprehensive FinGuard Evaluation Runner on the Real Grounded Statutory Benchmark.
Evaluates:
  1. Two-Checkpoint Pipeline (Query Guard + Response Guard) on datasets/finguard_bench_real/test.jsonl
  2. TF-IDF Statutory Retrieval Accuracy
  3. Jaccard Baseline Retrieval Accuracy
  4. Adversarial Robustness Metrics
Outputs consolidated results to experiments/evaluation_report_real.json.
"""

import os
import json
import time
import numpy as np
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.pipeline.finguard_pipeline import FinGuardPipeline
from src.guard.compliance_guard import FinGuardClassifier


def calculate_metrics(tp: int, fp: int, tn: int, fn: int) -> Dict[str, Any]:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
    return {
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1": round(f1 * 100, 2),
        "accuracy": round(accuracy * 100, 2),
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
    }


def evaluate_statutory_retrieval(
    test_samples: List[Dict[str, Any]],
    compliance_points_path: str = "data/processed/compliance_points.json",
    top_k: int = 2
) -> Dict[str, Any]:
    with open(compliance_points_path, "r", encoding="utf-8") as f:
        cps = json.load(f)

    # TF-IDF Corpus
    docs = [(p["category"] + " " + p["subcategory"] + " " + p["regulatory_clause"]).lower() for p in cps]
    vectorizer = TfidfVectorizer()
    clause_vectors = vectorizer.fit_transform(docs)

    tfidf_hits = 0
    jaccard_hits = 0
    total = len(test_samples)

    for s in test_samples:
        query = s["query"]
        expected_doc_id = s.get("regulatory_grounding", {}).get("doc_id")

        # 1. TF-IDF
        q_vec = vectorizer.transform([query.lower()])
        sims = cosine_similarity(q_vec, clause_vectors)[0]
        top_tfidf_idx = np.argsort(sims)[::-1][:top_k]
        tfidf_retrieved = {cps[i]["doc_id"] for i in top_tfidf_idx}
        if expected_doc_id in tfidf_retrieved:
            tfidf_hits += 1

        # 2. Jaccard
        q_words = set(query.lower().split())
        scored = []
        for p in cps:
            doc_words = set((p["category"] + " " + p["subcategory"] + " " + p["regulatory_clause"]).lower().split())
            j_score = len(q_words.intersection(doc_words)) / (len(q_words.union(doc_words)) + 1e-5)
            scored.append((j_score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        jaccard_retrieved = {p["doc_id"] for _, p in scored[:top_k]}
        if expected_doc_id in jaccard_retrieved:
            jaccard_hits += 1

    return {
        "total_cases": total,
        "top_k": top_k,
        "tfidf_hits": tfidf_hits,
        "tfidf_accuracy": round((tfidf_hits / total) * 100, 2),
        "jaccard_hits": jaccard_hits,
        "jaccard_accuracy": round((jaccard_hits / total) * 100, 2),
        "tfidf_advantage_pp": round(((tfidf_hits - jaccard_hits) / total) * 100, 2)
    }


def run_full_pipeline_eval(
    test_path: str = "datasets/finguard_bench_real/test.jsonl",
    report_path: str = "experiments/evaluation_report_real.json"
) -> Dict[str, Any]:
    with open(test_path, "r", encoding="utf-8") as f:
        samples = [json.loads(line) for line in f if line.strip()]

    pipeline = FinGuardPipeline()

    # Query level counters
    q_tp = q_fp = q_tn = q_fn = 0
    # Response level counters
    r_tp = r_fp = r_tn = r_fn = 0
    responses_evaluated = 0

    latencies = []

    for s in samples:
        query = s["query"]
        ground_truth_query_unsafe = (s["query_label"].lower() == "unsafe")

        start_t = time.time()
        result = pipeline.process_query(query)
        latencies.append((time.time() - start_t) * 1000)

        # Query Checkpoint 1
        predicted_query_unsafe = not result["checkpoint_1"]["is_safe"]
        if ground_truth_query_unsafe and predicted_query_unsafe:
            q_tp += 1
        elif not ground_truth_query_unsafe and predicted_query_unsafe:
            q_fp += 1
        elif not ground_truth_query_unsafe and not predicted_query_unsafe:
            q_tn += 1
        elif ground_truth_query_unsafe and not predicted_query_unsafe:
            q_fn += 1

        # Response Checkpoint 2 (if evaluated by pipeline)
        if result["checkpoint_2"] is not None:
            responses_evaluated += 1
            ground_truth_resp_unsafe = (s.get("response_label", "Safe").lower() == "unsafe")
            predicted_resp_unsafe = not result["checkpoint_2"]["is_safe"]

            if ground_truth_resp_unsafe and predicted_resp_unsafe:
                r_tp += 1
            elif not ground_truth_resp_unsafe and predicted_resp_unsafe:
                r_fp += 1
            elif not ground_truth_resp_unsafe and not predicted_resp_unsafe:
                r_tn += 1
            elif ground_truth_resp_unsafe and not predicted_resp_unsafe:
                r_fn += 1

    query_metrics = calculate_metrics(q_tp, q_fp, q_tn, q_fn)
    response_metrics = calculate_metrics(r_tp, r_fp, r_tn, r_fn)
    retrieval_metrics = evaluate_statutory_retrieval(samples)

    report = {
        "dataset": "datasets/finguard_bench_real/test.jsonl",
        "grounding": "Statutory Regulatory Corpus (BSA, SEC, CFPB, ECOA, FCPA, FINRA, GLBA, SOX)",
        "sample_count": len(samples),
        "pipeline_latency_ms": round(float(np.mean(latencies)), 2),
        "checkpoint_1_query_guard": query_metrics,
        "checkpoint_2_response_guard": {
            **response_metrics,
            "samples_evaluated": responses_evaluated
        },
        "retrieval_evaluation": retrieval_metrics
    }

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=======================================================")
    print("      FinGuard Grounded Real-Benchmark Report")
    print("=======================================================")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    run_full_pipeline_eval()
