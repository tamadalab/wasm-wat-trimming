# wasm-wat-trimming

## 概要

Wasm/WAT ファイルの類似度比較や解析において、ファイルサイズは処理時間に大きく影響します。本プロジェクトでは、ファイルを部分的にトリミング（削減）することで、「比較手法の処理時間短縮」と構造的特徴の維持（精度の保存)がされているかを検証します。

具体的には、オリジナルの WAT ファイルとトリミング後の WAT ファイルの N-gram 分布などを比較し、相関係数を計測することで、トリミングによって構造上の特徴が損なわれていないかを分析します。

## データの取得方法 (Data Acquisition)

本プロジェクトでは、同一のアルゴリズム（Bubble Sort, Collatz, FizzBuzz, Hello World, Word Count 等）を複数の言語で実装し、WebAssembly バイナリを生成します。

### ソースコードの配置:

`data/` ディレクトリ配下に、各アルゴリズム・各言語ごとのソースコード（`.c`, `.go`, `.ts`, `.rs`, `js`）を格納しています。

- 例: `data/bubsort/src/bubsort.c`

### 実験環境と使用コンパイラ (Environment & Compilers)

本実験では再現性を確保するため、Docker コンテナ上で以下のコンパイラバージョンを使用しています。

| 言語 (Language) | コンパイラ/ツール (Compiler) | バージョン (Version)    | 備考                                    |
| :-------------- | :--------------------------- | :---------------------- | :-------------------------------------- |
| **C**           | Emscripten (`emcc`)          | `latest` (Docker Image) | 最適化オプション: `-O3`                 |
| **JavaScript**  | Javy                         | `v3.0.1`                | QuickJS エンジン内蔵                    |
| **TypeScript**  | AssemblyScript (`asc`)       | `latest` (npm)          | 最適化オプション: `-O3`                 |
| **Go**          | TinyGo                       | `latest` (Docker Image) | オプション: `-no-debug`, target: `wasm` |

### コンパイル (Wasm 生成):

各言語に対応したコンパイラを使用し、ソースコードから `.wasm` ファイルを生成します。生成物は各言語ディレクトリ直下に配置します。

- **C**: Emscripten (`emcc`)

※ バイナリファイル（`.wasm`）は `.gitignore` によりリポジトリ管理外としているため、各環境でビルドが必要です。

以下のコマンドを`trimming-rondom`ディレクトリで実行してください

```bash
docker compose up --build
```
