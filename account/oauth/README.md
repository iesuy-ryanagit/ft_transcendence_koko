
エントリーポイント
/api/auth/login

メソッド
GET

42 oauthのurlを返す

{
  "42oath_url": "https://api.intra.42.fr/oauth/authorize?client_id=...&redirect_uri=...&response_type=code"
}

リターンはstatus successかerror

エントリーポイント
/api/auth/callback
successの場合は42oath_urlへ
errorの場合はloginへ


メソッド
GET
42のcodeを要求し、codeに基づき、42oauthからデータを取得し、ユーザーを作成またはログイン

リターンはstatus successかerror

successの場合はhomeへ

errorの場合はloginへ