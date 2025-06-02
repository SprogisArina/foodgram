from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import (
    Cart, Favorite, Follow, Ingredient, Recipe, Tag
)
from .serializers import (
    AvatarSerializer, IngredientSerializer, RecipeSerializer, TagSerializer
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
        recipe = Recipe.objects.filter(pk=self.kwargs.get('pk'))
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)
