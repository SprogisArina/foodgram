import os
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import NameSearchFilter, RecipeFilter
from .models import (Cart, Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, Tag)
from .permissions import AuthorOrAdminPermission
from .serializers import (AvatarSerializer, FollowSerializer,
                          FollowCreateSerializer, IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          TagSerializer)

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (NameSearchFilter,)
    pagination_class = None
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrAdminPermission, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(f'/recipes/{pk}/')
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        url_path='download_shopping_cart',
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        font_path = os.path.join(settings.BASE_DIR, 'fonts', 'arial.ttf')
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont('Arial', 14)
        p.drawString(100, 780, 'Список покупок:')

        cart = request.user.cart.select_related('recipe').all()
        ingredients = IngredientRecipe.objects.filter(
            recipe__in=[item.recipe for item in cart]
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum_amount=Sum('amount'))

        y_position = 740
        for ingr in ingredients:
            text = (
                f"- {ingr['ingredient__name']}: "
                f"{ingr['sum_amount']} {ingr['ingredient__measurement_unit']}"
            )
            p.drawString(100, y_position, text)
            y_position -= 20

        p.showPage()
        p.save()
        buffer.seek(0)
        response = FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_list.pdf',
            content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )
        return response

    def create_delete_relation(self, request, pk, model, message):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'detail': f'Рецепт уже в {message}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        deleted = model.objects.filter(
            user=request.user, recipe=recipe
        ).delete()[0]

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': f'Рецепта не было в {message}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        url_path='shopping_cart',
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self.create_delete_relation(request, pk, Cart, 'корзине')

    @action(
        detail=True,
        url_path='favorite',
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self.create_delete_relation(request, pk, Favorite, 'избранном')


class ProjectUserViewSet(UserViewSet):
    lookup_field = 'pk'

    @action(
        detail=False,
        url_path='me/avatar',
        methods=['PUT', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def set_avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user, data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {'avatar': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.avatar:
            user.avatar.delete()
            user.save()
            return Response(
                {'message': 'Аватар успешно удалён'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'message': 'Аватара нет'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        url_path='subscriptions',
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            followers__user=request.user
        ).prefetch_related('recipes').annotate(recipes_count=Count('recipes'))
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        url_path='subscribe',
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user
        following = get_object_or_404(
            User.objects.annotate(recipes_count=Count('recipes')), pk=pk
        )

        if request.method == 'POST':
            validator = FollowCreateSerializer(
                data={},
                context={'user': user, 'following': following}
            )
            validator.is_valid(raise_exception=True)
            serializer = FollowSerializer(
                following, context={'request': request}
            )
            Follow.objects.create(user=user, following=following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted = Follow.objects.filter(
            user=user, following=following
        ).delete()[0]

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Вы не были подписаны'},
            status=status.HTTP_400_BAD_REQUEST
        )
