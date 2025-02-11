from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar', 'match_history']

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'avatar']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        # print("Received data in validate:", data) 
        username = data.get('username')
        password = data.get('password')

        # # ユーザー名とパスワードの検証
        print("Received data in validate:", data) 
        if not username or not password:
            raise serializers.ValidationError('Username and password are required.')

        # # authenticateでユーザー認証
        user = authenticate(username=username, password=password)
        if user:
            data['user'] = user  # 認証に成功したら、userをdataに追加
        else:
            raise serializers.ValidationError('Invalid credentials')  # 認証に失敗したらエラーを返す

        return data



