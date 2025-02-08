# ベースとなるNode.jsのイメージを指定
FROM node:16-alpine

# 作業ディレクトリを作成して移動
WORKDIR /app

# 必要なパッケージをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install

# フロントエンドの静的ファイルをコピー
COPY . /app

# ポート3000を公開（Node.jsがデフォルトで使うポート）
EXPOSE 3000

# アプリケーションを起動
CMD ["npm", "start"]



