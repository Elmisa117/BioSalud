document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", function (e) {
        // Capturar los valores de los signos vitales
        const signos = {
            TA: document.getElementById("ta").value,
            FC: document.getElementById("fc").value,
            FR: document.getElementById("fr").value,
            Temp: document.getElementById("temp").value,
            SpO2: document.getElementById("spo2").value
        };

        // Eliminar campos vacíos
        Object.keys(signos).forEach(key => {
            if (!signos[key]) {
                delete signos[key];
            }
        });

        // Convertir a JSON
        const jsonString = JSON.stringify(signos);

        // Insertar en el campo oculto
        const signosInput = document.getElementById("signos_vitales");
        signosInput.value = jsonString;

        // Validar que el JSON sea válido
        try {
            JSON.parse(jsonString);
        } catch (err) {
            e.preventDefault(); // Evita que se envíe el formulario
            alert("⚠️ El formato de los signos vitales no es válido. Por favor, revisa los campos.");
        }
    });
});
