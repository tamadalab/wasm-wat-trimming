#!/usr/bin/env python3
"""
compute_average_matrix.py
-------------------------
trial_1 から trial_10 までの類似度行列を要素ごとに平均する
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np


def compute_average_for_method(method: str, input_base: Path, output_dir: Path) -> bool:
    """
    指定された類似度手法について、trial_1..10 の平均を計算
    
    Args:
        method: 類似度手法名 (cosine, jaccard, etc.)
        input_base: similarity_matrices のベースディレクトリ
        output_dir: 出力ディレクトリ
    
    Returns:
        成功したら True
    """
    # ファイル名のパターンを決定
    if method == "lcs":
        filename_pattern = "lcs_instruction_similarity_matrix_min.csv"
    else:
        filename_pattern = f"{method}_similarity_matrix.csv"
    
    # trial_1..10 の CSV を読み込む
    matrices = []
    for trial in range(1, 11):
        csv_path = input_base / f"trial_{trial}" / filename_pattern
        
        if not csv_path.exists():
            print(f"[WARN] {csv_path} が見つかりません")
            continue
        
        df = pd.read_csv(csv_path, index_col=0)
        matrices.append(df)
        print(f"  読み込み: trial_{trial} ({df.shape})")
    
    if not matrices:
        print(f"[ERROR] {method} の行列が見つかりませんでした")
        return False
    
    # 要素ごとに平均を計算
    # すべての DataFrame が同じ形状・同じインデックス/カラムと仮定
    avg_values = np.mean([df.values for df in matrices], axis=0)
    avg_df = pd.DataFrame(
        avg_values,
        index=matrices[0].index,
        columns=matrices[0].columns
    )
    
    # 出力
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if method == "lcs":
        output_path = output_dir / "lcs_instruction_similarity_matrix_min_avg.csv"
    else:
        output_path = output_dir / f"{method}_similarity_matrix_avg.csv"
    
    avg_df.to_csv(output_path)
    print(f"✓ 平均行列を保存: {output_path}")
    print(f"  試行数: {len(matrices)}")
    
    return True


def main():
    # ディレクトリ設定
    input_base = Path("output/similarity_matrices")
    output_dir = Path("output/average_matrices")
    
    if not input_base.exists():
        print(f"[ERROR] {input_base} が見つかりません")
        print("先に類似度行列を生成してください")
        return 1
    
    print("=" * 80)
    print("類似度行列の平均計算")
    print("=" * 80)
    print(f"入力: {input_base}/trial_1..10/")
    print(f"出力: {output_dir}/")
    print()
    
    # 6つの類似度手法について処理
    methods = ["cosine", "jaccard", "overlap", "manhattan", "kl", "lcs"]
    success_count = 0
    
    for method in methods:
        print(f"[{method.upper()}] 平均を計算中...")
        if compute_average_for_method(method, input_base, output_dir):
            success_count += 1
        print()
    
    print("=" * 80)
    print(f"完了: {success_count}/{len(methods)} 手法")
    print("=" * 80)
    
    return 0 if success_count == len(methods) else 1


if __name__ == "__main__":
    sys.exit(main())