document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modalPago");
  const cuotaIdInput = document.getElementById("cuotaIdSeleccionada");
  const montoInput = document.getElementById("montoPagoModal");
  const metodoInput = document.getElementById("metodoPagoModal");
  const confirmacionPagoContainer = document.getElementById("confirmacionPagoContainer");
  const btnConfirmar = document.getElementById("btnConfirmarPago");
  const radioConfirmacion = document.getElementById("confirmacionPagoRadio");

  // Aplicar formato solo-fecha a la columna 'Registrado' si es necesario
  document.querySelectorAll("td[data-fecha-completa]").forEach(td => {
    const fechaCompleta = td.dataset.fechaCompleta;
    td.textContent = formatearFechaSoloFecha(fechaCompleta);
  });

  // Mostrar modal al hacer clic en botón pagar
  document.querySelectorAll(".btn-pagar").forEach(btn => {
    btn.addEventListener("click", () => {
      const cuotaId = btn.dataset.cuota;
      const monto = parseFloat(btn.dataset.monto).toFixed(2);

      cuotaIdInput.value = cuotaId;
      montoInput.value = monto;
      montoInput.readOnly = true;

      confirmacionPagoContainer.style.display = "none";
      if (radioConfirmacion) radioConfirmacion.checked = false;

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

    if (!metodo) {
      mostrarToast("Debe seleccionar un método de pago.", "error");
      return;
    }

    if (requiereConfirmacion && !confirmado) {
      mostrarToast("Debe confirmar que recibió el monto.", "error");
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
        mostrarToast("Pago registrado correctamente", "exito");
        setTimeout(() => location.reload(), 2000);
      } else {
        mostrarToast("Error al registrar el pago: " + data.mensaje, "error");
      }
    })
    .catch(() => mostrarToast("Error de red al intentar registrar el pago.", "error"));
  });
});

// Función para extraer solo la parte de la fecha
function formatearFechaSoloFecha(fechaHora) {
  // Espera formato tipo "2025-06-15 04:55"
  return fechaHora.split(" ")[0];
}

// Cerrar modal
function cerrarModal() {
  document.getElementById("modalPago").style.display = "none";
}

// CSRF token helper
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

// Mostrar notificación toast
function mostrarToast(mensaje, tipo = "error") {
  const toast = document.getElementById("toast");
  const texto = document.getElementById("toast-mensaje");
  const icono = document.getElementById("toast-icon");

  toast.className = "toast visible";

  if (tipo === "exito") {
    toast.classList.add("exito");
    icono.textContent = "✅";
  } else if (tipo === "info") {
    toast.classList.add("informativo");
    icono.textContent = "ℹ️";
  } else {
    toast.classList.remove("exito", "informativo");
    icono.textContent = "❌";
  }

  texto.textContent = mensaje;

  setTimeout(() => {
    toast.classList.remove("visible", "exito", "informativo");
  }, 4000);
}

