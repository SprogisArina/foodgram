from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework import routers
from rest_framework.permissions import IsAuthenticated

from .views import (CartCreateDestroyApiView, FavoriteCreateDestroyApiView,
                    FollowCreateDestroyApiView, FollowListAPIView,
                    IngredientViewSet, RecipeViewSet, TagViewSet,
                    download_shopping_cart, set_avatar)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

users_urls = [
    path('me/', UserViewSet.as_view({'get': 'me'},
         permission_classes=[IsAuthenticated]),
         name='user-me'),
    path('me/avatar/', set_avatar, name='set_avatar'),
    path('subscriptions/', FollowListAPIView.as_view(),
         name='subscriptions'),
    path('<int:pk>/subscribe/',
         FollowCreateDestroyApiView.as_view(), name='subscribe'),
]

recipes_urls = [
    path('download_shopping_cart/', download_shopping_cart,
         name='download_shopping_cart'),
    path('<int:pk>/favorite/', FavoriteCreateDestroyApiView.as_view(),
         name='favorite'),
    path('<int:pk>/shopping_cart/', CartCreateDestroyApiView.as_view(),
         name='shopping_cart'),
]


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/', include(users_urls)),
    path('recipes/', include(recipes_urls)),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
