document.addEventListener("DOMContentLoaded", function () {
  const input = document.querySelector('input[name="q"]');
  const form = document.querySelector(".search-form");
  const tbody = document.querySelector(".tabla-pacientes tbody");

  function renderPacientes(pacientes) {
    tbody.innerHTML = "";

    if (pacientes.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center;">No se encontraron resultados.</td></tr>`;
      return;
    }

    pacientes.forEach(p => {
      const row = `
        <tr>
          <td>${p.nombres}</td>
          <td>${p.apellidos}</td>
          <td>${p.ci}</td>
          <td>${p.fechanacimiento}</td>
          <td>${p.telefono}</td>
          <td><a href="${p.url}" class="btn-ver">Ver</a></td>
        </tr>
      `;
      tbody.insertAdjacentHTML("beforeend", row);
    });
  }

  function guardarEnHistorial(paciente) {
    let historial = JSON.parse(localStorage.getItem("historialPacientes")) || [];

    historial = historial.filter(p => p.id !== paciente.id);
    historial.unshift(paciente);

    if (historial.length > 5) {
      historial = historial.slice(0, 5);
    }

    localStorage.setItem("historialPacientes", JSON.stringify(historial));
  }

  function mostrarHistorial() {
    const historial = JSON.parse(localStorage.getItem("historialPacientes")) || [];
    renderPacientes(historial);
  }

  function buscarPaciente(query) {
    fetch(`/cajero/buscar_pacientes_json/?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        if (data.pacientes.length > 0) {
          guardarEnHistorial(data.pacientes[0]);
        }
        renderPacientes(data.pacientes);
      });
  }

  input.addEventListener("input", function () {
    const query = input.value.trim();
    if (query === "") {
      mostrarHistorial();
    } else {
      buscarPaciente(query);
    }
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const query = input.value.trim();
    if (query !== "") {
      buscarPaciente(query);
    } else {
      mostrarHistorial();
    }
  });

  // Mostrar historial al cargar
  mostrarHistorial();
});
