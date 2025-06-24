document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", function (e) {
        const ta = document.getElementById("ta").value.trim();
        const fc = parseInt(document.getElementById("fc").value.trim(), 10);
        const fr = parseInt(document.getElementById("fr").value.trim(), 10);
        const temp = parseFloat(document.getElementById("temp").value.trim());
        const spo2 = parseInt(document.getElementById("spo2").value.trim(), 10);

        // Validaciones básicas
        const errores = [];

        if (!/^\d{2,3}\/\d{2,3}$/.test(ta)) {
            errores.push("TA debe tener el formato correcto (ej. 120/80)");
        }
        if (isNaN(fc) || fc < 30 || fc > 200) {
            errores.push("FC debe estar entre 30 y 200.");
        }
        if (isNaN(fr) || fr < 5 || fr > 60) {
            errores.push("FR debe estar entre 5 y 60.");
        }
        if (isNaN(temp) || temp < 30.0 || temp > 45.0) {
            errores.push("Temperatura debe estar entre 30.0°C y 45.0°C.");
        }
        if (isNaN(spo2) || spo2 < 50 || spo2 > 100) {
            errores.push("SpO₂ debe estar entre 50% y 100%.");
        }

        if (errores.length > 0) {
            e.preventDefault(); // Detener el envío del formulario
            alert("⚠️ Errores en los signos vitales:\n\n" + errores.join("\n"));
            return;
        }

        // Preparar JSON solo si todo es válido
        const signos = {
            TA: ta,
            FC: fc,
            FR: fr,
            Temp: temp,
            SpO2: spo2
        };

        const jsonString = JSON.stringify(signos);
        const signosInput = document.getElementById("signos_vitales");
        signosInput.value = jsonString;
    });
});
