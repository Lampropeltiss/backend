from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
import re
from django.contrib.auth import logout

from ..log_config import logger

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')

        logger.info(f"Попытка регистрации пользователя: {username}")

        # Валидация логина (латиница+цифры, 4-20 символов)
        if not re.match(r'^[A-Za-z][A-Za-z0-9]{3,19}$', username):
            logger.debug_log(f"Ошибка валидации логина: {username}")
            return Response({
                'error': 'Логин: только латиница, от 4 до 20 символов, первый - буква'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Валидация email
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            logger.debug_log(f"Ошибка валидации email: {email}")
            return Response({
                'error': 'Неверный формат email'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Валидация пароля
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=\[\]{};\':"\\|,.<>\/?`~-]).{6,}$', password):
            logger.debug_log(f"Ошибка валидации пароля для {username}")
            return Response({
                'error': 'Пароль: минимум 6 символов, заглавная буква, цифра, спецсимвол'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            logger.warning(f"Попытка регистрации существующего пользователя: {username}")
            return Response({'error': 'Пользователь уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )

        logger.bot(f"✅ Успешно зарегистрирован пользователь: {username} (ID: {user.id})")
        return Response({'message': 'Регистрация успешна'},
                        status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            logger.bot(f"✅ Успешный вход: {username} (ID: {user.id})")
            return Response({
                'message': 'Вход выполнен',
                'user'   : {
                    'id'       : user.id,
                    'username' : user.username,
                    'full_name': user.full_name,
                    'is_staff' : user.is_staff
                }
            })

        logger.warning(f"❌ Неудачная попытка входа: {username}")
        return Response({'error': 'Неверный логин или пароль'},
                        status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        username = request.user.username if request.user.is_authenticated else 'anonymous'
        logout(request)
        logger.bot(f"🚪 Выход пользователя: {username}")
        return Response({'message': 'Выход выполнен'})
