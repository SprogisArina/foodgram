import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .constants import MAX_COOKING_TIME
from .models import (Cart, Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, Tag)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        following = Follow.objects.filter(
            user=user, following=obj.pk
        )
        return following.exists()


class ProjectUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name', 'slug')


class InputIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = InputIngredientSerializer(
        many=True, write_only=True, allow_empty=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True,
        allow_empty=False
    )
    cooking_time = serializers.IntegerField(
        min_value=1, max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date',)
        read_only_fields = ('author',)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        tags = attrs.get('tags', [])

        if not tags:
            raise serializers.ValidationError('Укажите теги')

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Дубликаты тегов не допускаются')

        ingredients = attrs.get('ingredients', [])

        if not ingredients:
            raise serializers.ValidationError('Укажите ингредиенты')

        ids = [ingr['id'] for ingr in ingredients]

        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Дубликаты ингредиентов не допускаются'
            )

        for ingr in ingredients:
            if ingr['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть отрицательным'
                )

        return attrs

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def create_ingredient_recipe(self, recipe, ingredients_data):
        return IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                ingredient=ingredient_data['id'],
                recipe=recipe,
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data
        ])

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient_recipe(
            recipe, ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        ingredients_data = validated_data.pop('ingredients')
        instance.ingredientrecipe_set.all().delete()
        self.create_ingredient_recipe(
            instance, ingredients_data
        )
        instance.save()
        return super().update(instance, validated_data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredientrecipe_set'
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)
        read_only_fields = ('image', 'author', 'tags')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.cart.filter(user=user).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time')
        read_only_fields = ('id', 'image', 'name', 'cooking_time')


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'avatar',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = fields

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')

        try:
            recipes_limit = int(recipes_limit)
        except (ValueError, TypeError):
            recipes_limit = None

        if recipes_limit is not None and recipes_limit >= 0:
            recipes = recipes[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True).data


class FollowCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields: list[str] = []

    def validate(self, attrs):
        user = self.context['user']
        following = self.context['following']

        if user == following:
            raise serializers.ValidationError(
                {'detail': 'Нельзя подписаться на себя'}
            )

        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError(
                {'detail': 'Подписка уже существует'}
            )

        attrs['user'] = user
        attrs['following'] = following
        return attrs

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)

    def to_representation(self, instance):
        return FollowSerializer(instance.following, context=self.context).data


class RelationMixin:
    message = ''

    def validate(self, attrs):
        user = self.context['user']
        recipe = self.context['recipe']

        if self.relation_model.objects.filter(
            user=user, recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                {'detail': f'Рецепт уже в {self.message}'}
            )

        attrs['user'] = user
        attrs['recipe'] = recipe
        return attrs

    def create(self, validated_data):
        return self.relation_model.objects.create(**validated_data)

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class CartSerializer(RelationMixin, serializers.ModelSerializer):
    relation_model = Cart
    message = 'корзине'

    class Meta:
        model = Cart
        fields: list[str] = []


class FavoriteSerializer(RelationMixin, serializers.ModelSerializer):
    relation_model = Favorite
    message = 'избранном'

    class Meta:
        model = Favorite
        fields: list[str] = []
