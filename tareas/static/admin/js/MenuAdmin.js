document.addEventListener("DOMContentLoaded", function () {
    const menuItems = document.querySelectorAll('.menu li');
    const mainContent = document.querySelector('.main-content');

    function obtenerSaludo() {
        const hora = new Date().getHours();
        if (hora >= 6 && hora < 12) {
            return "¡Buenos días";
        } else if (hora >= 12 && hora < 18) {
            return "¡Buenas tardes";
        } else {
            return "¡Buenas noches";
        }
    }

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            const opcion = item.textContent.trim();

            if (opcion === "Cerrar sesión") {
                const confirmar = confirm("¿Estás seguro de que deseas cerrar sesión?");
                if (confirmar) {
                    window.location.href = "/cerrar/";
                }
                return;
            }

            if (opcion === "Inicio") {
                const saludo = obtenerSaludo();
                mainContent.innerHTML = `
                    <div class="welcome">
                        <img src="/static/admin/img/bienvenido.png" alt="Bienvenido" class="welcome-img">
                        <h1>${saludo}, ${NOMBRE}!</h1>
                        <p>Rol asignado: <strong>${ROL}</strong></p>
                        <p>Selecciona una opción del menú para comenzar.</p>
                    </div>
                `;
            } else if (opcion === "Gestión de Personal") {
                window.location.href = "/admin/listar_personal/";
            } else if (opcion === "Servicios Médicos") {
                window.location.href = "/admin/servicios/";
            } else if (opcion === "Gestión de Habitaciones") {
                window.location.href = "/admin/habitaciones/";
            } else if ( opcion === "Métodos de Pago") {
                window.location.href = "/admin/metodos_pago/";
            } else if (opcion === "Control de Pacientes") {
                window.location.href = "/admin/listar_pacientes/";
            } else if (opcion === "Consultas y Emergencias") {
                window.location.href = "/admin/consultas/";
            } else if (opcion === "Gestión Financiera") {
                window.location.href = "/admin/facturas/";
            } else if (opcion === "Reportes y Estadísticas") {
                window.location.href = "/admin/reportes/";
            } else if (opcion === "Control de Accesos") {
                window.location.href = "/admin/accesos/";
            } else if (opcion === "Configuraciones Generales") {
                window.location.href = "/admin/configuraciones/";
            } else {
                mainContent.innerHTML = `<h1>${opcion}</h1><p>Contenido en desarrollo...</p>`;
            }
        });
    });
});
