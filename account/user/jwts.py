import time
import jwt
from .models import CustomUser
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

SECRET_KEY = "hello"

def generate_jwt(user):
    timestamp = int(time.time()) + 60 * 60 * 24 * 7  # 1週間後
    encoded = jwt.encode(
        {"userid": user.pk, "username": user.username, "exp": timestamp},
        SECRET_KEY,
        algorithm="HS256"
    )
    return encoded

class JWTAuthentication(BaseAuthentication):
    keyword = "JWT"
    model = None

    def authenticate(self, request):
        try:
            token = request.COOKIES.get("jwt")
            print("jwt:")
            print(token)
            if not token:
                return None

            jwt_info = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            userid = jwt_info.get("userid")
            if userid is None:
                raise exceptions.AuthenticationFailed("Invalid token: lacking userid")
            try:
                user = CustomUser.objects.get(pk=userid)
                return (user, token)
            except CustomUser.DoesNotExist:
                raise exceptions.AuthenticationFailed("Invalid token: user not exist in db")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Invalid token: too late")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token: cannnot decode")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"token error: {str(e)}")

    def authentication_header(self, request):
        pass