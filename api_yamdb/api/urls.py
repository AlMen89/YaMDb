from django.urls import path, include
from rest_framework import routers

from ..api.views import UserViewSet, CommentViewSet, ReviewViewSet


router_v1 = routers.DefaultRouter()


router_v1.register('users', UserViewSet, basename='users')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment',
)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]