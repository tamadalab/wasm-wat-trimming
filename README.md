# wasm-wat-trimming

## 概要

Wasm/WAT ファイルの類似度比較や解析において、ファイルサイズは処理時間に大きく影響します。本プロジェクトでは、ファイルを部分的にトリミング（削減）することで、「比較手法の処理時間短縮」と構造的特徴の維持（精度の保存）がされているかを検証します。

具体的には、オリジナルの WAT ファイルとトリミング後の WAT ファイルの N-gram 分布などを比較し、相関係数を計測することで、トリミングによって構造上の特徴が損なわれていないかを分析します。

## 環境構成

本プロジェクトでは、以下の2つの環境を組み合わせて実験を実行します：

### Docker環境（Makefile実行環境）

- **用途**: Makefile実行環境の提供
  - Makefile内でwasm2watを呼び出してWAT変換を実行
  - 実験の自動化フローを管理
- **理由**: wasm2watツールの環境統一による再現性確保

### Python環境（ローカル）

- **用途**: トリミング処理、N-gram抽出、類似度計算、統計分析
- **理由**: 柔軟な開発・デバッグと高速な実行

## 前提条件

以下がインストールされていることを確認してください：

- **Docker** と **Docker Compose**: wasm2wat とMakefile実行用
- **Python 3.8以上**: ローカル環境での分析スクリプト実行用
- **pip**: Python パッケージマネージャ

## プロジェクト構造

本実験では16個の独立したプロジェクトルートが存在します：

```
wasm-wat-trimming/
├── trimming-random/
│   ├── 500/          # Random trimming, 500行
│   ├── 1000/         # Random trimming, 1000行
│   ├── 3000/         # Random trimming, 3000行
│   └── 5000/         # Random trimming, 5000行
├── trimming-head/
│   ├── 500/          # Head trimming, 500行
│   ├── 1000/
│   ├── 3000/
│   └── 5000/
├── trimming-middle/
│   ├── 500/          # Middle trimming, 500行
│   ├── 1000/
│   ├── 3000/
│   └── 5000/
└── trimming-tail/
    ├── 500/          # Tail trimming, 500行
    ├── 1000/
    ├── 3000/
    └── 5000/
```

各プロジェクトルート配下には以下のディレクトリが含まれます：

```
{project_root}/
├── Makefile              # 実験自動化
├── docker-compose.yml    # wasm2wat環境
├── requirements.txt      # Python依存関係
├── scripts/              # 分析スクリプト
├── data/                 # 入力WASMファイル
├── output/               # 実験結果
│   ├── not_trimmed/      # トリミング前WAT
│   └── trimmed/          # トリミング後WAT
└── results/              # 測定結果CSV
```

## セットアップ手順

### 1. Pythonローカル環境の構築

**注意**: この手順は各プロジェクトルートで実行する必要があります。

例として `trimming-random/500/` の環境を構築します：

```bash
# プロジェクトルートに移動
cd trimming-random/500/

# Python依存パッケージのインストール
pip install -r requirements.txt
```

他のプロジェクトルートでも同様に実行してください：

```bash
cd ../../trimming-head/1000/
pip install -r requirements.txt
# ... 以下同様
```

### 2. Docker環境の確認（必要に応じて）

Makefile内でwasm2watを実行する際、Docker環境が使用される場合があります。
必要に応じてDocker Composeの準備を行ってください：

```bash
# プロジェクトルートに移動（例）
cd trimming-random/500/

# Docker環境の確認・ビルド（必要な場合のみ）
docker compose build
```

**注**: Makefile内でのwasm2wat実行方法によっては、この手順は不要な場合があります。

## データの取得方法 (Data Acquisition)

本プロジェクトでは、同一のアルゴリズム（Bubble Sort, Collatz, FizzBuzz, Hello World, Word Count 等）を複数の言語で実装し、WebAssembly バイナリを生成します。

### 使用コンパイラ (Compilers)

本実験では再現性を確保するため、Docker コンテナ上で以下のコンパイラを使用しています。

