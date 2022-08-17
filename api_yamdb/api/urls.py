from rest_framework.routers import DefaultRouter
from django.urls import path, include

from . import views

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'users', views.UserViewSet, basename='users')
v1_router.register(r'categories', views.CategoryViewSet, basename='category')
v1_router.register(r'genres', views.GenreViewSet, basename='genre')
v1_router.register(r'titles', views.TitleViewSet, basename='title')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', views.ReviewViewSet, basename='review'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comment',
)
urlpatterns = [
    path('v1/auth/signup/', views.SignupAPIView.as_view(), name='signup'),
    path('v1/auth/token/', views.GetTokenAPIView.as_view(), name='tokens'),
    path('v1/', include(v1_router.urls), name='api-root'),
]
