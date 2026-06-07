from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task
def broadcast_new_comment(comment_data: dict):
    """
    Фонова задача Celery:
    відправляє новий коментар по WebSocket всім підключеним клієнтам.
    Запускається через чергу після збереження коментаря в БД.
    """
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            'comments',
            {
                'type': 'new_comment',
                'comment': comment_data,
            }
        )