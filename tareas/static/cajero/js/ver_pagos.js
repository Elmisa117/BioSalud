document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modalPago");
  const cuotaIdInput = document.getElementById("cuotaIdSeleccionada");
  const montoInput = document.getElementById("montoPagoModal");
  const metodoInput = document.getElementById("metodoPagoModal");
  const confirmacionPagoContainer = document.getElementById("confirmacionPagoContainer");
  const btnConfirmar = document.getElementById("btnConfirmarPago");
  const radioConfirmacion = document.getElementById("confirmacionPagoRadio");

  // Mostrar modal o mensaje elegante según estado de la cuota
  document.querySelectorAll(".btn-pagar").forEach(btn => {
    btn.addEventListener("click", () => {
      if (btn.classList.contains("cuota-bloqueada")) {
        mostrarErrorDebajoMonto("Debe pagar las cuotas anteriores antes de esta.");
        return;
      }

      const cuotaId = btn.dataset.cuota;
      const monto = parseFloat(btn.dataset.monto).toFixed(2);

      cuotaIdInput.value = cuotaId;
      montoInput.value = monto;
      montoInput.readOnly = true;

      confirmacionPagoContainer.style.display = "none";
      if (radioConfirmacion) radioConfirmacion.checked = false;

      limpiarErrorDebajoMonto();

      modal.style.display = "flex";
    });
  });

  // Mostrar u ocultar confirmación según el método de pago
  metodoInput.addEventListener("change", () => {
    const texto = metodoInput.options[metodoInput.selectedIndex].text.toLowerCase();
    const requiereConfirmacion = texto.includes("qr") || texto.includes("transferencia");
    confirmacionPagoContainer.style.display = requiereConfirmacion ? "block" : "none";
    if (!requiereConfirmacion && radioConfirmacion) radioConfirmacion.checked = false;
  });

  // Confirmar pago
  btnConfirmar.addEventListener("click", () => {
    const cuotaId = cuotaIdInput.value;
    const monto = montoInput.value;
    const metodo = metodoInput.value;
    const metodoTexto = metodoInput.options[metodoInput.selectedIndex].text.toLowerCase();
    const requiereConfirmacion = metodoTexto.includes("qr") || metodoTexto.includes("transferencia");
    const confirmado = radioConfirmacion && radioConfirmacion.checked;

    limpiarErrorDebajoMonto();

    if (!metodo) {
      mostrarErrorDebajoMonto("Debe seleccionar un método de pago.");
      return;
    }

    if (requiereConfirmacion && !confirmado) {
      mostrarErrorDebajoMonto("Debe confirmar que recibió el monto.");
      return;
    }

    fetch("/cajero/registrar_pago_cuota/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify({
        cuota_id: cuotaId,
        monto: monto,
        metodo_pago_id: metodo
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "ok") {
          mostrarToast("✅ Pago registrado correctamente", "exito");

          const contenedor = document.getElementById("detalleFacturaContenido");
          if (contenedor && contenedor.dataset.facturaId) {
            const facturaId = contenedor.dataset.facturaId;
            fetch(`/cajero/factura/${facturaId}/detalle/`)
              .then(res => res.text())
              .then(html => {
                contenedor.innerHTML = html;
              });
          } else {
            setTimeout(() => location.reload(), 2000);
          }
        } else {
          mostrarErrorDebajoMonto(data.mensaje || "Error al registrar el pago.");
        }
      })
      .catch(() => mostrarErrorDebajoMonto("Error de red al intentar registrar el pago."));
  });
});

function formatearFechaSoloFecha(fechaHora) {
  return fechaHora.split(" ")[0];
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    document.cookie.split(";").forEach(cookie => {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(trimmed.slice(name.length + 1));
      }
    });
  }
  return cookieValue;
}

function mostrarToast(mensaje, tipo = "error") {
  const toast = document.getElementById("toast");
  const texto = document.getElementById("toast-mensaje");
  const icono = document.getElementById("toast-icon");

  toast.className = "toast";

  if (tipo === "exito") {
    toast.classList.add("exito");
    icono.textContent = "✅";
  } else if (tipo === "info") {
    toast.classList.add("info");
    icono.textContent = "ℹ️";
  } else {
    icono.textContent = "❌";
  }

  texto.textContent = mensaje;
  toast.classList.add("visible");
  setTimeout(() => {
    toast.classList.remove("visible");
  }, 4000);
}

// Nueva función para mostrar errores dentro del modal, debajo del campo Monto
function mostrarErrorDebajoMonto(mensaje) {
  let errorDiv = document.getElementById("mensajeErrorPago");
  if (!errorDiv) {
    errorDiv = document.createElement("div");
    errorDiv.id = "mensajeErrorPago";
    errorDiv.style.color = "#c0392b";
    errorDiv.style.margin = "10px 0";
    errorDiv.style.fontWeight = "bold";
    montoInput.parentElement.appendChild(errorDiv);
  }
  errorDiv.textContent = mensaje;
}

function limpiarErrorDebajoMonto() {
  const errorDiv = document.getElementById("mensajeErrorPago");
  if (errorDiv) errorDiv.remove();
}