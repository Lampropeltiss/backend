import os
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    full_name = models.CharField(max_length=150)
    storage_path = models.CharField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Генерируем уникальный путь для хранилища при создании пользователя
        if not self.storage_path:
            # Используем UUID для имени папки
            folder_uuid = uuid.uuid4().hex[:16]
            self.storage_path = f'{folder_uuid}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


def user_storage_path(instance, filename):
    """Генерирует уникальный путь для файла в хранилище пользователя"""
    # Берем путь хранилища пользователя
    user_folder = instance.user.storage_path

    # Генерируем уникальное имя для файла (оригинальное имя сохраняется в БД)
    name_uuid = uuid.uuid4().hex[:20]

    # Получаем расширение файла
    _, ext = os.path.splitext(filename)
    if ext:
        new_filename = f"{name_uuid}{ext}"
    else:
        new_filename = name_uuid

    return os.path.join(user_folder, new_filename)


class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=user_storage_path)
    original_name = models.CharField(max_length=255)
    size = models.BigIntegerField(default=0)
    comment = models.TextField(blank=True, default='')
    upload_date = models.DateTimeField(auto_now_add=True)
    last_download_date = models.DateTimeField(null=True, blank=True)
    download_link = models.CharField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return f"{self.original_name} ({self.size} bytes, user: {self.user.username})"
