#!/bin/bash
set -e

# 引数で対象ディレクトリを指定（指定がなければデフォルトで output/not_trimmed）
# 使用法: ./run_extraction.sh ./output/trimmed
TARGET_DIR="${1:-./output/not_trimmed}"
SCRIPT_PATH="./scripts/extract_grams.py"

echo "========================================"
echo " Starting N-gram Extraction"
echo " Target Directory: $TARGET_DIR"
echo "========================================"

# 指定されたディレクトリが存在するかチェック
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory $TARGET_DIR does not exist."
    exit 1
fi

# 指定ディレクトリ以下の .wat ファイルを検索
find "$TARGET_DIR" -type f -name "*.wat" | while read wat_file; do
    echo "Processing: $wat_file"
    
    # Pythonスクリプトを実行 (1-gram から 6-gram まで)
    python3 "$SCRIPT_PATH" "$wat_file" --min 1 --max 6
    
done

echo "========================================"
echo " Extraction Completed Successfully!"
echo "========================================"