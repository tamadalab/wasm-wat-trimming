SHELL := /bin/bash

# ============================================================================
# 基本設定
# ============================================================================
DATA_DIR := data
OUT_DIR  := output/not_trimmed
WASM2WAT ?= wasm2wat
PYTHON   ?= python3

# --- n-gram 設定 ---
NGRAM_PY ?= ./scripts/extract_ngrams.py
NGRAM_PY := $(strip $(NGRAM_PY))
GRAM_MIN := 1
GRAM_MAX := 6

# --- Random Trim 設定 ---
TRIM_PY      ?= ./scripts/random_trim_tool.py
TRIM_PY      := $(strip $(TRIM_PY))
TRIM_LINES   ?= 500
TRIM_TRIALS  ?= 10
TRIM_SEED    ?=
TRIM_ALGOS   ?= bubsort,collatz,fizzbuzz,helloworld,wordcount
TRIM_LANGS   ?= c,go,js,ts,rust
TRIM_OUTBASE ?= output/trimmed

# --- Deterministic Trim 設定 ---
DET_TRIM_PY   ?= ./scripts/deterministic_trim.py
DET_TRIM_PY   := $(strip $(DET_TRIM_PY))
DET_TRIM_LINES ?= 500
DET_TRIM_ALGOS ?= bubsort,collatz,fizzbuzz,helloworld,wordcount
DET_TRIM_LANGS ?= c,go,js,ts,rust
DET_INPUT_BASE ?= output/not_trimmed

# --- 実験用スクリプト (Random) ---
MEASURE_COMPRESSION := scripts/measure_compression.py
CALC_SPEEDUP        := scripts/calc_speedup.py
COMPUTE_AVG_MATRIX  := scripts/compute_average_matrix.py
CORR_COMPARE        := scripts/corr_compare_selected.py
GEN_HEATMAP         := scripts/generate_heatmap_from_csv.py
GEN_SUMMARY         := scripts/generate_summary.py

# --- 実験用スクリプト (Deterministic) ---
MEASURE_COMPRESSION_DET := scripts/measure_compression_deterministic.py
CALC_SPEEDUP_DET        := scripts/calc_speedup_deterministic.py
CORR_COMPARE_DET        := scripts/corr_compare_deterministic.py

# --- 類似度計算スクリプト ---
GEN_COSINE     := scripts/generate_selected_cosine_heatmap.py
GEN_JACCARD    := scripts/generate_selected_jaccard_heatmap.py
GEN_OVERLAP    := scripts/generate_selected_overlap_heatmap.py
GEN_MANHATTAN  := scripts/generate_selected_manhattan_heatmap.py
GEN_KL         := scripts/generate_selected_kl_heatmap.py
GEN_LCS        := scripts/generate_selected_lcs_heatmap_full_timed.py

# --- 結果ディレクトリ ---
RESULTS_DIR := results

# ============================================================================
# デフォルトターゲット
# ============================================================================
.PHONY: all help
all: wat

