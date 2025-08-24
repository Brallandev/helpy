from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    # Basic schedule endpoints
    path('schedules/', views.schedule_list, name='schedule-list'),
    path('schedules/<int:pk>/', views.schedule_detail, name='schedule-detail'),
]
