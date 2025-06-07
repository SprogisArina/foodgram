from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    CartCreateDestroyApiView,
    FavoriteCreateDestroyApiView,
    FollowCreateDestroyApiView,
    FollowListAPIView,
    RecipeViewSet,
    TagViewSet,
    download_shopping_cart,
    set_avatar
)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', set_avatar, name='set_avatar'),
    path('users/subscriptions/', FollowListAPIView.as_view(),
         name='subscriptions'),
    path('users/<int:pk>/subscribe/',
         FollowCreateDestroyApiView.as_view(), name='subscribe'),
    path('recipes/download_shopping_cart/', download_shopping_cart,
         name='download_shopping_cart'),
    path('recipes/<int:pk>/favorite/', FavoriteCreateDestroyApiView.as_view(),
         name='favorite'),
    path('recipes/<int:pk>/shopping_cart/', CartCreateDestroyApiView.as_view(),
         name='shopping_cart'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
