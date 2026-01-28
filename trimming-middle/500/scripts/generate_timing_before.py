#!/usr/bin/env python3
"""
generate_timing_before.py
-------------------------
ベースライン（トリミング前）の類似度計算時間を測定し、
timing_before.csv を生成する

使い方:
  python3 scripts/generate_timing_before.py
  
出力:
  output/timing_before.csv
"""

import os
import sys
import csv
import time
import subprocess
from pathlib import Path


# 類似度計算スクリプト
SIMILARITY_SCRIPTS = [
    ("cosine", "generate_selected_cosine_heatmap.py"),
    ("jaccard", "generate_selected_jaccard_heatmap.py"),
    ("overlap", "generate_selected_overlap_heatmap.py"),
    ("manhattan", "generate_selected_manhattan_heatmap.py"),
    ("kl", "generate_selected_kl_heatmap.py"),
    ("lcs", "generate_selected_lcs_heatmap_full_timed.py"),
]


def find_script(script_name: str) -> Path:
    """スクリプトを探す"""
    search_paths = [
        Path("scripts") / script_name,
        Path(".") / script_name,
        Path("..") / script_name,
    ]
    
    for path in search_paths:
        if path.exists():
            return path.resolve()
    
    raise FileNotFoundError(f"Script not found: {script_name}")


def measure_baseline_time(method_name: str, script_name: str) -> float:
    """ベースライン（トリミング前）の実行時間を測定"""
    print(f"\n[{method_name.upper()}] 測定中...")
    
    script_path = find_script(script_name)
    base_dir = Path("output/not_trimmed")
    output_dir = Path("output/_temp_baseline_matrices")
    
    if not base_dir.exists():
        print(f"  [ERROR] {base_dir} が見つかりません")
        return -1.0
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # コマンド構築
    cmd = [
        sys.executable,
        str(script_path),
        "--base-dir", str(base_dir),
        "--output-dir", str(output_dir),
    ]
    
    # LCSの場合は追加オプション
    if "lcs" in script_name.lower():
        cmd.extend(["--method", "min"])
    
    # 時間測定
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start_time
        print(f"  測定完了: {elapsed:.2f}秒")
        return elapsed
    
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] スクリプト実行エラー")
        print(f"  stderr: {e.stderr[:200] if e.stderr else 'N/A'}")
        return -1.0
    except Exception as e:
        print(f"  [ERROR] {e}")
        return -1.0


def main():
    print("=" * 80)
    print("ベースライン時間測定（timing_before.csv生成）")
    print("=" * 80)
    
    # 出力先
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_csv = output_dir / "timing_before.csv"
    
    # 測定実行
    results = []
    
    for method_name, script_name in SIMILARITY_SCRIPTS:
        elapsed = measure_baseline_time(method_name, script_name)
        
        if elapsed > 0:
            results.append({
                'method': method_name,
                'time_seconds': elapsed
            })
    
    # CSV出力
    if results:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['method', 'time_seconds']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in sorted(results, key=lambda x: x['method']):
                writer.writerow(row)
        
        print(f"\n{'=' * 80}")
        print("測定完了")
        print(f"{'=' * 80}")
        print(f"結果を保存: {output_csv}")
        print()
        print("測定結果:")
        print(f"{'手法':<12} {'時間(秒)'}")
        print("-" * 30)
        for row in sorted(results, key=lambda x: x['method']):
            print(f"{row['method']:<12} {row['time_seconds']:>10.2f}")
        
        # 一時ディレクトリの削除
        import shutil
        temp_dir = Path("output/_temp_baseline_matrices")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n[CLEAN] 一時ディレクトリを削除: {temp_dir}")
        
        return 0
    else:
        print("\n[ERROR] 測定に失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())