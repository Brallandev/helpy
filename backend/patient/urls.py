from django.urls import path
from . import views

app_name = 'patient'

urlpatterns = [
    # Basic patient endpoints - we'll expand these later
    path('patients/', views.patient_list, name='patient-list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient-detail'),
]
