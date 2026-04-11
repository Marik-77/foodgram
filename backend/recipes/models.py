from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    RECIPE_NAME_MAX_LENGTH,
    TAG_MAX_LENGTH,
)
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=TAG_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        'Slug',
        max_length=TAG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Ед. измерения',
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_name_unit',
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(Tag, related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
    )
    name = models.CharField(
        'Название',
        max_length=RECIPE_NAME_MAX_LENGTH,
    )
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(MIN_COOKING_TIME)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite',
            ),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_carts',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart',
            ),
        ]
