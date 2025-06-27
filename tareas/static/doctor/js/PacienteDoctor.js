document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    const searchBySelect = document.querySelector('.search-select');
    const searchForm = searchInput ? searchInput.form : null;

    if (searchInput && searchForm && searchBySelect) {
        // Enviar el formulario cada vez que cambie el input o el criterio de búsqueda
        searchInput.addEventListener('input', function() {
            searchForm.submit();
        });

        searchBySelect.addEventListener('change', function() {
            searchForm.submit();
        });
    }

    // Manejo del botón registrar paciente (si existe)
    const registrarBtn = document.querySelector('.registrar-btn');
    if (registrarBtn) {
        registrarBtn.addEventListener('click', function() {
            alert('Función de registrar paciente será implementada');
        });
    }
});
