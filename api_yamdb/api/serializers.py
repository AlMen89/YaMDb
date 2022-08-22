import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )

    def validate(self, data):
        if self.context["request"].method != "POST":
            return data
        request = self.context.get('request')
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if Review.objects.filter(title=title, author=author).exists():
            raise ValidationError('Вы уже добавили отзыв'
                                  'на это произведение')
        return data

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве username. '
                'Придумайте, пожалуйста, другой username.'
            )
        if re.match(r'^[\w.@+-]+$', value) is None:
            raise serializers.ValidationError(
                'Допустимы только английские буквы, цифры и символы @/./+/-/_'
            )
        return value

    def validate(self, data):
        """Проверяет уникальность username и email с возможностью запрашивать
        код подтверждения на почту повторно, если переданная
        в запросе комбинация username и email уже есть в БД.
        """
        if (
            User.objects.filter(username=data.get('username'))
            and not User.objects.filter(email=data.get('email'))
        ):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        if (
            User.objects.filter(email=data.get('email'))
            and not User.objects.filter(username=data.get('username'))
        ):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data


class GetTokenSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    username = serializers.CharField(
        write_only=True,
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
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
        if data.get('confirmation_code') != user.confirmation_code:
            raise serializers.ValidationError('Некорректный код!')
        return data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве username. '
                'Придумайте, пожалуйста, другой username.'
            )
        if re.match(r'^[\w.@+-]+$', value) is None:
            raise serializers.ValidationError(
                'Допустимы только английские буквы, цифры и символы @/./+/-/_'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'category', 'genre', 'rating', 'description')


class TitlePostSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())
    genre = SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True)

    class Meta:
        fields = '__all__'
        model = Title
