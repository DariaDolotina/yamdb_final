from django.core.validators import ValidationError, validate_email
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Category, Comment, CustomUser, Genre, Review, Title


class NewUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['email']
        model = CustomUser


class TokenSerializer(serializers.ModelSerializer):

    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            validate_email(value)
            return value

        except ValidationError:
            return None

    class Meta:
        fields = ['email', 'confirmation_code']
        model = CustomUser


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    bio = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = [
            'first_name', 'last_name', 'username', 'bio', 'email', 'role'
        ]
        model = CustomUser
        lookup_field = 'username'
        partial = True
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ['id']
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ['id']
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        required=False,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        required=False,
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleReadOnlySerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id'
    )

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        if request._request.method == 'POST':
            title = get_object_or_404(Title, pk=title_id)
            if title.reviews.filter(author=request.user).exists():
                raise serializers.ValidationError(
                    'Не более одного отзыва на произведение'
                )
        return data

    class Meta:
        fields = ['id', 'title', 'text', 'author', 'score', 'pub_date']
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id'
    )

    class Meta:
        fields = ['id', 'review', 'text', 'author', 'pub_date']
        model = Comment
