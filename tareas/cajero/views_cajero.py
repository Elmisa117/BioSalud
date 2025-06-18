from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
from datetime import date
from django.contrib import messages  # Asegúrate de tener esto arriba

from tareas.models import (
    Paciente, Consulta, ConsultaServicios, Hospitalizacion,
    MetodoPago, Factura, Pago, PlanPago, CuotaPlanPago
)

# 📜 PANEL DEL CAJERO
def panel_cajero(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    nombre_completo = request.session.get('nombre', 'Cajero')
    return render(request, 'cajero/panel_cajero.html', {'nombre': nombre_completo})

# 📊 MENÚ DE REPORTES
def menu_reportes(request):
    return render(request, 'cajero/menu_reportes.html')

# 🔎 BUSCAR PACIENTE
def buscar_paciente(request):
    query = request.GET.get('q', '')
    pacientes = Paciente.objects.filter(nombres__icontains=query) if query else Paciente.objects.all()
    return render(request, 'cajero/BuscarPaciente.html', {'pacientes': pacientes, 'query': query})

# 👁️ PERFIL DEL PACIENTE
def ver_paciente(request, id):
    paciente = get_object_or_404(Paciente, pk=id)
    return render(request, 'cajero/PerfilPaciente.html', {'paciente': paciente})

# ✅ OBTENER DATOS PARA LA FACTURA EN JSON
def obtener_datos_factura(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    hoy = timezone.now().date()

    datos_paciente = {
        'nombre': f"{paciente.nombres} {paciente.apellidos}",
        'telefono': paciente.telefono,
        'direccion': paciente.direccion,
    }

    servicios_factura = []

    consultas = Consulta.objects.filter(
        paciente=paciente,
        estado=True,
        facturado=False,
        fechaconsulta__date=hoy
    )
    for c in consultas:
        descripcion = f"Consulta ({c.tipoconsulta}) - Motivo: {c.motivocita}"
        servicios_factura.append({
            'descripcion': descripcion,
            'cantidad': 1,
            'precio': float(c.costo),
            'subtotal': float(c.costo)
        })

    consulta_ids = consultas.values_list('consultaid', flat=True)
    consulta_servicios = ConsultaServicios.objects.filter(
        consultaid_id__in=consulta_ids,
        estado=True,
        facturado=False,
        fechaservicio__date=hoy
    ).select_related('servicioid')

    for cs in consulta_servicios:
        descripcion = f"Servicio Médico: {cs.servicioid.descripcion}"
        servicios_factura.append({
            'descripcion': descripcion,
            'cantidad': cs.cantidad,
            'precio': float(cs.servicioid.costo),
            'subtotal': round(cs.cantidad * float(cs.servicioid.costo), 2)
        })

    hospitalizaciones = Hospitalizacion.objects.filter(
        paciente=paciente,
        estado=True,
        facturado=False,
        fechaingreso__date=hoy
    ).select_related('habitacion__tipohabitacion')

    for h in hospitalizaciones:
        if h.fechaalta:
            dias = (h.fechaalta.date() - h.fechaingreso.date()).days + 1
        else:
            dias = 1
        dias = max(dias, 1)
        tipo = h.habitacion.tipohabitacion.nombre
        costo_diario = float(h.habitacion.tipohabitacion.costodiario)
        descripcion = f"Hospitalización {tipo} ({dias} días)"
        subtotal = costo_diario * dias

        servicios_factura.append({
            'descripcion': descripcion,
            'cantidad': dias,
            'precio': costo_diario,
            'subtotal': round(subtotal, 2)
        })

    return JsonResponse({
        'paciente': datos_paciente,
        'servicios': servicios_factura
    })


# 📄 GENERAR FACTURA
def generar_factura(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    hoy = timezone.now().date()

    tiene_consultas = Consulta.objects.filter(
        paciente=paciente,
        estado=True,
        facturado=False,
        fechaconsulta__date=hoy
    ).exists()

    consulta_ids = Consulta.objects.filter(
        paciente=paciente,
        estado=True,
        facturado=False,
        fechaconsulta__date=hoy
    ).values_list('consultaid', flat=True)

    tiene_servicios = ConsultaServicios.objects.filter(
        consultaid_id__in=consulta_ids,
        estado=True,
        facturado=False,
        fechaservicio__date=hoy
    ).exists()

    tiene_hospitalizaciones = Hospitalizacion.objects.filter(
        paciente=paciente,
        estado=True,
        facturado=False,
        fechaingreso__date=hoy
    ).exists()

    if not (tiene_consultas or tiene_servicios or tiene_hospitalizaciones):
        messages.warning(request, "⚠️ El paciente no tiene servicios pendientes para facturar.")
        return redirect('ver_paciente', id=paciente.pacienteid)

    metodos_pago = MetodoPago.objects.filter(estado=True)
    return render(request, 'cajero/GenerarFactura.html', {
        'paciente': paciente,
        'metodos_pago': metodos_pago
    })

# 📅 GUARDAR FACTURA Y PLAN DE PAGO
@csrf_exempt
def guardar_factura_y_plan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        paciente_id = request.POST.get('paciente_id')
        paciente = Paciente.objects.get(pk=paciente_id)
        hoy = timezone.now().date()

        numero_factura = request.POST.get('numeroFactura')
        fecha_emision = timezone.now()
        subtotal = float(request.POST.get('total', 0))
        monto_pagado = float(request.POST.get('montoPagado', 0))
        metodo_id = request.POST.get('metodoPago')
        numero_referencia = request.POST.get('numeroReferencia', '')
        observaciones = request.POST.get('observaciones', '')
        estado_factura = 'Pendiente' if monto_pagado < subtotal else 'Pagada'

        factura = Factura.objects.create(
            paciente=paciente,
            numerofactura=numero_factura,
            fechaemision=fecha_emision,
            subtotal=subtotal,
            descuento=0,
            impuesto=0,
            total=subtotal,
            observaciones=observaciones,
            estado=estado_factura
        )

        metodo_pago = MetodoPago.objects.get(pk=metodo_id)
        Pago.objects.create(
            factura=factura,
            metodopago=metodo_pago,
            monto=monto_pagado,
            fechapago=fecha_emision,
            numeroreferencia=numero_referencia,
            observaciones=observaciones
        )

        # 🔄 Marcar como facturadas las consultas, servicios y hospitalizaciones de hoy
        consultas = Consulta.objects.filter(
            paciente=paciente,
            estado=True,
            facturado=False,
            fechaconsulta__date=hoy
        )
        consultas.update(facturado=True)

        consulta_ids = consultas.values_list('consultaid', flat=True)
        consulta_servicios = ConsultaServicios.objects.filter(
            consultaid_id__in=consulta_ids,
            estado=True,
            facturado=False,
            fechaservicio__date=hoy
        )
        consulta_servicios.update(facturado=True)

        hospitalizaciones = Hospitalizacion.objects.filter(
            paciente=paciente,
            estado=True,
            facturado=False,
            fechaingreso__date=hoy
        )
        hospitalizaciones.update(facturado=True)

        # 👇 Plan de pago (sin cambios aquí)
        if request.POST.get('planPagoActivado') == 'true':
            planes_anteriores = PlanPago.objects.filter(factura__paciente=paciente)
            tiene_pendientes = CuotaPlanPago.objects.filter(
                planpago__in=planes_anteriores,
                estado='Pendiente'
            ).exists()

            if tiene_pendientes:
                return JsonResponse({
                    'error': 'El paciente ya tiene un plan de pago con cuotas pendientes. No puede registrar uno nuevo.'
                }, status=400)

            numero_cuotas = int(request.POST.get('planNumeroCuotas'))
            fecha_inicio = request.POST.get('planFechaInicio')
            fecha_fin = request.POST.get('planFechaFin')
            frecuencia = request.POST.get('frecuencia', 'mensual')
            cuotas_json = request.POST.get('planCuotasJSON')

            plan = PlanPago.objects.create(
                factura=factura,
                fechainicio=fecha_inicio,
                fechafin=fecha_fin,
                numerocuotas=numero_cuotas,
                montototal=subtotal - monto_pagado,
                frecuencia=frecuencia,
                observaciones="Generado automáticamente",
                estado='Activo'
            )

            cuotas = json.loads(cuotas_json)
            for i, cuota in enumerate(cuotas, start=1):
                CuotaPlanPago.objects.create(
                    planpago=plan,
                    numerocuota=i,
                    fechavencimiento=cuota['fecha'],
                    montocuota=cuota['monto'],
                    estado='Pendiente'
                )

        return JsonResponse({
            'mensaje': 'Factura y pagos registrados correctamente',
            'redirect_url': reverse('ver_paciente', args=[paciente.pacienteid])
        })

    except Exception as e:
        import traceback
        print("🚨 Error al guardar factura y plan de pago:")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


# ✅ VERIFICAR SI EL PACIENTE TIENE SERVICIOS HOY
def verificar_servicios_json(request, paciente_id):
    hoy = date.today()

    consultas = Consulta.objects.filter(paciente_id=paciente_id, fechaconsulta__date=hoy, estado=True)
    consulta_ids = consultas.values_list('consultaid', flat=True)
    consulta_servicios = ConsultaServicios.objects.filter(consultaid_id__in=consulta_ids, estado=True)
    hospitalizaciones = Hospitalizacion.objects.filter(
        paciente_id=paciente_id,
        fechaingreso__date=hoy,
        estado=True
    )

    tiene_servicios = consultas.exists() or consulta_servicios.exists() or hospitalizaciones.exists()

    if tiene_servicios:
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'empty', 'mensaje': 'El Paciente no se hizo ningún Servicio'})

# 📜 FUNCIÓN AUXILIAR: RESUMEN DE SERVICIOS DE UNA FACTURA
def resumen_servicios_factura(factura):
    try:
        resumenes = set()

        consultas = Consulta.objects.filter(paciente=factura.paciente, estado=True)
        for c in consultas:
            resumenes.add(f"Consulta {c.tipoconsulta}")

        consulta_ids = consultas.values_list('consultaid', flat=True)
        consulta_servicios = ConsultaServicios.objects.filter(
            consultaid_id__in=consulta_ids, estado=True
        ).select_related('servicioid')

        for cs in consulta_servicios:
            resumenes.add(cs.servicioid.descripcion)

        hospitalizaciones = Hospitalizacion.objects.filter(
            paciente=factura.paciente, estado=True
        ).select_related('habitacion__tipohabitacion')

        for h in hospitalizaciones:
            tipo = h.habitacion.tipohabitacion.nombre
            resumenes.add(f"Hospitalización {tipo}")

        lista = list(resumenes)
        return ", ".join(lista[:3]) if lista else "N/A"

    except Exception:
        return "N/A"

# ✅ VER PLAN DE PAGOS Y CUOTAS DEL PACIENTE
def ver_pagos_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    planes = PlanPago.objects.filter(factura__paciente=paciente).prefetch_related('cuotas', 'factura')
    metodos_pago = MetodoPago.objects.filter(estado=True)

    planes_actualizados = []
    for plan in planes:
        cuotas_ordenadas = plan.cuotas.filter(estado__in=['Pendiente', 'Pagada']).order_by('numerocuota')
        if cuotas_ordenadas.exists():
            plan.cuotas_ordenadas = cuotas_ordenadas
            plan.resumen_producto = resumen_servicios_factura(plan.factura)
            planes_actualizados.append(plan)

    return render(request, 'cajero/VerPagosPaciente.html', {
        'paciente': paciente,
        'planes': planes_actualizados,
        'metodos_pago': metodos_pago
    })

# ✅ REGISTRAR PAGO DE UNA CUOTA
@csrf_exempt
def registrar_pago_cuota(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        cuota_id = data.get('cuota_id')
        monto = float(data.get('monto'))
        metodo_id = int(data.get('metodo_pago_id'))

        cuota = get_object_or_404(CuotaPlanPago, pk=cuota_id)
        metodo = get_object_or_404(MetodoPago, pk=metodo_id)

        if cuota.estado != 'Pendiente':
            return JsonResponse({'status': 'error', 'mensaje': 'La cuota ya fue pagada o no es válida'})

        cuotas_anteriores = CuotaPlanPago.objects.filter(
            planpago=cuota.planpago,
            numerocuota__lt=cuota.numerocuota
        ).exclude(estado='Pagada')

        if cuotas_anteriores.exists():
            return JsonResponse({'status': 'error', 'mensaje': 'Debe pagar las cuotas anteriores antes de esta.'})

        Pago.objects.create(
            factura=cuota.planpago.factura,
            metodopago=metodo,
            monto=monto,
            fechapago=timezone.now(),
            numeroreferencia='Pago Manual desde Cuota',
            observaciones='Registro desde VerPagosPaciente'
        )

        cuota.estado = 'Pagada'
        cuota.fechapago = timezone.now()
        cuota.save()

        return JsonResponse({'status': 'ok', 'mensaje': 'Pago registrado correctamente'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=500)
