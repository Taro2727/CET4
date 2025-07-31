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
//<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>
    const result = await res.json();

    if (res.ok && result.success) {
      alert('¡Código verificado correctamente!');

      if (result.success && result.redirigir=='registrar') {
        window.location.href = '/crearcuenta';
      }else if (result.success && result.redirigir=='cambiar_contra'){
        window.location.href = '/actualizar';
      }else{
        alert(result.error || 'hubo un problema (gav linea 27 verificarOTP)');
      }


    } else {
      alert(result.error || 'Hubo un problema con la verificación');
    }

  } catch (err) {
    console.error('Error en la petición:', err);
    alert('Error de red');
  }
});