| 言語 (Language) | コンパイラ/ツール (Compiler) | バージョン (Version)          | 備考                                      |
| :-------------- | :--------------------------- | :---------------------------- | :---------------------------------------- |
| **C**           | Emscripten (`emcc`)          | `latest` (Docker Image)       | 最適化オプション: `-O3`                   |
| **JavaScript**  | Javy                         | `v3.0.1`                      | QuickJS エンジン内蔵                      |
| **TypeScript**  | AssemblyScript (`asc`)       | `latest` (npm)                | 最適化オプション: `-O3`                   |
| **Go**          | TinyGo                       | `latest` (Docker Image)       | オプション: `-no-debug`, target: `wasm`   |
| **Rust**        | rustc                        | `latest` (Docker Image)       | target: `wasm32-unknown-unknown`          |
| **WABT**        | wasm2wat                     | `latest` (Debian stable-slim) | Makefile経由で `.wasm` から `.wat` へ変換 |

※ WASMバイナリファイル（`.wasm`）は `.gitignore` によりリポジトリ管理外としているため、各環境でビルドが必要です。

### WASMファイルからWATへの変換

WASMバイナリは事前に用意されている前提です。Makefileを使ってWATファイルに変換します：

```bash
# プロジェクトルートに移動
cd trimming-random/500/

# WATファイル生成（Makefile内でwasm2watを実行）
make wat
```

**実行結果**: `output/not_trimmed/{algo}/{lang}/` 配下にWATファイルが生成されます。

## 実験の実行手順

以下の手順は、**各プロジェクトルート**で実行します。

### ステップ1: 初期セットアップ

```bash
# プロジェクトルートに移動（例: trimming-random/500/）
cd trimming-random/500/

# WATファイル生成（Makefile内でwasm2watを実行）
make wat

# n-gram抽出（Python環境で実行）
make grams
```

**実行結果**: `output/not_trimmed/{algo}/{lang}/` 配下にWATファイルとn-gramファイルが生成されます。

### ステップ2: ベースライン時間測定（初回のみ）

トリミング前の類似度計算にかかる時間を測定します：

```bash
# プロジェクトルート内で実行
make timing-before
```

**実行結果**: `output/timing_before.csv` が生成されます。

### ステップ3: トリミング実験

#### Random Trimmingの場合

```bash
# プロジェクトルート内で実行（例: trimming-random/500/）
cd trimming-random/500/

# トリミング実行（10試行）
make random-trim

# トリミング後のn-gram抽出
make grams-trimmed
```

#### Deterministic Trimmingの場合

```bash
# プロジェクトルート内で実行（例: trimming-head/1000/）
cd trimming-head/1000/

# トリミング実行
make head-trim

# トリミング後のn-gram抽出
make grams-trimmed-det
```

**実行結果**: `output/trimmed/` 配下にトリミング後のWATファイルとn-gramが生成されます。

### ステップ4: 評価実験

```bash
# プロジェクトルート内で実行

# Random trimming用
make experiment

# または Deterministic trimming用
make experiment-deterministic
```

**実行結果**: 以下のファイルが `results/` ディレクトリに生成されます：

- `compression_stats.csv` (RQ1: 圧縮効果)
- `speed_stats.csv` (RQ2: 高速化効果)
- `correlation_stats.csv` (RQ3: 類似度傾向の保存性)

## 全プロジェクトルートでの一括実行

すべての条件で実験を実行する場合の例：

```bash
# Random trimming (4条件)
for length in 500 1000 3000 5000; do
  cd trimming-random/$length/
  make timing-before
  make random-trim
  make grams-trimmed
  make experiment
  cd ../../
done

# Deterministic trimming (12条件)
for method in head middle tail; do
  for length in 500 1000 3000 5000; do
    cd trimming-$method/$length/
    make timing-before
    make ${method}-trim
    make grams-trimmed-det
    make experiment-deterministic
    cd ../../
  done
done
```

## トラブルシューティング

### Python環境のエラー

```bash
# 依存パッケージの再インストール
pip install -r requirements.txt --upgrade
```

### Makefileでのwasm2wat実行エラー

```bash
# wasm2watが見つからない場合
# Makefile内の設定を確認してください

# Docker経由で実行している場合
docker compose build --no-cache
```

### WATファイルが生成されない

```bash
# WASMファイルが存在するか確認
ls data/*/src/*.wasm

# Makefileのwatターゲットを再実行
make wat
```

## 実験結果の確認

各プロジェクトルートの `results/` ディレクトリに以下のCSVファイルが生成されます：

- **compression_stats.csv**: 行数・バイト削減率
- **speed_stats.csv**: スピードアップ率
- **correlation_stats.csv**: トリミング前後の相関係数

これらを統合して論文用の表を作成します。
