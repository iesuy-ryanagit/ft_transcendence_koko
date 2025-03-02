FROM nginx:alpine

# OpenSSLをインストール
RUN apk update && apk add --no-cache openssl

# Nginxの設定ファイルをコピー
COPY ./default.conf /etc/nginx/conf.d/default.conf

# SSL証明書と秘密鍵を生成
RUN mkdir -p /etc/ssl && \
    openssl req -x509 -nodes -out /etc/ssl/inception.crt -keyout /etc/ssl/inception.key -subj "/C=JP/ST=Tokyo/L=Shinjuku/O=42/OU=42/CN=local/UID=ryanagit"

# ポート80と443を公開
EXPOSE 80
EXPOSE 443
