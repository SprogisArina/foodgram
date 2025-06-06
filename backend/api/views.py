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
    FollowSerializer, RecipeSerializer, TagSerializer
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


class FollowCreateDestroyApiView(
    generics.CreateAPIView, generics.DestroyAPIView
):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()

    def get_follow(self, following):
        return Follow.objects.filter(
            user=self.request.user, following=following
        )

    def create(self, request, *args, **kwargs):
        following = get_object_or_404(User, pk=self.kwargs.get('pk'))

        if following == request.user:
            raise ValidationError({'datail': 'Нельзя подписаться на себя'})
        elif self.get_follow(following).exists():
            raise ValidationError({'datail': 'Подписка уже существует'})

        Follow.objects.create(user=request.user, following=following)
        serializer = self.get_serializer(following)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_object(self):
        following = get_object_or_404(User, pk=self.kwargs.get('pk'))
        follow = self.get_follow(following)

        if not follow:
            raise ValidationError({'datail': 'Вы не были подписаны'})

        return follow


class FollowListAPIView(generics.ListAPIView):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return self.request.user.following.prefetch_related('recipes')
    


