import logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, OTPSerializer, SignUpSerializer
import time

import jwt
from .models import CustomUser
from account.settings import SECRET_KEY
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

logger = logging.getLogger("user")

def generate_jwt(user):
    timestamp = int(time.time()) + 60 * 60 * 24 * 7
    return jwt.encode(
        {
            "userid": user.pk,
            "username": user.username,
            "email": user.email,
            "exp": timestamp,
        },
        SECRET_KEY,
    )


class JWTAuthentication(BaseAuthentication):
    keyword = "JWT"
    model = None

    def authenticate(self, request):
        try:
            token = request.COOKIES.get("jwt")
            if not token:
                return None

            jwt_info = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            userid = jwt_info.get("userid")
            if userid is None:
                raise exceptions.AuthenticationFailed("Token does not contain user ID")

            try:
                user = CustomUser.objects.get(pk=userid)
                return (user, token)
            except CustomUser.DoesNotExist:
                raise exceptions.AuthenticationFailed("User not found in database")

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token format")
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Authentication error: {str(e)}")

    def authentication_header(self, request):
        pass


@method_decorator([sensitive_post_parameters(), never_cache], name="dispatch")
class CustomLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            logger.info(f"Login attempt for user: {user.username}")
            if user.otp_enabled:
                logger.info(f"OTP verification required for user: {user.username}")
                return Response(
                    {"redirect": "user:verify_otp"}, status=status.HTTP_200_OK
                )
            jwt = generate_jwt(user)
            logger.info(f"Login successful for user: {user.username}")
            response = Response({"redirect": "homepage"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="jwt",
                value=jwt,
                max_age=86400,
                secure=True,
                httponly=True,
                samesite="Strict",
            )
            response.set_cookie(
                key="default_language",
                value=user.default_language,
                max_age=86400,
                secure=True,
                samesite="Strict",
            )
            return response
        logger.warning(f"Login failed with errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator([sensitive_post_parameters(), never_cache], name="dispatch")
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user registered: {user.username}")
            return Response(
                {"redirect": "user:login"}, status=status.HTTP_201_CREATED
            )
        logger.warning(f"User registration failed with errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator([never_cache], name="dispatch")
class SetupOTPView(APIView):
    authentication_classes = [
        JWTAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        user = request.user
        if not TOTPDevice.objects.filter(user=user, confirmed=True).exists():
            device = TOTPDevice.objects.create(user=user, confirmed=False)
            uri = device.config_url
            secret_key = device.bin_key.hex()
            logger.info(f"OTP setup initiated for user: {user.username}")
            return Response(
                {"otpauth_url": uri, "secret_key": secret_key},
                status=status.HTTP_200_OK,
            )
        logger.warning(f"OTP setup already completed for user: {user.username}")
        return Response(
            {"message": "OTP already set up"}, status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):
        user = request.user
        device = TOTPDevice.objects.filter(user=user).first()
        device.confirmed = True
        user.otp_enabled = True
        device.save()
        user.save()
        logger.info(f"OTP setup completed for user: {user.username}")
        return Response({"message": "OTP setup successful"}, status=status.HTTP_200_OK)


@method_decorator([sensitive_post_parameters()], name="dispatch")
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            otp = serializer.validated_data["otp_token"]
            device = TOTPDevice.objects.filter(user=user).first()

            logger.info(f"OTP verification attempt for user: {user.username}")
            if device and device.verify_token(otp):
                jwt = generate_jwt(user)
                logger.info(f"OTP verification successful for user: {user.username}")
                response = Response({"redirect": "homepage"}, status=status.HTTP_200_OK)
                response.set_cookie(
                    key="jwt",
                    value=jwt,
                    max_age=86400,
                    secure=True,
                    httponly=True,
                    samesite="Strict",
                )
                return response
            else:
                logger.warning(f"Invalid OTP provided for user: {user.username}")
                return Response(
                    {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
                )
        logger.warning(f"OTP verification failed with errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator([never_cache], name="dispatch")
class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Logout attempt for user: {request.user.username}")
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        response.delete_cookie("jwt")
        logger.info(f"Logout successful for user: {request.user.username}")
        return response
