# publications/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles new WebSocket connections."""
        # Get the article ID from the URL. The URL router will provide it in self.scope.
        self.article_id = self.scope['url_route']['kwargs']['article_id']
        self.room_group_name = f'article_{self.article_id}_comments'

        # Join the room group for this article.
        # Any messages sent to this group will be received by this consumer.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnections."""
        # Leave the room group when the connection is closed.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # This method is called when the backend view sends a message to the group.
    # The name 'comment_like_update' must match the 'type' in the group_send call.
    async def comment_like_update(self, event):
        """Receives a like update event and sends it to the client's WebSocket."""
        message = event['message']

        # Send the message to the connected client (the browser).
        await self.send(text_data=json.dumps({
            'comment_id': message['comment_id'],
            'like_count': message['like_count']
            # Note: We don't send 'liked' status here, as it's user-specific.
        }))