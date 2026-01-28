import os
from pathlib import Path
import pandas as pd

# watファイルのベースディレクトリ
base_dir = "."  # 現在のディレクトリ

data = []

# アルゴリズムのディレクトリをループ
algorithms = ["bubsort", "collatz", "fizzbuzz", "helloworld", "wordcount"]
languages = ["c", "go", "js", "rust", "ts"]

for algorithm in algorithms:
    for language in languages:
        # 変更されたパス
        wat_file = Path(base_dir) / "output" / "not_trimmed" / algorithm / language / f"{algorithm}.wat"
        
        if wat_file.exists():
            # ファイルの行数をカウント
            with open(wat_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for line in f)
            
            # ファイルサイズ
            size_bytes = os.path.getsize(wat_file)
            size_kb = size_bytes / 1024
            size_mb = size_kb / 1024
            
            data.append({
                "アルゴリズム": algorithm,
                "言語": language,
                "行数": line_count,
                "サイズ(KB)": round(size_kb, 2),
                "サイズ(MB)": round(size_mb, 2),
            })
        else:
            print(f"⚠️  ファイルが見つかりません: {wat_file}")

# DataFrameに変換
df = pd.DataFrame(data)
df_sorted = df.sort_values("行数", ascending=False)

print("=" * 80)
print("全ファイルの行数とサイズ（行数でソート）")
print("=" * 80)
print(df_sorted.to_string(index=False))

print("\n" + "=" * 80)
print("統計情報")
print("=" * 80)
stats = df["行数"].describe()
print(f"最小: {int(stats['min'])} 行")
print(f"最大: {int(stats['max'])} 行")
print(f"平均: {int(stats['mean'])} 行")
print(f"中央値: {int(stats['50%'])} 行")
print(f"25%点: {int(stats['25%'])} 行")
print(f"75%点: {int(stats['75%'])} 行")

print("\n" + "=" * 80)
print("言語別の平均行数")
print("=" * 80)
lang_avg = df.groupby("言語")["行数"].mean().sort_values(ascending=False)
for lang, avg in lang_avg.items():
    print(f"{lang:6s}: {int(avg):8d} 行")

print("\n" + "=" * 80)
print("アルゴリズム別の平均行数")
print("=" * 80)
algo_avg = df.groupby("アルゴリズム")["行数"].mean().sort_values(ascending=False)
for algo, avg in algo_avg.items():
    print(f"{algo:12s}: {int(avg):8d} 行")

print("\n" + "=" * 80)
print("言語 × アルゴリズム の行数マトリックス")
print("=" * 80)
pivot = df.pivot_table(values="行数", index="言語", columns="アルゴリズム", aggfunc='first')
print(pivot.to_string())

print("\n" + "=" * 80)
print("推奨トリミング基準")
print("=" * 80)
median = int(stats['50%'])
q25 = int(stats['25%'])
print(f"オプション1（中央値基準）: {median} 行")
print(f"オプション2（25%点基準）: {q25} 行")
print(f"オプション3（安全策）   : 1000 行")