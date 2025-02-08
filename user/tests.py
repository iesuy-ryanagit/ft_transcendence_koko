import time

from django.urls import reverse
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser
from .views import generate_jwt


class CustomLoginViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    def test_custom_login_view_valid_login(self):
        """正しいユーザー名とパスワードでログインできることを確認する、OTPが無効な場合"""
        response = self.client.post(
            reverse("user:login"),
            {"username": "testuser", "password": "password123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["redirect"], "homepage")

        # Cookieの検証
        self.assertIn("jwt", response.cookies)
        self.assertTrue(response.cookies["jwt"]["httponly"])
        self.assertEqual(response.cookies["jwt"]["samesite"], "Strict")

    def test_custom_login_view_valid_login_with_otp(self):
        """正しいユーザー名とパスワードでログインできることを確認する、OTPが有効な場合"""
        self.user.otp_enabled = True
        self.user.save()
        response = self.client.post(
            reverse("user:login"),
            {"username": "testuser", "password": "password123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["redirect"], "user:verify_otp")
        # OTPが有効な場合はJWTを発行しない
        self.assertNotIn("jwt", response.cookies)

    def test_custom_login_view_invalid_login(self):
        """間違ったパスワードでログインできないことを確認する"""
        response = self.client.post(
            reverse("user:login"),
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class SignUpViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("user:signup")
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    def test_signup_view_post_valid(self):
        """有効なデータでサインアップが成功することを確認する"""
        data = {
            "username": "newuser",
            "password": "password123",
            "email": "newuser@example.com",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"redirect": "user:login"})
        self.assertEqual(CustomUser.objects.count(), 1)
        user = CustomUser.objects.get(username="newuser")
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("password123"))

    def test_signup_view_post_invalid(self):
        """無効なデータでサインアップが失敗することを確認する"""
        data = {
            "username": "",
            "password": "password123",
            "email": "invalid-email",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 0)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)


class SetupOTPViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"
        self.token = generate_jwt(self.user)
        # JWTトークンの設定とユーザー認証を別々に行う
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_setup_otp_view_get(self):
        """OTPセットアップのGETリクエストが成功することを確認する"""
        self.client.force_authenticate(user=self.user)  # このテストの前に認証
        response = self.client.get(reverse("user:setup_otp"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("otpauth_url", response.data)
        self.assertIn("secret_key", response.data)

    def test_setup_otp_view_post(self):
        """OTPセットアップのPOSTリクエストが成功することを確認する"""
        self.client.force_authenticate(user=self.user)  # このテストの前に認証
        # デバイスを事前に作成
        device = TOTPDevice.objects.create(user=self.user, confirmed=False)
        response = self.client.post(reverse("user:setup_otp"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # デバイスとユーザーの状態を確認
        device.refresh_from_db()
        self.user.refresh_from_db()
        self.assertTrue(device.confirmed)
        self.assertTrue(self.user.otp_enabled)

    def test_setup_otp_view_get_without_jwt(self):
        """JWTトークンがない場合にOTPセットアップのGETリクエストが失敗することを確認する"""
        self.client.credentials()  # JWTトークンをクリア
        self.client.force_authenticate(user=None)  # 認証をクリア
        response = self.client.get(reverse("user:setup_otp"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_setup_otp_view_post_without_jwt(self):
        """JWTトークンがない場合にOTPセットアップのPOSTリクエストが失敗することを確認する"""
        self.client.credentials()  # JWTトークンをクリア
        self.client.force_authenticate(user=None)  # 認証をクリア
        response = self.client.post(reverse("user:setup_otp"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VerifyOTPViewTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123", otp_enabled=True
        )
        self.client.force_authenticate(user=self.user)
        self.device = TOTPDevice.objects.create(user=self.user, confirmed=True)
        self.client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
        self.client.defaults["wsgi.url_scheme"] = "https"

    def test_verify_otp_view_post_valid_otp(self):
        """正しいOTPトークンでOTP確認が成功することを確認する"""
        totp = TOTP(
            key=self.device.bin_key,
            step=self.device.step,
            t0=self.device.t0,
            digits=self.device.digits,
        )
        totp.time = time.time()
        valid_token = totp.token()

        response = self.client.post(
            f"{reverse('user:verify_otp')}?user={self.user.username}",
            {"otp_token": valid_token},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["redirect"], "homepage")

        # Cookieの検証
        self.assertIn("jwt", response.cookies)
        self.assertTrue(response.cookies["jwt"]["httponly"])
        self.assertEqual(response.cookies["jwt"]["samesite"], "Strict")

    def test_verify_otp_view_post_invalid_otp(self):
        """間違ったOTPトークンでOTP確認が失敗することを確認する"""
        response = self.client.post(
            f"{reverse('user:verify_otp')}?user={self.user.username}",
            {"otp_token": "123456"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid OTP")

    def test_verify_otp_view_post_without_username(self):
        """ユーザー名なしでOTP確認が失敗することを確認する"""
        response = self.client.post(
            reverse("user:verify_otp"),
            {"otp_token": "123456"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Username is required", str(response.data))