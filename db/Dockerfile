# ベースイメージを指定
FROM postgres:latest

# 初期化スクリプトをコピー（必要に応じて）
COPY init.sql /docker-entrypoint-initdb.d/

RUN chmod +777 /docker-entrypoint-initdb.d/init.sql

# PostgreSQLのデータディレクトリの権限設定（初期化後に適用される）
RUN chmod -R 777 /var/lib/postgresql/data

# ポートを公開
EXPOSE 5432


