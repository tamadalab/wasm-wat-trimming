#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deterministic_trim.py
--------------------
WATファイルを決まった位置（head/middle/tail）からトリミングする

使い方:
  python3 deterministic_trim.py --method head --lines 500
  python3 deterministic_trim.py --method middle --lines 1000  
  python3 deterministic_trim.py --method tail --lines 3000

出力先:
  ./output/trimmed/{algo}/{lang}/{algo}.wat
  （カレントディレクトリ基準）
"""

import argparse
import sys
from pathlib import Path
from typing import List


def trim_wat_head(lines: List[str], target_lines: int) -> List[str]:
    """先頭から指定行数を取得"""
    return lines[:target_lines]


def trim_wat_middle(lines: List[str], target_lines: int) -> List[str]:
    """中央部分から指定行数を取得"""
    total_lines = len(lines)
    
    if target_lines >= total_lines:
        return lines
    
    start = (total_lines - target_lines) // 2
    end = start + target_lines
    
    return lines[start:end]


def trim_wat_tail(lines: List[str], target_lines: int) -> List[str]:
    """末尾から指定行数を取得"""
    return lines[-target_lines:]


def process_wat_file(
    input_path: Path,
    output_path: Path,
    method: str,
    target_lines: int
) -> dict:
    """1つのWATファイルをトリミング"""
    if not input_path.exists():
        return {
            'status': 'error',
            'message': f'Input file not found: {input_path}'
        }
    
    # WATファイル読み込み
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_lines = len(lines)
    
    # トリミング実行
    if method == 'head':
        trimmed_lines = trim_wat_head(lines, target_lines)
    elif method == 'middle':
        trimmed_lines = trim_wat_middle(lines, target_lines)
    elif method == 'tail':
        trimmed_lines = trim_wat_tail(lines, target_lines)
    else:
        return {
            'status': 'error',
            'message': f'Unknown method: {method}'
        }
    
    # 出力ディレクトリ作成（gramsディレクトリも作成）
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grams_dir = output_path.parent / 'grams'
    grams_dir.mkdir(exist_ok=True)
    
    # WATファイル書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(trimmed_lines)
    
    return {
        'status': 'success',
        'original_lines': original_lines,
        'trimmed_lines': len(trimmed_lines),
        'method': method,
        'input_path': str(input_path),
        'output_path': str(output_path)
    }


def main():
    parser = argparse.ArgumentParser(
        description='WAT files deterministic trimming tool'
    )
    parser.add_argument(
        '--method',
        required=True,
        choices=['head', 'middle', 'tail'],
        help='Trimming method'
    )
    parser.add_argument(
        '--lines',
        type=int,
        required=True,
        help='Number of lines to keep'
    )
    parser.add_argument(
        '--algos',
        default='bubsort,collatz,fizzbuzz,helloworld,wordcount',
        help='Comma-separated algorithm names'
    )
    parser.add_argument(
        '--langs',
        default='c,go,js,ts,rust',
        help='Comma-separated language names'
    )
    parser.add_argument(
        '--input-base',
        default='output/not_trimmed',
        help='Base directory for input WAT files'
    )
    parser.add_argument(
        '--output-base',
        default='output/trimmed',
        help='Base directory for output WAT files'
    )
    
    args = parser.parse_args()
    
    # 入力・出力ディレクトリ（カレントディレクトリ基準）
    input_base = Path(args.input_base)
    output_dir = Path(args.output_base)
    
    # アルゴリズムと言語のリスト
    algos = [a.strip() for a in args.algos.split(',')]
    langs = [l.strip() for l in args.langs.split(',')]
    
    print("=" * 80)
    print(f"Deterministic WAT Trimming - {args.method.upper()}")
    print("=" * 80)
    print(f"Method:        {args.method}")
    print(f"Target lines:  {args.lines}")
    print(f"Current dir:   {Path.cwd()}")
    print(f"Input base:    {input_base}")
    print(f"Output dir:    {output_dir}")
    print(f"Algorithms:    {', '.join(algos)}")
    print(f"Languages:     {', '.join(langs)}")
    print()
    
    # 処理統計
    stats = {
        'success': 0,
        'error': 0,
        'skipped': 0,
        'total_original_lines': 0,
        'total_trimmed_lines': 0
    }
    
    # 各プログラム・言語の組み合わせを処理
    for algo in algos:
        for lang in langs:
            wat_filename = f'{algo}.wat'
            input_path = input_base / algo / lang / wat_filename
            output_path = output_dir / algo / lang / wat_filename
            
            # 入力ファイルが存在しない場合はスキップ
            if not input_path.exists():
                print(f"[SKIP] {algo}/{lang}: Input file not found")
                stats['skipped'] += 1
                continue
            
            # トリミング実行
            result = process_wat_file(
                input_path,
                output_path,
                args.method,
                args.lines
            )
            
            if result['status'] == 'success':
                stats['success'] += 1
                stats['total_original_lines'] += result['original_lines']
                stats['total_trimmed_lines'] += result['trimmed_lines']
                
                print(f"[OK] {algo}/{lang}: "
                      f"{result['original_lines']} → {result['trimmed_lines']} lines")
            else:
                stats['error'] += 1
                print(f"[ERROR] {algo}/{lang}: {result['message']}")
    
    # サマリー表示
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Success:  {stats['success']}")
    print(f"Error:    {stats['error']}")
    print(f"Skipped:  {stats['skipped']}")
    
    if stats['success'] > 0:
        avg_original = stats['total_original_lines'] / stats['success']
        avg_trimmed = stats['total_trimmed_lines'] / stats['success']
        reduction_rate = (1 - avg_trimmed / avg_original) * 100 if avg_original > 0 else 0
        
        print()
        print(f"Average original lines: {avg_original:.1f}")
        print(f"Average trimmed lines:  {avg_trimmed:.1f}")
        print(f"Reduction rate:         {reduction_rate:.1f}%")
    
    print()
    print(f"Output directory: {output_dir}")
    print("=" * 80)
    
    return 0 if stats['error'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())