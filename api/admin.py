from django.contrib import admin

from .models import Category, Comment, CustomUser, Genre, Review, Title


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'confirmation_code')
    search_fields = ('username', 'email')
    list_filter = ('username',)
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'author', 'pub_date', 'text')
    search_fields = ('title', 'author', 'text')
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review', 'author', 'pub_date', 'text')
    search_fields = ('review', 'author', 'text')
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
