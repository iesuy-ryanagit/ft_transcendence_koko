import os
import pyotp


class TwoFA:

    def make_uri(self, email, secret):
        totp = pyotp.TOTP(secret)

        # QRコードのURI生成
        uri = totp.provisioning_uri(name=email, issuer_name="42 Pong Game")
        return uri

    def app(self, user):
        email = user.email
        secret = user.app_secret
        return self.make_uri(email, secret)

    def verify_app(self, user, code):
        secret = user.app_secret
        totp = pyotp.TOTP(secret)
        totp.now()

        if code == totp.now():
            return True
        return False