# myapp/middleware.py
from django.utils.deprecation import MiddlewareMixin

class DisableCsrfForApi(MiddlewareMixin):
    def process_request(self, request):
        # Если путь начинается с /api/, отключаем CSRF
        if request.path.startswith('/api/'):
            # Django позволяет пометить запрос как «не требующий CSRF»
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
