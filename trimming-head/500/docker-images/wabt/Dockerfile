# Alpineの代わりに、より安定性の高い Debian (軽量版) を使用
FROM debian:stable-slim

# aptパッケージマネージャを使って wabt をインストール
# -y: 確認画面で自動的に Yes と答える
# rm -rf ...: インストール後に不要なキャッシュを削除して軽くする
RUN apt-get update && \
    apt-get install -y wabt && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENTRYPOINT []