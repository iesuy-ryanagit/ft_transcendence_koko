from django.contrib.auth import authenticate, login, logout
from rest_framework import status, views
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer, SignupSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from django_otp.plugins.otp_totp.models import TOTPDevice
from .jwts import generate_jwt,JWTAuthentication


class SetupTFAView(views.APIView):
    authentication_classes = [JWTAuthentication,]
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        user = request.user
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

class VerifyOTPView(views.APIView):
    def post(self, request):
        return Response({"message": "2FA setup successful"}, status=status.HTTP_400_BAD_REQUEST)


class SignupView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    def post(self, request, *args, **kwargs):
        print("Received data:", request.data) 
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            jwt = generate_jwt(user)
            response = Response({'status': 'success','jwt': jwt}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="jwt",
                value=jwt,
                max_age=86400,
                secure=False,
                httponly=False,
                samesite=None,
            )
            return response
        else:
            return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    def post(self, request, *args, **kwargs):
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

