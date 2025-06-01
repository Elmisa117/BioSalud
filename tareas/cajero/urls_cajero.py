from django.urls import path
from .views_cajero import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='cajero_dashboard'),
]
