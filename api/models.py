from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100,)
    last_name = models.CharField(max_length=100,)
    bio = models.TextField()
    confirmation_code = models.CharField(max_length=200)

    class UserRole(models.TextChoices):
        ADMIN = 'admin'
        MODERATOR = 'moderator'
        USER = 'user'

    role = models.CharField(
        max_length=100,
        choices=UserRole.choices,
        default=UserRole.USER,
    )

    def is_yamdb_admin(self):
        return self.role == self.UserRole.ADMIN

    def is_yamdb_moder(self):
        return self.role == self.UserRole.MODERATOR

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(default=0)
    description = models.TextField()
    category = models.ForeignKey(
        Category, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='titles', verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre, blank=True,
        related_name='titles',
        through='TitleGenres',
        verbose_name='Жанр'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id', ]


class Review(models.Model):
    text = models.TextField('отзыв')
    score = models.IntegerField(
        'рейтинг',
        validators=[MaxValueValidator(10), MinValueValidator(1)])
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField('комментарий')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class TitleGenres(models.Model):
    title = models.ForeignKey(
        Title,
        null=True,
        on_delete=models.SET_NULL
    )
    genre = models.ForeignKey(
        Genre,
        null=True,
        on_delete=models.SET_NULL
    )
