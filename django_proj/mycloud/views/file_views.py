from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from mycloud.models import UserFile

User = get_user_model()


class FileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Админ может указать user_id, обычный пользователь - только свои
        user_id = request.query_params.get('user_id')

        if request.user.is_staff and user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user

        files = UserFile.objects.filter(user=user)
        result = [{
            'id'                : f.id,
            'original_name'     : f.original_name,
            'size'              : f.size,
            'upload_date'       : f.upload_date.isoformat(),
            'last_download_date': f.last_download_date.isoformat() if f.last_download_date else None,
            'comment'           : f.comment,
            'download_link'     : f.download_link,
            'file_url'          : f.file.url if f.file else None
        } for f in files]

        return Response(result)


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        comment = request.data.get('comment', '')

        if not uploaded_file:
            return Response({'error': 'Файл не выбран'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Создаем запись в БД
        file_obj = UserFile(
            user=request.user,
            original_name=uploaded_file.name,
            size=uploaded_file.size,
            comment=comment,
            file=uploaded_file  # Django сам сохранит по пути из upload_to
        )
        file_obj.save()

        # Генерируем специальную ссылку
        import uuid
        link_token = uuid.uuid4().hex[:20]
        file_obj.download_link = f'share/{link_token}'
        file_obj.save()

        return Response({
            'message'      : 'Файл загружен',
            'file_id'      : file_obj.id,
            'download_link': file_obj.download_link
        }, status=status.HTTP_201_CREATED)


class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, file_id):
        file_obj = get_object_or_404(UserFile, id=file_id)

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        # Обновляем дату скачивания
        file_obj.last_download_date = timezone.now()
        file_obj.save()

        return FileResponse(
            file_obj.file.open('rb'),
            as_attachment=True,
            filename=file_obj.original_name
        )


class SharedFileDownloadView(APIView):
    def get(self, request, token):
        # Ищем файл по токену в download_link
        file_obj = get_object_or_404(UserFile, download_link=f'share/{token}')

        # Обновляем дату скачивания
        file_obj.last_download_date = timezone.now()
        file_obj.save()

        return FileResponse(
            file_obj.file.open('rb'),
            as_attachment=True,
            filename=file_obj.original_name
        )


class FileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        file_obj = get_object_or_404(UserFile, id=file_id)

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        # Удаляем физический файл
        if file_obj.file:
            file_obj.file.delete(save=False)

        file_obj.delete()
        return Response({'message': 'Файл удален'})


class FileRenameView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        new_name = request.data.get('new_name')
        if not new_name:
            return Response({'error': 'Не указано новое имя'},
                            status=status.HTTP_400_BAD_REQUEST)

        file_obj = get_object_or_404(UserFile, id=file_id)

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        file_obj.original_name = new_name
        file_obj.save()
        return Response({'message': 'Файл переименован', 'new_name': new_name})


class FileCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, file_id):
        comment = request.data.get('comment', '')
        file_obj = get_object_or_404(UserFile, id=file_id)

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        file_obj.comment = comment
        file_obj.save()
        return Response({'message': 'Комментарий обновлен'})


class FileGenerateLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, file_id):
        file_obj = get_object_or_404(UserFile, id=file_id)

        # Проверка прав
        if not request.user.is_staff and file_obj.user != request.user:
            return Response({'error': 'Нет прав доступа'},
                            status=status.HTTP_403_FORBIDDEN)

        import uuid
        new_token = uuid.uuid4().hex[:20]
        file_obj.download_link = f'share/{new_token}'
        file_obj.save()

        return Response({
            'message'      : 'Ссылка обновлена',
            'download_link': file_obj.download_link
        })
