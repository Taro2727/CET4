document.getElementById('otp').addEventListener('submit', async (e) => {
  e.preventDefault();

  const cod = document.getElementById('cod').value;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  try {
    const res = await fetch('/Verificar_codigo', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ cod })
    });

    const result = await res.json();

    if (res.ok && result.success) {
      alert('¡Código verificado correctamente!');

      if (result.redirigir) {
        // ⚡️ Es registro → redirigimos al formulario para completar nombre y contraseña
        window.location.href = result.redirigir;
      } else {
        // 🔁 Es recuperación → redirigimos al cambio de contraseña
        window.location.href = '/ActualizarContra';
      }

    } else {
      alert(result.error || 'Hubo un problema con la verificación');
    }

  } catch (err) {
    console.error('Error en la petición:', err);
    alert('Error de red');
  }
});