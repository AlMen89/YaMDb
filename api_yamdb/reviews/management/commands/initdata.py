import csv
import logging

from django.core.management import BaseCommand

from reviews.models import (
    User, Title, Category, Genre, GenreTitle, Review, Comment
)

logger = logging.getLogger(__name__)

CSV_FILES = [
    ['users.csv', User],
    ['category.csv', Category],
    ['genre.csv', Genre],
    ['titles.csv', Title],
    ['genre_title.csv', GenreTitle],
    ['review.csv', Review],
    ['comments.csv', Comment],
]


class Command(BaseCommand):
    help = 'import csv data into database'

    def handle(self, *args, **options):

        self.stdout.write(self.style.NOTICE('Очистка базы данных'))

        for _, model in reversed(CSV_FILES):
            model.objects.all().delete()

        self.stdout.write(self.style.NOTICE('Подготовка новых данных'))

        for file, model in CSV_FILES:
            with open('static/data/' + file, 'r', encoding='utf-8') as f:
                logger.info(f'Выполняется загрузка данных модели {model.__name__}, из файла {file}')
                reader = csv.DictReader(f)
                for dict_row in reader:
                    logger.info(f'Загрузка данных {dict_row} в модель {model.__name__}')
                    model.objects.get_or_create(**dict_row)

        self.stdout.write(self.style.SUCCESS('Новые данные внесены в базу'))