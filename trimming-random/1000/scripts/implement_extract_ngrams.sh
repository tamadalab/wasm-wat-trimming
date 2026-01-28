#!/usr/bin/env bash

# 存在する .wat ファイルのパスを配列に格納
wat_files=()

for i in {1..10}; do
  for algo in bubsort collatz fizzbuzz helloworld wordcount; do
    for lang in c go js rust ts; do
      # ★ $output ではなく output を使う
      path="output/trimmed/${i}/${algo}/${lang}/${algo}.wat"
      
      # ★ -f でファイルの存在をチェック
      if [ -f "$path" ]; then
        wat_files+=("$path")
      fi
    done
  done
done

# 見つかったファイル数を表示
echo "見つかった .wat ファイル: ${#wat_files[@]} 個"

# pythonを実行する(watファイルから1~6gramsのtxtファイルを作成する)
for path in "${wat_files[@]}"; do
  echo "処理中: ${path}"
  python3 scripts/extract_ngrams.py --min 1 --max 6 "$path"
done

echo "完了"