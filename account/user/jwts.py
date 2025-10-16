import time
import jwt
from .models import CustomUser
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from django.conf import settings

def generate_jwt(user):
    timestamp = int(time.time()) + 60 * 60 * 24 * 7  # 1週間後
    encoded = jwt.encode(
        {"login": settings.LOGIN_KEY,"userid": user.pk, "username": user.username, "exp": timestamp},
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    return encoded

class JWTAuthentication(BaseAuthentication):
    keyword = "JWT"
    model = None

    def authenticate(self, request):
        try:
            token = request.COOKIES.get("jwt")

            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            if not token:
                return None

            jwt_info = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            userid = jwt_info.get("userid")
            if userid is None:
                raise exceptions.AuthenticationFailed("Invalid token: lacking userid")
            try:
                user = CustomUser.objects.get(pk=userid)
                return (user, token)
            except CustomUser.DoesNotExist:
                raise exceptions.AuthenticationFailed("Invalid token: user not found")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Invalid token: expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token: failed to  decode")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"token error: {str(e)}")

    def authentication_header(self, request):
        pass