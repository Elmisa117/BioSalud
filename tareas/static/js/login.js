document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("togglePassword");
  const passField = document.getElementById("passwordField");

  // Mostrar / ocultar contraseña
  toggle.addEventListener("change", function () {
    passField.type = this.checked ? "text" : "password";
  });

  // Enviar login por fetch
  document.querySelector('.login-form form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    fetch("", {
      method: "POST",
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.rol) {
          let url = "";
          switch (data.rol) {
            case "Administrador": url = "/admin/"; break;
            case "Doctor": url = "/doctor/"; break;
            case "Enfermería": url = "/enfermeria/"; break;
            case "Cajero": url = "/cajero/"; break;
            default: url = "/inicio/";
          }
          window.location.href = url;  // 👈 Redirige en la misma pestaña
        } else {
          alert(data.error || "Credenciales incorrectas");
        }
      })
      .catch(error => {
        console.error("Error:", error);
        alert("Error de conexión");
      });
  });
});
