from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
import re
from django.contrib.auth import logout

User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')

        # Валидация логина (латиница+цифры, 4-20 символов)
        if not re.match(r'^[A-Za-z][A-Za-z0-9]{3,19}$', username):
            return Response({
                'error': 'Логин: только латиница, от 4 до 20 символов, первый - буква'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Валидация email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return Response({
                'error': 'Неверный формат email'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Валидация пароля
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+]).{6,}$', password):
            return Response({
                'error': 'Пароль: минимум 6 символов, заглавная буква, цифра, спецсимвол'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Пользователь уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        return Response({'message': 'Регистрация успешна'},
                        status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Вход выполнен',
                'user'   : {
                    'id'       : user.id,
                    'username' : user.username,
                    'full_name': user.full_name,
                    'is_staff' : user.is_staff
                }
            })
        return Response({'error': 'Неверный логин или пароль'},
                        status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Выход выполнен'})
