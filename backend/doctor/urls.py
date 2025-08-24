from django.urls import path
from . import views

app_name = 'doctor'

urlpatterns = [
    # Basic doctor endpoints
    path('doctors/', views.doctor_list, name='doctor-list'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor-detail'),
    path('doctors/phone-numbers/', views.doctor_phone_numbers, name='doctor-phone-numbers'),
]
