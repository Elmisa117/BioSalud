document.addEventListener("DOMContentLoaded", function () {
  const botonesDetalle = document.querySelectorAll('.btn-ver-detalle');

  botonesDetalle.forEach(btn => {
    btn.addEventListener('click', function () {
      const facturaId = this.dataset.id;

      // 🔁 Usamos la ruta semántica
      fetch(`/cajero/factura/${facturaId}/detalle/`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Error al obtener los detalles de la factura');
          }
          return response.text();
        })
        .then(html => {
          const contenido = document.getElementById('detalleFacturaContenido');
          contenido.innerHTML = html;

          const modal = new bootstrap.Modal(document.getElementById('detalleFacturaModal'));
          modal.show();
        })
        .catch(error => {
          console.error('Error:', error);
          alert('No se pudieron cargar los detalles de la factura.');
        });
    });
  });
});