help:
	@echo "============================================================================"
	@echo " WATトリミング実験 Makefile"
	@echo "============================================================================"
	@echo ""
	@echo "【基本タスク】"
	@echo "  make wat              - WASMからWATへ変換"
	@echo "  make wat-lines        - WAT行数を表示"
	@echo "  make grams            - n-gram抽出 (not_trimmed)"
	@echo ""
	@echo "【Random Trimming】"
	@echo "  make random-trim      - ランダムトリミング実行"
	@echo "  make grams-trimmed    - n-gram抽出 (trimmed)"
	@echo ""
	@echo "【Deterministic Trimming】"
	@echo "  make head-trim              - 先頭からトリミング"
	@echo "  make middle-trim            - 中央からトリミング"
	@echo "  make tail-trim              - 末尾からトリミング"
	@echo "  make deterministic-trim     - すべてのdeterministicトリミング実行"
	@echo "  make deterministic-trim-all - 全長さ(500/1000/3000/5000)で実行"
	@echo ""
	@echo "【実験タスク - Random】"
	@echo "  make experiment       - 全実験を実行 (RQ1+RQ2+RQ3)"
	@echo "  make rq1              - RQ1: 圧縮効果の測定"
	@echo "  make rq2              - RQ2: 高速化の測定"
	@echo "  make rq3              - RQ3: 保存性の測定"
	@echo "  make summary          - 統合表の生成"
	@echo ""
	@echo "【実験タスク - Deterministic】"
	@echo "  make experiment-deterministic  - 全実験を実行 (RQ1+RQ2+RQ3)"
	@echo "  make rq1-deterministic         - RQ1: 圧縮効果の測定"
	@echo "  make rq2-deterministic         - RQ2: 高速化の測定"
	@echo "  make rq3-deterministic         - RQ3: 保存性の測定"
	@echo "  make trimmed-matrices          - トリミング後の類似度行列生成"
	@echo "  make grams-trimmed-det         - n-gram抽出 (deterministic trimmed)"
	@echo ""
	@echo "【検証タスク】"
	@echo "  make check-trimmed-lines  - Trimmed行数確認"
	@echo "  make check-trimmed-diffs  - Trimmed差分確認"
	@echo "  make check-trimmed-sizes  - Trimmedサイズ比較"
	@echo ""
	@echo "【クリーンアップ】"
	@echo "  make clean                - output/not_trimmed 削除"
	@echo "  make clean-grams          - gramsディレクトリ削除"
	@echo "  make clean-trimmed        - Random trimmed削除"
	@echo "  make clean-deterministic  - Deterministic trimmed削除"
	@echo "  make clean-results        - results削除"
	@echo "  make clean-all            - すべて削除"
	@echo ""

# ============================================================================
# WAT変換
# ============================================================================
.PHONY: wat wat-lines
wat:
	@command -v "$(WASM2WAT)" >/dev/null 2>&1 || { \
		echo "[ERROR] wasm2wat が見つかりません (WABT をインストールしてください)"; \
		exit 1; \
	}
	@find "$(DATA_DIR)" -type f -name '*.wasm' | sort | while read -r wasm; do \
		rel="$${wasm#$(DATA_DIR)/}"; \
		wat="$(OUT_DIR)/$${rel%.wasm}.wat"; \
		mkdir -p "$$(dirname "$$wat")"; \
		"$(WASM2WAT)" "$$wasm" -o "$$wat"; \
		echo "[WAT] $$wasm -> $$wat"; \
	done

wat-lines:
	@find "$(OUT_DIR)" -type f -name '*.wat' | sort | while read -r f; do \
		printf "%8d  %s\n" "$$(wc -l < "$$f")" "$$f"; \
	done; \
	echo "--------------------------------"; \
	echo -n "TOTAL: "; \
	find "$(OUT_DIR)" -type f -name '*.wat' -print0 | xargs -0 wc -l | tail -n 1

# ============================================================================
# ベースライン時間測定
# ============================================================================
.PHONY: timing-before
timing-before: grams
	@echo "============================================================================"
	@echo " ベースライン時間測定（timing_before.csv生成）"
	@echo "============================================================================"
	@test -f "scripts/generate_timing_before.py" || { \
		echo "[ERROR] scripts/generate_timing_before.py が見つかりません"; \
		exit 1; \
	}
	@$(PYTHON) scripts/generate_timing_before.py
	@echo ""
	@echo "✓ timing_before.csv が生成されました"

# RQ2の前に timing-before を実行
rq2: timing-before $(RESULTS_DIR)/speed_stats.csv

rq2-deterministic: timing-before $(RESULTS_DIR)/speed_stats_deterministic.csv

