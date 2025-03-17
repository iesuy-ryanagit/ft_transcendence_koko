from django.contrib.auth import authenticate, login, logout
from rest_framework import status, views
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer, SignupSerializer, LoginSerializer, OTPLoginSerializer, UserSettingsSerializer
from rest_framework.permissions import IsAuthenticated
from django_otp.plugins.otp_totp.models import TOTPDevice
from .jwts import generate_jwt,JWTAuthentication
import datetime


class SetupTFAView(views.APIView):
    authentication_classes = [JWTAuthentication,]
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        user = request.user
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        if not device:
            device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if not device:
            device = TOTPDevice.objects.create(user=user, confirmed=False)
        uri = device.config_url
        secret_key = device.bin_key.hex()
        return Response(
                {"qr_url": uri, "secret_key": secret_key},
                status=status.HTTP_200_OK,
        )

    def post(self, request):
        user = request.user
        device = TOTPDevice.objects.filter(user=user).first()
        device.confirmed = True
        user.otp_enabled = True
        device.save()
        user.save()
        return Response({"status": "success"}, status=status.HTTP_200_OK)

class LoginTFAView(views.APIView):
    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # ユーザーの情報を取得
        user = serializer.validated_data["user"]
        password = serializer.validated_data["password"]
        otp =  serializer.validated_data["otp"]  # クライアントから送信されたOTP
        if not user or not otp:
            return Response({"detail": "OTP is required."}, status=status.HTTP_400_BAD_REQUEST)
        # ユーザーのTOTPデバイスを取得
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if not device:
            return Response({"detail": "No confirmed 2FA device found."}, status=status.HTTP_400_BAD_REQUEST)
        # OTPの検証
        if device.verify_token(otp):
            data ={
                "username": user,
                "password":password
            }
            user = authenticate(username=user, password=password)
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
                return response
            else :
                return Response({"detail": "not valid password"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "invalid otp"}, status=status.HTTP_400_BAD_REQUEST)


class SignupView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user.otp_enabled:
                 return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)
            else:
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
            return response
        else:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    authentication_classes = [
        JWTAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]
    def get(self, request, *args, **kwargs):
        response.delete_cookie("jwt")
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class ProfileView(views.APIView):
    authentication_classes = [
        JWTAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]
    def get(self, request, *args, **kwargs):
        # The `request.user` should already be authenticated if IsAuthenticated is used.
        return Response(CustomUserSerializer(request.user).data)


class UpdateUserSettingsView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user= request.user
            ball_speed = user.ball_speed
            timer = user.timer
            response = Response({'ball_speed': ball_speed, 'timer': timer}, status=status.HTTP_200_OK)
            return response
        except AttributeError:
            return Response({'error': 'User settings not found'}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSettingsSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # バリデーションを通過した場合に保存
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
