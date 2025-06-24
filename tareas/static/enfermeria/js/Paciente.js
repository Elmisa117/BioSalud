let pacientes = [];
const jsonScript = document.getElementById("datos-pacientes");

// Cargar datos desde el script JSON embebido
if (jsonScript) {
    try {
        pacientes = JSON.parse(jsonScript.textContent);
        console.log("✅ Pacientes cargados:", pacientes);
    } catch (error) {
        console.error("❌ Error al parsear los datos de pacientes:", error);
    }
}

const filtro = document.getElementById("filtro");
const criterio = document.getElementById("criterio");
const tablaPacientes = document.getElementById("tabla-pacientes");

criterio.addEventListener("input", filtrarPacientes);

// Función para filtrar pacientes según el criterio
function filtrarPacientes() {
    const tipoFiltro = filtro.value;
    const texto = criterio.value.toLowerCase();

    const resultados = pacientes.filter(p => {
        if (tipoFiltro === "nombre") {
            return `${p.nombres || ''} ${p.apellidos || ''}`.toLowerCase().includes(texto);
        } else {
            return (p.numero_documento || '').toLowerCase().includes(texto);
        }
    });

    mostrarPacientes(resultados);
}

// Función para mostrar la lista de pacientes
function mostrarPacientes(lista) {
    tablaPacientes.innerHTML = "";

    if (!lista || lista.length === 0) {
        tablaPacientes.innerHTML = `<tr><td colspan="3">No se encontraron resultados.</td></tr>`;
        return;
    }

    lista.forEach(p => {
        const fila = document.createElement("tr");

        // Columna Nombre Completo
        const tdNombre = document.createElement("td");
        tdNombre.textContent = `${p.nombres || ''} ${p.apellidos || ''}`;

        // Columna Cédula
        const tdCedula = document.createElement("td");
        tdCedula.textContent = p.numero_documento || '';

        // Columna Acciones
        const tdAcciones = document.createElement("td");

        // Botón Perfil
        const btnPerfil = document.createElement("button");
        btnPerfil.textContent = "Perfil";
        btnPerfil.className = "btn-accion";
        btnPerfil.onclick = () => {
            // Corregir la URL para el botón de perfil
            window.location.href = `/enfermeria/pacientes/perfil/${p.id}/`;
        };

        tdAcciones.appendChild(btnPerfil);

        fila.appendChild(tdNombre);
        fila.appendChild(tdCedula);
        fila.appendChild(tdAcciones);

        tablaPacientes.appendChild(fila);
    });
}

// Mostrar pacientes al cargar si hay datos
if (pacientes.length > 0) {
    mostrarPacientes(pacientes);
}

// Botón registrar paciente
function registrarPaciente() {
    window.location.href = '/enfermeria/pacientes/registro/';
}
