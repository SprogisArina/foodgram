from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, set_avatar

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('', include(router.urls)),
    path('users/me/avatar/', set_avatar),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
