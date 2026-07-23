import os
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
import shutil
from django.conf import settings

User = get_user_model()


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        result = []
        for user in users:
            # Подсчет файлов и их общего размера
            files = user.files.all()
            total_size = sum(f.size for f in files)
            result.append({
                'id'          : user.id,
                'username'    : user.username,
                'full_name'   : user.full_name,
                'email'       : user.email,
                'is_staff'    : user.is_staff,
                'file_count'  : files.count(),
                'total_size'  : total_size,
                'storage_path': f'storage/user_{user.id}/'
            })
        return Response(result)


class UserDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # Удаляем физическую папку пользователя
        user_path = os.path.join(settings.MEDIA_ROOT, f'storage/user_{user.id}')
        if os.path.exists(user_path):
            shutil.rmtree(user_path)

        user.delete()
        return Response({'message': 'Пользователь удален'})
