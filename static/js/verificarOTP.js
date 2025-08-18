document.getElementById('otp').addEventListener('submit', async (e) => {
  e.preventDefault();

  const cod = document.getElementById('cod').value;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  try {
    // 1. Verificar el código OTP
    const res = await fetch('/verificar_codigo', {
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

        window.location.href = destino;

      } else if (destino === '/actualizar') {
        alert('¡Código correcto! Ahora puedes cambiar tu contraseña.');
        window.location.href = destino;

      } else if (destino === 'indexhomeoinicio') {
        // --- ESTA ES LA CONDICIÓN QUE FALTABA ---
        // No es necesario un alert, simplemente redirigimos.
        window.location.href = '/indexhomeoinicio';
      } else if (destino === '/configuracion') {
        alert('¡Contraseña actualizada con éxito!');
        window.location.href = destino;

      } else if (destino === '/upgradear') {
        // Aquí mandas el POST real al backend
        // Ahora no usamos sessionStorage porque el servidor guarda id_usuario y rol_usuario en la session
        console.log("Ascendiendo usando datos guardados en session del servidor");

        const res2 = await fetch('/upgradear', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken
          }
          // No enviamos body porque el backend tomará los datos de session
        });

        if (!res2.ok) {
          alert('Error en la petición para ascender el usuario.');
          return;
        }

        const result2 = await res2.json();
        if (result2.success) {
          alert('¡Usuario ascendido con éxito!');
          window.location.href = '/paneladmin';
        } else {
          alert(result2.error || 'Hubo un problema al ascender el usuario');
        }
        
      }else if (destino === '/down') {
         // Aquí mandas el POST real al backend
        // Ahora no usamos sessionStorage porque el servidor guarda id_usuario y rol_usuario en la session
        console.log("degradando usando datos guardados en session del servidor");

        const res2 = await fetch('/down', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json' 
          }
          // No enviamos body porque el backend tomará los datos de session
        });

        if (!res2.ok) {
          alert('Error en la petición para degradar el usuario.');
          return;
        }

        const result2 = await res2.json();
        if (result2.success) {
          alert('¡Usuario degradado con éxito!');
          window.location.href = '/paneladmin';
        } else {
          alert(result2.error || 'Hubo un problema al degradar el usuario');
        }

      } else if (destino === '/eliminar_usuario'){
        console.log("eliminando usuario usando datos guardados en session del servidor");

        const res2 = await fetch('/eliminar_usuario', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json' 
          }
          // No enviamos body porque el backend tomará los datos de session
        });

        if (!res2.ok) {
          alert('Error en la petición para degradar el usuario.');
          return;
        }

        const result2 = await res2.json();
        if (result2.success) {
          alert('¡Usuario eliminado con éxito!');
          window.location.href = '/paneladmin';
        } else {
          alert(result2.error || 'Hubo un problema al degradar el usuario');
        }
      } else {
        // Si el servidor envía una redirección desconocida.
        alert('Respuesta desconocida del servidor.');
      }

    } else {
      // Si result.exito es false, mostramos el error del servidor.
     document.getElementById('textito').textContent= result.error || 'Hubo un problema con la verificación' ;
    }

  } catch (err) {
    console.error('Error en la petición:', err);
    alert('Error de red. Revisa la consola para más detalles.');
  }
});
