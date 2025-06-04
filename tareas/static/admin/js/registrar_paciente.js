// JS para registrar/editar pacientes
window.addEventListener('DOMContentLoaded', () => {
  const firstInput = document.querySelector('.form-grid input');
  if (firstInput) {
    firstInput.focus();
  }

  const tipo = document.getElementById('id_tipodocumento');
  const campoOtro = document.getElementById('id_otrodocumento').closest('.form-field');

  function toggleOtro() {
    if (tipo && campoOtro) {
      if (tipo.value === 'Otro') {
        campoOtro.style.display = '';
      } else {
        campoOtro.style.display = 'none';
        document.getElementById('id_otrodocumento').value = '';
      }
    }
  }

  if (tipo && campoOtro) {
    toggleOtro();
    tipo.addEventListener('change', toggleOtro);
  }
});
