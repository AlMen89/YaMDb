# from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Category

from .serializers import (
    CategorySerializer)
from .permissions import AdminOrReadOnly


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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