# ============================================================================
# n-gram抽出
# ============================================================================
.PHONY: grams grams-trimmed grams-trimmed-det clean-grams
grams:
	@test -f "$(NGRAM_PY)" || { \
		echo "[ERROR] n-gram スクリプトが見つかりません: $(NGRAM_PY)"; \
		exit 1; \
	}
	@find "$(OUT_DIR)" -type f -name '*.wat' | sort | while read -r wat; do \
		base="$$(basename "$$wat" .wat)"; \
		grams_dir="$$(dirname "$$wat")/grams"; \
		need=0; \
		for n in $$(seq $(GRAM_MIN) $(GRAM_MAX)); do \
			out="$$grams_dir/$${base}_$${n}gram.txt"; \
			if [ ! -f "$$out" ] || [ "$$wat" -nt "$$out" ]; then \
				need=1; \
			fi; \
		done; \
		if [ $$need -eq 1 ]; then \
			"$(PYTHON)" "$(NGRAM_PY)" "$$wat" --min $(GRAM_MIN) --max $(GRAM_MAX); \
			echo "[GRAMS] $$wat"; \
		else \
			echo "[SKIP] $$wat (up-to-date)"; \
		fi; \
	done

grams-trimmed:
	@test -f "$(NGRAM_PY)" || { \
		echo "[ERROR] n-gram スクリプトが見つかりません: $(NGRAM_PY)"; \
		exit 1; \
	}
	@test -d "$(TRIM_OUTBASE)" || { \
		echo "[ERROR] '$(TRIM_OUTBASE)' が見つかりません。先に make random-trim"; \
		exit 1; \
	}
	@find "$(TRIM_OUTBASE)" -type f -name '*.wat' | sort | while read -r wat; do \
		"$(PYTHON)" "$(NGRAM_PY)" "$$wat" --min $(GRAM_MIN) --max $(GRAM_MAX); \
		echo "[GRAMS] $$wat"; \
	done

# Deterministic trimmed 用の n-gram 抽出（既存ファイルチェック付き）
grams-trimmed-det:
	@test -f "$(NGRAM_PY)" || { \
		echo "[ERROR] n-gram スクリプトが見つかりません: $(NGRAM_PY)"; \
		exit 1; \
	}
	@test -d "output/trimmed" || { \
		echo "[ERROR] 'output/trimmed' が見つかりません。先に deterministic-trim を実行"; \
		exit 1; \
	}
	@find "output/trimmed" -type f -name '*.wat' | sort | while read -r wat; do \
		base="$$(basename "$$wat" .wat)"; \
		grams_dir="$$(dirname "$$wat")/grams"; \
		need=0; \
		for n in $$(seq $(GRAM_MIN) $(GRAM_MAX)); do \
			out="$$grams_dir/$${base}_$${n}gram.txt"; \
			if [ ! -f "$$out" ] || [ "$$wat" -nt "$$out" ]; then \
				need=1; \
			fi; \
		done; \
		if [ $$need -eq 1 ]; then \
			"$(PYTHON)" "$(NGRAM_PY)" "$$wat" --min $(GRAM_MIN) --max $(GRAM_MAX); \
			echo "[GRAMS] $$wat"; \
		else \
			echo "[SKIP] $$wat (up-to-date)"; \
		fi; \
	done

clean-grams:
	@find "$(OUT_DIR)" -type d -name 'grams' -prune -exec rm -rf {} + || true
	@echo "[CLEAN] removed grams dirs under '$(OUT_DIR)'"

# ============================================================================
# Random Trimming
# ============================================================================
.PHONY: random-trim clean-trimmed
random-trim: wat
	@test -f "$(TRIM_PY)" || { \
		echo "[ERROR] random trim スクリプトが見つかりません: $(TRIM_PY)"; \
		exit 1; \
	}
	@args="--lines $(TRIM_LINES) --trials $(TRIM_TRIALS) --algos $(TRIM_ALGOS) --langs $(TRIM_LANGS) --out-base $(TRIM_OUTBASE)"; \
	if [ -n "$(TRIM_SEED)" ]; then args="$$args --seed $(TRIM_SEED)"; fi; \
	"$(PYTHON)" "$(TRIM_PY)" $$args
	@echo "[OK] wrote: $(TRIM_OUTBASE)/{1..$(TRIM_TRIALS)}/<algo>/<lang>/..."

