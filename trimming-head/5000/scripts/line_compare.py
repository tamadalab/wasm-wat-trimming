#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
line_compare.py
---------------
トリミング前後の WAT ファイル行数を比較し、
差分・削減率(%)を整列した表で表示するツール。

+ 追加: 削減率(%)の棒グラフをPNG保存できる（--plot）
"""

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ALGORITHMS = ["bubsort", "collatz", "fizzbuzz", "helloworld", "wordcount"]
LANGUAGES  = ["c", "go", "js", "rust", "ts"]


def count_lines(path: Path):
    """行数を返す。ファイルがなければ None"""
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def format_table(df: pd.DataFrame) -> str:
    """列幅を固定してズレなし表に整形"""
    col_widths = {
        "アルゴリズム": 12,
        "言語": 6,
        "Before(行数)": 12,
        "After(行数)": 12,
        "削除行数": 10,
        "削減率(%)": 10,
    }

    header = ""
    for col in df.columns:
        header += f"{col:<{col_widths[col]}} "
    header += "\n" + "-" * (sum(col_widths.values()) + len(col_widths))

    rows = []
    for _, row in df.iterrows():
        line = ""
        for col in df.columns:
            val = row[col]
            if isinstance(val, (int, float)):
                line += f"{str(val):>{col_widths[col]}} "
            else:
                line += f"{str(val):<{col_widths[col]}} "
        rows.append(line)

    return header + "\n" + "\n".join(rows)


def compare_lines(
    before_root="output/not_trimmed",
    after_root="output/trimmed",
    save_csv="line_compare.csv"
) -> pd.DataFrame:

    before_root = Path(before_root)
    after_root = Path(after_root)

    rows = []
    for algo in ALGORITHMS:
        for lang in LANGUAGES:
            before = before_root / algo / lang / f"{algo}.wat"
            after  = after_root  / algo / lang / f"{algo}.wat"

            before_lines = count_lines(before)
            after_lines  = count_lines(after)

            if before_lines is None or after_lines is None:
                print(f"[WARN] Missing file for {algo}/{lang}")
                continue

            deleted = before_lines - after_lines
            percent = (deleted / before_lines * 100) if before_lines > 0 else 0.0

            rows.append({
                "アルゴリズム": algo,
                "言語": lang,
                "Before(行数)": before_lines,
                "After(行数)": after_lines,
                "削除行数": deleted,
                "削減率(%)": round(percent, 2),
            })

    df = pd.DataFrame(rows)

    print("\n" + "=" * 80)
    print("⭐ トリミング前後の WAT 行数比較")
    print("=" * 80)
    print(format_table(df))

    if save_csv:
        df.to_csv(save_csv, index=False, encoding="utf-8")
        print(f"\n[SAVED] CSV -> {save_csv}")

    return df


def plot_reduction_rate_bar(
    df: pd.DataFrame,
    output_path: str,
    by: str = "language",      # language / algorithm / pair
    agg: str = "mean",         # mean / median / min / max
    sort: str = "desc",        # asc / desc （pair のときだけ使う想定）
) -> None:
    value_col = "削減率(%)"
    if df.empty:
        raise ValueError("DataFrame is empty. Compare step might have failed or files are missing.")

    if by == "language":
        s = df.groupby("言語")[value_col].agg(agg).reindex(LANGUAGES)
        labels = list(s.index)
        values = list(s.values)
        title = f"Line Reduction Rate by Language ({agg})"

    elif by == "algorithm":
        s = df.groupby("アルゴリズム")[value_col].agg(agg).reindex(ALGORITHMS)
        labels = list(s.index)
        values = list(s.values)
        title = f"Line Reduction Rate by Algorithm ({agg})"

    elif by == "pair":
        d = df.copy()
        d["pair"] = d["アルゴリズム"] + "/" + d["言語"]
        d = d.sort_values(value_col, ascending=(sort == "asc"))
        labels = d["pair"].tolist()
        values = d[value_col].tolist()
        title = "Line Reduction Rate by Program (algo/lang)"

    else:
        raise ValueError("by must be one of: language, algorithm, pair")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    n = len(values)
    figsize = (10, 5) if n <= 10 else (14, 6)
    plt.figure(figsize=figsize)

    bars = plt.bar(labels, values)
    plt.ylabel("Reduction rate (%)")
    plt.ylim(0, 100)
    plt.title(title)

    if n > 10:
        plt.xticks(rotation=90)
    else:
        # 少数バーなら数値を上に出す（見やすい）
        for b, v in zip(bars, values):
            plt.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(str(out), dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[SAVED] Plot -> {out}")


def main():
    parser = argparse.ArgumentParser(description="Compare WAT line counts before/after trimming.")
    parser.add_argument("--before-root", default="output/not_trimmed")
    parser.add_argument("--after-root",  default="output/trimmed")
    parser.add_argument("--save-csv",    default="line_compare.csv")
    parser.add_argument("--plot", action="store_true", help="削減率(%)の棒グラフPNGを保存する")
    parser.add_argument("--plot-out", default="line_reduction_rate.png")
    parser.add_argument("--plot-by", choices=["language", "algorithm", "pair"], default="language")
    parser.add_argument("--agg", choices=["mean", "median", "min", "max"], default="mean")
    parser.add_argument("--sort", choices=["asc", "desc"], default="desc", help="pair のときの並び替え")
    args = parser.parse_args()

    df = compare_lines(
        before_root=args.before_root,
        after_root=args.after_root,
        save_csv=args.save_csv,
    )

    if args.plot:
        plot_reduction_rate_bar(
            df=df,
            output_path=args.plot_out,
            by=args.plot_by,
            agg=args.agg,
            sort=args.sort,
        )


if __name__ == "__main__":
    main()
