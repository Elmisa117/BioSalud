document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("togglePassword");
  const passField = document.getElementById("passwordField");

  // Mostrar/ocultar contraseña
  if (toggle && passField) {
    toggle.addEventListener("change", function () {
      passField.type = this.checked ? "text" : "password";
    });
  }

  // Manejo del formulario de login
  const loginForm = document.querySelector(".login-form form");
  if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = new FormData(this);

      fetch("", {
        method: "POST",
        body: formData
      })
        .then(response => {
          // Si no es JSON válido, lanza error
          if (!response.ok) {
            throw new Error("Error de servidor");
          }
          return response.json();
        })
        .then(data => {
          if (data.rol) {
            let url = "";
            switch (data.rol) {
              case "Administrador":
                url = "/admin/";
                break;
              case "Doctor":
                url = "/doctor/";
                break;
              case "Enfermera":
              case "Enfermería":
                url = "/enfermeria/";
                break;
              case "Caja":
                url = "/cajero/";
                break;
              default:
                url = "/inicio/";
            }
            window.location.href = url;
          } else {
            alert(data.error || "Credenciales incorrectas");
          }
        })
        .catch(error => {
          console.error("Error:", error);
          alert("Ocurrió un error al intentar iniciar sesión. Verifica tu conexión.");
        });
    });
  }
});
