from django.urls import path
from . import views_doctor

urlpatterns = [
    # Panel principal del doctor
    path('', views_doctor.menu_doctor, name='menu_doctor'),

    # Gestión de pacientes
    path('pacientes/', views_doctor.ver_pacientes, name='ver_pacientes'),
    path('paciente/<int:pacienteid>/perfil/', views_doctor.perfil_paciente_doctor, name='perfil_paciente_doctor'),
    path('paciente/<int:pacienteid>/consulta/', views_doctor.crear_consulta_doctor, name='crear_consulta_doctor'),
    path('paciente/<int:pacienteid>/actualizar/', views_doctor.actualizar_paciente_doctor, name='actualizar_paciente_doctor'),

    # Historial completo del paciente
    path('historial/<int:id>/', views_doctor.historial_paciente, name='historial_paciente'),

    # Hospitalizaciones activas del doctor
    path('hospitalizaciones/', views_doctor.ver_hospitalizaciones, name='ver_hospitalizaciones'),

    # Perfil profesional del doctor
    path('perfil/', views_doctor.perfil_doctor, name='perfil_doctor'),

    # Fichas clínicas creadas por el doctor
    path('ficha_clinico_doctor/', views_doctor.ficha_clinico_doctor, name='ficha_clinico_doctor'),

    # Consulta rápida de paciente desde historial (opcional si se usa)
    path('consulta_paciente/<int:id>/', views_doctor.consulta_paciente, name='consulta_paciente'),

    # Cierre de sesión
    path('cerrar/', views_doctor.logout_view, name='logout'),
]
