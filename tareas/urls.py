from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.pantalla_principal, name='pantalla_principal'),
]