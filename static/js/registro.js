document.addEventListener('DOMContentLoaded', function() {
    const formRegistro = document.getElementById('registro');

    if (formRegistro) {
        formRegistro.addEventListener('submit', async function(event) {
            event.preventDefault();

            const nombre = document.getElementById('name').value;
            const contra = document.getElementById('password').value;
            const confirmcontra = document.getElementById('confirm').value;
            const mensajehtml = document.getElementById("mensaje") //agarra el lugar en donde hay q poner u mensaje en el html
            // Validación de la contraseña
            // Asegúrate de que las contraseñas coincidan
            if (contra !== confirmcontra) {
               mensajehtml.textContent ="Error: Las contraseñas no coinciden.";
                return;
            }

            // Expresión regular para validar la contraseña
            // Mínimo 8 caracteres, una mayúscula y un número.
            const regex = /^(?=.*[A-Z])(?=.*[0-9]).{8,}$/;

            if (!regex.test(contra)) {
                mensajehtml.textContent ="Error: La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.";
                return;
            }


            const datos = {
                name: nombre,
                contra: contra,
                confcontra: confirmcontra
            };

            // Lee el token CSRF desde la etiqueta <meta>
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            try {
                const response = await fetch('/crearcuenta/registrar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(datos)
                });
                //<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

                const resultado = await response.json();

                if (response.ok) {
                    // Si el registro es exitoso
                    alert(resultado.mensaje); // "Usuario registrado correctamente"
                    window.location.href = '/iniciarsesion'; // Redirige al login
                } else {
                    // Si hay un error (ej: email ya existe, contraseñas no coinciden)
                    alert("Error: " + resultado.error);
                }
            } catch (error) {
                console.error('Error en la petición fetch:', error);
                alert('Ocurrió un error de red. Inténtalo de nuevo.');
            }
        });
    }
});