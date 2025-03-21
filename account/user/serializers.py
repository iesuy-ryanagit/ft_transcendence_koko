from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
import re

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'otp_enabled','ball_speed', 'timer']

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise ValidationError("This username is already taken.")
        return value
    def validate_password(self, value):
        if len(value) < 5:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):  # 大文字が含まれているか
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', value):  # 小文字が含まれているか
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'[0-9]', value):  # 数字が含まれているか
            raise ValidationError("Password must contain at least one digit.")
        return value
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
            raise serializers.ValidationError({'non_field_errors': ['Invalid credentials']})
        # # authenticateでユーザー認証
        user = authenticate(username=username, password=password)

        if user:
            data['user'] = user  # 認証に成功したら、userをdataに追加
        else:
            raise serializers.ValidationError({'non_field_errors': ['Invalid credentials']})
        return data

class OTPLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    otp = serializers.CharField()
    def validate(self, data):
        # print("Received data in validate:", data) 
        username = data.get('username')
        password = data.get('password')
        otp = data.get('otp')
        if not username or not password or not otp: 
            raise serializers.ValidationError({'non_field_errors': ['Invalid credentials']})

        # # authenticateでユーザー認証
        user = authenticate(username=username, password=password)
        if user:
            data['user'] = user  # 認証に成功したら、userをdataに追加
        else:
            raise serializers.ValidationError({'non_field_errors': ['Invalid credentials']})
        print("success authenticate")
        return data

class UserSettingsSerializer(serializers.ModelSerializer):
    ball_speed = serializers.DecimalField(max_digits=5, decimal_places=2)
    timer = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ['ball_speed', 'timer']

    def validate_ball_speed(self, value):
        if value < 0:
            raise serializers.ValidationError("Ball speed must be a positive value.")
        return value

    def validate_timer(self, value):
        if value < 1 or value > 3600:
            raise serializers.ValidationError("Timer must be between 1 and 3600 seconds.")
        return value
