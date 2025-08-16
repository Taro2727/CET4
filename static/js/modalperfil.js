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
  //condicional del menu de opciones
  if (valorSeleccionado === 1){

  }else if(valorSeleccionado === 2){

  }else if(valorSeleccionado === 3){

  }else{

  }
  
}//llave principal de la funcion MostrarAvatar