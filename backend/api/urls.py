from django.urls import include, path
from rest_framework import routers

from .views import (
    IngredientViewSet,
    FollowCreateDestroyApiView,
    FollowListAPIView,
    RecipeViewSet,
    TagViewSet,
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
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
