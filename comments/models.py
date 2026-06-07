import os
import re
from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image


def validate_user_name(value):
    """User Name: тільки цифри і букви латинського алфавіту (вимога ТЗ)."""
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        raise ValidationError('User Name може містити лише латинські букви та цифри.')


def validate_attached_file(file):
    """
    Валідація прикріпленого файлу:
    - JPG, GIF, PNG — дозволені (розмір перевіряється після збереження)
    - TXT — до 100 КБ
    - Інші формати — заборонені
    Викликається лише в серіалізаторі де файл вже існує як InMemoryUploadedFile,
    тому file.size і file.name доступні без звернення до диску.
    """
    if not file:
        return

    ext = os.path.splitext(file.name)[1].lower()

    if ext == '.txt':
        if file.size > 100 * 1024:
            raise ValidationError('Текстовий файл не повинен перевищувати 100 КБ.')
    elif ext in ('.jpg', '.jpeg', '.png', '.gif'):
        pass  # розмір зображення коригується в resize_image_if_needed()
    else:
        raise ValidationError('Дозволені формати файлів: JPG, GIF, PNG або TXT.')


def resize_image_if_needed(file_path):
    """
    Пропорційно зменшує зображення до 320×240 якщо воно більше.
    Викликається після збереження файлу на диск (коли path вже доступний).
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.gif'):
        return

    try:
        img = Image.open(file_path)
        max_size = (320, 240)
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(file_path)
    except Exception as e:
        raise ValidationError(f'Помилка обробки зображення: {e}')


class Comment(models.Model):
    user_name = models.CharField(
        max_length=100,
        validators=[validate_user_name],
    )
    email = models.EmailField()
    homepage = models.URLField(blank=True, null=True)
    text = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )
    attached_file = models.FileField(upload_to='attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # full_clean() навмисно не викликається тут —
        # уся валідація відбувається в серіалізаторі до збереження.
        # Виклик full_clean() тут призводив би до помилки:
        # attached_file.path недоступний поки файл не збережений на диск.
        super().save(*args, **kwargs)

        # Після збереження файл вже на диску — можна безпечно відкрити його
        if self.attached_file:
            resize_image_if_needed(self.attached_file.path)

    def __str__(self):
        return f'Comment by {self.user_name} at {self.created_at}'