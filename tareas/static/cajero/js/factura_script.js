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

    let total = 0;
    const pacienteId = document.getElementById("paciente_id")?.value;

    if (pacienteId) {
        fetch(`/cajero/api/factura/${pacienteId}/`)
            .then(res => res.json())
            .then(data => {
                document.getElementById("nombrePaciente").value = data.paciente.nombre;
                document.getElementById("telefonoPaciente").value = data.paciente.telefono;
                document.getElementById("direccionPaciente").value = data.paciente.direccion;
                document.getElementById("fechaEmision").valueAsDate = new Date();
                document.getElementById("numeroFactura").value = "FACT-" + Math.floor(100000 + Math.random() * 900000);

                const tbody = document.querySelector("#tablaServicios tbody");
                tbody.innerHTML = "";
                total = 0;

                data.servicios.forEach(s => {
                    total += parseFloat(s.subtotal);
                    tbody.insertAdjacentHTML("beforeend", 
                        `<tr>
                            <td>${s.descripcion}</td>
                            <td>${s.cantidad}</td>
                            <td>${parseFloat(s.precio).toFixed(2)} Bs</td>
                            <td>${parseFloat(s.subtotal).toFixed(2)} Bs</td>
                        </tr>`
                    );
                });

                document.getElementById("totalPagar").textContent = `${total.toFixed(2)} Bs`;
                totalHidden.value = total.toFixed(2);
            });
    }

    metodoPago.addEventListener("change", toggleVerificacionManual);
    montoPagado.addEventListener("input", handlePagoParcial);
    numeroCuotas.addEventListener("change", generarCuotas);
    frecuenciaCuota.addEventListener("change", () => {
        actualizarComboCuotas();
        generarCuotas();
    });
    fechaPrimeraCuota.addEventListener("change", generarCuotas);

    function toggleVerificacionManual() {
        const selectedOption = metodoPago.options[metodoPago.selectedIndex];
        const requiere = selectedOption?.dataset.requiereVerificacion === 'true' ||
                         selectedOption?.textContent.toLowerCase().includes("qr") ||
                         selectedOption?.textContent.toLowerCase().includes("transferencia");

        const verificacionManual = document.getElementById("verificacionManual");
        const radioConfirmacion = document.querySelector('input[name="confirmacionPago"]');

        verificacionManual.style.display = requiere ? "block" : "none";
        if (radioConfirmacion) {
            radioConfirmacion.required = requiere;
            radioConfirmacion.checked = false;
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
        let maxCuotas = 2;

        if (frecuencia === "quincenal") maxCuotas = 4;
        else if (frecuencia === "semanal") maxCuotas = 8;

        numeroCuotas.innerHTML = '<option value="">-- Selecciona --</option>';
        for (let i = 1; i <= maxCuotas; i++) {
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
        let fechaInicio = new Date(hoy);

        if (frecuencia === "mensual") fechaInicio.setDate(hoy.getDate() + 30);
        else if (frecuencia === "quincenal") fechaInicio.setDate(hoy.getDate() + 15);
        else if (frecuencia === "semanal") fechaInicio.setDate(hoy.getDate() + 7);

        fechaPrimeraCuota.value = fechaInicio.toISOString().split('T')[0];

        listaCuotas.innerHTML = "";
        const encabezado = document.createElement("div");
        encabezado.className = "cuota-item";
        encabezado.innerHTML = `
            <strong>Cuota</strong>
            <strong>Fecha</strong>
            <strong>Monto</strong>
            <strong>Estado</strong>`;
        listaCuotas.appendChild(encabezado);

        const cuotaBaseEntera = Math.floor(saldo / cuotas);
        const ultimaCuota = (saldo - cuotaBaseEntera * (cuotas - 1)).toFixed(2);
        const planCuotas = [];

        for (let i = 0; i < cuotas; i++) {
            let fecha = new Date(fechaInicio);
            if (frecuencia === "mensual") fecha.setMonth(fecha.getMonth() + i);
            if (frecuencia === "quincenal") fecha.setDate(fecha.getDate() + i * 15);
            if (frecuencia === "semanal") fecha.setDate(fecha.getDate() + i * 7);

            const monto = (i === cuotas - 1) ? ultimaCuota : cuotaBaseEntera.toFixed(2);

            planCuotas.push({
                numero: i + 1,
                fecha: fecha.toISOString().split('T')[0],
                monto: parseFloat(monto)
            });

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
        document.getElementById("planFechaInicio").value = planCuotas[0].fecha;
        document.getElementById("planFechaFin").value = planCuotas[planCuotas.length - 1].fecha;
        document.getElementById("fechaUltimaCuota").value = planCuotas[planCuotas.length - 1].fecha.split('-').reverse().join('/');
        document.getElementById("planMontoTotal").value = saldo.toFixed(2);
        document.getElementById("planCuotasJSON").value = JSON.stringify(planCuotas);
        document.getElementById("frecuenciaHidden").value = frecuencia;
    }

    document.getElementById("formFactura").addEventListener("submit", function (e) {
        e.preventDefault();
        const totalFactura = parseFloat(totalHidden.value);
        const pagado = parseFloat(montoPagado.value) || 0;

        if (pagado > totalFactura) {
            mostrarMensaje("❌ El monto pagado no puede ser mayor al total de la factura.");
            montoPagado.classList.add("input-error");
            montoPagado.focus();
            return;
        }

        const selectedOption = metodoPago.options[metodoPago.selectedIndex];
        if (selectedOption?.dataset.requiereVerificacion === 'true') {
            const confirmacion = document.querySelector('input[name="confirmacionPago"]:checked');
            if (!confirmacion) {
                alert("Por favor, confirma que el monto fue recibido.");
                return;
            }
        }

        const formData = new FormData(this);
        fetch(this.action, { method: "POST", body: formData })
            .then(res => res.ok ? res.json() : Promise.reject("Error en el servidor"))
            .then(response => {
                mostrarMensaje("✅ ¡Factura guardada exitosamente!", true);
                if (response.redirect_url) {
                    setTimeout(() => {
                        window.location.href = response.redirect_url;
                    }, 2000);
                } else {
                    setTimeout(() => location.reload(), 2500);
                }
            })
            .catch(err => {
                console.error("Error al guardar la factura:", err);
                mostrarMensaje("❌ Ocurrió un error al guardar la factura.");
            });
    });

    toggleVerificacionManual();
});

function mostrarMensaje(texto, exito = false) {
    let toast = document.getElementById("toastMensaje");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toastMensaje";
        document.body.appendChild(toast);
    }

    toast.textContent = texto;
    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.right = "20px";
    toast.style.padding = "12px 20px";
    toast.style.borderRadius = "8px";
    toast.style.backgroundColor = exito ? "#28a745" : "#ffc107";
    toast.style.color = "white";
    toast.style.fontWeight = "bold";
    toast.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";
    toast.style.zIndex = 9999;
    toast.style.opacity = 1;
    toast.style.transition = "opacity 0.5s ease";

    setTimeout(() => {
        toast.style.opacity = 0;
    }, 3000);
}

function verificarYGenerarFactura(pacienteId) {
    fetch(`/cajero/verificar_servicios/${pacienteId}/`)
        .then(res => res.ok ? res.json() : Promise.reject(`HTTP ${res.status}`))
        .then(data => {
            if (data.status === 'ok') {
                window.location.href = `/cajero/generar_factura/${pacienteId}/`;
            } else {
                mostrarMensaje(data.mensaje || "El Paciente no se hizo ningún Servicio");
            }
        })
        .catch(err => {
            console.error("Error al verificar servicios:", err);
            mostrarMensaje("⚠️ Ocurrió un error al verificar los servicios del paciente.");
        });
}

function cancelarFactura() {
    window.history.back();
}
