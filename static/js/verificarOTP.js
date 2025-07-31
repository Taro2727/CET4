document.getElementById('otp').addEventListener('submit', async (e) => {
  e.preventDefault();

  const cod = document.getElementById('cod').value;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  try {
    // 1. Verificar el código OTP
    const res = await fetch('/Verificar_codigo', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ cod })
    });

    const result = await res.json();

    if (res.ok && result.success && result.redirigir === 'ini_ses') {
      // 2. Si el OTP es correcto, ahora hace el login real
      const verificarRes = await fetch('/verificar', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        }
      });
      const verificarResult = await verificarRes.json();

      if (verificarRes.ok && verificarResult.exito) {
        window.location.href = '/indexhomeoinicio';
      } else {
        alert(verificarResult.error || 'Error al iniciar sesión');
      }
    } else if (result.success && result.redirigir === 'registrar') {
      window.location.href = '/crearcuenta';
    } else if (result.success && result.redirigir === 'cambiar_contra') {
      window.location.href = '/actualizar';
    } else {
      alert(result.error || 'hubo un problema (gav linea 27 verificarOTP)');
    }
  } catch (err) {
    console.error('Error en la petición:', err);
    alert('Error de red');
  }
});