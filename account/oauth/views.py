from rest_framework import status, views
from rest_framework.response import Response
from django.conf import settings
from user.models import CustomUser
import requests
from user.jwts import generate_jwt
from django.contrib.auth import authenticate
from user.serializers import SignupSerializer


class OauthUrlView(views.APIView):

    def get(self, request, *args, **kwargs):
        auth_url = 'https://api.intra.42.fr/oauth/authorize'
        client_id = settings.OAUTH2_CLIENT_ID  
        client_secret = settings.OAUTH2_CLIENT_SECRET
        redirect_uri = settings.OAUTH2_REDIRECT_URI
        auth_url = f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        
        # OAuth URLをレスポンスで返す
        return Response({
            "status": "success",
            "oauth_url": auth_url,
        }, status=status.HTTP_200_OK)

class OauthLoginView(views.APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
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
        user_name = user_data.get('login')
        data = {
            'username': user_name,
            'password': user_name + "42Tokyo",
        }
        print(user_name + "42Tokyo")
        user = authenticate(username=user_name, password=user_name)
        if user:
            jwt = generate_jwt(user)
            response = Response({'status': 'success','jwt': jwt}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="jwt",
                value=jwt,
                max_age=86400,
                secure=True,
                httponly=True,
                samesite=None,
            )
            return (response)
        else:
            serializer = SignupSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                jwt = generate_jwt(user)
                response = Response({'status': 'success','jwt': jwt}, status=status.HTTP_201_CREATED)
                response.set_cookie(
                    key="jwt",
                    value=jwt,
                    max_age=86400,
                    secure=True,
                    httponly=True,
                    samesite=None,
                )
                return response
            else:
                return Response({"status" : "error"}, status=status.HTTP_400_BAD_REQUEST)
