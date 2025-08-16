const modal = document.getElementById('modal1');
const btn = document.querySelector('openModalBtn');
const span = document.querySelector('closeModalBtn');

// Función para abrir el modal
btn.onclick = function() {
    modal.style.display = 'block';
}
// Función para cerrar el modal
span.onclick = function() {
    modal.style.display = 'none';
}
// Cerrar el modal al hacer clic fuera de él
window.onclick = function(event) {
  if (event.target === modal) {
    modal.style.display = 'none';
  }
}
