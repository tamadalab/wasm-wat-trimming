#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calc_speedup_deterministic.py
---------------
RQ2: Deterministicトリミングによる類似度計算の高速化を測定

処理:
1. output/timing_before.csv からベースライン時間を読み込み
2. output/trimmed/ に対して類似度計算を実行
3. スピードアップ率を計算
4. results/speed_stats_deterministic.csv に出力
"""

import os
import sys
import csv
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


# 類似度計算スクリプト
SIMILARITY_SCRIPTS = [
    ("cosine", "generate_selected_cosine_heatmap.py"),
    ("jaccard", "generate_selected_jaccard_heatmap.py"),
    ("overlap", "generate_selected_overlap_heatmap.py"),
    ("manhattan", "generate_selected_manhattan_heatmap.py"),
    ("kl", "generate_selected_kl_heatmap.py"),
    ("lcs", "generate_selected_lcs_heatmap_full_timed.py"),
]


def load_baseline_times(project_root: Path) -> Dict[str, float]:
    """
    既存のベースライン時間を読み込む
    
    優先順位:
    1. output/timing_before.csv から読み込み
    2. timing_before.csv から読み込み（カレントディレクトリ）
    
    Returns:
        各手法のベースライン時間の辞書
    """
    baseline = {}
    
    csv_paths = [
        project_root / "output" / "timing_before.csv",
        project_root / "timing_before.csv",
    ]
    
    for csv_path in csv_paths:
        if csv_path.exists():
            print(f"\n既存のタイミングデータを読み込み: {csv_path}")
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # method列を探す（大文字小文字を無視）
                        method = None
                        for key in row.keys():
                            if key.lower() == 'method':
                                method = row[key].lower()
                                break
                        
                        if not method:
                            continue
                        
                        # 時間の値を探す
                        time_val = None
                        for key in ['time_seconds', 'time_sec', 'baseline_time_sec', 
                                    'baseline_time', 'elapsed_sec']:
                            if key in row and row[key]:
                                try:
                                    time_val = float(row[key])
                                    break
                                except (ValueError, TypeError):
                                    continue
                        
                        if method and time_val and time_val > 0:
                            baseline[method] = time_val
                            print(f"  {method}: {time_val:.2f}秒")
                
                if baseline:
                    break
                    
            except Exception as e:
                print(f"  [WARN] CSV読み込みエラー: {e}")
    
    # 見つからなかった手法を報告
    expected_methods = ['cosine', 'jaccard', 'overlap', 'manhattan', 'kl', 'lcs']
    missing = [m for m in expected_methods if m not in baseline]
    if missing:
        print(f"\n[WARN] 以下の手法のベースライン時間が見つかりません: {', '.join(missing)}")
    
    return baseline


def measure_execution_time(script_path: Path, base_dir: Path, output_dir: Path) -> float:
    """
    類似度計算スクリプトの実行時間を測定
    
    Args:
        script_path: 実行するスクリプトのパス
        base_dir: WATファイルのベースディレクトリ
        output_dir: 出力ディレクトリ
    
    Returns:
        実行時間（秒）、エラーの場合は-1
    """
    start_time = time.time()
    
    cmd = [
        sys.executable,
        str(script_path),
        "--base-dir", str(base_dir),
        "--output-dir", str(output_dir),
    ]
    
    # LCSの場合は追加オプション
    if "lcs" in script_path.name.lower():
        cmd.extend(["--method", "min"])
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        elapsed = time.time() - start_time
        return elapsed
    
    except subprocess.CalledProcessError as e:
        print(f"    [ERROR] スクリプト実行エラー: {script_path.name}")
        print(f"      stderr: {e.stderr[:200] if e.stderr else 'N/A'}")
        return -1.0
    except Exception as e:
        print(f"    [ERROR] 予期しないエラー: {e}")
        return -1.0


def find_script(project_root: Path, script_name: str) -> Optional[Path]:
    """
    類似度計算スクリプトを探す
    """
    search_paths = [
        project_root / "scripts" / script_name,
        project_root / script_name,
        project_root / ".." / script_name,
    ]
    
    for path in search_paths:
        resolved = path.resolve()
        if resolved.exists():
            return resolved
    
    return None


def measure_trimmed(project_root: Path, method_name: str, script_name: str) -> float:
    """
    トリミング後（output/trimmed/）の実行時間を測定
    
    Args:
        project_root: プロジェクトルート
        method_name: 手法名
        script_name: スクリプト名
    
    Returns:
        実行時間（秒）、失敗時は-1
    """
    print(f"\n  トリミング後測定中...")
    
    script_path = find_script(project_root, script_name)
    
    if script_path is None:
        print(f"    [ERROR] スクリプトが見つかりません: {script_name}")
        return -1.0
    
    print(f"    スクリプト: {script_path}")
    
    trimmed_dir = project_root / "output" / "trimmed"
    
    if not trimmed_dir.exists():
        print(f"    [ERROR] trimmedディレクトリが見つかりません: {trimmed_dir}")
        return -1.0
    
    # 出力ディレクトリ（一時的）
    output_dir = project_root / "output" / "_temp_deterministic_matrices"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    elapsed = measure_execution_time(script_path, trimmed_dir, output_dir)
    
    if elapsed > 0:
        print(f"    実行時間: {elapsed:.2f}秒")
    else:
        print(f"    測定失敗")
    
    return elapsed


def main():
    print("=" * 80)
    print("RQ2: 類似度計算の高速化測定 (Deterministic)")
    print("=" * 80)
    
    # プロジェクトルート
    project_root = Path.cwd()
    
    # 既存のベースライン時間を読み込み
    print("\n" + "=" * 80)
    print("既存のベースライン時間を読み込み")
    print("=" * 80)
    baseline_times = load_baseline_times(project_root)
    
    if not baseline_times:
        print("\n[ERROR] ベースライン時間が見つかりません")
        print("\n対処方法:")
        print("  1. output/timing_before.csv を作成してベースライン時間を記録")
        print("\nCSVフォーマット例:")
        print("  method,time_seconds")
        print("  cosine,14.35")
        print("  jaccard,9.41")
        print("  ...")
        return 1
    
    # 結果の保存先
    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    output_csv = results_dir / "speed_stats_deterministic.csv"
    
    # 測定結果を保存
    results = []
    
    # 各手法について測定
    for method_name, script_name in SIMILARITY_SCRIPTS:
        print(f"\n{'=' * 80}")
        print(f"{method_name.upper()} の測定")
        print(f"{'=' * 80}")
        
        # ベースライン時間を取得
        baseline_time = baseline_times.get(method_name)
        
        if baseline_time is None or baseline_time <= 0:
            print(f"[SKIP] {method_name} のベースライン時間が見つかりません")
            continue
        
        print(f"\n  ベースライン時間: {baseline_time:.2f}秒 (既存データ)")
        
        # トリミング後測定
        trimmed_time = measure_trimmed(project_root, method_name, script_name)
        
        if trimmed_time <= 0:
            print(f"[SKIP] {method_name} のトリミング後測定に失敗しました")
            continue
        
        # スピードアップ率
        speedup = baseline_time / trimmed_time if trimmed_time > 0 else 0.0
        
        results.append({
            'method': method_name,
            'baseline_time_sec': baseline_time,
            'trimmed_time_sec': trimmed_time,
            'speedup': speedup,
        })
        
        print(f"\n  スピードアップ: {speedup:.2f}x")
    
    # CSV出力
    if results:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['method', 'baseline_time_sec', 'trimmed_time_sec', 'speedup']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # メソッド名でソート
            results.sort(key=lambda x: x['method'])
            
            for row in results:
                writer.writerow(row)
        
        print(f"\n{'=' * 80}")
        print("測定完了")
        print(f"{'=' * 80}")
        print(f"結果を保存: {output_csv}")
        print()
        print("=" * 80)
        print("スピードアップのサマリー")
        print("=" * 80)
        print(f"{'手法':<12} {'ベースライン':<15} {'トリミング後':<15} {'スピードアップ'}")
        print("-" * 60)
        
        for row in results:
            print(f"{row['method']:<12} {row['baseline_time_sec']:>13.2f}秒  "
                  f"{row['trimmed_time_sec']:>12.2f}秒  {row['speedup']:>13.2f}x")
        
        avg_speedup = sum(r['speedup'] for r in results) / len(results)
        print("-" * 60)
        print(f"平均スピードアップ: {avg_speedup:.2f}x")
        
        # 一時ディレクトリの削除
        import shutil
        temp_dir = project_root / "output" / "_temp_deterministic_matrices"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n[CLEAN] 一時ディレクトリを削除: {temp_dir}")
        
        return 0
    else:
        print()
        print("[ERROR] 測定データが得られませんでした")
        print()
        print("確認事項:")
        print("  1. プロジェクトルートで実行していますか？")
        print("  2. output/timing_before.csv が正しく読み込まれていますか？")
        print("  3. output/trimmed/ にWATファイルが存在しますか？")
        print("  4. 類似度計算スクリプト (generate_selected_*.py) が存在しますか？")
        return 1


if __name__ == "__main__":
    sys.exit(main())
