# management/commands/create_test_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users'

    def handle(self, *args, **options):
        users_data = [
            {
                'username' : 'admin1',
                'password' : 'admin123',
                'email'    : 'admin1@example.com',
                'full_name': 'Admin One',
                'is_staff' : True,
            },
            {
                'username' : 'admin2',
                'password' : 'admin456',
                'email'    : 'admin2@example.com',
                'full_name': 'Admin Two',
                'is_staff' : True,
            },
            {
                'username' : 'user1',
                'password' : 'user123',
                'email'    : 'user1@example.com',
                'full_name': 'Regular User One',
                'is_staff' : False,
            },
            {
                'username' : 'user2',
                'password' : 'user456',
                'email'    : 'user2@example.com',
                'full_name': 'Regular User Two',
                'is_staff' : False,
            }
        ]

        for user_data in users_data:
            # Проверяем, существует ли пользователь
            username = user_data['username']
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f"⚠️ Пользователь {username} уже существует, пропускаем...")
                )
                continue

            # Хэшируем пароль перед созданием
            user_data['password'] = make_password(user_data['password'])

            # Создаем пользователя - storage_path заполнится автоматически в save()
            user = User.objects.create(**user_data)

            self.stdout.write(
                self.style.SUCCESS(f"✅ Создан пользователь: {user.username} (storage: {user.storage_path})")
            )

        self.stdout.write(self.style.SUCCESS('✓ Все тестовые пользователи загружены.'))
