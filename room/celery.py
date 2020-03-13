from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
import requests
import json
from django.utils.crypto import get_random_string
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room.settings')
app = Celery('room')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(name='debug_task')
def debug_task(data):
    unique_id = get_random_string(length=32)
    data = {"roomId": unique_id, "users": list(data["Message"])}
    response = requests.post(settings.AWS_BASE_URL, data=json.dumps(data))
    print(response)
    return "Done!!!"
