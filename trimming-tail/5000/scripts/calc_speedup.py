#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calc_speedup.py (修正版 - timing_before.csv対応)
---------------
RQ2: 類似度計算の高速化を測定

修正点:
- ベースライン測定をスキップ
- timing_before.csv から既存のベースライン時間を読み込み
- トリミング後の10試行のみ測定

処理:
1. timing_before.csv からベースライン時間を読み込み
2. output/trimmed/1..10 に対して類似度計算を実行
3. スピードアップ率を計算
4. results/speed_stats.csv に出力
"""

import os
import sys
import csv
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


# 類似度計算スクリプト
SIMILARITY_SCRIPTS = [
    ("cosine", "generate_selected_cosine_heatmap.py"),
    ("jaccard", "generate_selected_jaccard_heatmap.py"),
    ("overlap", "generate_selected_overlap_heatmap.py"),
    ("manhattan", "generate_selected_manhattan_heatmap.py"),
    ("kl", "generate_selected_kl_heatmap.py"),
    ("lcs", "generate_selected_lcs_heatmap_full_timed.py"),
]

# 既存のベースライン時間（秒）- timing_before.csv から読み込むか、ここに直接指定
# None の場合は timing_before.csv から自動読み込み
BASELINE_TIMES = {
    'cosine': None,
    'jaccard': None,
    'overlap': None,
    'manhattan': None,
    'kl': None,
    'lcs': None,
}

# trial数
NUM_TRIALS = 10


def load_baseline_times(project_root: Path) -> Dict[str, float]:
    """
    既存のベースライン時間を読み込む
    
    優先順位:
    1. BASELINE_TIMES に指定されている値
    2. output/timing_before.csv から読み込み
    3. timing_before.csv から読み込み（カレントディレクトリ）
    4. output/timing_results.csv から読み込み
    
    Returns:
        各手法のベースライン時間の辞書
    """
    baseline = {}
    
    # 1. ハードコードされた値を使用
    for method, time_val in BASELINE_TIMES.items():
        if time_val is not None and time_val > 0:
            baseline[method] = time_val
            print(f"  {method}: {time_val:.2f}秒 (スクリプト内指定値)")
    
    # 2. timing_before.csv から読み込み（優先）
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
                        for key in ['time_seconds', 'time_sec', 'baseline_time_sec', 'baseline_time', 'elapsed_sec']:
                            if key in row and row[key]:
                                try:
                                    time_val = float(row[key])
                                    break
                                except (ValueError, TypeError):
                                    continue
                        
                        if method and time_val and time_val > 0:
                            # すでに指定されていない場合のみ上書き
                            if method not in baseline or baseline[method] is None:
                                baseline[method] = time_val
                                print(f"  {method}: {time_val:.2f}秒 (CSVから読み込み)")
                
                # 見つかったら他のファイルを探さない
                if baseline:
                    break
                    
            except Exception as e:
                print(f"  [WARN] CSV読み込みエラー: {e}")
    
    # 3. 従来のtiming_results.csvも試す
    if not baseline:
        csv_path = project_root / "output" / "timing_results.csv"
        if csv_path.exists():
            print(f"\n既存のタイミングデータを読み込み: {csv_path}")
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        method = row.get('method', '').lower()
                        time_val = None
                        for key in ['baseline_time_sec', 'baseline_time', 'time_sec', 'elapsed_sec']:
                            if key in row and row[key]:
                                try:
                                    time_val = float(row[key])
                                    break
                                except (ValueError, TypeError):
                                    continue
                        
                        if method and time_val and time_val > 0:
                            if method not in baseline or baseline[method] is None:
                                baseline[method] = time_val
                                print(f"  {method}: {time_val:.2f}秒 (CSVから読み込み)")
            except Exception as e:
                print(f"  [WARN] CSV読み込みエラー: {e}")
    
    # 4. 見つからなかった手法を報告
    missing = [m for m in BASELINE_TIMES.keys() if m not in baseline or baseline[m] <= 0]
    if missing:
        print(f"\n[WARN] 以下の手法のベースライン時間が見つかりません: {', '.join(missing)}")
        print("  対処方法:")
        print("    1. output/timing_before.csv を配置")
        print("    2. スクリプト内の BASELINE_TIMES 辞書に直接値を指定")
    
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
        print(f"      stderr: {e.stderr[:200]}")
        return -1.0
    except Exception as e:
        print(f"    [ERROR] 予期しないエラー: {e}")
        return -1.0


def find_script(project_root: Path, script_name: str) -> Optional[Path]:
    """
    類似度計算スクリプトを探す
    
    探索順序:
    1. プロジェクトルート直下
    2. scripts/ ディレクトリ
    3. ../ (親ディレクトリ)
    4. ../../ (祖父ディレクトリ)
    
    Args:
        project_root: 現在のディレクトリ
        script_name: スクリプト名
    
    Returns:
        スクリプトのパス、見つからない場合はNone
    """
    search_paths = [
        project_root / script_name,
        project_root / "scripts" / script_name,
        project_root / ".." / script_name,
        project_root / "../.." / script_name,
        project_root / "../../.." / script_name,
    ]
    
    for path in search_paths:
        resolved = path.resolve()
        if resolved.exists():
            return resolved
    
    return None


def measure_trimmed_trials(project_root: Path, method_name: str, script_name: str) -> List[float]:
    """
    トリミング後（trimmed/1..10）の実行時間を測定
    
    Args:
        project_root: プロジェクトルート
        method_name: 手法名
        script_name: スクリプト名
    
    Returns:
        各trialの実行時間のリスト
    """
    print(f"\n  トリミング後測定中（{NUM_TRIALS}試行）...")
    
    script_path = find_script(project_root, script_name)
    
    if script_path is None:
        print(f"    [ERROR] スクリプトが見つかりません: {script_name}")
        return []
    
    print(f"    スクリプト: {script_path}")
    
    trimmed_base = project_root / "output" / "trimmed"
    
    if not trimmed_base.exists():
        print(f"    [ERROR] trimmedディレクトリが見つかりません: {trimmed_base}")
        return []
    
    times = []
    
    for trial in range(1, NUM_TRIALS + 1):
        trial_dir = trimmed_base / str(trial)
        
        if not trial_dir.exists():
            print(f"    [WARN] Trial {trial} が見つかりません: {trial_dir}")
            continue
        
        # 出力ディレクトリ
        output_dir = project_root / "output" / "similarity_matrices" / f"trial_{trial}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        elapsed = measure_execution_time(script_path, trial_dir, output_dir)
        
        if elapsed > 0:
            times.append(elapsed)
            print(f"    Trial {trial:2d}: {elapsed:.2f}秒")
        else:
            print(f"    Trial {trial:2d}: 測定失敗")
    
    if times:
        avg = sum(times) / len(times)
        print(f"    平均: {avg:.2f}秒 (測定成功: {len(times)}/{NUM_TRIALS})")
    
    return times


def main():
    print("=" * 80)
    print("RQ2: 類似度計算の高速化測定（修正版 - timing_before.csv対応）")
    print("=" * 80)
    print("\n特徴:")
    print("  - ベースライン測定をスキップ（既存データを使用）")
    print("  - timing_before.csv からベースライン時間を読み込み")
    print("  - トリミング後の10試行のみ測定")
    
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
        print("  2. スクリプト内の BASELINE_TIMES 辞書に直接値を指定")
        print("\nCSVフォーマット例:")
        print("  method,time_seconds")
        print("  Cosine,14.35")
        print("  Jaccard,9.41")
        print("  ...")
        return 1
    
    # 結果の保存先
    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    output_csv = results_dir / "speed_stats.csv"
    
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
        trimmed_times = measure_trimmed_trials(project_root, method_name, script_name)
        
        if not trimmed_times:
            print(f"[SKIP] {method_name} のトリミング後測定に失敗しました")
            continue
        
        # 平均時間
        avg_trimmed_time = sum(trimmed_times) / len(trimmed_times)
        
        # スピードアップ率
        speedup = baseline_time / avg_trimmed_time if avg_trimmed_time > 0 else 0.0
        
        results.append({
            'method': method_name,
            'baseline_time_sec': baseline_time,
            'trimmed_time_avg_sec': avg_trimmed_time,
            'speedup': speedup,
            'trials_measured': len(trimmed_times),
        })
        
        print(f"\n  スピードアップ: {speedup:.2f}x")
    
    # CSV出力
    if results:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['method', 'baseline_time_sec', 'trimmed_time_avg_sec', 'speedup', 'trials_measured']
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
        print(f"{'手法':<12} {'ベースライン':<15} {'トリミング後(平均)':<20} {'スピードアップ'}")
        print("-" * 70)
        
        for row in results:
            print(f"{row['method']:<12} {row['baseline_time_sec']:>13.2f}秒  "
                  f"{row['trimmed_time_avg_sec']:>17.2f}秒  {row['speedup']:>13.2f}x")
        
        avg_speedup = sum(r['speedup'] for r in results) / len(results)
        print("-" * 70)
        print(f"平均スピードアップ: {avg_speedup:.2f}x")
        
        # 一時ディレクトリの削除
        import shutil
        temp_dir = project_root / "output" / "_temp_trimmed"
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
        print("  2. timing_before.csv が正しく読み込まれていますか？")
        print("  3. output/trimmed/1..10/ にWATファイルが存在しますか？")
        print("  4. 類似度計算スクリプト (generate_selected_*.py) が存在しますか？")
        return 1


if __name__ == "__main__":
    sys.exit(main())