from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .models import Category, Comment, CustomUser, Genre, Review, Title
from .permissions import IsAdmin, IsAuthor, IsModer, IsOwner, ReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, NewUserSerializer, ReviewSerializer,
                          TitleReadOnlySerializer, TitleSerializer,
                          TokenSerializer, UserSerializer)


class APINewUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = NewUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user, created = CustomUser.objects.get_or_create(
            email=email,
            username=(email.split('@')[0])
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Confirm registration',
            'Your confirmation code is %s' % confirmation_code,
            None, [email], fail_silently=True
        )
        return Response(serializer.data)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'token': str(refresh.access_token),
    }


class APIGetToken(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            CustomUser, email=serializer.validated_data['email']
        )
        if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            return Response(get_tokens_for_user(user))
        return Response(
            {'confirmation_code': "confirmation code doesn't match"}
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]
    lookup_field = 'username'

    @action(
        detail=False, methods=['GET', 'PATCH'],
        permission_classes=[IsAuthenticated, IsOwner]
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return None


class ListCreateViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin | ReadOnly]
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'PUT']:
            if self.request.user.is_superuser:
                return TitleSerializer
        return TitleReadOnlySerializer


class GenreViewSet(ListCreateViewSet):
    permission_classes = [IsAdmin | ReadOnly]
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'


class CategoryViewSet(ListCreateViewSet):
    permission_classes = [IsAdmin | ReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly & (IsAdmin | IsModer | IsAuthor | ReadOnly)
    ]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        if title_id is None:
            return self.queryset
        title = get_object_or_404(Title, pk=title_id)
        #queryset = title.reviews.all()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly & (IsAdmin | IsModer | IsAuthor | ReadOnly)
    ]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        if review_id is None or title_id is None:
            return self.queryset
        review = get_object_or_404(Review, title__pk=title_id, pk=review_id)
        #queryset = review.comments.all()
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            title__pk=self.kwargs.get('title_id'),
            pk=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)
