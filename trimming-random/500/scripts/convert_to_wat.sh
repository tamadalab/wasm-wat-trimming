#!/bin/bash
set -e

# 設定
SRC_ROOT="./data"
DEST_ROOT="./output/not_trimmed"

echo "========================================"
echo " Starting WASM to WAT Conversion"
echo "========================================"

# dataディレクトリ内の .wasm ファイルを全て検索
find "$SRC_ROOT" -type f -name "*.wasm" | while read wasm_file; do
    # ディレクトリパスの取得 (例: ./data/bubsort/c)
    dir_path=$(dirname "$wasm_file")
    
    # ルートパスを除去して相対パスを取得 (例: bubsort/c)
    rel_path=${dir_path#$SRC_ROOT/}
    
    # 出力先ディレクトリを作成 (例: ./output/not_trimmed/bubsort/c)
    # ※ユーザー様のディレクトリ構成に合わせています
    output_dir="$DEST_ROOT/$rel_path"
    mkdir -p "$output_dir"
    
    # ファイル名操作
    filename=$(basename "$wasm_file")       # bubsort.wasm
    filename_no_ext="${filename%.*}"        # bubsort
    output_file="$output_dir/$filename_no_ext.wat"

    echo "Converting: $rel_path/$filename -> $output_file"

    # wasm2wat実行
    # --enable-all: 全てのWasm機能を有効化（エラー回避のため）
    wasm2wat "$wasm_file" -o "$output_file" --enable-all
done

echo "========================================"
echo " Conversion Completed Successfully!"
echo "========================================"