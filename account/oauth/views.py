from rest_framework import status, views
from rest_framework.response import Response
from django.conf import settings
import requests

class OauthView(views.APIView):

    def get(self, request, *args, **kwargs):
        """
        GET /api/auth/login
        42 OAuthの認証URLを返す
        """
        auth_url = 'https://api.intra.42.fr/oauth/authorize'
        client_id = settings.OAUTH2_CLIENT_ID  
        client_secret = settings.OAUTH2_CLIENT_SECRET
        redirect_uri = settings.OAUTH2_REDIRECT_URI
        auth_url = f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        
        # OAuth URLをレスポンスで返す
        return Response({
            "status": "success",
            "42oauth_url": auth_url,
        }, status=status.HTTP_200_OK)

class CallbackView(views.APIView):
    def get(self, request, *args, **kwargs):
        """
        GET /api/auth/callback
        42 OAuthから返されたコードに基づいてユーザーを作成またはログイン
        """
        error = request.GET.get('error')
        if error:
            # エラーがあればloginへリダイレクト
            return Response({
            "status": "errror",
                "message": "request get error",
        }, status=status.HTTP_400_BAD_REQUEST)
        
        code = request.GET.get('code')
        if not code:
            # codeがない場合はエラー
            return Response({
                "status": "error",
                "message": "Missing 'code' parameter"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authorization Code を使ってアクセストークンを取得する
        client_id = settings.OAUTH2_CLIENT_ID
        client_secret = settings.OAUTH2_CLIENT_SECRET
        redirect_uri = settings.OAUTH2_REDIRECT_URI
        token_url = "https://api.intra.42.fr/oauth/token"
        
        # トークンを取得
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            return Response({
                "status": "error",
                "message": "Failed to obtain access token"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # トークンを取得したら、ユーザー情報を取得
        access_token = response.json().get('access_token')
        user_url = "https://api.intra.42.fr/v2/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(user_url, headers=headers)
        
        if user_response.status_code != 200:
            return Response({
                "status": "error",
                "message": "Failed to fetch user data"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_data = user_response.json()
        
        # ユーザーを作成またはログイン処理（仮にユーザーIDで管理する例）
        user_id = user_data.get('id')
        user_name = user_data.get('login')
        
        # ここでユーザーをデータベースに保存または更新する処理を追加できます
        
        # ユーザーが正常にログインした場合、ホームページにリダイレクト
        return Response({
            "status": "success",
            "message": "User authenticated successfully",
            "user_info": {
                "id": user_id,
                "name": user_name,
            }
        }, status=status.HTTP_200_OK)
