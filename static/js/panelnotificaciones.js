document.addEventListener("DOMContentLoaded", function() {
    obtenerNotificaciones();
});

async function obtenerNotificaciones() {
    try {
        const response = await fetch('/mis_notificaciones_data');

        if (!response.ok) {
            console.error(`Error de la API: ${response.status} ${response.statusText}`);
            mostrarMensajeError("No se pudieron cargar las notificaciones. Intenta de nuevo más tarde.");
            return;
        }

        const data = await response.json();
        renderizarNotificaciones(data.notificaciones);

    } catch (error) {
        console.error('Error al obtener notificaciones:', error);
        mostrarMensajeError("Hubo un problema de conexión. Por favor, verifica tu conexión a internet.");
    }
}

function renderizarNotificaciones(notificaciones) {
    const contenedor = document.getElementById('contenedor-notificaciones');
    contenedor.innerHTML = ''; // Limpiar el contenedor antes de renderizar

    if (notificaciones.length === 0) {
        const p = document.createElement('p');
        p.textContent = 'No tienes notificaciones nuevas.';
        p.classList.add('sin-notificaciones'); // Opcional: agrega una clase para estilizar
        contenedor.appendChild(p);
        return;
    }

    notificaciones.forEach(notificacion => {
        const divNotificacion = document.createElement('div');
        divNotificacion.classList.add('notificacion-item');
        
        divNotificacion.innerHTML = `
            <div class="notificacion-usuario">
                <span class="usuario-nombre">Notificación</span>
            </div>
            <div class="notificacion-contenido">
                <p>${notificacion.contenido}</p>
            </div>
            <div class="notificacion-fecha">
                <span class="fecha">${new Date(notificacion.fecha_creacion).toLocaleString()}</span>
            </div>
        `;
        
        contenedor.appendChild(divNotificacion);
    });
}

function mostrarMensajeError(mensaje) {
    const contenedor = document.getElementById('contenedor-notificaciones');
    contenedor.innerHTML = `<p class="error-mensaje">${mensaje}</p>`;
}