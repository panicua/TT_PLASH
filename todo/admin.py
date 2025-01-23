from django.contrib import admin

from todo.models import Todo, TelegramUser

admin.site.register(Todo)
admin.site.register(TelegramUser)
