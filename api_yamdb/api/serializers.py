from random import randint

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве username. '
                'Придумайте, пожалуйста, другой username.'
            )
        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            confirmation_code=randint(10000000, 99999999)
        )
        return user

    def update(self, instance, validated_data):
        instance.confirmation_code = randint(10000000, 99999999)
        instance.save()
        return instance


class GetTokenSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    username = serializers.CharField(write_only=True)
    confirmation_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code', 'token')

    def get_token(self, user):
        user = get_object_or_404(
            User, username=self.validated_data.get('username')
        )
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def validate(self, data):
        user = get_object_or_404(User, username=data.get('username'))
        confirmation_code = user.confirmation_code
        if data.get('confirmation_code') != confirmation_code:
            raise serializers.ValidationError('Некорректный код!')
        return data


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
