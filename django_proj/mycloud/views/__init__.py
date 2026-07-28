# views/__init__.py
from .auth_views import RegisterView, LoginView, LogoutView
from .admin_views import UserListView, UserDeleteView, UserToggleAdminStatusView
from .file_views import (
    FileListView, FileUploadView, FileDownloadView,
    SharedFileDownloadView, FileDeleteView, FileRenameView,
    FileCommentView, FileGenerateLinkView
)

__all__ = [
    # Auth
    'RegisterView', 'LoginView', 'LogoutView',
    # Admin
    'UserListView', 'UserDeleteView', 'UserToggleAdminStatusView',
    # Files
    'FileListView', 'FileUploadView', 'FileDownloadView',
    'SharedFileDownloadView', 'FileDeleteView', 'FileRenameView',
    'FileCommentView', 'FileGenerateLinkView',
]