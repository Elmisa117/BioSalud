// 👉 Versión actualizada de factura_script.js

document.addEventListener("DOMContentLoaded", function () {
    const metodoPago = document.getElementById("metodoPago");
    const montoPagado = document.getElementById("montoPagado");
    const estadoPago = document.getElementById("estadoPago");
    const estadoTexto = document.getElementById("estadoTexto");
    const montoRestante = document.getElementById("montoRestante");
    const planPagoSection = document.getElementById("planPagoSection");
    const numeroCuotas = document.getElementById("numeroCuotas");
    const frecuenciaCuota = document.getElementById("frecuenciaCuota");
    const fechaPrimeraCuota = document.getElementById("fechaPrimeraCuota");
    const cronogramaPagos = document.getElementById("cronogramaPagos");
    const listaCuotas = document.getElementById("listaCuotas");
    const totalHidden = document.getElementById("totalInputHidden");
    const pacienteId = document.getElementById("paciente_id")?.value;

    let total = 0;

    if (pacienteId) {
        fetch(`/cajero/api/factura2/${pacienteId}/`)
            .then(res => res.ok ? res.json() : Promise.reject(`HTTP ${res.status}`))
            .then(data => {
                const tbody = document.querySelector("#tablaServicios tbody");
                tbody.innerHTML = "";
                total = 0;
                const servicios = [];

                data.consultas.forEach(item => {
                    const precio = parseFloat(item.precio) || 0;
                    servicios.push({
                        descripcion: `Consulta (Consulta Externa) - Motivo: ${item.motivo}`,
                        cantidad: 1,
                        precio: precio,
                        subtotal: precio
                    });
                });

                data.consultaservicios.forEach(item => {
                    const precio = parseFloat(item.servicio__costo) || 0;
                    const nombre = item.servicio__nombre || "Servicio indefinido";
                    servicios.push({
                        descripcion: `Servicio Médico: ${nombre}`,
                        cantidad: 1,
                        precio: precio,
                        subtotal: precio
                    });
                });

                data.hospitalizaciones.forEach(item => {
                    const dias = parseInt(item.dias) || 1;
                    const totalHosp = parseFloat(item.total) || 0;
                    servicios.push({
                        descripcion: `Hospitalización Privada (${dias} día${dias > 1 ? 's' : ''}) - Motivo: ${item.motivo}`,
                        cantidad: dias,
                        precio: (totalHosp / dias).toFixed(2),
                        subtotal: totalHosp.toFixed(2)
                    });
                });

                data.hospitalizacionservicios.forEach(item => {
                    const precio = parseFloat(item.servicio__costo) || 0;
                    const nombre = item.servicio__nombre || "Servicio indefinido";
                    servicios.push({
                        descripcion: `Servicio Médico: ${nombre} (Hospitalización)`,
                        cantidad: 1,
                        precio: precio,
                        subtotal: precio
                    });
                });

                if (servicios.length === 0) {
                    mostrarMensaje("⚠️ No hay servicios pendientes para facturar.");
                    return;
                }

                servicios.forEach(s => {
                    total += parseFloat(s.subtotal);
                    tbody.insertAdjacentHTML("beforeend", `
                        <tr>
                            <td>${s.descripcion}</td>
                            <td>${s.cantidad}</td>
                            <td>${parseFloat(s.precio).toFixed(2)} Bs</td>
                            <td>${parseFloat(s.subtotal).toFixed(2)} Bs</td>
                        </tr>`);
                });

                document.getElementById("totalPagar").textContent = `${total.toFixed(2)} Bs`;
                totalHidden.value = total.toFixed(2);
                document.getElementById("numeroFactura").value = "FACT-" + Math.floor(100000 + Math.random() * 900000);
            })
            .catch(err => {
                console.error("Error al cargar servicios:", err);
                mostrarMensaje("⚠️ Error al verificar los servicios del paciente.");
            });
    }

    metodoPago?.addEventListener("change", toggleVerificacionManual);
    montoPagado?.addEventListener("input", handlePagoParcial);
    numeroCuotas?.addEventListener("change", generarCuotas);
    frecuenciaCuota?.addEventListener("change", () => {
        actualizarComboCuotas();
        generarCuotas();
    });
    fechaPrimeraCuota?.addEventListener("change", generarCuotas);

    function toggleVerificacionManual() {
        const selected = metodoPago.options[metodoPago.selectedIndex];
        const requiere = selected?.dataset.requiereVerificacion === 'true';
        const verificacion = document.getElementById("verificacionManual");
        const radio = document.querySelector('input[name="confirmacionPago"]');

        verificacion.style.display = requiere ? "block" : "none";
        if (radio) {
            radio.required = requiere;
            radio.checked = false;
        }
    }

    function handlePagoParcial() {
        const pagado = parseFloat(montoPagado.value) || 0;
        const saldo = total - pagado;

        if (pagado >= total) {
            estadoPago.style.display = "none";
            planPagoSection.style.display = "none";
            cronogramaPagos.style.display = "none";
            document.getElementById("planPagoActivado").value = "false";
        } else if (pagado > 0) {
            estadoPago.style.display = "flex";
            estadoTexto.textContent = "⚠️ Pago Parcial";
            montoRestante.textContent = `Saldo pendiente: ${saldo.toFixed(2)} Bs`;
            planPagoSection.style.display = "block";
            document.getElementById("planPagoActivado").value = "true";
            actualizarComboCuotas();
            generarCuotas();
        } else {
            estadoPago.style.display = "none";
            planPagoSection.style.display = "none";
            cronogramaPagos.style.display = "none";
            document.getElementById("planPagoActivado").value = "false";
        }

        montoPagado.classList.remove("input-error");
    }

    function actualizarComboCuotas() {
        const frecuencia = frecuenciaCuota.value;
        let max = 2;
        if (frecuencia === "quincenal") max = 4;
        else if (frecuencia === "semanal") max = 8;

        numeroCuotas.innerHTML = '<option value="">-- Selecciona --</option>';
        for (let i = 1; i <= max; i++) {
            const opt = document.createElement("option");
            opt.value = i;
            opt.textContent = `${i} ${i === 1 ? "cuota" : "cuotas"}`;
            numeroCuotas.appendChild(opt);
        }
    }

    function generarCuotas() {
        const pagado = parseFloat(montoPagado.value) || 0;
        const saldo = total - pagado;
        const cuotas = parseInt(numeroCuotas.value);
        const frecuencia = frecuenciaCuota.value;

        if (!cuotas || saldo <= 0) {
            cronogramaPagos.style.display = "none";
            return;
        }

        const hoy = new Date();
        let inicio = new Date(hoy);
        if (frecuencia === "mensual") inicio.setDate(hoy.getDate() + 30);
        if (frecuencia === "quincenal") inicio.setDate(hoy.getDate() + 15);
        if (frecuencia === "semanal") inicio.setDate(hoy.getDate() + 7);

        fechaPrimeraCuota.value = inicio.toISOString().split('T')[0];

        listaCuotas.innerHTML = "";
        const cuotaFija = Math.floor(saldo / cuotas);
        const ultima = (saldo - cuotaFija * (cuotas - 1)).toFixed(2);
        const plan = [];

        for (let i = 0; i < cuotas; i++) {
            const fecha = new Date(inicio);
            if (frecuencia === "mensual") fecha.setMonth(inicio.getMonth() + i);
            if (frecuencia === "quincenal") fecha.setDate(inicio.getDate() + i * 15);
            if (frecuencia === "semanal") fecha.setDate(inicio.getDate() + i * 7);

            const monto = (i === cuotas - 1) ? ultima : cuotaFija.toFixed(2);
            plan.push({ numero: i + 1, fecha: fecha.toISOString().split('T')[0], monto: parseFloat(monto) });

            listaCuotas.innerHTML += `
                <div class="cuota-item">
                    <div>Cuota ${i + 1}</div>
                    <div>${fecha.toLocaleDateString("es-ES")}</div>
                    <div><strong>${monto} Bs</strong></div>
                    <div>⏳ Pendiente</div>
                </div>`;
        }

        cronogramaPagos.style.display = "block";
        document.getElementById("planNumeroCuotas").value = cuotas;
        document.getElementById("planFechaInicio").value = plan[0].fecha;
        document.getElementById("planFechaFin").value = plan[plan.length - 1].fecha;
        document.getElementById("fechaUltimaCuota").value = plan[plan.length - 1].fecha.split('-').reverse().join('/');
        document.getElementById("planMontoTotal").value = saldo.toFixed(2);
        document.getElementById("planCuotasJSON").value = JSON.stringify(plan);
        document.getElementById("frecuenciaHidden").value = frecuencia;
    }

    document.getElementById("formFactura")?.addEventListener("submit", function (e) {
        e.preventDefault();
        const pagado = parseFloat(montoPagado.value) || 0;
        if (pagado > total) {
            mostrarMensaje("❌ El monto pagado no puede superar el total.");
            montoPagado.classList.add("input-error");
            return;
        }

        const requiere = metodoPago.options[metodoPago.selectedIndex]?.dataset.requiereVerificacion === 'true';
        if (requiere && !document.querySelector('input[name="confirmacionPago"]:checked')) {
            alert("Debes confirmar que el monto fue recibido.");
            return;
        }

        const formData = new FormData(this);
        fetch(this.action, { method: "POST", body: formData })
            .then(res => res.json())
            .then(data => {
                mostrarMensaje("✅ ¡Factura guardada exitosamente!", true);
                setTimeout(() => window.location.href = data.redirect_url || "/cajero/", 2000);
            })
            .catch(err => {
                console.error("Error al guardar factura:", err);
                mostrarMensaje("❌ Error al guardar la factura.");
            });
    });

    toggleVerificacionManual();
});

function verificarYGenerarFactura(pacienteId) {
    fetch(`/cajero/verificar_servicios/${pacienteId}/`)
        .then(res => res.ok ? res.json() : Promise.reject(`HTTP ${res.status}`))
        .then(data => {
            if (data.status === 'ok') {
                window.location.href = `/cajero/generar_factura/${pacienteId}/`;
            } else {
                mostrarMensaje(data.mensaje || "El paciente no tiene servicios pendientes para facturar.");
            }
        })
        .catch(err => {
            console.error("Error al verificar servicios:", err);
            mostrarMensaje("⚠️ Ocurrió un error al verificar los servicios del paciente.");
        });
}

function mostrarMensaje(texto, exito = false) {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.className = "toast";
        document.body.appendChild(toast);
    }

    toast.textContent = texto;
    toast.className = "toast show";
    toast.style.backgroundColor = exito ? "#28a745" : "#ffc107";

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

function cancelarFactura() {
    window.history.back();
}
