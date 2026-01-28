#!/usr/bin/env bash

# output/trimmed/{1..10}/<algo>/<lang>/ 配下で
# *.wat が存在しない場合に grams ディレクトリを削除する

for trial in {1..10}; do
  base_dir="output/trimmed/${trial}"
  
  # 試行ディレクトリが存在しない場合はスキップ
  if [ ! -d "$base_dir" ]; then
    continue
  fi
  
  for algo in bubsort collatz fizzbuzz helloworld wordcount; do
    for lang in c go js rust ts; do
      target_dir="${base_dir}/${algo}/${lang}"
      
      # ディレクトリが存在しない場合はスキップ
      if [ ! -d "$target_dir" ]; then
        continue
      fi
      
      # .wat ファイルの数をカウント
      wat_count=$(find "$target_dir" -maxdepth 1 -name "*.wat" -type f 2>/dev/null | wc -l)
      
      # .wat が存在しない場合、grams ディレクトリを削除
      if [ "$wat_count" -eq 0 ]; then
        grams_dir="${target_dir}/grams"
        if [ -d "$grams_dir" ]; then
          echo "削除: ${grams_dir} (対応する .wat ファイルなし)"
          rm -rf "$grams_dir"
        fi
      fi
    done
  done
done

echo "完了: 不要な grams ディレクトリを削除しました"