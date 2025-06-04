from django.urls import path
from .views_admin import dashboard_view
from .views_admin import (
    dashboard_view, registrar_personal, listar_personal,
    registrar_paciente, listar_pacientes, ver_paciente,
    editar_paciente, inactivar_paciente, reactivar_paciente,
    exportar_pacientes
)


urlpatterns = [
    path('', dashboard_view, name='admin_dashboard'),
    path('registrar_personal/', registrar_personal, name='registrar_personal'),
    path('listar_personal/', listar_personal, name='listar_personal'),
    path('registrar_paciente/', registrar_paciente, name='registrar_paciente'),
    path('listar_pacientes/', listar_pacientes, name='listar_pacientes'),
    path('paciente/<int:paciente_id>/', ver_paciente, name='ver_paciente'),
    path('paciente/<int:paciente_id>/editar/', editar_paciente, name='editar_paciente'),
    path('paciente/<int:paciente_id>/inactivar/', inactivar_paciente, name='inactivar_paciente'),
    path('paciente/<int:paciente_id>/reactivar/', reactivar_paciente, name='reactivar_paciente'),
    path('exportar_pacientes/', exportar_pacientes, name='exportar_pacientes'),
]
