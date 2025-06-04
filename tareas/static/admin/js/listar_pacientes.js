window.addEventListener('DOMContentLoaded', () => {
  const nombreInput = document.getElementById('buscar-nombre');
  const ciInput = document.getElementById('buscar-ci');
  const tabla = document.getElementById('tabla-pacientes');

  function buscar() {
    const params = new URLSearchParams({
      ajax: '1',
      nombre: nombreInput.value,
      ci: ciInput.value
    });
    fetch(`?${params.toString()}`)
      .then(r => r.text())
      .then(html => {
        tabla.innerHTML = html;
      });
  }

  if (nombreInput && ciInput) {
    nombreInput.addEventListener('input', buscar);
    ciInput.addEventListener('input', buscar);
  }
});
