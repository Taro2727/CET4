document.getElementById('otp').addEventListener('submit', async (e) => {
  e.preventDefault();

  const cod = document.getElementById('cod').value;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  try {
<<<<<<< HEAD
    const res = await fetch('/Verificar_codigo', {
=======
    // 1. Verificar el código OTP
    const res = await fetch('/verificar_codigo', {
>>>>>>> bde7f753eb2cf331007ec5adc6de0248ad6a666a
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ cod: cod })
    });

    const result = await res.json();

    if (result.exito) {
      // El servidor dice que el código es correcto, ahora vemos a dónde ir.
      const destino = result.redirigir;

      if (destino === '/crearcuenta') {
        alert('¡Correo verificado! Ahora completa tu registro.');
        window.location.href = destino;
      } else if (destino === '/actualizar') {
        alert('¡Código correcto! Ahora puedes cambiar tu contraseña.');
        window.location.href = destino;
      } else if (destino === 'indexhomeoinicio') {
        // --- ESTA ES LA CONDICIÓN QUE FALTABA ---
        // No es necesario un alert, simplemente redirigimos.
        window.location.href = '/indexhomeoinicio'; 
      } else {
        // Si el servidor envía una redirección desconocida.
        alert('Respuesta desconocida del servidor.');
      }
    } else {
      // Si result.exito es false, mostramos el error del servidor.
      alert(result.error || 'Hubo un problema con la verificación');
    }

  } catch (err) {
    console.error('Error en la petición:', err);
    alert('Error de red. Revisa la consola para más detalles.');
  }
});