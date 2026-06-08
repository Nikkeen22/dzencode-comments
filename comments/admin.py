from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = ('id', 'user_name', 'email', 'created_at', 'parent')

    search_fields = ('user_name', 'email', 'text')

    list_filter = ('created_at',)