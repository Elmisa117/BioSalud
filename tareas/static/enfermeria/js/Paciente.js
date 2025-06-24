let pacientes = [];
const jsonScript = document.getElementById("datos-pacientes");

if (jsonScript) {
    try {
        pacientes = JSON.parse(jsonScript.textContent);
        console.log(" Pacientes cargados:", pacientes);
    } catch (error) {
        console.error(" Error al parsear los datos de pacientes:", error);
    }
}

const filtro = document.getElementById("filtro");
const criterio = document.getElementById("criterio");
const tablaPacientes = document.getElementById("tabla-pacientes");

criterio.addEventListener("input", filtrarPacientes);

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

function mostrarPacientes(lista) {
    tablaPacientes.innerHTML = "";

    if (!lista || lista.length === 0) {
        tablaPacientes.innerHTML = `<tr><td colspan="3">No se encontraron resultados.</td></tr>`;
        return;
    }

    lista.forEach(p => {
        const fila = document.createElement("tr");

        // Columna Nombre
        const tdNombre = document.createElement("td");
        tdNombre.textContent = `${p.nombres || ''} ${p.apellidos || ''}`;

        // Columna Cédula
        const tdCedula = document.createElement("td");
        tdCedula.textContent = p.numero_documento || '';

        // Columna Acciones
        const tdAcciones = document.createElement("td");

        // Botón Actualizar
        const btnActualizar = document.createElement("button");
        btnActualizar.textContent = "Actualizar";
        btnActualizar.className = "btn-accion";
        btnActualizar.onclick = () => editarPaciente(p.id);

        // Botón Ficha Clínico
        const btnFicha = document.createElement("button");
        btnFicha.textContent = "Ficha Clínico";
        btnFicha.className = "btn-accion amarillo";
        btnFicha.onclick = () => {
        window.location.href = `/enfermeria/ficha_clinico/${p.id}/`;

        };

        // Botón Historial
        const btnHistorial = document.createElement("button");
        btnHistorial.textContent = "Historial";
        btnHistorial.className = "btn-accion morado";
        btnHistorial.onclick = () => {
            window.location.href = `/enfermeria/historial/${p.id}/`;
        };

        tdAcciones.appendChild(btnActualizar);
        tdAcciones.appendChild(btnFicha);
        tdAcciones.appendChild(btnHistorial);

        fila.appendChild(tdNombre);
        fila.appendChild(tdCedula);
        fila.appendChild(tdAcciones);

        tablaPacientes.appendChild(fila);
    });
}

if (pacientes.length > 0) {
    mostrarPacientes(pacientes);
}

function registrarPaciente() {
    window.location.href = '/enfermeria/pacientes/registro/';
}

function editarPaciente(id) {
    window.location.href = `/enfermeria/pacientes/registro/?id=${id}`;
}