clean-trimmed:
	@rm -rf "$(TRIM_OUTBASE)"
	@echo "[CLEAN] removed '$(TRIM_OUTBASE)'"

# ============================================================================
# Deterministic Trimming
# ============================================================================
.PHONY: head-trim middle-trim tail-trim deterministic-trim clean-deterministic

# 先頭からトリミング
head-trim: wat
	@test -f "$(DET_TRIM_PY)" || { \
		echo "[ERROR] deterministic trim スクリプトが見つかりません: $(DET_TRIM_PY)"; \
		exit 1; \
	}
	@echo "[INFO] Deterministicトリミング: head ($(DET_TRIM_LINES)行)"
	@$(PYTHON) "$(DET_TRIM_PY)" --method head --lines $(DET_TRIM_LINES) \
		--algos $(DET_TRIM_ALGOS) --langs $(DET_TRIM_LANGS) \
		--input-base $(DET_INPUT_BASE) --output-base output/trimmed

# 中央からトリミング
middle-trim: wat
	@test -f "$(DET_TRIM_PY)" || { \
		echo "[ERROR] deterministic trim スクリプトが見つかりません: $(DET_TRIM_PY)"; \
		exit 1; \
	}
	@echo "[INFO] Deterministicトリミング: middle ($(DET_TRIM_LINES)行)"
	@$(PYTHON) "$(DET_TRIM_PY)" --method middle --lines $(DET_TRIM_LINES) \
		--algos $(DET_TRIM_ALGOS) --langs $(DET_TRIM_LANGS) \
		--input-base $(DET_INPUT_BASE) --output-base output/trimmed

# 末尾からトリミング
tail-trim: wat
	@test -f "$(DET_TRIM_PY)" || { \
		echo "[ERROR] deterministic trim スクリプトが見つかりません: $(DET_TRIM_PY)"; \
		exit 1; \
	}
	@echo "[INFO] Deterministicトリミング: tail ($(DET_TRIM_LINES)行)"
	@$(PYTHON) "$(DET_TRIM_PY)" --method tail --lines $(DET_TRIM_LINES) \
		--algos $(DET_TRIM_ALGOS) --langs $(DET_TRIM_LANGS) \
		--input-base $(DET_INPUT_BASE) --output-base output/trimmed

# すべてのdeterministicトリミングを実行（head, middle, tail）
deterministic-trim: head-trim middle-trim tail-trim
	@echo ""
	@echo "============================================================================"
	@echo " ✓ すべてのdeterministicトリミングが完了しました"
	@echo "============================================================================"

# 全長さでdeterministicトリミングを実行
.PHONY: deterministic-trim-all
deterministic-trim-all:
	@echo "============================================================================"
	@echo " すべての長さでdeterministicトリミングを実行"
	@echo "============================================================================"
	@$(MAKE) deterministic-trim DET_TRIM_LINES=500
	@$(MAKE) deterministic-trim DET_TRIM_LINES=1000
	@$(MAKE) deterministic-trim DET_TRIM_LINES=3000
	@$(MAKE) deterministic-trim DET_TRIM_LINES=5000
	@echo ""
	@echo "============================================================================"
	@echo " ✓ すべての長さ (500/1000/3000/5000) でトリミング完了"
	@echo "============================================================================"

# すべてのdeterministicトリミング結果を削除
clean-deterministic:
	@rm -rf "output/trimmed"
	@rm -rf "output/trimmed_matrices"
	@echo "[CLEAN] removed 'output/trimmed' and 'output/trimmed_matrices'"

