from django.contrib.auth import authenticate, login, logout
from rest_framework import status, views
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer, SignupSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

class SignupView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(CustomUserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Create JWT tokens (access and refresh tokens)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Send the access token in the response
            return Response({
                'access_token': access_token,
                'user': CustomUserSerializer(user).data,
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class ProfileView(views.APIView):
    permission_classes = [IsAuthenticated]  # This ensures only authenticated users can access this view.

    def get(self, request, *args, **kwargs):
        # The `request.user` should already be authenticated if IsAuthenticated is used.
        if request.user.is_authenticated:
            user = request.user
            return Response(CustomUserSerializer(user).data)
        else:
            return Response({'error': 'You must be logged in to view the profile.'}, status=status.HTTP_401_UNAUTHORIZED)


