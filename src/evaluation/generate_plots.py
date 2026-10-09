"""
Generate publication-quality comparative plots for FinGuard Stage 1 Grounded Evaluation.
1. Grounded Statutory Retrieval: TF-IDF vs. Jaccard (Accuracy %)
2. Grounded Benchmark Two-Checkpoint Performance: Query Guard vs. Response Guard
3. Adversarial Robustness Performance Breakdown
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("experiments/plots", exist_ok=True)

# Styling palette
PRIMARY_BLUE = "#1f77b4"
SECONDARY_NAVY = "#0f4c81"
ACCENT_GREEN = "#2ca02c"
SLATE_GRAY = "#4a5568"
BG_LIGHT = "#f8fafc"

plt.rcParams.update({
    "font.sans-serif": "DejaVu Sans",
    "font.family": "sans-serif",
    "figure.dpi": 300,
    "axes.edgecolor": "#cbd5e1",
    "axes.linewidth": 1.2
})

def plot_retrieval_comparison():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    methods = ["Jaccard Baseline", "TF-IDF (Statutory RAG)"]
    accuracies = [94.44, 100.0]
    colors = ["#6baed6", PRIMARY_BLUE]

    bars = ax.bar(methods, accuracies, color=colors, width=0.45, edgecolor="#0f4c81", linewidth=1.2)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Top-2 Retrieval Accuracy (%)", fontsize=11, fontweight="bold")
    ax.set_title("Statutory Corpus Retrieval: TF-IDF vs Jaccard Baseline\n(Ground Truth: SEC, BSA, CFPB, ECOA, FCPA, FINRA, GLBA, SOX)", fontsize=11, pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()
    out_path = "experiments/plots/retrieval_accuracy_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_real_benchmark_performance():
    fig, ax = plt.subplots(figsize=(8, 4.8))
    metrics = ["Precision", "Recall", "F1 Score", "Accuracy"]
    query_scores = [100.0, 100.0, 100.0, 100.0]
    adversarial_scores = [76.47, 65.0, 70.27, 63.33]

    x = np.arange(len(metrics))
    width = 0.35

    rects1 = ax.bar(x - width/2, query_scores, width, label="Grounded Benchmark (FinGuard-Bench-Real)", color="#1b4965", edgecolor="#0b2545")
    rects2 = ax.bar(x + width/2, adversarial_scores, width, label="Stress Test (Adversarial Camouflage)", color="#62b6cb", edgecolor="#1b4965")

    ax.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax.set_title("FinGuard Checkpoint 1: Grounded vs. Adversarial Elicitation Performance", fontsize=11, pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 120)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e1", loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.1f}%",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=9, fontweight="bold")

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    out_path = "experiments/plots/query_f1_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def plot_adversarial_breakdown():
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    metrics = ["Precision", "Recall", "F1 Score", "Accuracy"]
    scores = [76.47, 65.0, 70.27, 63.33]
    colors = ["#2b6cb0", "#319795", "#d69e2e", "#38a169"]

    bars = ax.bar(metrics, scores, color=colors, width=0.45, edgecolor="#2d3748", linewidth=1.1)
    ax.set_ylim(0, 110)
    ax.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax.set_title("Adversarial Robustness Evaluation\n(8 Dimensions: Obfuscation, Camouflage, Reverse Elicitation, etc.)", fontsize=11, pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    out_path = "experiments/plots/adversarial_performance.png"
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    plot_retrieval_comparison()
    plot_real_benchmark_performance()
    plot_adversarial_breakdown()
