#!/usr/bin/env bash

# 番号が異なるファイル同士を比較
for algo in bubsort collatz fizzbuzz helloworld wordcount; do
  for lang in c go js rust ts; do
    echo "=== ${algo} (${lang}) の比較 ==="
    
    # 存在するファイルを収集
    files=()
    for i in {1..10}; do
      path="output/trimmed/${i}/${algo}/${lang}/${algo}.wat"
      if [ -f "$path" ]; then
        files+=("$i:$path")
      fi
    done
    
    # ファイルが2つ以上ある場合のみ比較
    if [ ${#files[@]} -lt 2 ]; then
      echo "  比較対象が不足: ${#files[@]} 個"
      echo ""
      continue
    fi
    
    # すべてのペアを比較
    for file_a in "${files[@]}"; do
      num_a="${file_a%%:*}"
      path_a="${file_a#*:}"
      
      for file_b in "${files[@]}"; do
        num_b="${file_b%%:*}"
        path_b="${file_b#*:}"
        
        # 番号が小さい方を先に比較(重複を避ける)
        if [ "$num_a" -ge "$num_b" ]; then
          continue
        fi
        
        # 差分チェック
        if ! diff -q "$path_a" "$path_b" > /dev/null 2>&1; then
          echo "  差分あり: ${num_a} vs ${num_b}"
          
          # 詳細な差分(最初の5行)
          diff -u "$path_a" "$path_b" | head -n 15
          echo ""
        else
          echo "  同一: ${num_a} vs ${num_b}"
        fi
      done
    done
    echo ""
  done
done

echo "完了"

