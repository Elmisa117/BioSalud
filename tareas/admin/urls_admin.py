from django.urls import path
from .views_admin import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='admin_dashboard'),
]
