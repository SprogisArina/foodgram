import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import (
    Cart, Favorite, Follow, Ingredient, IngredientRecipe, Recipe, Tag,
    TagRecipe
)


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        following = Follow.objects.filter(
            user=user, following=obj.pk
        )
        return following.exists()

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        return instance


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'id', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context['request'].user,
            recipe=obj.pk
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return Cart.objects.filter(
            user=self.context['request'].user,
            recipe=obj.pk
        ).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(
                tag=tag, recipe=recipe
            )
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient['ingredient'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'name', instance.cooking_time
        )
        fields = {
            'tags': instance.tags,
            'ingredients': instance.ingredients
        }
        for field, instance_field in fields.items():
            new_values = validated_data.pop(field)
            instance_field.clear()
            for value in new_values:
                instance_field.add(value)
        instance.save()
        return instance


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('recipes', 'recipes_count')
        read_only_fields = ('recipes', 'recipes_count')

    def validate_following(self, value):
        if value == self.context['request'].user.id:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        return value


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('user', 'recipe')
