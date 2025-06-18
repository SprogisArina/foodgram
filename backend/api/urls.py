from django.urls import include, path
from rest_framework import routers
from rest_framework.permissions import IsAuthenticated

from .views import (IngredientViewSet, ProjectUserViewSet,
                    RecipeViewSet, TagViewSet)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', ProjectUserViewSet, basename='users')

users_urls = [
    path('me/', ProjectUserViewSet.as_view({'get': 'me'},
         permission_classes=[IsAuthenticated]),
         name='user-me'),
]


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/', include(users_urls)),
    path('', include(router.urls))
]
