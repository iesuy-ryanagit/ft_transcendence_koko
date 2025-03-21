FROM nginx:alpine

# OpenSSLのインストール
RUN apk update && apk add openssl

# SSL証明書の作成
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -out /etc/nginx/ssl/inception.crt -keyout /etc/nginx/ssl/inception.key -subj "/C=JP/ST=Tokyo/L=Shinjuku/O=42/OU=42/CN=ryanagit42.ja/UID=ryanagit"

# nginx.confをコンテナにコピー
COPY ./nginx.conf /etc/nginx/nginx.conf

# ポート80を公開
EXPOSE 4423

# コンテナのデフォルトのコマンドを設定（Nginxを起動）
CMD ["nginx", "-g", "daemon off;"]
