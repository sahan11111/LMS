from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'role', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'role')
    list_filter = ('role', 'is_active')
    ordering = ('id',)
    list_per_page = 20