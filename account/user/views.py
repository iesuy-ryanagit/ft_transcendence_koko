from django.contrib.auth import authenticate, login, logout
from rest_framework import status, views
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer, SignupSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

class SignupView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Signed in successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    def post(self, request, *args, **kwargs):
        print("Received data:", request.data) 
        serializer = LoginSerializer(data=request.data)
        print("Received data:", request.data) 
        if serializer.is_valid():
            return Response({'message': 'Logged in successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Error in Login', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class ProfileView(views.APIView):
    permission_classes = [IsAuthenticated]  # This ensures only authenticated users can access this view.

    def get(self, request, *args, **kwargs):
        # The `request.user` should already be authenticated if IsAuthenticated is used.
        return Response(CustomUserSerializer(user).data)

