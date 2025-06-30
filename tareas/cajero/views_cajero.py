from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import traceback
import json
from datetime import datetime
from django.db.models import F, Value, ExpressionWrapper, DecimalField
from datetime import date
from django.contrib import messages  # Asegúrate de tener esto arriba
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
import os #esto agregue

from tareas.models import (
    Pacientes,
    Consultas,
    Consultaservicios,
    Hospitalizaciones,
    Hospitalizacionservicios,
    Metodospago,
    Facturas,
    Pagos,
    Planespago,
    Cuotasplanpago
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
def buscar_paciente_cajero(request):
    query = request.GET.get('q', '')
    pacientes = Pacientes.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(numerodocumento__icontains=query)  # <-- Aquí está el cambio
    ) if query else Pacientes.objects.all()
    return render(request, 'cajero/BuscarPaciente.html', {'pacientes': pacientes, 'query': query})

# 👁️ PERFIL DEL PACIENTE
def ver_paciente(request, id):
    paciente = get_object_or_404(Pacientes, pk=id)

    # Mostrar mensajes si viene un parámetro GET
    if request.GET.get("sin_servicios") == "1":
        messages.warning(request, "⚠️ El paciente no tiene servicios pendientes para facturar.")
    elif request.GET.get("error") == "1":
        messages.error(request, "❌ Error al verificar los servicios. Intenta nuevamente.")

    return render(request, 'cajero/PerfilPaciente.html', {'paciente': paciente})


def generar_factura(request, paciente_id):
    paciente = get_object_or_404(Pacientes, pk=paciente_id)

    # Consultas no facturadas
    consultas = Consultas.objects.filter(
        pacienteid=paciente,
        estado=True,
        facturado=False
    )
    consulta_ids = consultas.values_list('consultaid', flat=True)

    # Servicios de consultas no facturados
    consulta_servicios = Consultaservicios.objects.filter(
        consultaid_id__in=consulta_ids,
        estado=True,
        facturado=False
    )

    # Hospitalizaciones no facturadas
    hospitalizaciones = Hospitalizaciones.objects.filter(
        pacienteid=paciente,
        estado=True,
        facturado=False
    )
    hosp_ids = hospitalizaciones.values_list('hospitalizacionid', flat=True)

    # Servicios de hospitalización no facturados
    hospitalizacion_servicios = Hospitalizacionservicios.objects.filter(
        hospitalizacionid_id__in=hosp_ids,
        estado=True,
        facturado=False
    )

    # Verificar si no hay ningún servicio
    if not (consultas.exists() or consulta_servicios.exists() or hospitalizaciones.exists() or hospitalizacion_servicios.exists()):
        messages.warning(request, "⚠️ El paciente no tiene servicios pendientes para facturar.")
        return redirect('ver_paciente', id=paciente.pacienteid)

    # Métodos de pago activos
    metodos_pago = Metodospago.objects.filter(estado=True)

    return render(request, 'cajero/GenerarFactura.html', {
        'paciente': paciente,
        'metodos_pago': metodos_pago,
        'consultas': consultas,
        'consulta_servicios': consulta_servicios,
        'hospitalizaciones': hospitalizaciones,
        'hospitalizacion_servicios': hospitalizacion_servicios,
        'fecha_emision': timezone.now(),  # ✅ Agregado
    })



# 📅 GUARDAR FACTURA Y PLAN DE PAGO

