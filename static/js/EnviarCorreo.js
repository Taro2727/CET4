//AGARRA EL FORMULARIO DEL CORREO DE CAMBIARCONTRA.HTML CNDO APRETAS EL BOTON
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('correo-recuperacion');
  const email = document.getElementById("email").value; //x algun motivo no se usa (averiguar dsps)
  // localStorage.setItem("userEmail", email); // Guarda el email //PROBLEMA (GUARDAR EN PYTHON)
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault(); // evita o frena q la pag se recargue

      const email = document.getElementById('email').value;
      const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

      try {
        const res = await fetch('/CambiarContra', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          body: JSON.stringify({ email })
        });

        //aca es la division (aca abajo se redirije a  ingresar el codigo)
        const result = await res.json();

        if (res.ok) { //desde aca
          alert('Código OTP enviado al mail');
          window.location.href = '/IngresarCodigo';
        } else {
          alert(result.error || 'Hubo un problema');
        }
      } catch (err) {
          console.error('Error en la petición:', err);
          alert('Error de red'); //hasta aca no me acuerdo perdon :_(
        }
    });
  }
});