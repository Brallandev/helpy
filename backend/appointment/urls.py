from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    # Basic appointment endpoints
    path('appointments/', views.appointment_list, name='appointment-list'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment-detail'),
]