# ============================================================================
# 実験タスク - RQ1: 圧縮効果 (Random)
# ============================================================================
.PHONY: rq1
rq1: $(RESULTS_DIR)/compression_stats.csv

$(RESULTS_DIR)/compression_stats.csv:
	@echo "============================================================================"
	@echo " RQ1: 圧縮効果の測定 (Random)"
	@echo "============================================================================"
	@test -f "$(MEASURE_COMPRESSION)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(MEASURE_COMPRESSION)"; \
		exit 1; \
	}
	@mkdir -p "$(RESULTS_DIR)"
	@$(PYTHON) "$(MEASURE_COMPRESSION)"

# ============================================================================
# 実験タスク - RQ2: 高速化 (Random)
# ============================================================================
.PHONY: rq2
rq2: $(RESULTS_DIR)/speed_stats.csv

$(RESULTS_DIR)/speed_stats.csv:
	@echo "============================================================================"
	@echo " RQ2: 高速化の測定 (Random)"
	@echo "============================================================================"
	@test -f "$(CALC_SPEEDUP)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(CALC_SPEEDUP)"; \
		exit 1; \
	}
	@mkdir -p "$(RESULTS_DIR)"
	@$(PYTHON) "$(CALC_SPEEDUP)"

# ============================================================================
# 実験タスク - RQ3: 保存性 (Random)
# ============================================================================
.PHONY: rq3 rq3-avg-matrix rq3-correlation rq3-heatmaps rq3-cleanup
rq3: rq3-avg-matrix rq3-correlation rq3-heatmaps rq3-cleanup

rq3-avg-matrix:
	@echo "============================================================================"
	@echo " RQ3-1: Random試行の平均行列を計算"
	@echo "============================================================================"
	@test -f "$(COMPUTE_AVG_MATRIX)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(COMPUTE_AVG_MATRIX)"; \
		exit 1; \
	}
	@$(PYTHON) "$(COMPUTE_AVG_MATRIX)"

rq3-correlation: $(RESULTS_DIR)/correlation_stats.csv

$(RESULTS_DIR)/correlation_stats.csv:
	@echo "============================================================================"
	@echo " RQ3-2: 相関係数の計算 (Random)"
	@echo "============================================================================"
	@test -f "$(CORR_COMPARE)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(CORR_COMPARE)"; \
		exit 1; \
	}
	@mkdir -p "$(RESULTS_DIR)"
	@$(PYTHON) "$(CORR_COMPARE)"

rq3-heatmaps:
	@echo "============================================================================"
	@echo " RQ3-3: ヒートマップの生成 (Random)"
	@echo "============================================================================"
	@test -f "$(GEN_HEATMAP)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(GEN_HEATMAP)"; \
		exit 1; \
	}
	@$(PYTHON) "$(GEN_HEATMAP)"

rq3-cleanup:
	@echo "============================================================================"
	@echo " RQ3-4: 一時ファイルのクリーンアップ"
	@echo "============================================================================"
	@if [ -d "output/similarity_matrices" ]; then \
		rm -rf "output/similarity_matrices"; \
		echo "[CLEAN] output/similarity_matrices を削除しました"; \
	fi

# ============================================================================
# 統合表の生成 (Random)
# ============================================================================
.PHONY: summary
summary: $(RESULTS_DIR)/summary_table.csv

$(RESULTS_DIR)/summary_table.csv: rq1 rq2 rq3-correlation
	@echo "============================================================================"
	@echo " 統合表の生成 (Random)"
	@echo "============================================================================"
	@test -f "$(GEN_SUMMARY)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(GEN_SUMMARY)"; \
		exit 1; \
	}
	@$(PYTHON) "$(GEN_SUMMARY)"

