#!/usr/bin/env python3
import argparse
from collections import Counter
from pathlib import Path
import re
import sys

# 単語だけの命令（ドット無し）で採用したい代表例
SINGLE_WORD_OPS = {
    "block", "loop", "if", "else", "end",
    "call", "drop", "return", "nop", "unreachable",
    "br", "br_if", "br_table", "select"
}

# ドットを含む命令（i32.add, local.get, global.set, memory.size など）はパターンで拾う
DOT_INSTR_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+$")

# 先頭トークンとして無視したい宣言系（命令ではないもの）
DECL_TOKENS = {
    "module", "func", "type", "import", "export",
    "param", "result", "local", "global", "memory", "table", "elem", "data"
}

TOKEN_SPLIT_RE = re.compile(r"[()\s]+")

def is_instruction_token(tok: str) -> bool:
    """命令トークンかどうかを判定（数字・即値・宣言は除外）"""
    if not tok:
        return False
    # 数字・符号付き数値・16進の即値などを除外
    if re.fullmatch(r"[-+]?\d+", tok) or re.fullmatch(r"0x[0-9a-fA-F]+", tok):
        return False
    # 宣言トークン（param, result など）除外
    if tok in DECL_TOKENS:
        return False
    # ドットを含む命令 or 代表的な単語命令のみ採用
    if DOT_INSTR_RE.match(tok):
        return True
    if tok in SINGLE_WORD_OPS:
        return True
    return False

def tokenize_instructions_only(wat_text: str):
    """
    WAT 全文から命令だけを順序通りに抽出。
    - () や改行で分割
    - 先頭トークンが宣言系の行であっても、命令として使えるトークンのみを残す
    """
    raw_tokens = TOKEN_SPLIT_RE.split(wat_text)
    return [t for t in raw_tokens if is_instruction_token(t)]

def generate_ngrams(tokens, n):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def main():
    ap = argparse.ArgumentParser(
        description="Extract 1-6 gram instruction sequences from a .wat (numbers excluded)."
    )
    ap.add_argument("wat_file", help=".wat file path (e.g., bubsort/pkg/bubsort_bg.wat)")
    ap.add_argument("--min", type=int, default=1, help="minimum n (default: 1)")
    ap.add_argument("--max", type=int, default=6, help="maximum n (default: 6)")
    args = ap.parse_args()

    wat_path = Path(args.wat_file)
    if not wat_path.is_file():
        print(f"[ERROR] File not found: {wat_path}", file=sys.stderr)
        sys.exit(1)

    text = wat_path.read_text(encoding="utf-8", errors="ignore")
    tokens = tokenize_instructions_only(text)

    # 出力先は .wat と同じ階層に grams/ を作る
    outdir = wat_path.parent / "grams"
    outdir.mkdir(parents=True, exist_ok=True)

    base = wat_path.stem  # 例: 'bubsort_bg'
    for n in range(args.min, args.max + 1):
        ngrams = generate_ngrams(tokens, n)
        counter = Counter(ngrams)
        out_file = outdir / f"{base}_{n}gram.txt"
        with out_file.open("w", encoding="utf-8") as f:
            for ngram, count in counter.most_common():
                f.write(f"{ngram}\t{count}\n")
        print(f"[INFO] Saved {n}-grams -> {out_file}")

if __name__ == "__main__":
    main()
