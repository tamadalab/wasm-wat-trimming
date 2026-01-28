# x86_64向けのDebianを使用するよう強制
FROM --platform=linux/amd64 debian:bookworm-slim

# 必要なツールをインストール
RUN apt-get update && apt-get install -y \
    curl \
    gzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# バージョン指定
ARG JAVY_VERSION=v3.0.1

# 修正箇所: ファイル名から「gnu」を削除し、バージョン番号を含む形式に変更
# 正しいファイル名: javy-x86_64-linux-v3.0.1.gz
RUN curl -L -o javy.gz https://github.com/bytecodealliance/javy/releases/download/${JAVY_VERSION}/javy-x86_64-linux-${JAVY_VERSION}.gz \
    && gunzip javy.gz \
    && mv javy /usr/local/bin/javy \
    && chmod +x /usr/local/bin/javy

WORKDIR /app
ENTRYPOINT []
