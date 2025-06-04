document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("togglePassword");
  const passField = document.getElementById("passwordField");
  const messageBox = document.getElementById("loginMessage");

  toggle.addEventListener("change", function () {
    passField.type = this.checked ? "text" : "password";
  });

  document.getElementById('loginForm').addEventListener('submit', function (e) {
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
          messageBox.textContent = "¡Bienvenido! Redirigiendo...";
          messageBox.className = "login-message success";
          messageBox.style.display = "block";
          setTimeout(() => { window.location.href = url; }, 800);
        } else {
          messageBox.textContent = data.error || "Credenciales incorrectas";
          messageBox.className = "login-message error";
          messageBox.style.display = "block";
          setTimeout(() => { messageBox.style.display = "none"; }, 3000);
        }
      })
      .catch(error => {
        console.error("Error:", error);
        messageBox.textContent = "Error de conexión";
        messageBox.className = "login-message error";
        messageBox.style.display = "block";
        setTimeout(() => { messageBox.style.display = "none"; }, 3000);
      });
  });
});
