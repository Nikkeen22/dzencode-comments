from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Які поля відображати в списку
    list_display = ('id', 'user_name', 'email', 'created_at', 'parent')
    # За якими полями працюватиме пошук
    search_fields = ('user_name', 'email', 'text')
    # Фільтрація за датою
    list_filter = ('created_at',)