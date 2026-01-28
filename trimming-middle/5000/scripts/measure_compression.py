#!/usr/bin/env python3
"""
measure_compression.py (パターンA用)
RQ1: トリミングによるWATファイルの圧縮効果を測定

現在のディレクトリ構造:
プロジェクトルート/
├── output/
│   ├── not_trimmed/
│   └── trimmed/
│       ├── 1/
│       ├── 2/
│       ...
│       └── 10/

Before/After の行数・バイト数を測定し、削減率を計算
Random は10試行の平均を計算
"""

import os
import sys
import csv
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def count_lines_and_bytes(filepath: Path) -> Tuple[int, int]:
    """WATファイルの行数とバイト数を取得"""
    if not filepath.exists():
        return 0, 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = sum(1 for _ in f)
    
    bytes_size = filepath.stat().st_size
    return lines, bytes_size


def find_wat_files(base_dir: Path) -> List[Tuple[str, str, Path]]:
    """
    指定ディレクトリ配下の全WATファイルを探す
    Returns: [(program, language, filepath), ...]
    """
    wat_files = []
    
    if not base_dir.exists():
        return wat_files
    
    for wat_path in base_dir.rglob("*.wat"):
        # パスから program と language を抽出
        # 例: output/not_trimmed/bubsort/c/bubsort.wat
        parts = wat_path.relative_to(base_dir).parts
        if len(parts) >= 3:
            program = parts[0]
            language = parts[1]
            wat_files.append((program, language, wat_path))
    
    return wat_files


def measure_random_trimming_simple(program: str, language: str) -> Dict:
    """
    Random トリミングの測定（10試行の平均）
    シンプル構造用: output/not_trimmed と output/trimmed/1..10
    """
    # Before
    before_path = Path("output/not_trimmed") / program / language / f"{program}.wat"
    lines_before, bytes_before = count_lines_and_bytes(before_path)
    
    if lines_before == 0:
        return None
    
    # After (trials 1..10)
    lines_after_list = []
    bytes_after_list = []
    
    for trial in range(1, 11):
        after_path = Path("output/trimmed") / str(trial) / program / language / f"{program}.wat"
        lines, bytes_size = count_lines_and_bytes(after_path)
        if lines > 0:
            lines_after_list.append(lines)
            bytes_after_list.append(bytes_size)
    
    if not lines_after_list:
        return None
    
    # 平均を計算
    lines_after_avg = sum(lines_after_list) / len(lines_after_list)
    bytes_after_avg = sum(bytes_after_list) / len(bytes_after_list)
    
    # トリミング長を推定（平均行数）
    estimated_length = int(lines_after_avg)
    
    # 削減率
    reduction_rate_lines = 1 - (lines_after_avg / lines_before) if lines_before > 0 else 0
    reduction_rate_bytes = 1 - (bytes_after_avg / bytes_before) if bytes_before > 0 else 0
    
    return {
        'method': 'random',
        'length': estimated_length,  # 推定値
        'program': program,
        'language': language,
        'lines_before': lines_before,
        'lines_after': lines_after_avg,
        'bytes_before': bytes_before,
        'bytes_after': bytes_after_avg,
        'reduction_rate_lines': reduction_rate_lines,
        'reduction_rate_bytes': reduction_rate_bytes,
        'trials_count': len(lines_after_list)
    }


def main():
    # 出力ディレクトリ
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    output_file = results_dir / "compression_stats.csv"
    
    all_results = []
    
    print("=" * 80)
    print("RQ1: 圧縮効果の測定 (シンプル構造用)")
    print("=" * 80)
    
    # output/not_trimmed が存在するか確認
    not_trimmed_dir = Path("output/not_trimmed")
    if not not_trimmed_dir.exists():
        print(f"\n[ERROR] {not_trimmed_dir} が見つかりません")
        print("プロジェクトのルートディレクトリで実行してください")
        return 1
    
    # Random トリミング（シンプル構造）
    print("\n[1] Random Trimming の測定...")
    
    # WATファイルを探す
    wat_files = find_wat_files(not_trimmed_dir)
    
    if not wat_files:
        print(f"  [ERROR] {not_trimmed_dir} 配下にWATファイルが見つかりません")
        return 1
    
    print(f"  見つかったファイル数: {len(wat_files)}")
    
    for program, language, _ in wat_files:
        result = measure_random_trimming_simple(program, language)
        if result:
            all_results.append(result)
            print(f"    {program}/{language}: "
                  f"lines={result['lines_before']:.0f}→{result['lines_after']:.1f} "
                  f"({result['reduction_rate_lines']*100:.1f}%), "
                  f"bytes={result['bytes_before']}→{result['bytes_after']:.1f} "
                  f"({result['reduction_rate_bytes']*100:.1f}%)")
        else:
            print(f"    [SKIP] {program}/{language}: トリミング後データが見つかりません")
    
    # CSV出力
    if all_results:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'method', 'length', 'program', 'language',
                'lines_before', 'lines_after', 'bytes_before', 'bytes_after',
                'reduction_rate_lines', 'reduction_rate_bytes', 'trials_count'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # method, length, program, language の順でソート
            all_results.sort(key=lambda x: (x['method'], x['length'], x['program'], x['language']))
            
            for row in all_results:
                writer.writerow(row)
        
        print(f"\n✓ 結果を保存: {output_file}")
        print(f"  総データ数: {len(all_results)}")
        
        # 集計表示
        print("\n" + "=" * 80)
        print("削減率の要約")
        print("=" * 80)
        
        # 全体の平均削減率
        avg_lines = sum(r['reduction_rate_lines'] for r in all_results) / len(all_results) * 100
        avg_bytes = sum(r['reduction_rate_bytes'] for r in all_results) / len(all_results) * 100
        estimated_length = int(sum(r['length'] for r in all_results) / len(all_results))
        
        print(f"\nトリミング長（推定平均）: {estimated_length} 行")
        print(f"行数削減率（平均）: {avg_lines:.1f}%")
        print(f"バイト削減率（平均）: {avg_bytes:.1f}%")
        print(f"測定ファイル数: {len(all_results)}")
        
        # プログラム別の削減率
        print("\n--- プログラム別削減率 ---")
        by_program = defaultdict(lambda: {'lines': [], 'bytes': []})
        for r in all_results:
            by_program[r['program']]['lines'].append(r['reduction_rate_lines'])
            by_program[r['program']]['bytes'].append(r['reduction_rate_bytes'])
        
        print(f"{'Program':<15} {'行削減率':<12} {'バイト削減率'}")
        print("-" * 40)
        for program, values in sorted(by_program.items()):
            avg_l = sum(values['lines']) / len(values['lines']) * 100
            avg_b = sum(values['bytes']) / len(values['bytes']) * 100
            print(f"{program:<15} {avg_l:>10.1f}%  {avg_b:>10.1f}%")
    
    else:
        print("\n[ERROR] 測定データが見つかりませんでした")
        print("\n確認事項:")
        print("  1. output/not_trimmed/ にWATファイルが存在するか")
        print("  2. output/trimmed/1..10/ にWATファイルが存在するか")
        print("  3. プロジェクトのルートディレクトリで実行しているか")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())