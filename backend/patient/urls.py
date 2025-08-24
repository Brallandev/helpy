from django.urls import path
from . import views

app_name = 'patient'

urlpatterns = [
    # Patient CRUD endpoints
    path('patients/', views.patient_list, name='patient-list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient-detail'),
    path('patients/intake/', views.patient_intake, name='patient-intake'),
    
    # Patient search endpoint
    path('patients/search/', views.patient_search, name='patient-search'),
    
    # Medical history endpoints
    path('patients/<int:patient_pk>/medical-history/', views.patient_medical_history, name='patient-medical-history'),
    
    # Document endpoints
    path('patients/<int:patient_pk>/documents/', views.patient_documents, name='patient-documents'),
]
