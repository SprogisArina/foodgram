from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (Cart, Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, Tag)

admin.site.empty_value_display = 'Не указано'


User = get_user_model()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    search_fields = ('author', 'name')
    list_filter = ('tags',)
    readonly_fields = ('favorites_count',)

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'followers', 'recipes_count')
    search_fields = ('username', 'email')

    @admin.display(description='Количество подписчиков')
    def followers(self, obj):
        return obj.followers.count()

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Cart, Favorite, Follow, IngredientRecipe)
class UniversalAdmin(admin.ModelAdmin):
    pass
