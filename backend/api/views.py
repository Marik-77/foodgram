from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarDeleteSerializer,
    AvatarSerializer,
    FavoriteCreateSerializer,
    FavoriteDeleteSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    SetPasswordSerializer,
    ShoppingCartCreateSerializer,
    ShoppingCartDeleteSerializer,
    SubscriptionCreateSerializer,
    SubscriptionDeleteSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer,
)
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)
from users.models import User


class SerializerActionMixin:
    @staticmethod
    def _run_create(request, serializer_class, *, context):
        serializer = serializer_class(
            data=getattr(request, 'data', None) or {},
            context=context,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _run_update(
        request, serializer_class, instance, *, context, partial=False
    ):
        serializer = serializer_class(
            instance,
            data=request.data,
            context=context,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _run_delete(request, serializer_class, *, context):
        serializer = serializer_class(data={}, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(SerializerActionMixin, DjoserUserViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return UserSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=('put',),
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    def avatar(self, request):
        return self._run_update(
            request,
            AvatarSerializer,
            request.user,
            context={'request': request},
        )

    @avatar.mapping.delete
    def delete_avatar(self, request):
        return self._run_delete(
            request,
            AvatarDeleteSerializer,
            context={'request': request},
        )

    @action(
        detail=False,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
        url_path='set_password',
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        current = serializer.validated_data['current_password']
        if not user.check_password(current):
            return Response(
                {'current_password': ['Неверный пароль.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        authors = User.objects.filter(
            subscribers__user=request.user,
        ).distinct()
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            authors,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None, pk=None):
        author_id = id or pk
        author = get_object_or_404(User, id=author_id)
        return self._run_create(
            request,
            SubscriptionCreateSerializer,
            context={'request': request, 'author': author},
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None, pk=None):
        author_id = id or pk
        author = get_object_or_404(User, id=author_id)
        return self._run_delete(
            request,
            SubscriptionDeleteSerializer,
            context={'request': request, 'author': author},
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(SerializerActionMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.all().select_related('author').prefetch_related(
        'tags',
        'recipe_ingredients__ingredient',
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self._run_create(
            request,
            FavoriteCreateSerializer,
            context={'request': request, 'recipe': recipe},
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self._run_delete(
            request,
            FavoriteDeleteSerializer,
            context={'request': request, 'recipe': recipe},
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self._run_create(
            request,
            ShoppingCartCreateSerializer,
            context={'request': request, 'recipe': recipe},
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self._run_delete(
            request,
            ShoppingCartDeleteSerializer,
            context={'request': request, 'recipe': recipe},
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_carts__user=request.user,
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(total=Sum('amount'))
        )

        lines = ['Список покупок:']
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            total = item['total']
            lines.append(f'- {name} ({unit}) — {total}')
        content = '\n'.join(lines)
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=('get',),
        url_path='get-link',
        permission_classes=(AllowAny,),
    )
    def get_link(self, request, pk=None):
        link = f'{request.scheme}://{request.get_host()}/s/{pk}/'
        return Response(
            {'short-link': link},
            status=status.HTTP_200_OK,
        )
