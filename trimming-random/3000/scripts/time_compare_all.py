#!/usr/bin/env python3
"""
time_compare_all.py
類似度計算スクリプトの実行時間を測定

使用方法:
    python3 time_compare_all.py [--base-dir BASE_DIR] [--output OUTPUT_CSV]

デフォルト:
    --base-dir: output/not_trimmed
    --output: output/timing_results.csv
"""

import os
import sys
import csv
import time
import subprocess
from pathlib import Path
from typing import Dict, List
import argparse


def find_similarity_scripts(scripts_dir: Path) -> List[Path]:
    """類似度計算スクリプトを探す"""
    similarity_scripts = [
        "cosine_similarity.py",
        "jaccard_similarity.py",
        "overlap_similarity.py",
        "manhattan_similarity.py",
        "kl_similarity.py",
        "lcs_similarity.py",
    ]
    
    found_scripts = []
    for script_name in similarity_scripts:
        script_path = scripts_dir / script_name
        if script_path.exists():
            found_scripts.append(script_path)
    
    return found_scripts


def measure_execution_time(script_path: Path, base_dir: Path, output_dir: Path) -> float:
    """
    類似度計算スクリプトの実行時間を測定
    
    Args:
        script_path: 実行するスクリプトのパス
        base_dir: WATファイルのベースディレクトリ
        output_dir: 出力ディレクトリ
    
    Returns:
        実行時間（秒）
    """
    start_time = time.time()
    
    try:
        # スクリプトを実行
        result = subprocess.run(
            ["python3", str(script_path), "--base-dir", str(base_dir), "--output-dir", str(output_dir)],
            capture_output=True,
            text=True,
            check=True
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"  ✓ {script_path.stem}: {elapsed_time:.2f}秒")
        return elapsed_time
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {script_path.stem}: エラー発生")
        print(f"    STDOUT: {e.stdout}")
        print(f"    STDERR: {e.stderr}")
        return -1.0
    except Exception as e:
        print(f"  ✗ {script_path.stem}: 予期しないエラー: {e}")
        return -1.0


def extract_method_name(script_name: str) -> str:
    """スクリプト名から手法名を抽出"""
    method_map = {
        "cosine_similarity.py": "Cosine",
        "jaccard_similarity.py": "Jaccard",
        "overlap_similarity.py": "Overlap",
        "manhattan_similarity.py": "Manhattan",
        "kl_similarity.py": "KL",
        "lcs_similarity.py": "LCS",
    }
    return method_map.get(script_name, script_name.replace("_similarity.py", "").title())


def main():
    parser = argparse.ArgumentParser(description="類似度計算の実行時間を測定")
    parser.add_argument("--base-dir", type=str, default="output/not_trimmed",
                        help="WATファイルのベースディレクトリ（デフォルト: output/not_trimmed）")
    parser.add_argument("--output", type=str, default="output/timing_results.csv",
                        help="出力CSVファイル（デフォルト: output/timing_results.csv）")
    parser.add_argument("--scripts-dir", type=str, default="scripts",
                        help="類似度計算スクリプトのディレクトリ（デフォルト: scripts）")
    
    args = parser.parse_args()
    
    # パスの設定
    base_dir = Path(args.base_dir)
    output_csv = Path(args.output)
    scripts_dir = Path(args.scripts_dir)
    
    # 出力ディレクトリの作成
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    # 類似度計算用の出力ディレクトリ
    similarity_output_dir = output_csv.parent / "similarity_matrices"
    similarity_output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("類似度計算の実行時間測定")
    print("=" * 80)
    print(f"ベースディレクトリ: {base_dir}")
    print(f"スクリプトディレクトリ: {scripts_dir}")
    print(f"出力CSV: {output_csv}")
    print()
    
    # スクリプトの確認
    if not scripts_dir.exists():
        print(f"[ERROR] スクリプトディレクトリが見つかりません: {scripts_dir}")
        return 1
    
    if not base_dir.exists():
        print(f"[ERROR] ベースディレクトリが見つかりません: {base_dir}")
        return 1
    
    similarity_scripts = find_similarity_scripts(scripts_dir)
    
    if not similarity_scripts:
        print(f"[ERROR] 類似度計算スクリプトが見つかりません")
        print(f"期待されるスクリプト: cosine_similarity.py, jaccard_similarity.py, ...")
        return 1
    
    print(f"見つかったスクリプト: {len(similarity_scripts)}個")
    for script in similarity_scripts:
        print(f"  - {script.name}")
    print()
    
    # 時間測定
    print("実行時間測定中...")
    results = []
    
    for script_path in similarity_scripts:
        method_name = extract_method_name(script_path.name)
        elapsed_time = measure_execution_time(script_path, base_dir, similarity_output_dir)
        
        if elapsed_time >= 0:
            results.append({
                'method': method_name,
                'time_seconds': elapsed_time
            })
    
    # CSV出力
    if results:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['method', 'time_seconds']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # メソッド名でソート
            results.sort(key=lambda x: x['method'])
            
            for row in results:
                writer.writerow(row)
        
        print()
        print("=" * 80)
        print("測定完了")
        print("=" * 80)
        print(f"結果を保存: {output_csv}")
        print()
        print("測定結果:")
        print(f"{'手法':<15} {'実行時間'}")
        print("-" * 35)
        for row in results:
            print(f"{row['method']:<15} {row['time_seconds']:>10.2f}秒")
        
        total_time = sum(r['time_seconds'] for r in results)
        print("-" * 35)
        print(f"{'合計':<15} {total_time:>10.2f}秒")
        
        return 0
    else:
        print()
        print("[ERROR] 測定データが得られませんでした")
        return 1


if __name__ == "__main__":
    sys.exit(main())
