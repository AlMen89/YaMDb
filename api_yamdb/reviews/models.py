from django.db import models


class Category(models.Model):
    name = models.CharField("Название категории", max_length=256)
    slug = models.SlugField(
        "Название категории для url",
        unique=True,
        max_length=50
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField("Название жанра", max_length=100)
    slug = models.SlugField("Название жанра для url", unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField("Название произведения", max_length=200)
    year = models.IntegerField("Год выпуска")
    description = models.CharField("Описание", max_length=256)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='category',
        verbose_name="Категория",
        help_text="Категория, к которой относится произведение",
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self):
        return self.name
