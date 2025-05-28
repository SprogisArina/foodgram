from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, Tag


admin.site.empty_value_display = 'Не указано'


User = get_user_model()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    search_fields = ('author', 'name')
    list_filter = ('tags',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User, UserAdmin)
