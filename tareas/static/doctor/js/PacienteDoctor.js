document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('.search-input');
    const searchBySelect = document.querySelector('.search-select');
    const searchForm = searchInput ? searchInput.form : null;

    if (searchInput && searchForm && searchBySelect) {
        // Ya no se envía el formulario en cada letra escrita (evita comportamiento molesto)
        // Solo actualizamos criterios si el usuario cambia el tipo de búsqueda
        searchBySelect.addEventListener('change', function () {
            searchForm.submit();
        });
    }

    // Manejo del botón registrar paciente (si existe)
    const registrarBtn = document.querySelector('.registrar-btn');
    if (registrarBtn) {
        registrarBtn.addEventListener('click', function () {
            alert('Función de registrar paciente será implementada');
        });
    }
});
