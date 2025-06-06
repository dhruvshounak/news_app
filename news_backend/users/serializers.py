from rest_framework import serializers
from django.contrib.auth.models import User
import re 

class registerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username','email','passowrd']

    def create(self, validated_data):
        user = User.objects.create.user(
            username=validated_data['username'],
            email=validated_data.get('email',""),
            password=validated_data['password']


            )
        return user


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    def validate_password(self, value):
        """Ensure password contains at least one number and one special character"""
        if not re.search(r"\d", value) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one number and one special character.")
        return value
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