# ============================================================================
# 全実験の実行 (Random)
# ============================================================================
.PHONY: experiment
experiment: rq1 rq2 rq3 summary
	@echo ""
	@echo "============================================================================"
	@echo " ✓ すべての実験が完了しました (Random)"
	@echo "============================================================================"
	@echo "成果物:"
	@echo "  - $(RESULTS_DIR)/compression_stats.csv    (RQ1)"
	@echo "  - $(RESULTS_DIR)/speed_stats.csv          (RQ2)"
	@echo "  - $(RESULTS_DIR)/correlation_stats.csv    (RQ3)"
	@echo "  - $(RESULTS_DIR)/summary_table.csv        (統合)"
	@echo ""

# ============================================================================
# 実験タスク - Deterministic
# ============================================================================
.PHONY: rq1-deterministic rq2-deterministic rq3-deterministic
.PHONY: trimmed-matrices experiment-deterministic

# RQ1: 圧縮効果 (Deterministic)
rq1-deterministic: $(RESULTS_DIR)/compression_stats_deterministic.csv

$(RESULTS_DIR)/compression_stats_deterministic.csv:
	@echo "============================================================================"
	@echo " RQ1: 圧縮効果の測定 (Deterministic)"
	@echo "============================================================================"
	@test -f "$(MEASURE_COMPRESSION_DET)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(MEASURE_COMPRESSION_DET)"; \
		exit 1; \
	}
	@test -d "output/trimmed" || { \
		echo "[ERROR] output/trimmed が見つかりません"; \
		echo "先に make head-trim / middle-trim / tail-trim を実行してください"; \
		exit 1; \
	}
	@mkdir -p "$(RESULTS_DIR)"
	@$(PYTHON) "$(MEASURE_COMPRESSION_DET)"

# RQ2: 高速化 (Deterministic)
rq2-deterministic: $(RESULTS_DIR)/speed_stats_deterministic.csv

$(RESULTS_DIR)/speed_stats_deterministic.csv: grams-trimmed-det
	@echo "============================================================================"
	@echo " RQ2: 高速化の測定 (Deterministic)"
	@echo "============================================================================"
	@test -f "$(CALC_SPEEDUP_DET)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(CALC_SPEEDUP_DET)"; \
		exit 1; \
	}
	@test -f "output/timing_before.csv" || { \
		echo "[ERROR] output/timing_before.csv が見つかりません"; \
		echo "ベースライン時間のCSVを配置してください"; \
		exit 1; \
	}
	@mkdir -p "$(RESULTS_DIR)"
	@$(PYTHON) "$(CALC_SPEEDUP_DET)"

# トリミング後の類似度行列を生成
trimmed-matrices: grams-trimmed-det
	@echo "============================================================================"
	@echo " トリミング後の類似度行列を生成"
	@echo "============================================================================"
	@test -d "output/trimmed" || { \
		echo "[ERROR] output/trimmed が見つかりません"; \
		exit 1; \
	}
	@mkdir -p "output/trimmed_matrices"
	@echo "[1/6] Cosine..."
	@$(PYTHON) "$(GEN_COSINE)" --base-dir output/trimmed --output-dir output/trimmed_matrices
	@echo "[2/6] Jaccard..."
	@$(PYTHON) "$(GEN_JACCARD)" --base-dir output/trimmed --output-dir output/trimmed_matrices
	@echo "[3/6] Overlap..."
	@$(PYTHON) "$(GEN_OVERLAP)" --base-dir output/trimmed --output-dir output/trimmed_matrices
	@echo "[4/6] Manhattan..."
	@$(PYTHON) "$(GEN_MANHATTAN)" --base-dir output/trimmed --output-dir output/trimmed_matrices
	@echo "[5/6] KL..."
	@$(PYTHON) "$(GEN_KL)" --base-dir output/trimmed --output-dir output/trimmed_matrices
	@echo "[6/6] LCS..."
	@$(PYTHON) "$(GEN_LCS)" --base-dir output/trimmed --output-dir output/trimmed_matrices --method min
	@echo ""
	@echo "✓ 類似度行列を生成: output/trimmed_matrices/"

