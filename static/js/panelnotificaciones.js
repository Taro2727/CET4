// Variable global para guardar el criterio de ordenación
let criterioNotificaciones = 'reciente';
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Cuando el documento HTML esté listo, ejecutamos todo
document.addEventListener("DOMContentLoaded", function() {
    // 1. Obtenemos las notificaciones del servidor en cuanto carga la página
    obtenerNotificaciones();

    // 2. Configuramos el menú para ordenar
    const menuOrdenar = document.getElementById('menu-ordenar');
    const ordenarBtn = document.getElementById('ordenar-btn');

    if (ordenarBtn && menuOrdenar) {
        // Mostrar/ocultar el menú al hacer clic en el botón
        ordenarBtn.addEventListener('click', () => {
            menuOrdenar.classList.toggle('oculto');
        });

        // Cambiar el criterio de ordenación al hacer clic en una opción del menú
        menuOrdenar.addEventListener('click', (e) => {
            if (e.target.tagName === 'LI') {
                criterioNotificaciones = e.target.dataset.orden;
                obtenerNotificaciones(); // Volvemos a cargar las notificaciones con el nuevo orden
                menuOrdenar.classList.add('oculto');
            }
        });

        // Ocultar el menú si se hace clic fuera de él
        document.addEventListener('click', (e) => {
            if (!ordenarBtn.contains(e.target) && !menuOrdenar.contains(e.target)) {
                menuOrdenar.classList.add('oculto');
            }
        });
    }
    const contenedorPrincipal = document.getElementById('contenedor-notificaciones');

    contenedorPrincipal.addEventListener('click', async function(event) {
        // Verificamos si el clic fue sobre un botón con la clase 'btn-eliminar'
        const botonEliminar = event.target.closest('.btn-eliminar');
        
        if (botonEliminar) {
            const notifId = botonEliminar.dataset.id;
            
            if (confirm("¿Estás seguro de que quieres eliminar esta notificación?")) {
                try {
                    // Le mandamos la orden de borrado a nuestro app.py
                    const response = await fetch(`/eliminar_notificacion/${notifId}`, {
                        method: 'DELETE',
                        headers: { 
                        'Content-Type': 'application/json', 
                        'X-CSRFToken': csrfToken 
                    },

                    });
                    const result = await response.json();
                    
                    if (result.success) {
                        // Si el servidor confirma el borrado, eliminamos la notificación de la pantalla
                        botonEliminar.closest('.notificacion-item').remove();
                    } else {
                        console.error('Error al eliminar:', result.error);
                    }
                } catch (error) {
                    console.error('Error de conexión:', error);
                }
            }
        }
    });
});


// --- FUNCIONES AUXILIARES ---

// Obtiene las notificaciones del servidor
async function obtenerNotificaciones() {
    try {
        const response = await fetch(`/mis_notificaciones_data?orden=${criterioNotificaciones}`);
        if (!response.ok) throw new Error('Error en la respuesta del servidor');
        
        const data = await response.json();
        renderizarNotificaciones(data.notificaciones);
    } catch (error) {
        console.error('Error al obtener notificaciones:', error);
        mostrarMensajeError("Hubo un problema de conexión.");
    }
}

// Dibuja las notificaciones en la pantalla
function renderizarNotificaciones(notificaciones) {
    const contenedor = document.getElementById('contenedor-notificaciones');
    contenedor.innerHTML = ''; // Limpiamos el contenedor

    if (!notificaciones || notificaciones.length === 0) {
        mostrarMensajeError('No tienes notificaciones nuevas.');
        return;
    }

    notificaciones.forEach(notificacion => {
        const divNotificacion = document.createElement('div');
        divNotificacion.classList.add('notificacion-item', notificacion.leida ? 'leida' : 'nueva');
        
        const labelLeida = notificacion.leida ? '' : '<span class="label-nueva">Nueva</span>';
        
        divNotificacion.innerHTML = `
            <div class="notificacion-usuario">
                <span class="usuario-nombre">Notificación</span>
                ${labelLeida}
            </div>
            <div class="notificacion-contenido">
                <p id="msj">${notificacion.mensaje}</p>
            </div>
            <button class="btn-eliminar" data-id="${notificacion.id_notif}">🗑️</button>
            <div class="notificacion-fecha">
                <span class="fecha">${new Date(notificacion.fecha).toLocaleString()}</span>
            </div>
        `;
        contenedor.appendChild(divNotificacion);
    });
}

// Muestra un mensaje de error o de "no hay notificaciones"
function mostrarMensajeError(mensaje) {
    const contenedor = document.getElementById('contenedor-notificaciones');
    contenedor.innerHTML = `<p class="error-mensaje">${mensaje}</p>`;
}