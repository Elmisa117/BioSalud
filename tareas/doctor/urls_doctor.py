from django.urls import path
from . import views_doctor

urlpatterns = [
    # Vista principal del panel del doctor
    path('', views_doctor.menu_doctor, name='menu_doctor'),

    # Listado de pacientes accesible desde el módulo del doctor
    path('pacientes/', views_doctor.ver_pacientes, name='ver_pacientes'),

    # Gestión de hospitalizaciones
    path('hospitalizaciones/', views_doctor.ver_hospitalizaciones, name='ver_hospitalizaciones'),

    # Perfil del doctor (visualización o edición)
    path('perfil/', views_doctor.perfil_doctor, name='perfil_doctor'),

    # Consulta médica para un paciente específico
    path('consulta/<int:id>/', views_doctor.consulta_paciente, name='consulta_paciente'),

    # Historial del paciente desde el módulo doctor
    path('historial/<int:id>/', views_doctor.historial_paciente, name='historial_paciente'),

    # Cierre de sesión desde el módulo doctor
    path('cerrar/', views_doctor.logout_view, name='logout'),

    # Nueva ruta para las fichas clínicas del doctor (solo hoy)
    path('ficha_clinico_doctor/', views_doctor.ficha_clinico_doctor, name='ficha_clinico_doctor'),
]