# RQ3: 保存性 (Deterministic)
rq3-deterministic: $(RESULTS_DIR)/correlation_stats_deterministic.csv

$(RESULTS_DIR)/correlation_stats_deterministic.csv: trimmed-matrices
	@echo "============================================================================"
	@echo " RQ3: 相関係数の計算 (Deterministic)"
	@echo "============================================================================"
	@test -f "$(CORR_COMPARE_DET)" || { \
		echo "[ERROR] スクリプトが見つかりません: $(CORR_COMPARE_DET)"; \
		exit 1; \
	}
	@test -d "output/not_trimmed_matrices" || { \
		echo "[ERROR] output/not_trimmed_matrices が見つかりません"; \
		echo "Before の類似度行列を生成してください"; \
		exit 1; \
	}
	@mkdir -p "$(RESULTS_DIR)"
	@$(PYTHON) "$(CORR_COMPARE_DET)"

# 全実験の実行 (Deterministic)
experiment-deterministic: rq1-deterministic rq2-deterministic rq3-deterministic
	@echo ""
	@echo "============================================================================"
	@echo " ✓ すべての実験が完了しました (Deterministic)"
	@echo "============================================================================"
	@echo "成果物:"
	@echo "  - $(RESULTS_DIR)/compression_stats_deterministic.csv    (RQ1)"
	@echo "  - $(RESULTS_DIR)/speed_stats_deterministic.csv          (RQ2)"
	@echo "  - $(RESULTS_DIR)/correlation_stats_deterministic.csv    (RQ3)"
	@echo "  - output/trimmed_matrices/                              (類似度行列)"
	@echo ""

# ============================================================================
# 検証タスク
# ============================================================================
.PHONY: check-trimmed-lines check-trimmed-diffs check-trimmed-sizes time-compare

