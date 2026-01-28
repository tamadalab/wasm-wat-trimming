#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_selected_cosine_heatmap.py
----------------------------------
指定された15件のWASM n-gramデータを用いて、
コサイン類似度に基づく類似度ヒートマップを生成する。
"""

import os
import argparse
from collections import Counter
from math import sqrt
from time import time

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# 対象 (アルゴリズム, 言語) の 15 組
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

# 使用する n-gram の n
N_RANGE = range(1, 7)


def load_ngram_file(path: str) -> Counter:
    """n-gram ファイルを Counter に読み込む"""
    counter = Counter()
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return counter
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 2:
                continue
            ngram, count = parts
            try:
                counter[ngram] = int(count)
            except ValueError:
                continue
    return counter


def cosine_similarity(c1: Counter, c2: Counter) -> float:
    """コサイン類似度を計算"""
    if not c1 or not c2:
        return 0.0
    keys = set(c1.keys()) | set(c2.keys())
    dot = sum(c1.get(k, 0) * c2.get(k, 0) for k in keys)
    norm1 = sqrt(sum(v * v for v in c1.values()))
    norm2 = sqrt(sum(v * v for v in c2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def compute_avg_cosine(base_dir: str, algo1: str, lang1: str,
                       algo2: str, lang2: str) -> float:
    """n=1〜6 のコサイン類似度の平均を取る"""
    sims = []
    for n in N_RANGE:
        path1 = f"{base_dir}/{algo1}/{lang1}/grams/{algo1}_{n}gram.txt"
        path2 = f"{base_dir}/{algo2}/{lang2}/grams/{algo2}_{n}gram.txt"
        print(f"[DEBUG] Cosine: n={n} file1={path1}")
        print(f"[DEBUG] Cosine: n={n} file2={path2}")
        c1 = load_ngram_file(path1)
        c2 = load_ngram_file(path2)
        sim = cosine_similarity(c1, c2)
        print(f"[DEBUG] Cosine: n={n} sim={sim}")
        sims.append(sim)
    return sum(sims) / len(sims) if sims else 0.0


def build_similarity_matrix(base_dir: str) -> pd.DataFrame:
    """15×15 の類似度行列を構築"""
    labels = [f"{a}_{l}" for a, l in TARGETS]
    n = len(labels)
    matrix = [[0.0] * n for _ in range(n)]

    total_pairs = n * (n - 1) // 2
    done = 0
    start = time()
    print(f"[INFO] Cosine: total pairs = {total_pairs}")

    for i, (a1, l1) in enumerate(TARGETS):
        for j, (a2, l2) in enumerate(TARGETS):
            if i == j:
                matrix[i][j] = 1.0
            elif i < j:
                print(f"\n[PROGRESS] Cosine pair {done+1}/{total_pairs}")
                print(f"  {a1}_{l1}  vs  {a2}_{l2}")
                sim = compute_avg_cosine(base_dir, a1, l1, a2, l2)
                matrix[i][j] = matrix[j][i] = sim
                done += 1
                elapsed = time() - start
                print(f"[INFO] Cosine: sim={sim:.4f}, elapsed={elapsed:.2f}s")

    return pd.DataFrame(matrix, index=labels, columns=labels)


def plot_heatmap(df: pd.DataFrame, output_path: str) -> None:
    """ヒートマップを描画・保存"""
    plt.figure(figsize=(12, 10))
    sns.heatmap(df, cmap="YlOrRd", vmin=0, vmax=1, cbar=True,
                linewidths=0.5)
    plt.title("Cosine Similarity (15 Selected Files)", fontsize=14)
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
    parser.add_argument("--output-dir", default="heatmaps_cosine",
                        help="ヒートマップの出力先ディレクトリ")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 80)
    print("COSINE SIMILARITY HEATMAP GENERATOR")
    print("=" * 80)

    df = build_similarity_matrix(args.base_dir)
    csv_path = f"{args.output_dir}/cosine_similarity_matrix.csv"
    df.to_csv(csv_path)
    print(f"[SAVED] {csv_path}")

    png_path = f"{args.output_dir}/cosine_heatmap.png"
    plot_heatmap(df, png_path)

    print("[INFO] Cosine heatmap generation completed.")


if __name__ == "__main__":
    main()
