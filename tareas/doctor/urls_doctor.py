from django.urls import path
from . import views_doctor

urlpatterns = [
    # 🏠 Panel principal del doctor
    path('', views_doctor.menu_doctor, name='menu_doctor'),

    # 👨‍⚕️ Gestión de pacientes
    path('pacientes/', views_doctor.ver_pacientes, name='ver_pacientes'),
    path('paciente/<int:pacienteid>/perfil/', views_doctor.perfil_paciente_doctor, name='perfil_paciente_doctor'),
    path('paciente/<int:pacienteid>/consulta/', views_doctor.crear_consulta_doctor, name='crear_consulta_doctor'),
    path('paciente/<int:pacienteid>/actualizar/', views_doctor.actualizar_paciente_doctor, name='actualizar_paciente_doctor'),

    # 📋 Historial clínico del paciente (filtro de fichas)
    path('paciente/<int:pacienteid>/historial/', views_doctor.historial_paciente, name='historial_paciente'),

    # 🔍 Ver detalle completo de una ficha clínica
    path('ficha/<int:fichaid>/ver/', views_doctor.ver_historial_detalle_doctor, name='ver_historial_detalle_doctor'),

    # 🚑 Consulta rápida desde historial
    path('consulta_paciente/<int:pacienteid>/', views_doctor.consulta_paciente, name='consulta_paciente'),

    # 🏥 Hospitalizaciones
    path('hospitalizaciones/', views_doctor.ver_hospitalizaciones, name='ver_hospitalizaciones'),
    path('hospitalizacion/alta/<int:hosp_id>/', views_doctor.alta_doctor, name='alta_doctor'),
    path('hospitalizacion/servicios/<int:hosp_id>/', views_doctor.servicios_hospitalizacion, name='servicios_hospitalizacion'),

    # 🗂️ Fichas clínicas creadas por el doctor
    path('ficha_clinico_doctor/', views_doctor.ficha_clinico_doctor, name='ficha_clinico_doctor'),

    # ⚡ AJAX: habitaciones disponibles
    path('ajax/habitaciones_disponibles/<int:tipoid>/', views_doctor.habitaciones_disponibles, name='habitaciones_disponibles'),

    # 🧑‍⚕️ Perfil del profesional
    path('perfil/', views_doctor.perfil_doctor, name='perfil_doctor'),

    # 🔐 Cierre de sesión
    path('cerrar/', views_doctor.logout_view, name='logout'),
]
