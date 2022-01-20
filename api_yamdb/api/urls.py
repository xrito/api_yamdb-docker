from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (TitleViewSet, GenreViewSet, CategoryViewSet,
                       UserViewSet, ReviewViewSet, CommentViewSet, get_token,
                       send_auth_code, profile)


router = SimpleRouter()
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register('categories', CategoryViewSet, basename='categories')
router.register('users', UserViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')


urlpatterns = [
    path('v1/users/me/', profile, name='profile'),
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', send_auth_code, name='send_auth_code'),
    path('v1/auth/token/', get_token, name='get_access_token')
]
