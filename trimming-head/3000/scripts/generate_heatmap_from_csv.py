#!/usr/bin/env python3
"""
generate_heatmap_from_csv.py
----------------------------
CSVの類似度行列からヒートマップPNGを生成する
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def generate_heatmap(csv_path: Path, output_path: Path, title: str, cmap: str = "YlOrRd"):
    """
    CSVファイルからヒートマップを生成
    
    Args:
        csv_path: 入力CSVファイル
        output_path: 出力PNGファイル
        title: ヒートマップのタイトル
        cmap: カラーマップ名
    """
    if not csv_path.exists():
        print(f"[ERROR] {csv_path} が見つかりません")
        return False
    
    # CSV読み込み
    df = pd.read_csv(csv_path, index_col=0)
    
    # ヒートマップ描画
    plt.figure(figsize=(12, 10))
    sns.heatmap(df, cmap=cmap, vmin=0, vmax=1, cbar=True, linewidths=0.5)
    plt.title(title, fontsize=14)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    
    # 保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"✓ ヒートマップ生成: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="CSV類似度行列からヒートマップを生成"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("output/average_matrices"),
        help="CSVファイルの入力ディレクトリ"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/average_heatmaps"),
        help="PNGファイルの出力ディレクトリ"
    )
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print(f"[ERROR] {args.input_dir} が見つかりません")
        return 1
    
    print("=" * 80)
    print("ヒートマップ生成")
    print("=" * 80)
    print(f"入力: {args.input_dir}")
    print(f"出力: {args.output_dir}")
    print()
    
    # 各手法のカラーマップ設定
    method_configs = {
        "cosine": {"cmap": "YlOrRd", "title": "Cosine Similarity (Average of 10 Trials)"},
        "jaccard": {"cmap": "Blues", "title": "Jaccard Similarity (Average of 10 Trials)"},
        "overlap": {"cmap": "Greens", "title": "Overlap Coefficient (Average of 10 Trials)"},
        "manhattan": {"cmap": "PuBuGn", "title": "Manhattan Similarity (Average of 10 Trials)"},
        "kl": {"cmap": "Oranges", "title": "KL-based Similarity (Average of 10 Trials)"},
        "lcs": {"cmap": "RdPu", "title": "LCS Instruction Similarity (Average of 10 Trials)"},
    }
    
    success_count = 0
    
    for method, config in method_configs.items():
        # 入力ファイル名を決定
        if method == "lcs":
            csv_filename = "lcs_instruction_similarity_matrix_min_avg.csv"
            png_filename = "lcs_instruction_heatmap_min_avg.png"
        else:
            csv_filename = f"{method}_similarity_matrix_avg.csv"
            png_filename = f"{method}_heatmap_avg.png"
        
        csv_path = args.input_dir / csv_filename
        png_path = args.output_dir / png_filename
        
        print(f"[{method.upper()}]")
        if generate_heatmap(csv_path, png_path, config["title"], config["cmap"]):
            success_count += 1
        print()
    
    print("=" * 80)
    print(f"完了: {success_count}/{len(method_configs)} 手法")
    print("=" * 80)
    
    return 0 if success_count == len(method_configs) else 1


if __name__ == "__main__":
    sys.exit(main())