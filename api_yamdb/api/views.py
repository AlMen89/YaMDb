from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, mixins
from django_filters import FilterSet, CharFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from users.models import User

from .permissions import AdminOrSuperuserOnly, AdminOrReadOnly
from .serializers import (
    GetTokenSerializer, MeSerializer, SignupSerializer, UserSerializer,
    CategorySerializer, GenreSerializer, TitleSerializer, TitlePostSerializer)
from reviews.models import Category, Genre, Title


class SignupAPIView(APIView):
    def post(self, request):
        try:
            instance = User.objects.get(
                username=request.data.get('username'),
                email=request.data.get('email')
            )
        except User.DoesNotExist:
            instance = None
        serializer = SignupSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTokenAPIView(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AdminOrSuperuserOnly,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = MeSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = MeSerializer(request.user)
        return Response(serializer.data)


class CreateListDelViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class CategoryViewSet(CreateListDelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def destroy(self, request, pk=None):
        queryset = Category.objects.all()
        category = get_object_or_404(queryset, slug=pk)
        self.perform_destroy(category)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(CreateListDelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AdminOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def destroy(self, request, pk=None):
        queryset = Genre.objects.all()
        genre = get_object_or_404(queryset, slug=pk)
        self.perform_destroy(genre)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TitleFilterSet(FilterSet):
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')
    name = CharFilter(field_name='name', lookup_expr='icontains')
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ['category', 'genre', 'name', 'year']


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [AdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilterSet
    ordering_fields = ('name', 'year')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitlePostSerializer
        return TitleSerializer
