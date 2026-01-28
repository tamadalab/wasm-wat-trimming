#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
corr_compare_selected.py
------------------------
トリミング前後の類似度行列CSVを読み込み、
その相関係数（Pearson r）を計算して評価するスクリプト。

使い方:
  python scripts/corr_compare_selected.py

前提条件:
- output/not_trimmed_matrices/ に Before の類似度行列CSV（6手法）が存在
- output/average_matrices/ に After の平均類似度行列CSV（6手法）が存在
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# 各比較手法ごとの設定
# ----------------------------------------------------------------------
METHODS = {
    "Cosine": {
        "before_csv": "cosine_similarity_matrix.csv",
        "after_csv": "cosine_similarity_matrix_avg.csv",
    },
    "Jaccard": {
        "before_csv": "jaccard_similarity_matrix.csv",
        "after_csv": "jaccard_similarity_matrix_avg.csv",
    },
    "Overlap": {
        "before_csv": "overlap_similarity_matrix.csv",
        "after_csv": "overlap_similarity_matrix_avg.csv",
    },
    "Manhattan": {
        "before_csv": "manhattan_similarity_matrix.csv",
        "after_csv": "manhattan_similarity_matrix_avg.csv",
    },
    "KL": {
        "before_csv": "kl_similarity_matrix.csv",
        "after_csv": "kl_similarity_matrix_avg.csv",
    },
    "LCS": {
        "before_csv": "lcs_instruction_similarity_matrix_min.csv",
        "after_csv": "lcs_instruction_similarity_matrix_min_avg.csv",
    },
}


def load_matrix(csv_path: Path) -> pd.DataFrame:
    """CSV から類似度行列 (DataFrame) を読み込む"""
    if not csv_path.exists():
        raise FileNotFoundError(f"Matrix CSV not found: {csv_path}")
    return pd.read_csv(csv_path, index_col=0)


def flatten_upper_triangle(df: pd.DataFrame) -> np.ndarray:
    """
    対角成分を除いた「上三角成分」を 1 次元に並べたベクトルにする。
    """
    mat = df.values
    n = mat.shape[0]
    iu = np.triu_indices(n, k=1)  # k=1 で対角の一つ上から
    return mat[iu]


def compute_correlation(v_before: np.ndarray, v_after: np.ndarray) -> float:
    """
    2つのベクトル間のPearson相関係数を計算
    NaNや無効値のハンドリングを含む
    """
    # NaNを除去
    mask = ~(np.isnan(v_before) | np.isnan(v_after))
    v_before_clean = v_before[mask]
    v_after_clean = v_after[mask]
    
    if len(v_before_clean) < 2:
        print("  [WARN] 有効なデータポイントが2未満です")
        return np.nan
    
    # 標準偏差が0の場合のチェック
    if np.std(v_before_clean) == 0 or np.std(v_after_clean) == 0:
        print("  [WARN] 標準偏差が0です（すべて同じ値）")
        return np.nan
    
    # Pearson相関係数を計算
    correlation = np.corrcoef(v_before_clean, v_after_clean)[0, 1]
    
    return correlation


def main():
    # ディレクトリ設定
    before_dir = Path("output/not_trimmed_matrices")
    after_dir = Path("output/average_matrices")
    results_dir = Path("results")
    
    # ディレクトリの存在確認
    if not before_dir.exists():
        print(f"[ERROR] {before_dir} が見つかりません")
        print("先に類似度行列（Before）を生成してください")
        return 1
    
    if not after_dir.exists():
        print(f"[ERROR] {after_dir} が見つかりません")
        print("先に平均行列（After）を生成してください")
        print("実行: make rq3-avg-matrix")
        return 1
    
    results = []
    
    print("=" * 80)
    print("トリミング前後の類似度行列 相関係数比較")
    print("=" * 80)
    print(f"Before: {before_dir}/")
    print(f"After:  {after_dir}/")
    print()
    
    for method_name, cfg in METHODS.items():
        print("-" * 80)
        print(f"[{method_name}]")
        
        # CSVパス
        csv_before = before_dir / cfg["before_csv"]
        csv_after = after_dir / cfg["after_csv"]
        
        # 存在確認
        if not csv_before.exists():
            print(f"  [ERROR] Before CSV が見つかりません: {csv_before}")
            results.append({
                "手法": method_name,
                "相関係数 r": np.nan,
                "状態": "Before CSV missing"
            })
            continue
        
        if not csv_after.exists():
            print(f"  [ERROR] After CSV が見つかりません: {csv_after}")
            results.append({
                "手法": method_name,
                "相関係数 r": np.nan,
                "状態": "After CSV missing"
            })
            continue
        
        try:
            # CSV読み込み
            df_before = load_matrix(csv_before)
            df_after = load_matrix(csv_after)
            
            print(f"  Before: {df_before.shape}")
            print(f"  After:  {df_after.shape}")
            
            # 形状チェック
            if df_before.shape != df_after.shape:
                print(f"  [ERROR] 行列の形状が一致しません")
                results.append({
                    "手法": method_name,
                    "相関係数 r": np.nan,
                    "状態": "Shape mismatch"
                })
                continue
            
            # 上三角成分を抽出
            v_before = flatten_upper_triangle(df_before)
            v_after = flatten_upper_triangle(df_after)
            
            print(f"  上三角成分数: {len(v_before)}")
            
            # 相関係数を計算
            r = compute_correlation(v_before, v_after)
            
            if np.isnan(r):
                status = "計算エラー"
            else:
                status = "OK"
            
            results.append({
                "手法": method_name,
                "相関係数 r": r,
                "状態": status
            })
            
            print(f"  相関係数 r = {r:.4f}" if not np.isnan(r) else f"  相関係数 r = NaN")
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({
                "手法": method_name,
                "相関係数 r": np.nan,
                "状態": f"Error: {str(e)}"
            })
        
        print()
    
    # まとめを DataFrame にして出力
    res_df = pd.DataFrame(results)
    
    print("=" * 80)
    print("⭐ トリミング前後の類似度行列 相関係数まとめ")
    print("=" * 80)
    print(res_df.to_string(index=False))
    print()
    
    # 統計情報
    valid_r = res_df[res_df["状態"] == "OK"]["相関係数 r"]
    if len(valid_r) > 0:
        print(f"有効な手法数: {len(valid_r)}/{len(METHODS)}")
        print(f"平均相関係数: {valid_r.mean():.4f}")
        print(f"最小相関係数: {valid_r.min():.4f}")
        print(f"最大相関係数: {valid_r.max():.4f}")
        print()
    
    # CSV 保存
    results_dir.mkdir(exist_ok=True)
    save_path = results_dir / "correlation_stats.csv"
    res_df.to_csv(save_path, index=False)
    print(f"[SAVED] {save_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())