@csrf_exempt
def guardar_factura_y_plan(request):
    if request.method == 'POST':
        try:
            data = request.POST

            # 📥 Datos principales
            numero = data.get('numeroFactura')
            fechaemision = timezone.now()
            paciente = Pacientes.objects.get(pk=int(data.get('paciente_id')))
            total = float(data.get('total'))
            metodo_pago = Metodospago.objects.get(pk=int(data.get('metodoPago')))
            monto_pagado = float(data.get('montoPagado', 0))
            observaciones = data.get('observaciones', '')

            # 📄 Crear factura
            factura = Facturas.objects.create(
                pacienteid=paciente,
                numerofactura=numero,
                fechaemision=fechaemision,
                subtotal=total,
                total=total,
                estado='Pagado' if monto_pagado >= total else 'Parcial',
                observaciones=observaciones,
                fecharegistro=timezone.now()
            )

            # 💰 Registrar pago
            Pagos.objects.create(
                facturaid=factura,
                metodopagoid=metodo_pago,
                monto=monto_pagado,
                fechapago=timezone.now(),
                observaciones=observaciones,
                fecharegistro=timezone.now(),
                estado=True
            )

            # 📆 Si se activó plan de pago
            if data.get('planPagoActivado') == 'true':
                cuotas_json = json.loads(data.get('planCuotasJSON', '[]'))
                plan = Planespago.objects.create(
                    facturaid=factura,
                    fechainicio=data.get('planFechaInicio'),
                    fechafin=data.get('planFechaFin'),
                    numerocuotas=int(data.get('planNumeroCuotas')),
                    montototal=float(data.get('planMontoTotal')),
                    observaciones='Plan de pago generado automáticamente',
                    frecuencia=data.get('frecuencia'),
                    estado='Activo',
                    fecharegistro=timezone.now()
                )

                # 💳 Crear cada cuota
                for cuota in cuotas_json:
                    Cuotasplanpago.objects.create(
                        planpagoid=plan,
                        numerocuota=cuota['numero'],
                        montocuota=cuota['monto'],
                        fechavencimiento=cuota['fecha'],
                        estado='Pendiente',
                        fecharegistro=timezone.now()
                    )

            # ✅ Marcar servicios como facturados
            consultas = Consultas.objects.filter(pacienteid=paciente, facturado=False)
            for consulta in consultas:
                consulta.facturado = True
                consulta.save()

                Consultaservicios.objects.filter(consultaid=consulta.consultaid, facturado=False).update(facturado=True)

            hospitalizaciones = Hospitalizaciones.objects.filter(pacienteid=paciente, facturado=False)
            for hosp in hospitalizaciones:
                hosp.facturado = True
                hosp.save()

                Hospitalizacionservicios.objects.filter(hospitalizacionid=hosp.hospitalizacionid, facturado=False).update(facturado=True)

            return JsonResponse({
                'success': True,
                'message': 'Factura y plan guardados correctamente.',
                'redirect_url': f'/cajero/ver_paciente/{paciente.pacienteid}/'
            })

        except Exception as e:
            print("🚨 Error al guardar factura y plan de pago:", e)
            return JsonResponse({'success': False, 'message': 'Error interno al guardar.'}, status=400)

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)



def verificar_servicios_json(request, paciente_id):
    consultas = Consultas.objects.filter(pacienteid=paciente_id, facturado=False, estado=True)
    hospitalizacion_servicios = Hospitalizacionservicios.objects.filter(
        hospitalizacionid__pacienteid=paciente_id, facturado=False, estado=True)

    tiene_servicios = consultas.exists() or hospitalizacion_servicios.exists()

    if tiene_servicios:
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({
            'status': 'empty',
            'mensaje': 'El paciente no tiene servicios pendientes para facturar.'
        })
    
