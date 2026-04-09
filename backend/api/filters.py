import django_filters
from django.db.models import QuerySet

from recipes.models import Ingredient, Recipe


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart',
    )
    author = django_filters.NumberFilter(field_name='author_id')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def _filter_user_relation(
        self,
        queryset: QuerySet,
        relation: str,
        value: int,
    ):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(**{f'{relation}__user': user})
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self._filter_user_relation(queryset, 'favorited_by', value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter_user_relation(queryset, 'in_shopping_carts', value)
