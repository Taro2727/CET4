document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("modal1");
  const btn = document.getElementById("openModalBtn");
  const span = document.querySelector(".closeModalBtn");

  // Abrir modal
  btn.onclick = () => {
    modal.style.display = "flex"; // o "block" según tu CSS
  };

  // Cerrar modal
  span.onclick = () => {
    modal.style.display = "none";
  };

  // Cerrar al hacer clic afuera
  window.onclick = (event) => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  };
});