# 📜 FUNCIÓN AUXILIAR: RESUMEN DE SERVICIOS DE UNA FACTURA
def resumen_servicios_factura(factura):
    try:
        resumenes = set()

        consultas = Consultas.objects.filter(paciente=factura.paciente, estado=True)
        for c in consultas:
            resumenes.add(f"Consulta {c.tipoconsulta}")

        consulta_ids = consultas.values_list('consultaid', flat=True)
        consulta_servicios = Consultaservicios.objects.filter(
            consultaid_id__in=consulta_ids, estado=True
        ).select_related('servicioid')

        for cs in consulta_servicios:
            resumenes.add(cs.servicioid.descripcion)

        hospitalizaciones = Hospitalizaciones.objects.filter(
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
    paciente = get_object_or_404(Pacientes, pk=paciente_id)

    # Obtener todos los planes de pago del paciente
    planes = Planespago.objects.filter(facturaid__pacienteid=paciente_id).prefetch_related('facturaid')

    metodos_pago = Metodospago.objects.filter(estado=True)

    planes_actualizados = []
    for plan in planes:
        # Obtener cuotas pendientes o pagadas ordenadas
        cuotas_ordenadas = plan.cuotasplanpago_set.filter(estado__in=['Pendiente', 'Pagada']).order_by('numerocuota')
        if cuotas_ordenadas.exists():
            plan.cuotas_ordenadas = cuotas_ordenadas
            plan.resumen_producto = resumen_servicios_factura(plan.facturaid)  # función que genera resumen visual
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

        cuota = get_object_or_404(Cuotasplanpago, pk=cuota_id)
        metodo = get_object_or_404(Metodospago, pk=metodo_id)

        if cuota.estado != 'Pendiente':
            return JsonResponse({'status': 'error', 'mensaje': 'La cuota ya fue pagada o no es válida.'})

        # Verificar cuotas anteriores impagas
        cuotas_anteriores = Cuotasplanpago.objects.filter(
            planpagoid=cuota.planpagoid,
            numerocuota__lt=cuota.numerocuota
        ).exclude(estado='Pagada')

        if cuotas_anteriores.exists():
            return JsonResponse({
                'status': 'error',
                'mensaje': 'Debe pagar las cuotas anteriores antes de esta.'
            })

        # Crear el pago
        pago = Pagos.objects.create(
            facturaid=cuota.planpagoid.facturaid,
            metodopagoid=metodo,
            monto=monto,
            fechapago=timezone.now(),
            numeroreferencia='Pago Manual desde Cuota',
            observaciones='Registro desde VerPagosPaciente',
            fecharegistro=timezone.now(),
            estado=True
        )

        # Actualizar cuota
        cuota.estado = 'Pagada'
        cuota.fechapago = timezone.now()
        cuota.pagoid = pago
        cuota.save()

        # ✅ Verificar si todas las cuotas del plan ya están pagadas
        cuotas_restantes = Cuotasplanpago.objects.filter(
            planpagoid=cuota.planpagoid,
        ).exclude(estado='Pagada')

        if not cuotas_restantes.exists():
            factura = cuota.planpagoid.facturaid
            factura.estado = 'Pagado'
            factura.save()

        return JsonResponse({'status': 'ok', 'mensaje': 'Pago registrado correctamente'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=500)
    
# ✅ BUSCAR PACIENTES EN TIEMPO REAL (JSON)
def buscar_pacientes_json(request):
    query = request.GET.get('q', '')
    pacientes = Pacientes.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(numerodocumento__icontains=query)
    )[:20]  # Limitar a 20 resultados opcionalmente

    data = []
    for p in pacientes:
        data.append({
            'id': p.pacienteid,
            'nombres': p.nombres,
            'apellidos': p.apellidos,
            'ci': p.numerodocumento,
            'fechanacimiento': p.fechanacimiento.strftime('%b. %d, %Y'),
            'telefono': p.telefono,
            'url': reverse('ver_paciente', args=[p.pacienteid])
        })

    return JsonResponse({'pacientes': data})

def ver_facturas_pagadas(request, paciente_id):
    paciente = Pacientes.objects.get(pacienteid=paciente_id)

    facturas = Facturas.objects.filter(
        pacienteid=paciente,
        estado__in=["Pagado", "Parcial"]
    ).order_by('-fechaemision')

    facturas_con_detalle = []
    for factura in facturas:
        plan = Planespago.objects.filter(facturaid=factura).first()

        # ✅ Aquí corregido
        cuotas = Cuotasplanpago.objects.filter(planpagoid=plan) if plan else Cuotasplanpago.objects.none()

        cuotas_pagadas = cuotas.filter(estado="Pagado")
        total_cuotas_pagadas = sum(c.montocuota for c in cuotas_pagadas)

        pagos_directos = Pagos.objects.filter(facturaid=factura)
        total_pagos_directos = sum(p.monto for p in pagos_directos)

        total_pagado = total_cuotas_pagadas + total_pagos_directos

        if factura.estado == "Parcial" and total_pagado >= factura.total:
            factura.estado = "Pagado"
            factura.save()

        facturas_con_detalle.append({
            'factura': factura,
            'cuotas': cuotas,
            'total_pagado': total_pagado,
        })

    return render(request, 'cajero/ver_facturas_pagadas.html', {
        'paciente': paciente,
        'facturas': facturas_con_detalle,
    })


def factura_detalle(request, factura_id):
    factura = Facturas.objects.get(pk=factura_id)
    return render(request, 'partials/detalle_factura_modal.html', {'factura': factura})


@csrf_exempt
def api_factura(request, paciente_id):
    try:
        print(f"🔍 Verificando servicios para paciente {paciente_id}")
        # Consultas no facturadas
        consultas = Consultas.objects.filter(pacienteid=paciente_id, facturado=False)
        consultas_data = [
            {
                'consulta_id': c.consultaid,
                'fecha': c.fechaconsulta.strftime('%Y-%m-%d'),
                'motivo': c.motivocita,
                'precio': float(c.costo or 0)
            }
            for c in consultas
        ]
        print(f"📋 Consultas encontradas: {len(consultas_data)}")

        # Servicios de consulta no facturados
        consulta_servicios = Consultaservicios.objects.filter(
            consultaid__pacienteid=paciente_id, facturado=False
        ).select_related('servicioid')
        consulta_servicios_data = [
            {
                'servicio__nombre': cs.servicioid.nombre,
                'servicio__costo': float(cs.servicioid.costo or 0)
            }
            for cs in consulta_servicios
        ]

        # Hospitalizaciones no facturadas
        hospitalizaciones = Hospitalizaciones.objects.filter(
            pacienteid=paciente_id,
            facturado=False
        ).select_related('habitacionid__tipohabitacionid')
        hospitalizaciones_data = []
        for h in hospitalizaciones:
            if not h.fechaingreso:
                continue
            fecha_alta = h.fechaalta or datetime.now()
            dias = max((fecha_alta.date() - h.fechaingreso.date()).days, 1)
            costo_diario = h.habitacionid.tipohabitacionid.costodiario
            total = dias * float(costo_diario)
            hospitalizaciones_data.append({
                'hospitalizacion_id': h.hospitalizacionid,
                'motivo': h.motivohospitalizacion,
                'dias': dias,
                'costo_diario': float(costo_diario),
                'total': round(total, 2)
            })
        print(f"🏥 Hospitalizaciones encontradas: {len(hospitalizaciones_data)}")

        # Servicios de hospitalización no facturados
        hosp_servicios = Hospitalizacionservicios.objects.filter(
            hospitalizacionid__pacienteid=paciente_id,
            facturado=False
        ).select_related('servicioid')
        hosp_servicios_data = [
            {
                'servicio__nombre': hs.servicioid.nombre,
                'servicio__costo': float(hs.servicioid.costo or 0)
            }
            for hs in hosp_servicios
        ]

        tiene_servicios = any([consultas_data, consulta_servicios_data, hospitalizaciones_data, hosp_servicios_data])
        print(f"✅ Tiene servicios: {tiene_servicios}")

        return JsonResponse({
            'consultas': consultas_data,
            'consultaservicios': consulta_servicios_data,
            'hospitalizaciones': hospitalizaciones_data,
            'hospitalizacionservicios': hosp_servicios_data,
            'tiene_servicios': tiene_servicios
        })

    except Exception as e:
        print(f"❌ Error en api_factura: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def factura_detalle(request, factura_id):
    factura = get_object_or_404(Facturas, pk=factura_id)

    plan = Planespago.objects.filter(facturaid=factura).first()
    cuotas = Cuotasplanpago.objects.filter(planpagoid=plan).order_by('numerocuota') if plan else []

    pagos_directos = Pagos.objects.filter(facturaid=factura)

    total_cuotas_pagadas = sum(c.montocuota for c in cuotas if c.estado == 'Pagado')
    total_pagos_directos = sum(p.monto for p in pagos_directos)
    total_pagado = total_cuotas_pagadas + total_pagos_directos

    html = render_to_string('cajero/detalle_factura_modal.html', {
        'factura': factura,
        'plan': plan,
        'cuotas': cuotas,
        'pagos_directos': pagos_directos,
        'total_pagos_directos': total_pagos_directos,
        'total_cuotas_pagadas': total_cuotas_pagadas,
        'total_pagado': total_pagado,
    })

    return HttpResponse(html)

