from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField


from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Category
