document.addEventListener('DOMContentLoaded', function() {
    const formFicha = document.getElementById('form-ficha');
    
    formFicha.addEventListener('submit', function(e) {
        e.preventDefault();  // Evitar que el formulario se envíe de manera tradicional

        // Crear el objeto FormData con los datos del formulario
        const formData = new FormData(formFicha);

        // Enviar los datos al servidor usando fetch y AJAX
        fetch("{% url 'ficha_clinico_doctor' %}", {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())  // Recibir la respuesta del servidor en formato JSON
        .then(data => {
            // Si la respuesta contiene HTML, actualizamos el contenido de la tabla
            if (data.html) {
                document.getElementById('tabla-fichas-container').innerHTML = data.html;
            }
            // Limpiar el formulario después de enviar los datos
            formFicha.reset(); 
        })
        .catch(error => console.error('Error:', error));  // Manejo de errores
    });
});
