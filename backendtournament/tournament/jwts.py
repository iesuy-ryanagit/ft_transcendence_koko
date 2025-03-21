import time
import jwt
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from django.conf import settings


class JWTNoUserAuthentication(BaseAuthentication):
    keyword = "JWT"
    model = None

    def authenticate(self, request):
        try:
            # クッキーからJWTトークンを取得
            token = request.COOKIES.get("jwt")
            if not token:
                raise exceptions.AuthenticationFailed("Lacking token")

            # JWTトークンをデコード
            jwt_info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            login = jwt_info.get("login")

            # loginが存在すれば、ユーザー関係なく認証通過
            if login != settings.LOGIN_KEY:
                raise exceptions.AuthenticationFailed("Invalid token: missing login")
            
            # もし`login`があれば認証通過
            return (None, token)  # ユーザー情報は特に必要ないので、Noneを返す

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Invalid token: expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token: failed to decode")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Token error: {str(e)}")

    def authentication_header(self, request):
        pass