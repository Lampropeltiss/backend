"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from mycloud.views import (
    RegisterView, LoginView, LogoutView,
    UserListView, UserDeleteView, UserToggleAdminStatusView,
    FileListView, FileUploadView, FileDownloadView,
    SharedFileDownloadView, FileDeleteView, FileRenameView,
    FileCommentView, FileGenerateLinkView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Администрирование
    path('api/register/', RegisterView.as_view()),
    path('api/login/', LoginView.as_view()),
    path('api/logout/', LogoutView.as_view()),
    path('api/users/', UserListView.as_view()),
    path('api/users/<int:user_id>/', UserDeleteView.as_view()),
    path('api/users/<int:user_id>/toggle-admin/', UserToggleAdminStatusView.as_view()),

    # Файлы
    path('api/files/', FileListView.as_view()),
    path('api/files/upload/', FileUploadView.as_view()),
    path('api/files/<int:file_id>/download/', FileDownloadView.as_view()),
    path('api/files/<int:file_id>/delete/', FileDeleteView.as_view()),
    path('api/files/<int:file_id>/rename/', FileRenameView.as_view()),
    path('api/files/<int:file_id>/comment/', FileCommentView.as_view()),
    path('api/files/<int:file_id>/generate-link/', FileGenerateLinkView.as_view()),
    path('share/<str:token>/', SharedFileDownloadView.as_view()),

    # Публичная ссылка
    path('share/<str:token>/', SharedFileDownloadView.as_view()),
]
