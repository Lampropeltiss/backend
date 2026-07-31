import uuid
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from mycloud.models import UserFile

from ..RainbowLogger import run_rainbow
import logging

from config import settings

logger = run_rainbow(logging.DEBUG)

User = get_user_model()


class FileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        username = request.user.username

        logger.info(f"Запрос списка файлов от {username}" +
                    (f" для user_id={user_id}" if user_id else ""))

        if request.user.is_staff and user_id:
            user = get_object_or_404(User, id=user_id)
            logger.debug_log(f"Админ {username} просматривает файлы пользователя {user.username}")
        else:
            user = request.user
            logger.debug_log(f"Пользователь {username} просматривает свои файлы")

        files = UserFile.objects.filter(user=user).order_by('id')
        result = [{
            'id'                : f.id,
            'original_name'     : f.original_name,
            'size'              : f.size,
            'upload_date'       : f.upload_date.isoformat(),
            'last_download_date': f.last_download_date.isoformat() if f.last_download_date else None,
            'comment'           : f.comment,
            'download_link'     : f.download_link,
        } for f in files]

        logger.db(f"📁 Найдено {len(result)} файлов для {user.username}")

        return Response(result)


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        target_user_id = request.data.get('target', '')
        comment = request.data.get('comment', '')
        username = request.user.username

        if request.user.is_staff and target_user_id:
            target_user = get_object_or_404(User, id=target_user_id)
        else:
            target_user = request.user

        logger.info(f"Попытка загрузки файла от {username}")

        if not uploaded_file:
            logger.warning(f"Ошибка: файл не выбран для {username}")
            return Response({'error': 'Файл не выбран'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Создаем запись в БД
        file_obj = UserFile(
            user=target_user,
            original_name=uploaded_file.name,
            size=uploaded_file.size,
            comment=comment,
            file=uploaded_file
        )
        file_obj.save()

        # Генерируем специальную ссылку
        link_token = uuid.uuid4().hex[:20]
        file_obj.download_link = f'{settings.BASE_URL}/share/{link_token}'
        file_obj.save()

        logger.bot(
            f"✅ Файл загружен: {uploaded_file.name} ({uploaded_file.size} байт) пользователем {username}, ID файла: {file_obj.id}")
        logger.db(f"📎 Ссылка для скачивания: {file_obj.download_link}")

        return Response({
            'message'      : 'Файл загружен',
            'file_id'      : file_obj.id,
            'download_link': file_obj.download_link
        }, status=status.HTTP_201_CREATED)


class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        file_obj = get_object_or_404(UserFile, id=file_id)
        username = request.user.username

        logger.info(f"Скачивание файла ID {file_id} пользователем {username}")

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            logger.warning(
                f"❌ Отказ в доступе: {username} пытается скачать файл {file_obj.id} пользователя {file_obj.user.username}")
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        # Обновляем дату скачивания
        file_obj.last_download_date = timezone.now()
        file_obj.save()

        logger.bot(f"📥 Файл скачан: {file_obj.original_name} пользователем {username}")

        return FileResponse(
            file_obj.file.open('rb'),
            as_attachment=True,
            filename=file_obj.original_name
        )


class SharedFileDownloadView(APIView):
    def get(self, request, token):
        logger.info(f"Попытка скачивания по общей ссылке: {token}")

        file_obj = get_object_or_404(UserFile, download_link=f'{settings.BASE_URL}/share/{token}')

        # Обновляем дату скачивания
        file_obj.last_download_date = timezone.now()
        file_obj.save()

        logger.bot(f"📥 Файл скачан по общей ссылке: {file_obj.original_name}")

        return FileResponse(
            file_obj.file.open('rb'),
            as_attachment=True,
            filename=file_obj.original_name
        )


class FileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        file_obj = get_object_or_404(UserFile, id=file_id)
        username = request.user.username

        logger.info(f"Попытка удаления файла ID {file_id} пользователем {username}")

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            logger.warning(
                f"❌ Отказ в доступе: {username} пытается удалить файл {file_obj.id} пользователя {file_obj.user.username}")
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        # Удаляем физический файл
        if file_obj.file:
            file_obj.file.delete(save=False)

        logger.bot(f"🗑️ Файл удален: {file_obj.original_name} (ID: {file_obj.id}) пользователем {username}")
        file_obj.delete()

        return Response({'message': 'Файл удален'})


class FileRenameView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        new_name = request.data.get('new_name')
        username = request.user.username

        logger.info(f"Попытка переименования файла ID {file_id} пользователем {username}")

        if not new_name:
            logger.warning(f"Ошибка: не указано новое имя для файла {file_id}")
            return Response({'error': 'Не указано новое имя'},
                            status=status.HTTP_400_BAD_REQUEST)

        file_obj = get_object_or_404(UserFile, id=file_id)

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            logger.warning(
                f"❌ Отказ в доступе: {username} пытается переименовать файл {file_obj.id} пользователя {file_obj.user.username}")
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        old_name = file_obj.original_name
        file_obj.original_name = new_name
        file_obj.save()

        logger.bot(f"✏️ Файл переименован: '{old_name}' → '{new_name}' пользователем {username}")

        return Response({'message': 'Файл переименован', 'new_name': new_name})


class FileCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        comment = request.data.get('comment', '')
        username = request.user.username

        logger.info(f"Обновление комментария к файлу ID {file_id} пользователем {username}")

        file_obj = get_object_or_404(UserFile, id=file_id)

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            logger.warning(
                f"❌ Отказ в доступе: {username} пытается изменить комментарий к файлу {file_obj.id} пользователя {file_obj.user.username}")
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        file_obj.comment = comment
        file_obj.save()

        logger.debug_log(f"Комментарий к файлу {file_obj.original_name} обновлен: '{comment}'")

        return Response({'message': 'Комментарий обновлен'})


class FileGenerateLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        file_obj = get_object_or_404(UserFile, id=file_id)
        username = request.user.username

        logger.info(f"Генерация новой ссылки для файла ID {file_id} пользователем {username}")

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            logger.warning(
                f"❌ Отказ в доступе: {username} пытается сгенерировать ссылку для файла {file_obj.id} пользователя {file_obj.user.username}")
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        new_token = uuid.uuid4().hex[:20]
        old_link = file_obj.download_link
        file_obj.download_link = f'{settings.BASE_URL}/share/{new_token}'
        file_obj.save()

        logger.bot(f"🔗 Ссылка обновлена для {file_obj.original_name}: {old_link} → {file_obj.download_link}")

        return Response({
            'message'      : 'Ссылка обновлена',
            'download_link': file_obj.download_link
        })
