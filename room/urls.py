from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('room/', include('match.urls')),
    path('userApi/', include('user.urls'))
]
