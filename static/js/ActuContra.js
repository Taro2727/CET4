
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('correo-recuperacion');
    if (form) {
      form.addEventListener('submit', async (e) => {
      e.preventDefault();

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
          body: JSON.stringify({ newpassword, newconfirm })
        });

        const result = await res.json();

        if (res.ok) {
          window.location.href = '/';
        } else {
          console.error('Error')
        }
      } catch (err) {
        console.error('Error en la petición:', err);
      }
    });
  }
});
