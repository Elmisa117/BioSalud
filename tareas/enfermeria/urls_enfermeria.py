from django.urls import path
from .views_enfermeria import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='enfermeria_dashboard'),
]
