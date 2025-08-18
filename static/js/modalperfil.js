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


//mostrar avatar

async function MostrarAvatar() {
  const selectElement = document.getElementById('avatarSelect');
  const valorSeleccionado = selectElement.value;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  //fetch a python
  const respuesta=await fetch('/cambiar_avatar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ valorSeleccionado})
    });
    const result = await respuesta.json();
    if (result.success) {
        alert('se cambio tu avatar');

        window.location.href = '/perfil';
    } else {
        alert(result.error || "No se pudo cambiar");
}

  
}//llave principal de la funcion MostrarAvatar


//aca esta la funcion de cambiar nombre de usuario
document.getElementById("loginForm").addEventListener("submit", async function(event) {

  event.preventDefault();

  const nombre = document.getElementById("new-name").value;
  const password = document.getElementById("password").value;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  const respuesta = await fetch("/cambiar_nombre", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    body: JSON.stringify({ nombre, password })
  });

  const resultado = await respuesta.json();

  if (resultado.success) {
    // Redirige a la página para ingresar el código OTP
    window.location.href = '/perfil';
  } else {
    document.getElementById("mensaje").textContent = resultado.error || "No se pudo enviar el código OTP";
  }
  
  
});