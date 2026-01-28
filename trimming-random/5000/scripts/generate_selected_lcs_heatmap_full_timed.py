#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_selected_lcs_heatmap_full_timed.py
-------------------------------------------
指定された15件の WAT ファイルについて、
「トリミングを行わずに」命令列の LCS に基づく類似度ヒートマップを生成し、
同時に処理時間を計測するスクリプト。

ポイント
- generate_selected_lcs_heatmap_fast.py と同じ TARGETS を使用
- limit によるトリミングはデフォルトでは行わない（全命令を対象）
- 各ペアの LCS 計算時間と、全ペア計算に要した総時間を表示
"""

import os
import argparse
import re
import time

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 対象 15 件 (アルゴリズム, 言語)  ※ fast 版と同じ
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

LANGUAGES = ["ts", "js", "c", "rust", "go"]
ALGORITHMS = ["helloworld", "fizzbuzz", "collatz", "bubsort", "wordcount"]

# ---------------------------------------------------------
# 命令トークン抽出関連
# ---------------------------------------------------------
TOKEN_SPLIT_RE = re.compile(r"[()\s]+")
DOT_INSTR_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+$")
DECL_TOKENS = {
    "module", "func", "type", "import", "export",
    "param", "result", "local", "global", "memory", "table", "elem", "data"
}
SINGLE_WORD_OPS = {
    "block", "loop", "if", "else", "end",
    "call", "drop", "return", "nop", "unreachable",
    "br", "br_if", "br_table", "select"
}


def is_instruction_token(tok: str) -> bool:
    """命令トークンかどうかを判定"""
    if not tok:
        return False
    # 整数リテラルなどは除外
    if re.fullmatch(r"[-+]?\d+", tok) or re.fullmatch(r"0x[0-9a-fA-F]+", tok):
        return False
    # 宣言系トークンは除外
    if tok in DECL_TOKENS:
        return False
    # i32.add などの "xxx.yyy" 形式
    if DOT_INSTR_RE.match(tok):
        return True
    # block, loop など単語一発の命令
    if tok in SINGLE_WORD_OPS:
        return True
    return False


def load_wat_instructions(wat_path: str, limit: int = None) -> list:
    """
    WAT ファイルから命令列を抽出（limit が指定されていれば先頭 limit 命令まで）
    base_dir は ./output/not_trimmed などを想定
    """
    if not os.path.exists(wat_path):
        print(f"[WARN] File not found: {wat_path}")
        return []

    with open(wat_path, encoding="utf-8", errors="ignore") as f:
        text = f.read()

    raw_tokens = TOKEN_SPLIT_RE.split(text)
    instructions = [t for t in raw_tokens if is_instruction_token(t)]

    if limit is not None and len(instructions) > limit:
        instructions = instructions[:limit]

    return instructions


# ---------------------------------------------------------
# LCS 関連
# ---------------------------------------------------------
def lcs_length_fast(seq1: list, seq2: list) -> int:
    """
    LCS 長を計算（メモリ最適化版）
    O(min(m, n)) のメモリ使用量
    """
    # メモリ節約のため、短い方を seq2 にする
    if len(seq1) < len(seq2):
        seq1, seq2 = seq2, seq1

    m, n = len(seq1), len(seq2)
    if m == 0 or n == 0:
        return 0

    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        ai = seq1[i - 1]
        for j in range(1, n + 1):
            if ai == seq2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = prev[j] if prev[j] >= curr[j - 1] else curr[j - 1]
        prev = curr
    return prev[n]


def lcs_similarity(seq1: list, seq2: list, method: str = "min") -> float:
    """LCS 類似度を計算"""
    if not seq1 or not seq2:
        return 0.0

    lcs_len = lcs_length_fast(seq1, seq2)
    len1, len2 = len(seq1), len(seq2)

    if method == "min":
        denom = min(len1, len2)
        return lcs_len / denom if denom > 0 else 0.0
    elif method == "avg":
        denom = len1 + len2
        return (2 * lcs_len) / denom if denom > 0 else 0.0
    elif method == "max":
        denom = max(len1, len2)
        return lcs_len / denom if denom > 0 else 0.0
    else:
        raise ValueError(f"Unknown method: {method}")


# ---------------------------------------------------------
# 15件用の類似度行列計算（時間計測付き）
# ---------------------------------------------------------
def compute_lcs_sim_for_pair(
    base_dir: str,
    algo1: str,
    lang1: str,
    algo2: str,
    lang2: str,
    method: str = "min",
    limit: int = None,
) -> tuple:
    """
    2つの (アルゴリズム, 言語) ペアに対する LCS 類似度を計算。
    戻り値: (similarity, elapsed_sec)
    """
    wat1 = f"{base_dir}/{algo1}/{lang1}/{algo1}.wat"
    wat2 = f"{base_dir}/{algo2}/{lang2}/{algo2}.wat"

    print(f"[DEBUG] LCS: file1={wat1}")
    print(f"[DEBUG] LCS: file2={wat2}")

    seq1 = load_wat_instructions(wat1, limit=limit)
    seq2 = load_wat_instructions(wat2, limit=limit)

    print(f"[DEBUG]  len(seq1)={len(seq1)}, len(seq2)={len(seq2)}, limit={limit}")

    start = time.perf_counter()
    sim = lcs_similarity(seq1, seq2, method=method)
    elapsed = time.perf_counter() - start

    print(f"[DEBUG]  sim={sim:.4f}, elapsed={elapsed:.2f}s")

    return sim, elapsed


def build_similarity_matrix(
    base_dir: str,
    method: str = "min",
    limit: int = None,
) -> tuple:
    """
    15×15 の LCS 類似度行列を構築し、総処理時間も返す。
    """
    labels = [f"{a}_{l}" for a, l in TARGETS]
    n = len(labels)
    matrix = [[0.0] * n for _ in range(n)]

    total_pairs = n * (n - 1) // 2
    done = 0
    start_all = time.perf_counter()

    limit_str = "ALL" if limit is None else str(limit)
    print(f"[INFO] LCS (instruction-based, full test)")
    print(f"[INFO]   total pairs = {total_pairs}")
    print(f"[INFO]   method={method}, limit={limit_str}")
    print(f"[INFO]   base_dir={base_dir}")

    # 対称行列なので i < j のみ計算
    for i, (a1, l1) in enumerate(TARGETS):
        for j, (a2, l2) in enumerate(TARGETS):
            if i == j:
                matrix[i][j] = 1.0
                continue
            if i < j:
                print("\n[PROGRESS] LCS pair {}/{}".format(done + 1, total_pairs))
                print(f"  {a1}_{l1}  vs  {a2}_{l2}")
                sim, elapsed_pair = compute_lcs_sim_for_pair(
                    base_dir, a1, l1, a2, l2,
                    method=method, limit=limit,
                )
                matrix[i][j] = matrix[j][i] = sim
                done += 1
                elapsed_all = time.perf_counter() - start_all
                print(f"[INFO]   pair_elapsed={elapsed_pair:.2f}s, total_elapsed={elapsed_all:.2f}s")

    total_elapsed = time.perf_counter() - start_all
    df = pd.DataFrame(matrix, index=labels, columns=labels)

    print("\n" + "=" * 80)
    print("LCS (instruction-based, full length) timing summary")
    print("=" * 80)
    print(f"Total pairs         : {total_pairs}")
    print(f"Method              : {method}")
    print(f"Limit               : {limit_str}")
    print(f"Total elapsed (sec) : {total_elapsed:.2f}")
    print("=" * 80)

    return df, total_elapsed


# ---------------------------------------------------------
# ヒートマップ描画
# ---------------------------------------------------------
def plot_heatmap(
    df: pd.DataFrame,
    output_path: str,
    method: str = "min",
    limit: int = None,
) -> None:
    plt.figure(figsize=(12, 10))
    sns.heatmap(df, cmap="RdPu", vmin=0, vmax=1,
                cbar=True, linewidths=0.5)
    limit_str = "ALL" if limit is None else str(limit)
    title = f"LCS Instruction Similarity (15 Selected Files)\nmethod={method}, limit={limit_str}"
    plt.title(title, fontsize=14)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[SAVED] {output_path}")
    plt.close()


# ---------------------------------------------------------
# メイン
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate full-length LCS-based similarity heatmap for 15 selected WAT files (with timing)."
    )
    parser.add_argument(
        "--base-dir", required=True,
        help="例: ./output/not_trimmed (WAT が [algo]/[lang]/[algo].wat にあるディレクトリ)"
    )
    parser.add_argument(
        "--output-dir", default="heatmaps_lcs_full",
        help="ヒートマップと行列 CSV の出力ディレクトリ"
    )
    parser.add_argument(
        "--method", choices=["min", "avg", "max"], default="min",
        help="LCS 類似度の正規化方法 (min / avg / max)"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="任意: 先頭から何命令までを対象とするか。省略時はトリミングせず全命令(ALL)。"
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 80)
    print("FULL-LENGTH LCS HEATMAP GENERATOR (15 selected files)")
    print("=" * 80)

    # limit=None のときは本当にトリミングしない
    limit = args.limit

    df, total_elapsed = build_similarity_matrix(
        base_dir=args.base_dir,
        method=args.method,
        limit=limit,
    )

    limit_suffix = "" if limit is None else f"_limit{limit}"
    csv_path = f"{args.output_dir}/lcs_instruction_similarity_matrix_{args.method}{limit_suffix}.csv"
    df.to_csv(csv_path)
    print(f"[SAVED] {csv_path}")

    png_path = f"{args.output_dir}/lcs_instruction_heatmap_{args.method}{limit_suffix}.png"
    plot_heatmap(df, png_path, method=args.method, limit=limit)

    print(f"[DONE] Total elapsed time = {total_elapsed:.2f} sec")


if __name__ == "__main__":
    main()
