from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'is_staff', 'is_active')
    exclude = ('first_name', 'last_name', 'is_superuser', 'date_joined')
