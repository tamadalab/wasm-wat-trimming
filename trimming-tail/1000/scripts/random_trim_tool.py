#!/usr/bin/env python3
# random_trim_wat_to_output_trimmed.py

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path
from typing import List, Tuple


ALGOS_DEFAULT = {"bubsort", "collatz", "fizzbuzz", "helloworld", "wordcount"}
LANGS_DEFAULT = {"ts", "js", "go", "c", "rust"}


def list_target_wat_files(in_base: Path, algos: set[str], langs: set[str]) -> List[Path]:
    """
    in_base = <ROOT>/output/not_trimmed
    期待する相対パス: <algo>/<lang>/.../*.wat
    """
    files: List[Path] = []
    for p in in_base.rglob("*.wat"):
        try:
            rel = p.relative_to(in_base)
        except ValueError:
            continue

        parts = rel.parts
        if len(parts) < 3:
            # <algo>/<lang>/<file>.wat になっていないものは除外
            continue

        algo, lang = parts[0], parts[1]
        if algo in algos and lang in langs:
            files.append(p)

    return sorted(files)


def trim_contiguous(lines: List[str], n: int, rng: random.Random) -> Tuple[List[str], int]:
    """
    連続 n 行をランダムに取得（行順維持）。
    戻り値: (切り出し行, start_index[0-based])
    """
    total = len(lines)
    if total <= n:
        return lines, 0
    start = rng.randint(0, total - n)
    return lines[start : start + n], start


def write_log_csv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "trial",
                "algo",
                "lang",
                "relpath_after_lang",
                "total_lines",
                "kept_lines",
                "start_index",
            ],
        )
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", type=int, default=500, help="keep N lines (default: 500)")
    ap.add_argument("--trials", type=int, default=10, help="number of random trials (default: 10)")
    ap.add_argument("--seed", type=int, default=None, help="seed for reproducibility (optional)")
    ap.add_argument(
        "--algos",
        type=str,
        default=",".join(sorted(ALGOS_DEFAULT)),
        help="target algos (comma-separated)",
    )
    ap.add_argument(
        "--langs",
        type=str,
        default=",".join(sorted(LANGS_DEFAULT)),
        help="target langs (comma-separated)",
    )
    ap.add_argument(
    "--out-base",
    type=str,
    default="trimmed",
    help="output base dir (default: trimmed)",
    )
    args = ap.parse_args()

    # ★ current_directory.txt は使わない：実行ディレクトリをルートとする
    root = Path.cwd().resolve()

    in_base = root / "output" / "not_trimmed"
    if not in_base.exists():
        raise FileNotFoundError(f"入力ディレクトリが見つかりません: {in_base}")

    algos = {s.strip() for s in args.algos.split(",") if s.strip()}
    langs = {s.strip() for s in args.langs.split(",") if s.strip()}

    wat_files = list_target_wat_files(in_base, algos, langs)
    if not wat_files:
        raise FileNotFoundError(
            f"対象の .wat が見つかりません: {in_base}（algos={sorted(algos)}, langs={sorted(langs)}）"
        )

    out_base = root / args.out_base
    out_base.mkdir(parents=True, exist_ok=True)

    base_rng = random.Random(args.seed)

    for trial in range(1, args.trials + 1):
        # seed指定時でも trialごとに異なり、かつ再現可能にする
        trial_seed = base_rng.randint(0, 2**31 - 1)
        rng = random.Random(trial_seed)

        log_rows: List[dict] = []

        for src in wat_files:
            rel = src.relative_to(in_base)  # <algo>/<lang>/.../*.wat
            algo, lang = rel.parts[0], rel.parts[1]
            after_lang = Path(*rel.parts[2:])  # <lang>より下（存在するなら）維持

            # ★ 出力：output/trimmed/{trial}/{algo}/{lang}/*.wat（＋サブディレクトリがあれば維持）
            dst = out_base / str(trial) / algo / lang / after_lang
            dst.parent.mkdir(parents=True, exist_ok=True)

            lines = src.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            trimmed, start = trim_contiguous(lines, args.lines, rng)
            dst.write_text("".join(trimmed), encoding="utf-8")

            log_rows.append(
                {
                    "trial": trial,
                    "algo": algo,
                    "lang": lang,
                    "relpath_after_lang": str(after_lang).replace("\\", "/"),
                    "total_lines": len(lines),
                    "kept_lines": len(trimmed),
                    "start_index": start,
                }
            )

        write_log_csv(out_base / str(trial) / "trim_log.csv", log_rows)

    print(f"OK root: {root}")
    print(f"IN : {in_base}  (files={len(wat_files)})")
    print(f"OUT: {out_base}/{{1..{args.trials}}}/<algo>/<lang>/...  (lines={args.lines})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
