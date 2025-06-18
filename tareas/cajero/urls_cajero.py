from django.urls import path
from . import views_cajero

urlpatterns = [
    # 🧾 Panel principal del cajero
    path('', views_cajero.panel_cajero, name='panel_cajero'),

    # 📊 Menú de reportes del cajero
    path('reportes/', views_cajero.menu_reportes, name='menu_reportes'),

    # 🔎 Buscar y ver paciente
    path('buscar_paciente/', views_cajero.buscar_paciente, name='buscar_paciente'),
    path('ver_paciente/<int:id>/', views_cajero.ver_paciente, name='ver_paciente'),

    # 📄 Generar factura (HTML) y obtener datos (JSON)
    path('generar_factura/<int:paciente_id>/', views_cajero.generar_factura, name='generar_factura'),
    path('api/factura/<int:paciente_id>/', views_cajero.obtener_datos_factura, name='obtener_datos_factura'),

    # 💾 Guardar factura y plan de pago (POST desde JS)
    path('guardar_factura/', views_cajero.guardar_factura_y_plan, name='guardar_factura'),

    # ✅ Validar si el paciente tiene servicios HOY
    path('verificar_servicios/<int:paciente_id>/', views_cajero.verificar_servicios_json, name='verificar_servicios'),

    # 📅 Ver historial de planes de pago y cuotas del paciente
    path('ver_pagos/<int:paciente_id>/', views_cajero.ver_pagos_paciente, name='ver_pagos_paciente'),

    # 💰 Registrar el pago de una cuota desde el modal
    path('registrar_pago_cuota/', views_cajero.registrar_pago_cuota, name='registrar_pago_cuota'),
]
