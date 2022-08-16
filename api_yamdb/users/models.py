from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('user', 'пользователь'),
    ('moderator', 'модератор'),
    ('admin', 'администратор'),
)


class User(AbstractUser):  # переопределены email, first_name и password
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=13, choices=ROLE_CHOICES, default='user'
    )
    confirmation_code = models.CharField(max_length=8)
    password = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.username
