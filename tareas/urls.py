from django.urls import path, include
from .views import login_view, cerrar_sesion
from django.urls import path
from tareas.views import resultado_biometrico
from tareas.views import registrar_huella

urlpatterns = [
    path('', login_view, name='login'),
    path('cerrar/', cerrar_sesion, name='cerrar_sesion'),
    # path('inicio/', inicio_view, name='inicio'),

    # Rutas de cada módulo por rol
    path('admin/', include('tareas.admin.urls_admin')),
    path('doctor/', include('tareas.doctor.urls_doctor')),
    path('enfermeria/', include('tareas.enfermeria.urls_enfermeria')),
    path('cajero/', include('tareas.cajero.urls_cajero')),
    path('api/resultado_biometrico/', resultado_biometrico, name='resultado_biometrico'),
    path('api/registrar_huella/', registrar_huella, name='registrar_huella'),
]
