document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", function (event) {
        const accion = event.submitter?.value;

        // Validamos solo si es acción "guardar"
        if (accion === "guardar") {
            event.preventDefault(); // Prevenimos el envío inmediato

            // Simulamos espera o validación (puedes quitar este setTimeout si conectas a backend real)
            setTimeout(() => {
                alert(" Paciente registrado exitosamente.");

                // Redirigir a la pantalla de lista de pacientes
                window.location.href = "/enfermeria/pacientes/";
            }, 300);
        }
    });
});
