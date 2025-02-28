
エントリーポイント
/api/auth/login

メソッド
GET

42 oauthのurlを返す

{
  "42oath_url": "https://api.intra.42.fr/oauth/authorize?client_id=...&redirect_uri=...&response_type=code"
}

リターンはstatus successかerror

successの場合は、42oath_urlへ
errorの場合は、login画面へ戻るとか


エントリーポイント
/api/auth/callback

"注意"
こいつはフロントエンドから呼ぶのではなく、/api/auth/loginでから行く42oath_urlからアクセスされるエンドポイント


メソッド
GET
ユーザーを作成またはログインする

リターンはstatus successかerror

successの場合はhomeへ

errorの場合はloginへ


フロントエンドとしては、42oath_urlのレスポンスをゲット
リダイレクトしてもらう