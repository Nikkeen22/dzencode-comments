from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.core.cache import cache

from .models import Comment
from .serializers import CommentSerializer
from .tasks import broadcast_new_comment
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

# Ключ кешу для списку коментарів — використовується для інвалідації після POST
COMMENTS_CACHE_KEY_PREFIX = 'views.decorators.cache.cache_page'


class CommentPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet навмисно обмежений до двох операцій:
    - GET  /api/comments/  — список коментарів (кешований)
    - POST /api/comments/  — створення коментаря

    PUT / PATCH / DELETE не передбачені ТЗ і тому прибрані
    щоб не відкривати зайвих endpoints без авторизації.
    """
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['user_name', 'email', 'created_at']
    ordering = ['-created_at']  # LIFO за замовчуванням

    def get_queryset(self):
        # prefetch_related('replies') усуває N+1 при рекурсивній серіалізації відповідей
        return (
            Comment.objects
            .filter(parent=None)
            .prefetch_related('replies')
        )

    @method_decorator(cache_page(60 * 1))  # кеш на 1 хвилину
    @method_decorator(vary_on_headers('Accept', 'Accept-Language'))
    def list(self, request, *args, **kwargs):
        """GET /api/comments/ — кешований список коментарів."""
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Після збереження коментаря:
        1. Інвалідуємо кеш списку — щоб наступний GET повернув свіжі дані.
        2. Відправляємо WebSocket-повідомлення через Celery (асинхронно).
        """
        comment = serializer.save()

        # Інвалідація кешу: видаляємо всі ключі що починаються з префіксу
        # django cache_page формує ключі виду:
        # views.decorators.cache.cache_page.<method>.<url_hash>.<lang>.<tz>
        # cache.delete_pattern() доступний через django-redis
        try:
            cache.delete_pattern(f'{COMMENTS_CACHE_KEY_PREFIX}*')
        except AttributeError:
            # Якщо бекенд кешу не підтримує delete_pattern (наприклад LocMemCache)
            cache.clear()

        # Серіалізуємо і кладемо задачу в чергу Celery
        data = CommentSerializer(comment, context={'request': self.request}).data
        broadcast_new_comment.delay(dict(data))


class CaptchaAPIView(APIView):
    """GET /api/captcha/refresh/ — повертає новий ключ і URL картинки капчі."""

    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        full_image_url = request.build_absolute_uri(image_url)

        return Response({
            'captcha_key': hashkey,
            'captcha_image_url': full_image_url,
        })