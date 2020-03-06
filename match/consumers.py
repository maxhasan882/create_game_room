from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from room import settings


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))


class ChatConsumerFloor(WebsocketConsumer):

    def connect(self):
        self.room_name = 'floor'
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        print("I am in floor: ", text_data)
        settings.PLAYER_QUEUE.put(text_data)
        len = settings.PLAYER_QUEUE.qsize()
        if len >= 5:
            self.pull_item_from_queue()

    def pull_item_from_queue(self):
        import uuid
        message = uuid.uuid4().hex[:6].upper()
        self.send_chat_message(message)
        for i in range(5):
            print(settings.PLAYER_QUEUE.get())
        print("Number of player: ", settings.PLAYER_QUEUE.qsize())

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))