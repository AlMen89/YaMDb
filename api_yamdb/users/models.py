from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('user', 'пользователь'),
    ('moderator', 'модератор'),
    ('admin', 'администратор'),
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=13, choices=CHOICES, default='user')
    bio = models.TextField(blank=True)
    confirmation_code = models.CharField(max_length=8)
    password = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.username
