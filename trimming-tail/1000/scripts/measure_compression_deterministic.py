#!/usr/bin/env python3
"""
measure_compression_deterministic.py
RQ1: Deterministicトリミングによる圧縮効果を測定

ディレクトリ構造:
プロジェクトルート/
├── output/
│   ├── not_trimmed/
│   │   └── {algo}/{lang}/{algo}.wat
│   └── trimmed/
│       └── {algo}/{lang}/{algo}.wat

Before/After の行数・バイト数を測定し、削減率を計算
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


def measure_deterministic_trimming(program: str, language: str, 
                                    not_trimmed_dir: Path, 
                                    trimmed_dir: Path) -> Dict:
    """
    Deterministic トリミングの測定
    シンプル構造用: output/not_trimmed と output/trimmed
    """
    # Before
    before_path = not_trimmed_dir / program / language / f"{program}.wat"
    lines_before, bytes_before = count_lines_and_bytes(before_path)
    
    if lines_before == 0:
        return None
    
    # After (single file, no trials)
    after_path = trimmed_dir / program / language / f"{program}.wat"
    lines_after, bytes_after = count_lines_and_bytes(after_path)
    
    if lines_after == 0:
        return None
    
    # 削減率
    reduction_rate_lines = 1 - (lines_after / lines_before) if lines_before > 0 else 0
    reduction_rate_bytes = 1 - (bytes_after / bytes_before) if bytes_before > 0 else 0
    
    return {
        'method': 'deterministic',
        'length': lines_after,
        'program': program,
        'language': language,
        'lines_before': lines_before,
        'lines_after': lines_after,
        'bytes_before': bytes_before,
        'bytes_after': bytes_after,
        'reduction_rate_lines': reduction_rate_lines,
        'reduction_rate_bytes': reduction_rate_bytes,
    }


def main():
    # ディレクトリ設定
    not_trimmed_dir = Path("output/not_trimmed")
    trimmed_dir = Path("output/trimmed")
    results_dir = Path("results")
    
    results_dir.mkdir(exist_ok=True)
    output_file = results_dir / "compression_stats_deterministic.csv"
    
    all_results = []
    
    print("=" * 80)
    print("RQ1: 圧縮効果の測定 (Deterministic)")
    print("=" * 80)
    
    # ディレクトリ存在確認
    if not not_trimmed_dir.exists():
        print(f"\n[ERROR] {not_trimmed_dir} が見つかりません")
        print("プロジェクトのルートディレクトリで実行してください")
        return 1
    
    if not trimmed_dir.exists():
        print(f"\n[ERROR] {trimmed_dir} が見つかりません")
        print("先に deterministic trimming を実行してください")
        return 1
    
    print(f"\nBefore: {not_trimmed_dir}")
    print(f"After:  {trimmed_dir}")
    
    # Deterministic トリミング測定
    print("\n[1] Deterministic Trimming の測定...")
    
    # WATファイルを探す（not_trimmed側から）
    wat_files = find_wat_files(not_trimmed_dir)
    
    if not wat_files:
        print(f"  [ERROR] {not_trimmed_dir} 配下にWATファイルが見つかりません")
        return 1
    
    print(f"  見つかったファイル数: {len(wat_files)}")
    
    for program, language, _ in wat_files:
        result = measure_deterministic_trimming(
            program, language, not_trimmed_dir, trimmed_dir
        )
        if result:
            all_results.append(result)
            print(f"    {program}/{language}: "
                  f"lines={result['lines_before']}→{result['lines_after']} "
                  f"({result['reduction_rate_lines']*100:.1f}%), "
                  f"bytes={result['bytes_before']}→{result['bytes_after']} "
                  f"({result['reduction_rate_bytes']*100:.1f}%)")
        else:
            print(f"    [SKIP] {program}/{language}: トリミング後データが見つかりません")
    
    # CSV出力
    if all_results:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'method', 'length', 'program', 'language',
                'lines_before', 'lines_after', 'bytes_before', 'bytes_after',
                'reduction_rate_lines', 'reduction_rate_bytes'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # program, language の順でソート
            all_results.sort(key=lambda x: (x['program'], x['language']))
            
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
        avg_length = sum(r['length'] for r in all_results) / len(all_results)
        
        print(f"\nトリミング後行数（平均）: {avg_length:.1f} 行")
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
        print("  2. output/trimmed/ にWATファイルが存在するか")
        print("  3. プロジェクトのルートディレクトリで実行しているか")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
