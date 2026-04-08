import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

# Минимальный валидный PNG 1×1 (серый пиксель)
MINI_PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)

# Имена как в data/ingredients.csv (после load_ingredients).
DEMO = (
    {
        'name': 'Демо: яичница',
        'text': 'Разогреть сковороду, разбить яйца, жарить до готовности.',
        'cooking_time': 15,
        'tag_slugs': ('breakfast',),
        'ingredients': (('яйца куриные', 2), ('молоко', 50)),
    },
    {
        'name': 'Демо: бутерброд',
        'text': 'Намазать хлеб маслом, положить сыр.',
        'cooking_time': 5,
        'tag_slugs': ('lunch',),
        'ingredients': (('хлеб', 2), ('сливочное масло', 20)),
    },
    {
        'name': 'Демо: салат',
        'text': 'Нарезать овощи, заправить маслом.',
        'cooking_time': 20,
        'tag_slugs': ('dinner',),
        'ingredients': (('помидоры', 200), ('огурцы', 150)),
    },
)


class Command(BaseCommand):
    help = 'Создать несколько демо-рецептов (нужны пользователь, теги и ингредиенты в БД).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default=None,
            help='Email автора; иначе первый суперпользователь или первый пользователь.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        email = options.get('email')
        if email:
            user = User.objects.filter(email=email).first()
            if not user:
                self.stderr.write(self.style.ERROR(f'Пользователь с email={email} не найден.'))
                return
        else:
            user = User.objects.filter(is_superuser=True).first() or User.objects.order_by('id').first()
            if not user:
                self.stderr.write(
                    self.style.ERROR('Нет пользователей. Зарегистрируйтесь на сайте или создайте суперпользователя.')
                )
                return

        created = 0
        for item in DEMO:
            if Recipe.objects.filter(name=item['name'], author=user).exists():
                self.stdout.write(f"Пропуск (уже есть): {item['name']}")
                continue
            tags = list(Tag.objects.filter(slug__in=item['tag_slugs']))
            if len(tags) != len(item['tag_slugs']):
                self.stderr.write(
                    self.style.WARNING(
                        f"Не все теги найдены для «{item['name']}». Выполните миграции и проверьте теги breakfast/lunch/dinner."
                    )
                )
                continue
            ings = []
            for exact_name, amount in item['ingredients']:
                ing = Ingredient.objects.filter(name=exact_name).first()
                if not ing:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Ингредиент «{exact_name}» не найден — пропуск рецепта «{item['name']}». "
                            'Выполните: python manage.py load_ingredients --path /data/ingredients.csv'
                        )
                    )
                    ings = None
                    break
                ings.append((ing, amount))
            if not ings:
                continue
            recipe = Recipe.objects.create(
                author=user,
                name=item['name'],
                text=item['text'],
                cooking_time=item['cooking_time'],
            )
            recipe.image.save('demo.png', ContentFile(MINI_PNG), save=True)
            recipe.tags.set(tags)
            for ing, amount in ings:
                RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, amount=amount)
            created += 1
            self.stdout.write(self.style.SUCCESS(f"Создан рецепт: {item['name']}"))
        self.stdout.write(self.style.SUCCESS(f'Готово. Новых рецептов: {created}.'))
