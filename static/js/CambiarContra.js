//AGARRA EL FORMULARIO DEL CORREO DE CAMBIARCONTRA.HTML CNDO APRETAS EL BOTON
document.getElementById('correo-recuperacion').addEventListener('submit', async (e) => {
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


    const result = await res.json();

    if (res.ok) {
      alert('Código OTP enviado al mail');
      window.location.href = '/IngresarCodigo';
    } else {
      alert(result.error || 'Hubo un problema');
    }
  } catch (err) {
    console.error('Error en la petición:', err);
    alert('Error de red');
  }
});


document.getElementById('correo-recuperacion').addEventListener('submit', async (e) => {
  e.preventDefault(); // evita o frena q la pag se recargue

  const newpassword = document.getElementById('newpassword').value;
  const newconfirm = document.getElementById('newconfirm').value;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  try {
    const res = await fetch('/ActualizarContra', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ newpassword,newconfirm })
    });


    const result = await res.json();

    if (res.ok) {
      alert('cambiaste tu contraseña');
      window.location.href = '/';
    } else {
      alert(result.error || 'Hubo un problema');
    }
  } catch (err) {
    console.error('Error en la petición:', err);
    alert('Error de red');
  }
});

