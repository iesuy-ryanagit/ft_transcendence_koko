import time
# from .models import CustomUser
# from rest_framework import exceptions
# from rest_framework.authentication import BaseAuthentication

SECRET_KEY = "hello"

import jwt
print(jwt.__version__)  # PyJWT のバージョンを確認
print(jwt.__file__)     # モジュールのファイルパスを確認

def generate_jwt():
    timestamp = int(time.time()) + 60 * 60 * 24 * 7  # 1週間後
    encoded = jwt.encode(
        {"username": "hello", "exp": timestamp},
        SECRET_KEY,
        algorithm="HS256"
    )
    return encoded




tmp =generate_jwt()

print(tmp)

origin= jwt.decode(tmp, SECRET_KEY, algorithms="HS256")

print(origin)

