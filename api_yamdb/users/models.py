from random import randint

from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('user', 'пользователь'),
    ('moderator', 'модератор'),
    ('admin', 'администратор'),
)


def max_length_value(choice_tuple):
    max_value = 0
    for choice in choice_tuple:
        if len(choice[0]) > max_value:
            max_value = len(choice[0])
    return max_value


class User(AbstractUser):  # переопределены email, first_name и password
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=max_length_value(ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default='user'
    )
    confirmation_code = models.CharField(max_length=6)
    password = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def get_confirmation_code(self):
        """Генерирует код для подтверждения учетных данных пользователя."""
        return randint(100000, 999999)

    @property
    def admin_access(self):
        """Проверяет наличие прав админа/суперпользователя."""
        return (
            self.is_authenticated and (
                self.role == ROLE_CHOICES[2][0]
                or self.is_superuser
                or self.is_staff
            )
        )

    @property
    def moderator_access(self):
        """Проверяет наличие прав модератора."""
        return (
            self.is_authenticated
            and self.role == ROLE_CHOICES[1][0]
        )
