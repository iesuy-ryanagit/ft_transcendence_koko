# システム概要

このシステムは複数のコンテナで構成されており、それぞれが特定の役割を担当しています。リバースプロキシとしてNginxを使用して、外部からのリクエストを適切なコンテナにルーティングします。HTTPS接続はNginxを通じて実現されています。

## コンテナ構成

| コンテナ名              | 役割                                      | ポート番号 |
|--------------------|-----------------------------------------|---------|
| `account`          | アカウント管理を担当                          | 8000    |
| `backendgame`      | ゲーム（試合）の進行を担当                     | 8001    |
| `backendtournament`| トーナメントの進行を担当                     | 8002    |
| `db`               | データベース（予定）                          | 5432    |
| `frontend`         | フロントエンド（ユーザーインターフェース）       | 3000    |
| `nginx`            | リバースプロキシを担当（HTTPS対応）           | 443     |

## アクセス方法

すべてのコンテナには直接アクセスせず、`nginx` を経由してHTTPS通信を行う。`nginx`はリバースプロキシとして機能し、特定のパスに基づいてリクエストを適切なコンテナにルーティングする。

### 各コンテナのURLパス

- **アカウント管理**（account コンテナ）  
  - URL: `/account/`
  - ポート: `8000`

- **ゲーム（試合）**（backendgame コンテナ）  
  - URL: `/game/`
  - ポート: `8001`

- **トーナメント**（backendtournament コンテナ）  
  - URL: `/tournament/`
  - ポート: `8002`

- **フロントエンド**（frontend コンテナ）  
  - URL: `/html/`
  - ポート: `3000`

### リバースプロキシ設定

Nginxは以下のように各コンテナにリクエストを転送する。

- `/account/` → `account` コンテナ（ポート8000）
- `/game/` → `backendgame` コンテナ（ポート8001）
- `/tournament/` → `backendtournament` コンテナ（ポート8002）
- `/html/` → `frontend` コンテナ（ポート3000）

これにより、外部からはNginx（ポート443）を通じてアクセスし、内部の各コンテナには適切にルーティングされます。
