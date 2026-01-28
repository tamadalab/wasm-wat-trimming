#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_selected_kl_heatmap.py
----------------------------------
指定された15件のWASM n-gramデータを用いて、
KL Divergence（カルバック＝ライブラー情報量）に基づく
類似度ヒートマップを生成する。
"""

import os
import argparse
from collections import Counter
from math import log
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
EPS = 1e-10


def load_freq(path: str) -> dict:
    """n-gram ファイルを確率分布 (dict) として読み込む"""
    counter = Counter()
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return {}
    total = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 2:
                continue
            ngram, count = parts
            try:
                c = int(count)
            except ValueError:
                continue
            counter[ngram] += c
            total += c
    if total == 0:
        return {}
    return {k: v / total for k, v in counter.items()}


def kl_divergence(p: dict, q: dict) -> float:
    """KL(P || Q)"""
    keys = set(p.keys()) | set(q.keys())
    kl = 0.0
    for k in keys:
        pk = p.get(k, 0.0) + EPS
        qk = q.get(k, 0.0) + EPS
        kl += pk * log(pk / qk)
    return kl


def kl_similarity(p: dict, q: dict) -> float:
    """対称 KL を 1 / (1 + D) に変換して類似度にする"""
    if not p or not q:
        return 0.0
    d = kl_divergence(p, q) + kl_divergence(q, p)
    return 1.0 / (1.0 + d)


def compute_avg_kl(base_dir: str, algo1: str, lang1: str,
                   algo2: str, lang2: str) -> float:
    sims = []
    for n in N_RANGE:
        path1 = f"{base_dir}/{algo1}/{lang1}/grams/{algo1}_{n}gram.txt"
        path2 = f"{base_dir}/{algo2}/{lang2}/grams/{algo2}_{n}gram.txt"
        print(f"[DEBUG] KL: n={n} file1={path1}")
        print(f"[DEBUG] KL: n={n} file2={path2}")
        p = load_freq(path1)
        q = load_freq(path2)
        sim = kl_similarity(p, q)
        print(f"[DEBUG] KL: n={n} sim={sim}")
        sims.append(sim)
    return sum(sims) / len(sims) if sims else 0.0


def build_similarity_matrix(base_dir: str) -> pd.DataFrame:
    labels = [f"{a}_{l}" for a, l in TARGETS]
    n = len(labels)
    matrix = [[0.0] * n for _ in range(n)]

    total_pairs = n * (n - 1) // 2
    done = 0
    start = time()
    print(f"[INFO] KL: total pairs = {total_pairs}")

    for i, (a1, l1) in enumerate(TARGETS):
        for j, (a2, l2) in enumerate(TARGETS):
            if i == j:
                matrix[i][j] = 1.0
            elif i < j:
                print(f"\n[PROGRESS] KL pair {done+1}/{total_pairs}")
                print(f"  {a1}_{l1}  vs  {a2}_{l2}")
                sim = compute_avg_kl(base_dir, a1, l1, a2, l2)
                matrix[i][j] = matrix[j][i] = sim
                done += 1
                elapsed = time() - start
                print(f"[INFO] KL: sim={sim:.4f}, elapsed={elapsed:.2f}s")

    return pd.DataFrame(matrix, index=labels, columns=labels)


def plot_heatmap(df: pd.DataFrame, output_path: str) -> None:
    plt.figure(figsize=(12, 10))
    sns.heatmap(df, cmap="Oranges", vmin=0, vmax=1, cbar=True,
                linewidths=0.5)
    plt.title("KL-based Similarity (15 Selected Files)", fontsize=14)
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
    parser.add_argument("--output-dir", default="heatmaps_kl",
                        help="ヒートマップの出力先ディレクトリ")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 80)
    print("KL DIVERGENCE-BASED SIMILARITY HEATMAP GENERATOR")
    print("=" * 80)

    df = build_similarity_matrix(args.base_dir)
    csv_path = f"{args.output_dir}/kl_similarity_matrix.csv"
    df.to_csv(csv_path)
    print(f"[SAVED] {csv_path}")

    png_path = f"{args.output_dir}/kl_heatmap.png"
    plot_heatmap(df, png_path)

    print("[INFO] KL heatmap generation completed.")


if __name__ == "__main__":
    main()
