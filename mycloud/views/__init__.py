# views/__init__.py
from .admin_views import UserDeleteView, UserListView, UserToggleAdminStatusView
from .auth_views import LoginView, LogoutView, RegisterView, csrf
from .file_views import (
    FileCommentView,
    FileDeleteView,
    FileDownloadView,
    FileGenerateLinkView,
    FileListView,
    FileRenameView,
    FileUploadView,
    SharedFileDownloadView,
)

__all__ = [
    # Auth
    "RegisterView",
    "LoginView",
    "LogoutView",
    "csrf",
    # Admin
    "UserListView",
    "UserDeleteView",
    "UserToggleAdminStatusView",
    # Files
    "FileListView",
    "FileUploadView",
    "FileDownloadView",
    "SharedFileDownloadView",
    "FileDeleteView",
    "FileRenameView",
    "FileCommentView",
    "FileGenerateLinkView",
]
