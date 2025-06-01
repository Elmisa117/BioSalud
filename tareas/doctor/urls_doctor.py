from django.urls import path
from .views_doctor import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='doctor_dashboard'),
]
