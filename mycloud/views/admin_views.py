import os
import shutil

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..log_config import logger
from config import settings

User = get_user_model()


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        admin_user = request.user.username
        logger.info(f"Админ {admin_user} запрашивает список пользователей")

        users = User.objects.all().order_by('id')
        result = []
        for user in users:
            files = user.files.all()
            total_size = sum(f.size for f in files)
            result.append({
                'id'        : user.id,
                'username'  : user.username,
                'full_name' : user.full_name,
                'email'     : user.email,
                'is_staff'  : user.is_staff,
                'file_count': files.count(),
                'total_size': total_size,
            })

        logger.db(f"📋 Найдено {len(result)} пользователей")
        return Response(result)


class UserDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        admin_user = request.user.username
        logger.info(f"Админ {admin_user} пытается удалить пользователя ID {user_id}")

        user = get_object_or_404(User, id=user_id)
        username = user.username

        # Удаляем физическую папку пользователя
        user_path = os.path.join(settings.MEDIA_ROOT, f'storage/user_{user.id}')
        if os.path.exists(user_path):
            shutil.rmtree(user_path)
            logger.debug_log(f"🗑️ Удалена папка пользователя: {user_path}")

        user.delete()

        logger.bot(f"👤 Пользователь удален: {username} (ID: {user_id}) админом {admin_user}")

        return Response({'message': 'Пользователь удален'})


class UserToggleAdminStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        admin_user = request.user.username
        logger.info(f"Админ {admin_user} пытается переключить статус админа у пользователя ID {user_id}")

        user = get_object_or_404(User, id=user_id)

        # Не позволяем админу отключать самого себя — защита от случайной потери прав
        if user.id == request.user.id:
            logger.warning(f"Админ {admin_user} попытался изменить свой собственный статус админа")
            return Response(
                {'error': 'Нельзя менять статус админа для самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = user.is_staff
        new_status = not old_status

        user.is_staff = new_status
        user.save(update_fields=['is_staff'])

        status_text = 'стал админом' if new_status else 'больше не админ'
        logger.bot(
            f"🔐 Пользователь {user.username} (ID: {user.id}) {status_text} — действие админа {admin_user}"
        )

        return Response({
            'message' : f'Статус админа изменён: {"админ" if new_status else "не админ"}',
            'user_id' : user.id,
            'username': user.username,
            'is_admin': new_status,
        })