check-trimmed-lines:
	@echo "=== Checking line counts for .wat files in '$(TRIM_OUTBASE)' ==="
	@algos="$(TRIM_ALGOS)"; algos=$${algos//,/ }; \
	langs="$(TRIM_LANGS)"; langs=$${langs//,/ }; \
	count=0; \
	for i in $$(seq 1 $(TRIM_TRIALS)); do \
	  for algo in $$algos; do \
	    for lang in $$langs; do \
	      wat_file="$(TRIM_OUTBASE)/$$i/$$algo/$$lang/$$algo.wat"; \
	      if [ -f "$$wat_file" ]; then \
	        printf "%-50s " "$$wat_file"; \
	        wc -l < "$$wat_file"; \
	        count=$$((count + 1)); \
	      fi; \
	    done; \
	  done; \
	done; \
	echo "Total files checked: $$count"

check-trimmed-diffs:
	@echo "=== Verifying .wat differences across $(TRIM_TRIALS) trials in '$(TRIM_OUTBASE)' ==="
	@algos="$(TRIM_ALGOS)"; algos=$${algos//,/ }; \
	langs="$(TRIM_LANGS)"; langs=$${langs//,/ }; \
	for algo in $$algos; do \
	  for lang in $$langs; do \
	    target_file="$${algo}.wat"; \
	    echo "--- Checking $$target_file ($$lang) ---"; \
	    files=(); \
	    for i in $$(seq 1 $(TRIM_TRIALS)); do \
	      path="$(TRIM_OUTBASE)/$$i/$$algo/$$lang/$$target_file"; \
	      if [ -f "$$path" ]; then \
	        files+=("$$i:$$path"); \
	      fi; \
	    done; \
	    if [ $${#files[@]} -lt 2 ]; then \
	      echo "  [SKIP] 比較対象不足 (found $${#files[@]})"; \
	      continue; \
	    fi; \
	    for file_a in "$${files[@]}"; do \
	      num_a="$${file_a%%:*}"; \
	      path_a="$${file_a#*:}"; \
	      for file_b in "$${files[@]}"; do \
	        num_b="$${file_b%%:*}"; \
	        path_b="$${file_b#*:}"; \
	        if [ "$$num_a" -ge "$$num_b" ]; then continue; fi; \
	        if ! diff -q "$$path_a" "$$path_b" >/dev/null 2>&1; then \
	          echo "  [DIFF] Trial $$num_a vs $$num_b"; \
	        else \
	          echo "  [SAME] Trial $$num_a vs $$num_b"; \
	        fi; \
	      done; \
	    done; \
	    echo ""; \
	  done; \
	done

check-trimmed-sizes:
	@echo "========================================================================================"
	@echo " Byte Size Comparison: Not Trimmed vs Trimmed (Avg of $(TRIM_TRIALS) trials)"
	@echo "========================================================================================"
	@printf "%-12s %-6s | %8s | %8s %8s %8s | %s\n" "ALGO" "LANG" "BASE(B)" "AVG(B)" "MIN(B)" "STDDEV" "RATIO(%)"
	@echo "---------------------+----------+-----------------------------+---------"
	@algos="$(TRIM_ALGOS)"; algos=$${algos//,/ }; \
	langs="$(TRIM_LANGS)"; langs=$${langs//,/ }; \
	for algo in $$algos; do \
	  for lang in $$langs; do \
	    base_file="output/not_trimmed/$$algo/$$lang/$$algo.wat"; \
	    if [ ! -f "$$base_file" ]; then continue; fi; \
	    base_size=$$(wc -c < "$$base_file" | tr -d ' '); \
	    sizes=""; \
	    count=0; \
	    for i in $$(seq 1 $(TRIM_TRIALS)); do \
	      trim_file="output/trimmed/$$i/$$algo/$$lang/$$algo.wat"; \
	      if [ -f "$$trim_file" ]; then \
	        s=$$(wc -c < "$$trim_file" | tr -d ' '); \
	        sizes="$$sizes $$s"; \
	        count=$$((count + 1)); \
	      fi; \
	    done; \
	    if [ $$count -gt 0 ]; then \
	      echo "$$sizes" | xargs -n1 | awk -v base="$$base_size" -v algo="$$algo" -v lang="$$lang" ' \
	        BEGIN {sum=0; sum_sq=0; min=999999999; max=0} \
	        { \
	          val=$$1; \
	          sum+=val; \
	          sum_sq+=val*val; \
	          if(val<min) min=val; \
	          if(val>max) max=val; \
	        } \
	        END { \
	          n=NR; \
	          if (n > 0) { \
	            mean=sum/n; \
	            variance=(sum_sq/n)-(mean*mean); \
	            if(variance<0) variance=0; \
	            stddev=sqrt(variance); \
	            ratio=(mean/base)*100; \
	            printf "%-12s %-6s | %8d | %8.0f %8d %8.1f | %6.1f%%\n", \
	                   algo, lang, base, mean, min, stddev, ratio; \
	          } \
	        }' ; \
	    else \
	      printf "%-12s %-6s | %8s | (No trimmed files found)\n" $$algo $$lang "$$base_size"; \
	    fi; \
	  done; \
	  echo "---------------------+----------+-----------------------------+---------"; \
	done

time-compare:
	@echo "=== Measuring Processing Time for Trimmed Data ==="
	@python3 scripts/time_compare_all.py

# ============================================================================
# クリーンアップ
# ============================================================================
.PHONY: clean clean-all clean-results

clean:
	@rm -rf "$(OUT_DIR)"
	@echo "[CLEAN] removed '$(OUT_DIR)'"

clean-results:
	@rm -rf "$(RESULTS_DIR)"
	@echo "[CLEAN] removed '$(RESULTS_DIR)'"

clean-all: clean clean-grams clean-trimmed clean-deterministic clean-results
	@echo "[CLEAN] すべてのビルド成果物を削除しました"