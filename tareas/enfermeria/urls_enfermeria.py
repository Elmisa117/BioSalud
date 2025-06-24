from django.urls import path
from . import views_enfermeria

urlpatterns = [
    # Menú principal de enfermería
    path('', views_enfermeria.menu_enfermeria_enfermeria, name='menu_enfermeria'),

    # Vista general de pacientes
    path('pacientes/', views_enfermeria.vista_pacientes_enfermeria, name='vista_pacientes_enfermeria'),

    # Registro y edición de pacientes
    path('pacientes/registro/', views_enfermeria.registrar_paciente_enfermeria, name='registrar_paciente_enfermeria'),

    # Vista del perfil individual del paciente
    path('pacientes/perfil/<int:paciente_id>/', views_enfermeria.perfil_paciente_enfermeria, name='perfil_paciente_enfermeria'),

    # Registro de ficha clínica
    path('ficha_clinico/<int:id>/', views_enfermeria.ficha_clinico_enfermeria, name='ficha_clinico_enfermeria'),

    # Historial clínico del paciente
    path('historial/<int:id>/', views_enfermeria.historial_enfermeria, name='historial_enfermeria'),

    # Ver detalle de ficha clínica
    path('ver_historial/<int:fichaid>/', views_enfermeria.ver_historial_enfermeria, name='ver_historial_enfermeria'),

    # Vista gráfica de hospitalización (mapa de camas)
    path('mapa-habitaciones/', views_enfermeria.vista_hospitalizacion_enfermeria, name='mapa_habitaciones_enfermeria'),

    # Perfil del personal logueado
    path('perfil/', views_enfermeria.perfil_personal_enfermeria, name='perfil_personal_enfermeria'),
]
