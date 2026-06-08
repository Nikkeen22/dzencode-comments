import re
from rest_framework import serializers
from .models import Comment, validate_attached_file, validate_user_name as validate_user_name_field
from captcha.models import CaptchaStore
from django.core.exceptions import ValidationError as DjangoValidationError



ALLOWED_TAG_PATTERNS = [
    r'^<a(\s+(href|title)="[^"]*"){1,2}>$',
    r'^</a>$',
    r'^<code>$',
    r'^</code>$',
    r'^<i>$',
    r'^</i>$',
    r'^<strong>$',
    r'^</strong>$',
]


def validate_html_tags(value):
    """
    Перевіряє що в тексті використовуються лише дозволені теги
    і що всі відкриті теги закриті (валідний XHTML).
    """
    tags = re.findall(r'<[^>]*>', value)

    for tag in tags:
        is_allowed = any(re.match(pattern, tag) for pattern in ALLOWED_TAG_PATTERNS)
        if not is_allowed:
            raise serializers.ValidationError(f'Тег {tag} недопустимий.')

    # Перевірка парності тегів (валідний XHTML)
    stack = []
    paired = {'a', 'code', 'i', 'strong'}
    open_tag_re = re.compile(r'^<([a-z]+)[\s>]')
    close_tag_re = re.compile(r'^</([a-z]+)>')

    for tag in tags:
        open_match = open_tag_re.match(tag)
        close_match = close_tag_re.match(tag)

        if open_match:
            tag_name = open_match.group(1)
            if tag_name in paired:
                stack.append(tag_name)
        elif close_match:
            tag_name = close_match.group(1)
            if not stack or stack[-1] != tag_name:
                raise serializers.ValidationError(
                    f'Тег </{tag_name}> закритий без відповідного відкриваючого тегу.'
                )
            stack.pop()

    if stack:
        raise serializers.ValidationError(
            f'Теги не закриті: {", ".join(f"<{t}>" for t in stack)}'
        )

    return value


class CommentSerializer(serializers.ModelSerializer):
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    # Вкладені відповіді — рекурсивно
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'user_name', 'email', 'homepage', 'text', 'parent',
            'attached_file', 'created_at', 'replies',
            'captcha_key', 'captcha_value',
        ]
        read_only_fields = ['created_at']

    def get_replies(self, obj):
        # prefetch_related('replies') у get_queryset() гарантує що тут немає N+1
        if obj.replies.exists():
            return CommentSerializer(
                obj.replies.all().order_by('-created_at'),
                many=True,
                context=self.context,
            ).data
        return []

    def validate_user_name(self, value):
        try:
            validate_user_name_field(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
        return value

    def validate_text(self, value):
        return validate_html_tags(value)

    def validate_attached_file(self, value):
        """
        Валідація файлу на рівні серіалізатора — файл ще в пам'яті
        (InMemoryUploadedFile), тому file.size і file.name доступні.
        Ресайз зображення відбувається в Model.save() після запису на диск.
        """
        if value:
            try:
                validate_attached_file(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.message)
        return value

    def validate(self, data):
        """Перевірка CAPTCHA."""
        captcha_key = data.get('captcha_key')
        captcha_value = data.get('captcha_value')

        try:
            captcha = CaptchaStore.objects.get(hashkey=captcha_key)
            if captcha.response != captcha_value.lower().strip():
                raise serializers.ValidationError(
                    {'captcha_value': 'Неправильне значення капчі. Спробуйте ще раз.'}
                )
            captcha.delete()
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError(
                {'captcha_key': 'Капча застаріла або не існує. Оновіть сторінку.'}
            )

        return data

    def create(self, validated_data):
        validated_data.pop('captcha_key', None)
        validated_data.pop('captcha_value', None)
        return super().create(validated_data)