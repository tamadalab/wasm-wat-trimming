#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_selected_jaccard_heatmap.py
----------------------------------
指定された15件のWASM n-gramデータを用いて、
Jaccard係数に基づく類似度ヒートマップを生成する。
"""

import os
import argparse
from time import time

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


TARGETS = [
    ("bubsort", "go"), ("collatz", "go"),
    ("collatz", "js"), ("bubsort", "js"),
    ("helloworld", "go"), ("fizzbuzz", "go"),
    ("wordcount", "go"), ("collatz", "rust"),
    ("bubsort", "rust"), ("wordcount", "c"),
    ("fizzbuzz", "c"), ("collatz", "c"),
    ("bubsort", "c"), ("bubsort", "ts"),
    ("helloworld", "ts"),
]

N_RANGE = range(1, 7)


def load_ngram_set(path: str) -> set:
    """n-gram を集合として読み込む（ngram 文字列のみ）"""
    s = set()
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return s
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if not parts:
                continue
            ngram = parts[0]
            s.add(ngram)
    return s


def jaccard_similarity(s1: set, s2: set) -> float:
    if not s1 and not s2:
        return 0.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union if union > 0 else 0.0


def compute_avg_jaccard(base_dir: str, algo1: str, lang1: str,
                        algo2: str, lang2: str) -> float:
    sims = []
    for n in N_RANGE:
        path1 = f"{base_dir}/{algo1}/{lang1}/grams/{algo1}_{n}gram.txt"
        path2 = f"{base_dir}/{algo2}/{lang2}/grams/{algo2}_{n}gram.txt"
        print(f"[DEBUG] Jaccard: n={n} file1={path1}")
        print(f"[DEBUG] Jaccard: n={n} file2={path2}")
        s1 = load_ngram_set(path1)
        s2 = load_ngram_set(path2)
        sim = jaccard_similarity(s1, s2)
        print(f"[DEBUG] Jaccard: n={n} sim={sim}")
        sims.append(sim)
    return sum(sims) / len(sims) if sims else 0.0


def build_similarity_matrix(base_dir: str) -> pd.DataFrame:
    labels = [f"{a}_{l}" for a, l in TARGETS]
    n = len(labels)
    matrix = [[0.0] * n for _ in range(n)]

    total_pairs = n * (n - 1) // 2
    done = 0
    start = time()
    print(f"[INFO] Jaccard: total pairs = {total_pairs}")

    for i, (a1, l1) in enumerate(TARGETS):
        for j, (a2, l2) in enumerate(TARGETS):
            if i == j:
                matrix[i][j] = 1.0
            elif i < j:
                print(f"\n[PROGRESS] Jaccard pair {done+1}/{total_pairs}")
                print(f"  {a1}_{l1}  vs  {a2}_{l2}")
                sim = compute_avg_jaccard(base_dir, a1, l1, a2, l2)
                matrix[i][j] = matrix[j][i] = sim
                done += 1
                elapsed = time() - start
                print(f"[INFO] Jaccard: sim={sim:.4f}, elapsed={elapsed:.2f}s")

    return pd.DataFrame(matrix, index=labels, columns=labels)


def plot_heatmap(df: pd.DataFrame, output_path: str) -> None:
    plt.figure(figsize=(12, 10))
    sns.heatmap(df, cmap="Blues", vmin=0, vmax=1, cbar=True,
                linewidths=0.5)
    plt.title("Jaccard Similarity (15 Selected Files)", fontsize=14)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[SAVED] {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", required=True,
                        help="output/not_trimmed または output/trimmed など")
    parser.add_argument("--output-dir", default="heatmaps_jaccard",
                        help="ヒートマップの出力先ディレクトリ")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 80)
    print("JACCARD SIMILARITY HEATMAP GENERATOR")
    print("=" * 80)

    df = build_similarity_matrix(args.base_dir)
    csv_path = f"{args.output_dir}/jaccard_similarity_matrix.csv"
    df.to_csv(csv_path)
    print(f"[SAVED] {csv_path}")

    png_path = f"{args.output_dir}/jaccard_heatmap.png"
    plot_heatmap(df, png_path)

    print("[INFO] Jaccard heatmap generation completed.")


if __name__ == "__main__":
    main()
