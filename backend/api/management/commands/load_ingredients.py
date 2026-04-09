import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from CSV'

    def add_arguments(self, parser):
        parser.add_argument('--path', default='../data/ingredients.csv')

    def handle(self, *args, **options):
        path = options['path']
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 2:
                    continue
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
        self.stdout.write(self.style.SUCCESS('Ingredients loaded.'))
