from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, CaptchaAPIView

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('captcha/refresh/', CaptchaAPIView.as_view(), name='api-captcha-refresh'),
]