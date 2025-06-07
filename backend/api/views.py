from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .models import (
    Cart, Favorite, Follow, Ingredient, Recipe, Tag
)
from .serializers import (
    AvatarSerializer, IngredientSerializer,
    FollowSerializer, RecipeSerializer, ShortRecipeSerializer, TagSerializer
)


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@api_view(http_method_names=['PUT', 'DELETE'])
def set_avatar(request):
    user = request.user
    if request.method == 'PUT':
        serializer = AvatarSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'avatar': ["Обязательное поле."]},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.avatar = None
    user.save()
    return Response(
        {'message': 'Аватар успешно удалён'},
        status=status.HTTP_204_NO_CONTENT
    )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(f'/api/recipes/{pk}/')
        return Response(
            {'short-link': short_link}, status=status.HTTP_200_OK
        )


class FollowListAPIView(generics.ListAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return User.objects.filter(
            followers__user=self.request.user
        ).prefetch_related('recipes')


class BasicCreateDestroyApiView(
    generics.CreateAPIView, generics.DestroyAPIView
):
    """Базовый класс для создания и удаления связей."""

    def get_related_object(self):
        return get_object_or_404(self.related_model, pk=self.kwargs.get('pk'))

    def get_relation(self, related_obj):
        return self.relation_model.objects.filter(
            user=self.request.user, **{self.relation_field: related_obj}
        )

    def create(self, request, *args, **kwargs):
        related_object = self.get_related_object()

        # Проверка только для Follow
        if hasattr(self, 'check_self_following'):
            self.check_self_following(related_object)

        if self.get_relation(related_object).exists():
            raise ValidationError({'detail': self.exist_message})

        self.relation_model.objects.create(
            user=self.request.user, **{self.relation_field: related_object}
        )

        serializer = self.get_serializer(related_object)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_object(self):
        related_object = self.get_related_object()
        relation = self.get_relation(related_object)

        if not relation:
            raise ValidationError({'detail': self.not_exist_message})

        return relation


class FollowCreateDestroyApiView(BasicCreateDestroyApiView):
    related_model = User
    serializer_class = FollowSerializer
    relation_model = Follow
    relation_field = 'following'
    exist_message = 'Подписка уже существует'
    not_exist_message = 'Вы не были подписаны'

    def check_self_following(self, related_obj):
        if related_obj == self.request.user:
            raise ValidationError({'detail': 'Нельзя подписаться на себя'})


class FavoriteCreateDestroyApiView(BasicCreateDestroyApiView):
    related_model = Recipe
    serializer_class = ShortRecipeSerializer
    relation_model = Favorite
    relation_field = 'recipe'
    exist_message = 'Рецепт уже в избранном'
    not_exist_message = 'Рецепта не было в избранном'


class CartCreateDestroyApiView(BasicCreateDestroyApiView):
    related_model = Recipe
    serializer_class = ShortRecipeSerializer
    relation_model = Cart
    relation_field = 'recipe'
    exist_message = 'Рецепт уже в корзине'
    not_exist_message = 'Рецепта не было в корзине'


# class CartCreateDestroyApiView(
#     generics.CreateAPIView, generics.DestroyAPIView
# ):
#     serializer_class = ShortRecipeSerializer

#     def create(self, request, *args, **kwargs):
#         recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])

#         if Cart.objects.filter(user=request.user, recipe=recipe).exists():
#             raise ValidationError({'detail': 'Рецепт уже в корзине'})

#         Cart.objects.create(user=request.user, recipe=recipe)
#         serialiser = self.get_serializer(recipe)
#         return Response(
#             serialiser.data, status=status.HTTP_201_CREATED
#         )

#     def get_object(self):
#         recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
#         in_cart = Cart.objects.filter(
#             user=self.request.user, recipe=recipe
#         )
#         if not in_cart:
#             raise ValidationError({'detail': 'Рецепта не было корзине'})

#         return in_cart
