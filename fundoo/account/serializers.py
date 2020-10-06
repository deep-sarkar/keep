from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    confirm = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'confirm',
            ]
        extra_kwargs = {'password':{'write_only':True}}
        required_fields = ['username','email','password','confirm']
        read_only_fields = ["id"]

class LoginSerializer(serializers.ModelSerializer):
    password        = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model  = User
        fields = [
            'username',
            'password',
        ]
        extra_kwargs = {'password':{'write_only':True}}
        required_fields = fields

class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    confirm = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = User
        fields = [
            'password',
            'confirm'
        ]

class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['email']