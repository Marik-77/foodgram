from django.db import migrations

# Теги по умолчанию (пустая БД после деплоя — без них форма рецепта бесполезна).
DEFAULT_TAGS = (
    ('Завтрак', 'breakfast'),
    ('Обед', 'lunch'),
    ('Ужин', 'dinner'),
)


def create_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    for name, slug in DEFAULT_TAGS:
        Tag.objects.get_or_create(slug=slug, defaults={'name': name})


def remove_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    for _, slug in DEFAULT_TAGS:
        Tag.objects.filter(slug=slug).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(create_tags, remove_tags),
    ]
