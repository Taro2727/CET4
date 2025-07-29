document.getElementById('otp').addEventListener('submit', async (e) => {
  e.preventDefault(); // evita o frena q la pag se recargue

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

    if (result.success) {
        alert('¡Código verificado correctamente!');  
        window.location.href = '/actualizar';     
    } else {
      alert(result.error || 'Hubo un problema con la verificación');
    }
  } catch (err) {
    console.error('Error en la petición:', err);
    alert('Error de red');
  }
});