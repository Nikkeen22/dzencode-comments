import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CommentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для real-time оновлення коментарів.
    
    Клієнт підключається до ws://host/ws/comments/
    і отримує нові коментарі одразу після їх створення.
    """

    GROUP_NAME = 'comments'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    # Цей метод викликається коли хтось робить group_send з type='new_comment'
    async def new_comment(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_comment',
            'comment': event['comment'],
        }))