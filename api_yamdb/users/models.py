from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('юзер', 'user'),
    ('модератор', 'moderator'),
    ('админ', 'admin'),
)


class User(AbstractUser):
    role = models.CharField(max_length=9, choices=CHOICES, default='user')
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username

