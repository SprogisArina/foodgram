import json

from django.core.management.base import BaseCommand

from api.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients data'

    def handle(self, *args, **options):
        with open('data/ingredients.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            infredients = [
                Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )for item in data
            ]
            Ingredient.objects.bulk_create(infredients)
        self.stdout.write('Данные успешно загружены!')
