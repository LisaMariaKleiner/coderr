from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        return data


class RegistrationSerializer(serializers.Serializer):
    """Serializer for user registration"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    repeated_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    type = serializers.ChoiceField(choices=['customer', 'business'])

    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

    def validate(self, data):
        """Check if passwords match"""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=user_type
        )
        return user
