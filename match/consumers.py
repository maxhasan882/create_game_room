from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from channels.layers import get_channel_layer

from room import settings

import queue
from heapq import heappush, heappop

st = set()


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope["user"]
        print("user: ", user)
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
        user = self.scope["user"]
        print("user: ", user)
        print("I am in floor: ", text_data)
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
        user = self.scope["user"]
        print("user____: ", user)
        self.room_name = 'floor'
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        if close_code is not 1000:
            print("nije nijei")
            st.remove(self.scope['user'])
        print("Why man?", close_code)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        #print("I am in floor: ", text_data)
        user = self.scope["user"]
        #print("user: ", user.username)
        st.add(user)
        if len(st) > 5:
            if self.scope['user'] in st:
                self.close()

        #print(len(st))
        # if len(user)>4:
        #     self.pull_item_from_queue()

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
