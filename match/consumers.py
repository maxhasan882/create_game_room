from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from room.celery import debug_task
from room import settings


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
        if close_code != 1000:
            print("Self Disconnect: ", close_code)
            settings.st.remove(self.scope['user'])
        print("Connection Code: ", close_code)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        user = text_data
        print(self.scope['user'])
        if settings.CHECK:
            settings.st.add(user)
        print("Queue size: ", len(settings.st))
        if len(settings.st) > 3:
            if settings.CHECK:
                settings.st1 = settings.st.copy()
                settings.CHECK = False
            if settings.CHECK is False and user in settings.st1:
                settings.st1.remove(user)
                print("Len of new Queue: ", len(settings.st1))
                if len(settings.st1) == 0:
                    debug_task.delay({"Message": [user for user in settings.st]})
                    settings.st.clear()
                    print("Message sent to message broker")
                    settings.CHECK = True
                print(user, "has been removed")
                self.close()

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
