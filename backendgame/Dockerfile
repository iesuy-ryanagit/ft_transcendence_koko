# Pythonの公式イメージをベースとして使用
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# システムの依存関係をインストール
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコピー
COPY requirements.txt requirements.txt

# Pythonパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# プロジェクトのソースコードをコピー
COPY . /app/

# アプリケーションを実行するポートを指定
EXPOSE 8001

# コピーしたmigrate.shを実行可能にする
RUN chmod +x /app/entry-point.sh

# マイグレーションを実行する（`docker-entrypoint.sh`などを用意しても良い）
ENTRYPOINT ["/app/entry-point.sh"]