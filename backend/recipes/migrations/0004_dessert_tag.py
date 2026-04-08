from django.db import migrations


def add_dessert(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    Tag.objects.get_or_create(slug='dessert', defaults={'name': 'Десерт'})


def remove_dessert(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    Tag.objects.filter(slug='dessert').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_default_tags'),
    ]

    operations = [
        migrations.RunPython(add_dessert, remove_dessert),
    ]
