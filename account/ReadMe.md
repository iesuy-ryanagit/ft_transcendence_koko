Django API Documentation - User Authentication & 2FA

このドキュメントでは、Djangoを使用して構築したユーザー認証および2FA（Two-Factor Authentication）に関連するAPIを説明します。

ベースURL

BASE_URL = http://localhost:8000/api/

エンドポイント一覧

1. ユーザー登録 (Sign Up)

POST /signup/

新しいユーザーを作成します。

リクエストボディ:
{
  "username": "ユーザー名",
  "email": "メールアドレス",
  "password": "パスワード"
}

レスポンス:
- 成功時 (201 Created):
  {
    "status": "success"
  }
- 失敗時 (400 Bad Request):
  - 必要な情報が足りない場合、エラーメッセージが返されます。

---

2. ログイン (Login)

POST /login/

ユーザーがログインします。成功するとJWTトークンがクッキーに保存されます。

リクエストボディ:
{
  "username": "ユーザー名",
  "password": "パスワード"
}

レスポンス:
- 成功時 (200 OK):
  {
    "status": "success",
    "jwt": "JWTトークン"
  }
- 失敗時 (400 Bad Request):
  - ユーザー名またはパスワードが間違っている場合、エラーメッセージが返されます。

---

3. ユーザー情報取得 (Profile)

GET /profile/

ログイン後、JWTトークンを使用してユーザーの情報を取得します。

リクエストヘッダー:
- Authorization: Bearer <JWTトークン>

レスポンス:
- 成功時 (200 OK):
  {
    "username": "ユーザー名",
    "email": "メールアドレス",
    "other_info": "その他の情報"
  }
- 失敗時 (401 Unauthorized):
  - ログインしていない場合や、無効なトークンの場合、エラーメッセージが返されます。

---

4. ログアウト (Logout)

POST /logout/

JWTトークンを削除して、ユーザーをログアウトします。

レスポンス:
- 成功時 (200 OK):
  {
    "status": "success"
  }
- 失敗時 (400 Bad Request):
  - 無効なトークン、またはトークンが設定されていない場合、エラーメッセージが返されます。

---

5. 2FA設定 (TFA Setup)

GET /signup-tfa/

ログイン後、2FA（Two-Factor Authentication）の設定用QRコードを取得します。

リクエストヘッダー:
- Authorization: Bearer <JWTトークン>

レスポンス:
- 成功時 (200 OK):
  {
    "qr_url": "QRコードのURL",
    "secret_key": "シークレットキー"
  }
- 失敗時 (400 Bad Request):
  - 2FAが既に設定されている場合、エラーメッセージが返されます。

POST /signup-tfa/

2FAを有効にするための設定を行います。

リクエストボディ:
{
  "secret_key": "シークレットキー"
}

レスポンス:
- 成功時 (200 OK):
  {
    "status": "success"
  }
- 失敗時 (400 Bad Request):
  - シークレットキーが無効な場合、エラーメッセージが返されます。

---

6. 2FAを使用したログイン (Login with 2FA)

POST /login-2fa/

2FAを有効にしたユーザーが、認証コードを使用してログインします。

リクエストボディ:
{
  "username": "ユーザー名",
  "password": "パスワード",
  "code": "2FA認証コード"
}

レスポンス:
- 成功時 (200 OK):
  {
    "jwt": "JWTトークン"
  }
- 失敗時 (401 Unauthorized):
  - 認証コードが間違っている場合、エラーメッセージが返されます。

---

サンプルリクエスト

ユーザー登録（サインアップ）
curl -X POST http://localhost:8000/api/signup/ \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

ログイン
curl -X POST http://localhost:8000/api/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "password123"}'

ユーザー情報取得
curl -X GET http://localhost:8000/api/profile/ \
    -H "Authorization: Bearer <JWTトークン>"

2FA設定（QRコード取得）
curl -X GET http://localhost:8000/api/signup-tfa/ \
    -H "Authorization: Bearer <JWTトークン>"

セキュリティに関する注意

- JWTトークンは、セキュアなHTTPOnlyのクッキーとして保存することを推奨します。これはブラウザでのXSS攻撃から保護するためです。
- 本番環境では、必ず`secure=True`（HTTPS接続）を設定し、`httponly=True`、`samesite="Strict"`など、セキュリティ向上のためのオプションも考慮してください。

最後に

これで、APIを通じてユーザー認証、ログイン、2FA設定を行うための基本的な設計書が完成しました。実際の環境に合わせてエンドポイントのURLやリクエストの詳細を調整してください。
