from rest_framework import serializers
from django.contrib.auth.models import User
import re
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.validators import UniqueValidator
from .models import Product, Card,UserProfile

from rest_framework import serializers
from .models import Entity

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'name', 'description']


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['card_number', 'card_password', 'balance']




class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        return value

    def validate_email(self, value):
        if not value.endswith("@gmail.com"):
            raise serializers.ValidationError("Only Gmail addresses are allowed.")
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({"password": "Passwords do not match!"})

        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})

        if not any(ch.isupper() for ch in password):
            raise serializers.ValidationError({"password": "Password must contain at least one uppercase letter."})

        if not any(ch.islower() for ch in password):
            raise serializers.ValidationError({"password": "Password must contain at least one lowercase letter."})

        if '.' not in password:
            raise serializers.ValidationError({"password": "Password must contain at least one '.' (dot) character."})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "This email is already registered!"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()

        code = ''.join(random.choices(string.digits, k=6))  # Например, 6-значный код
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.verification_code = code
        profile.save()
        send_mail(
            'Email verification',
            f'Your verification code is: {code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return user
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'category']
