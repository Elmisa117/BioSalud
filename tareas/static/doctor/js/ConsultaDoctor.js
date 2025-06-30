document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const motivo = document.getElementById('motivocita');

    if (form) {
        form.addEventListener('submit', function (e) {
            if (motivo && motivo.value.trim() === '') {
                alert('Por favor ingrese el motivo de la consulta.');
                motivo.focus();
                e.preventDefault();  // evita envío si está vacío
            }
        });
    }
});
