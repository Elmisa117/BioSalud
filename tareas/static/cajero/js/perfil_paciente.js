// ✅ Verifica si el paciente tiene servicios pendientes y redirige si corresponde
function verificarYGenerarFactura(pacienteId) {
  fetch(`/cajero/verificar_servicios/${pacienteId}/`)
    .then(response => {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then(data => {
      if (data.status === 'ok') {
        // ✅ Redirige al formulario de generación de factura
        window.location.href = `/cajero/generar_factura/${pacienteId}/`;
      } else {
        // ❌ Redirige con parámetro de advertencia si no hay servicios
        window.location.href = `/cajero/ver_paciente/${pacienteId}/?sin_servicios=1`;
      }
    })
    .catch(error => {
      console.error("❌ Error al verificar servicios:", error);
      // 🔁 Redirige con error si falla la verificación
      window.location.href = `/cajero/ver_paciente/${pacienteId}/?error=1`;
    });
}
