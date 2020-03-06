from django.urls import path, include
from .views import index, room, landing

urlpatterns = [
    path('index/', index, name='index'),
    path('landing/', landing, name='landing'),
    path('cr/<str:room_name>/', room, name='room'),
]
