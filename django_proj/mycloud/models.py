from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    full_name = models.CharField(max_length=150)
    # storage_path = models.CharField(max_length=255, unique=True)
    # # Из коробки:
    # username = models.CharField(max_length=150, unique=True)  # Логин
    # password = models.CharField(max_length=128)  # Хеш пароля
    # email = models.EmailField(blank=True)  # Email
    # is_staff = models.BooleanField(default=False)  # Может входить в админку
    # ---
    # last_login = models.DateTimeField(null=True, blank=True)  # Время последнего входа
    # is_active = models.BooleanField(default=True)  # Активен ли пользователь

    def __str__(self):
        return self.username

def user_storage_path(instance, filename):
    return f'storage/user_{instance.user.id}/{filename}'

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
        return f"{self.original_name} ({self.size} bytes, by {self.user.id})"