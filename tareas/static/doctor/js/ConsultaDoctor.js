document.addEventListener('DOMContentLoaded', function () {
    console.log("✅ JS CARGADO: ConsultaDoctor.js está ejecutándose");

    const form = document.querySelector('form');
    const motivo = document.getElementById('motivocita');
    const checkboxServicios = document.getElementById('requiere_servicio');
    const boxServicios = document.getElementById('servicio_box');
    const checkboxHospitalizacion = document.getElementById('requiere_hospitalizacion');
    const boxHospitalizacion = document.getElementById('hospitalizacion_box');

    const tipoHabitacionSelect = document.getElementById('tipo_habitacion');
    const btnBuscarHabitaciones = document.getElementById('btnBuscarHabitaciones');
    const habitacionesListaDiv = document.getElementById('habitaciones_lista');

    // Mostrar secciones si ya están marcadas al cargar
    if (checkboxServicios?.checked) boxServicios.style.display = 'block';
    if (checkboxHospitalizacion?.checked) boxHospitalizacion.style.display = 'block';

    // Mostrar/ocultar servicios
    checkboxServicios?.addEventListener('change', () => {
        boxServicios.style.display = checkboxServicios.checked ? 'block' : 'none';
    });

    // Mostrar/ocultar hospitalización
    checkboxHospitalizacion?.addEventListener('change', () => {
        boxHospitalizacion.style.display = checkboxHospitalizacion.checked ? 'block' : 'none';
    });

    // Validación del formulario
    if (form) {
        form.addEventListener('submit', function (e) {
            if (motivo && motivo.value.trim() === '') {
                alert('Por favor ingrese el motivo de la consulta.');
                motivo.focus();
                e.preventDefault();
                return;
            }

            if (checkboxServicios?.checked) {
                const servicio = document.getElementById('servicioid');
                const cantidad = document.getElementById('cantidad');

                if (!servicio.value) {
                    alert('Seleccione un servicio.');
                    servicio.focus();
                    e.preventDefault();
                    return;
                }

                if (!cantidad.value || parseInt(cantidad.value) < 1) {
                    alert('Ingrese una cantidad válida.');
                    cantidad.focus();
                    e.preventDefault();
                    return;
                }
            }

            if (checkboxHospitalizacion?.checked) {
                const tipoHab = tipoHabitacionSelect.value;
                const habitacionSeleccionada = document.querySelector('input[name="habitacionid"]:checked');

                if (!tipoHab) {
                    alert('Seleccione un tipo de habitación.');
                    tipoHabitacionSelect.focus();
                    e.preventDefault();
                    return;
                }

                if (!habitacionSeleccionada) {
                    alert('Seleccione una habitación disponible.');
                    e.preventDefault();
                    return;
                }
            }
        });
    }

    // Buscar habitaciones disponibles al hacer clic
    if (btnBuscarHabitaciones) {
        btnBuscarHabitaciones.addEventListener('click', function () {
            const tipoId = tipoHabitacionSelect.value;
            habitacionesListaDiv.innerHTML = '<em>Cargando habitaciones disponibles...</em>';

            if (!tipoId) {
                habitacionesListaDiv.innerHTML = '<span style="color:red;">⚠️ Debe seleccionar primero un tipo de habitación.</span>';
                return;
            }

            fetch(`/doctor/ajax/habitaciones_disponibles/${tipoId}/`)
                .then(res => res.json())
                .then(data => {
                    const habitaciones = data.habitaciones || [];

                    if (habitaciones.length === 0) {
                        habitacionesListaDiv.innerHTML = '<em>No hay habitaciones disponibles para este tipo.</em>';
                        return;
                    }

                    const grid = document.createElement('div');
                    grid.className = 'grid-habitaciones';

                    habitaciones.forEach(h => {
                        const card = document.createElement('div');
                        card.className = 'habitacion-card';

                        const radio = document.createElement('input');
                        radio.type = 'radio';
                        radio.name = 'habitacionid';
                        radio.value = h.id;
                        radio.id = `hab-${h.id}`;
                        radio.style.display = 'none';  // ocultamos el radio pero sigue funcional

                        const label = document.createElement('label');
                        label.className = 'habitacion-label';
                        label.setAttribute('for', `hab-${h.id}`);
                        label.innerHTML = `🛏️ <strong>Cama ${h.nombre}</strong>`;

                        card.appendChild(radio);
                        card.appendChild(label);
                        grid.appendChild(card);
                    });

                    habitacionesListaDiv.innerHTML = '';
                    habitacionesListaDiv.appendChild(grid);
                })
                .catch(err => {
                    console.error('❌ Error al cargar habitaciones:', err);
                    habitacionesListaDiv.innerHTML = '<span style="color:red;">Error al cargar habitaciones disponibles.</span>';
                });
        });
    }
});
