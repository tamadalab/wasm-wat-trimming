#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rename_with_prefix.py
---------------------
プロジェクトルートの親ディレクトリ名をプレフィックスとしてファイルをリネームする

プロジェクトルート例: /path/to/trimming-tail/500/
  - 二つ前: trimming-tail
  - 一つ前: 500
  - プレフィックス: trimming-tail_500_

対象ディレクトリ:
  - results/
  - output/trimmed_matrices/

使い方:
  cd trimming-tail/500/
  python3 scripts/rename_with_prefix.py [--dry-run]

オプション:
  --dry-run    実際にはリネームせず、変更内容を表示のみ
"""

import argparse
import sys
from pathlib import Path


def get_prefix_from_project_root(project_root: Path) -> str:
    """
    プロジェクトルートから親ディレクトリ名を取得してプレフィックスを生成
    
    例: /path/to/trimming-tail/500/ -> "trimming-tail_500"
    """
    # 絶対パスに変換
    project_root = project_root.resolve()
    
    # 一つ前（直接の親）
    one_up = project_root.name
    
    # 二つ前（親の親）
    two_up = project_root.parent.name
    
    # プレフィックスを生成
    prefix = f"{two_up}_{one_up}"
    
    return prefix


def rename_files_in_directory(target_dir: Path, prefix: str, dry_run: bool = False) -> int:
    """
    指定ディレクトリ内のファイルをリネーム
    
    Args:
        target_dir: 対象ディレクトリ
        prefix: 追加するプレフィックス
        dry_run: Trueの場合、実際にはリネームしない
    
    Returns:
        リネームしたファイル数
    """
    if not target_dir.exists():
        print(f"  [SKIP] ディレクトリが存在しません: {target_dir}")
        return 0
    
    count = 0
    
    for file_path in target_dir.iterdir():
        if not file_path.is_file():
            continue
        
        old_name = file_path.name
        
        # すでにプレフィックスが付いている場合はスキップ
        if old_name.startswith(prefix):
            print(f"  [SKIP] すでにプレフィックス付き: {old_name}")
            continue
        
        new_name = f"{prefix}_{old_name}"
        new_path = file_path.parent / new_name
        
        if dry_run:
            print(f"  [DRY-RUN] {old_name}")
            print(f"         -> {new_name}")
        else:
            file_path.rename(new_path)
            print(f"  [RENAMED] {old_name}")
            print(f"         -> {new_name}")
        
        count += 1
    
    return count


def main():
    parser = argparse.ArgumentParser(
        description="プロジェクトルートの親ディレクトリ名をプレフィックスとしてファイルをリネーム"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際にはリネームせず、変更内容を表示のみ"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="プロジェクトルート（デフォルト: カレントディレクトリ）"
    )
    args = parser.parse_args()
    
    project_root = args.project_root.resolve()
    
    print("=" * 80)
    print("ファイルリネーム（親ディレクトリ名プレフィックス追加）")
    print("=" * 80)
    print(f"プロジェクトルート: {project_root}")
    print(f"  一つ前（親）:     {project_root.name}")
    print(f"  二つ前（親の親）: {project_root.parent.name}")
    
    # プレフィックスを取得
    prefix = get_prefix_from_project_root(project_root)
    print(f"  プレフィックス:   {prefix}_")
    print()
    
    if args.dry_run:
        print("*** DRY-RUN モード（実際にはリネームしません） ***")
        print()
    
    # 対象ディレクトリ
    target_dirs = [
        project_root / "results",
        project_root / "output" / "trimmed_matrices",
    ]
    
    total_count = 0
    
    for target_dir in target_dirs:
        print(f"[{target_dir.relative_to(project_root)}]")
        count = rename_files_in_directory(target_dir, prefix, args.dry_run)
        total_count += count
        print()
    
    # サマリー
    print("=" * 80)
    print("サマリー")
    print("=" * 80)
    print(f"リネーム対象ファイル数: {total_count}")
    
    if args.dry_run:
        print()
        print("実際にリネームするには --dry-run オプションを外して実行してください:")
        print(f"  python3 {sys.argv[0]}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())