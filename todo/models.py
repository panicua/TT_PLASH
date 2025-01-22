from django.db import models


class Todo(models.Model):
    description = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.description[:20]

    class Meta:
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'


class TelegramUser(models.Model):
    telegram_id = models.PositiveIntegerField(unique=True)
    is_admin = models.BooleanField(default=False, null=True, blank=True)
    is_user = models.BooleanField(default=False, null=True, blank=True)
    group = models.CharField(max_length=100, null=True, blank=True)
