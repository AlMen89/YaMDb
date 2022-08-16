from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    path('v1/auth/signup/', views.SignupAPIView.as_view(), name='signup'),
    path('v1/auth/token/', views.GetTokenAPIView.as_view(), name='tokens'),
    path('v1/', include(router.urls), name='api-root'),
]
