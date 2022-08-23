from django.conf import settings
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import CharFilter, FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination)
from django.shortcuts import get_object_or_404

from users.models import User
from reviews.models import Category, Genre, Title, Review
from .permissions import (
    AdminOrSuperuserOnly, AdminOrReadOnly, CommentReviewPermission)
from .serializers import (
    GetTokenSerializer, SignupSerializer, UserSerializer,
    CategorySerializer, GenreSerializer, TitleSerializer, TitlePostSerializer,
    CommentSerializer, ReviewSerializer)


class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, stat = User.objects.get_or_create(
                **serializer.validated_data
            )
            user.confirmation_code = User.get_confirmation_code(self)
            user.save()
            subject = 'YaMDb: Подтверждение учетных данных'
            message = (
                'Здравствуйте! Код для подтверждения ваших учетных данных:'
                f' {user.confirmation_code}. Никому его не сообщайте!'
            )
            user.email_user(subject, message, settings.EMAIL_BACKEND)
        except Exception as error:
            raise (error)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = [CommentReviewPermission]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all().order_by('pub_date')

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = [CommentReviewPermission]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(
            title.reviews, id=self.kwargs.get('review_id'))
        return review.comments.all().order_by('pub_date')

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'),
                                   title__id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review=review)


class GetTokenAPIView(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=self.request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
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
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')).order_by('id')
    serializer_class = TitleSerializer
    permission_classes = [AdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilterSet
    ordering_fields = ('name', 'year')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitlePostSerializer
        return TitleSerializer
