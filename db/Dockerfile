# ベースイメージを指定
FROM postgres:latest


# 初期化スクリプトをコピー（必要に応じて）
COPY init.sql /docker-entrypoint-initdb.d/

# ポートを公開
EXPOSE 5432

# PostgreSQLを実行
CMD ["postgres"]