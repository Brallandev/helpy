from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    # Basic room endpoints
    path('rooms/', views.room_list, name='room-list'),
    path('rooms/<int:pk>/', views.room_detail, name='room-detail'),
]
