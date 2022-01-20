from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import PasswordResetTokenGenerator


from rest_framework import mixins, viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import api_view, permission_classes


from reviews.models import Category, Genre, Review, Title
from api_yamdb.settings import AUTH_FROM_EMAIL

from .filters import Filter
from .permissions import (AdminOnlyPermission, AdminOrReadOnlyPermission,
                          AdminOrModeratorOrAuthorPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleListSerializer, TitleCreateSerializer,
                          UserSerializer, AuthCodeSerializer,
                          SendAuthCodeSerializer, ProfileSerializer)

User = get_user_model()


class ListCreateDeleteViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    pass


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, AdminOrReadOnlyPermission)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, AdminOrReadOnlyPermission)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score'))
    pagination_class = PageNumberPagination
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, AdminOrReadOnlyPermission)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = Filter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrModeratorOrAuthorPermission, )

    def get_queryset(self):
        title_id = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title_id.reviews.all()

    def perform_create(self, serializer):
        title_id = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title_id)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrModeratorOrAuthorPermission,)

    def get_queryset(self):
        review_id = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review_id.comments.all()

    def perform_create(self, serializer):
        review_id = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review_id)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AdminOnlyPermission]
    lookup_field = 'username'


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_auth_code(request):
    serializer = SendAuthCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = request.data['username']
    email = request.data['email']
    username_exists = User.objects.filter(username=username).exists()
    email_exists = User.objects.filter(email=email).exists()
    if not username_exists and not email_exists:
        User.objects.create_user(email=email, username=username)
    if not username_exists and email_exists:
        return Response(
            {'message': 'Вы не можете создать пользователя с этим email'},
            status=status.HTTP_400_BAD_REQUEST)
    if username_exists and not email_exists:
        return Response(
            {'message': 'Вы не можете создать пользователя с этим username'},
            status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(username=username)
    generator = PasswordResetTokenGenerator()
    auth_code = generator.make_token(user)
    User.objects.filter(username=username).update(
        auth_code=auth_code
    )
    email_subject = 'Ваш код подтверждения'
    email_message = (f'Используйте код подтверждения {auth_code},'
                     'чтобы авторизоваться')
    send_mail(subject=email_subject, message=email_message,
              recipient_list=[user.email], from_email=AUTH_FROM_EMAIL)
    return Response(
        {
            'email': f'{email}',
            'username': f'{username}'
        },
        status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = AuthCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = request.data['username']
    user = get_object_or_404(User, username=username)
    generator = PasswordResetTokenGenerator()
    if generator.check_token(user, request.data['confirmation_code']):
        access_token = AccessToken.for_user(user)
        return Response(
            {
                'error': None,
                'token': f'{access_token}'
            },
            status=status.HTTP_200_OK
        )
    return Response(
        {
            'error': 'Неверный код подтверждения',
            'token': None
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.AllowAny])
def profile(request):
    if not request.user.is_authenticated:
        return Response('Not authorized', status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    serializer = ProfileSerializer(request.user, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
