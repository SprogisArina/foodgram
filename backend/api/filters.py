from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Recipe, Tag


class NameSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=True
    )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_base(self, queryset, name, value, related_name):
        user = self.request.user

        if value == 1 and user.is_authenticated:
            return queryset.filter(**{f'{related_name}__user': user})

        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self.filter_base(
            queryset, name, value, related_name='favorites'
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.filter_base(queryset, name, value, related_name='cart')
