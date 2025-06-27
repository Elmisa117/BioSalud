from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from tareas.views import login_view, cerrar_sesion
from tareas.cajero import views_cajero as views  # Solo si usas views.generar_factura
from tareas.views import resultado_biometrico
from tareas.views import registrar_huella

urlpatterns = [
    # Redirección raíz al login
    path('', lambda request: redirect('login')),

    # Autenticación
    path('login/', login_view, name='login'),
    path('cerrar/', cerrar_sesion, name='cerrar'),
    #Super AdministradorDjango
    path('djangoadmin/', admin.site.urls),  # Habilita el Django admin clásico en /djangoadmin/
    # Rutas por módulo (rol)
    path('admin/', include('tareas.admin.urls_admin')),
    path('doctor/', include('tareas.doctor.urls_doctor')),
    path('enfermeria/', include('tareas.enfermeria.urls_enfermeria')),
    path('cajero/', include('tareas.cajero.urls_cajero')),
    # Ruta específica del cajero (fuera del include)
    path('facturar/<int:paciente_id>/', views.generar_factura, name='generar_factura'),
    # Rutas para las API biometricos
    path('api/resultado_biometrico/', resultado_biometrico, name='resultado_biometrico'),
    path('api/registrar_huella/', registrar_huella, name='registrar_huella'),
]

# Servir archivos estáticos en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
