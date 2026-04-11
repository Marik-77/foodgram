from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj,
        ).exists()

    def get_avatar(self, obj):
        request = self.context.get('request')
        if not obj.avatar:
            return None
        url = obj.avatar.url
        return request.build_absolute_uri(url) if request else url


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def to_representation(self, instance):
        request = self.context.get('request')
        if not instance.avatar:
            return {'avatar': None}
        url = instance.avatar.url
        return {
            'avatar': request.build_absolute_uri(url) if request else url,
        }


class AvatarDeleteSerializer(serializers.Serializer):
    def create(self, validated_data):
        user = self.context['request'].user
        user.avatar.delete(save=True)
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        if not obj.image:
            return None
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def _user_has_relation(self, obj, model):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return model.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    def get_is_favorited(self, obj):
        return self._user_has_relation(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._user_has_relation(obj, ShoppingCart)

    def get_image(self, obj):
        request = self.context.get('request')
        if not obj.image:
            return None
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientInRecipeWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        tags = attrs.get('tags')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': ['Обязательное поле.']},
            )
        if not tags:
            raise serializers.ValidationError(
                {'tags': ['Обязательное поле.']},
            )

        ingredient_ids = [item['id'] for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': ['Ингредиенты не должны повторяться.']},
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': ['Теги не должны повторяться.']},
            )
        return attrs

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=item['id']),
                amount=item['amount'],
            )
            for item in ingredients_data
        ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data,
        )
        recipe.tags.set(tags)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._save_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class FavoriteCreateSerializer(serializers.Serializer):
    def validate(self, attrs):
        recipe = self.context['recipe']
        user = self.context['request'].user
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен.'},
            )
        return attrs

    def create(self, validated_data):
        return Favorite.objects.create(
            user=self.context['request'].user,
            recipe=self.context['recipe'],
        )

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context,
        ).data


class FavoriteDeleteSerializer(serializers.Serializer):
    def validate(self, attrs):
        recipe = self.context['recipe']
        user = self.context['request'].user
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт не найден в списке.'},
            )
        return attrs

    def create(self, validated_data):
        Favorite.objects.filter(
            user=self.context['request'].user,
            recipe=self.context['recipe'],
        ).delete()
        return None


class ShoppingCartCreateSerializer(serializers.Serializer):
    def validate(self, attrs):
        recipe = self.context['recipe']
        user = self.context['request'].user
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен.'},
            )
        return attrs

    def create(self, validated_data):
        return ShoppingCart.objects.create(
            user=self.context['request'].user,
            recipe=self.context['recipe'],
        )

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context,
        ).data


class ShoppingCartDeleteSerializer(serializers.Serializer):
    def validate(self, attrs):
        recipe = self.context['recipe']
        user = self.context['request'].user
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт не найден в списке.'},
            )
        return attrs

    def create(self, validated_data):
        ShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=self.context['recipe'],
        ).delete()
        return None


class SubscriptionCreateSerializer(serializers.Serializer):
    def validate(self, attrs):
        author = self.context['author']
        user = self.context['request'].user
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя.'},
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                {'errors': 'Подписка уже существует.'},
            )
        return attrs

    def create(self, validated_data):
        return Subscription.objects.create(
            user=self.context['request'].user,
            author=self.context['author'],
        )

    def to_representation(self, instance):
        return SubscriptionSerializer(
            self.context['author'],
            context=self.context,
        ).data


class SubscriptionDeleteSerializer(serializers.Serializer):
    def validate(self, attrs):
        author = self.context['author']
        user = self.context['request'].user
        if not Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                {'errors': 'Подписка не найдена.'},
            )
        return attrs

    def create(self, validated_data):
        Subscription.objects.filter(
            user=self.context['request'].user,
            author=self.context['author'],
        ).delete()
        return None


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None
        recipes = obj.recipes.all()
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeMinifiedSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value
