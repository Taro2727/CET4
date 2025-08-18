
let criterioNotificaciones = 'reciente';
document.addEventListener("DOMContentLoaded", function() {
    obtenerNotificaciones();
    const menuOrdenarNotificaciones = document.getElementById('menu-ordenar');
    const ordenarNotificacionesBtn = document.getElementById('ordenar-btn');

    if (ordenarNotificacionesBtn && menuOrdenarNotificaciones) {
        ordenarNotificacionesBtn.addEventListener('click', () => {
            menuOrdenarNotificaciones.classList.toggle('oculto');
        });
    menuOrdenarNotificaciones.addEventListener('click', (e) => {
            if (e.target.tagName === 'LI') {
                const nuevoCriterio = e.target.dataset.orden;
                if (nuevoCriterio !== criterioNotificaciones) {
                    criterioNotificaciones = nuevoCriterio;
                    obtenerNotificaciones(); // Volvemos a obtener y renderizar
                }
                menuOrdenarNotificaciones.classList.add('oculto');
            }
        });

        document.addEventListener('click', (e) => {
            if (!ordenarNotificacionesBtn.contains(e.target) && !menuOrdenarNotificaciones.contains(e.target)) {
                menuOrdenarNotificaciones.classList.add('oculto');
            }
        });
    }
    const listaNotificaciones = document.getElementById('contenedor-notificaciones');
    listaNotificaciones.addEventListener('click', async function(event) {
        if (event.target.closest('.btn-eliminar')) {
            const botonEliminar = event.target.closest('.btn-eliminar');
            const notifId = botonEliminar.dataset.id;
            
            if (confirm("¿Estás seguro de que quieres eliminar esta notificación?")) {
                try {
                    const response = await fetch(`/eliminar_notificacion/${notifId}`, {
                        method: 'DELETE'
                    });
                    const result = await response.json();
                    
                    if (result.success) {
                        // Eliminar el elemento del DOM
                        const itemAEliminar = botonEliminar.closest('.notificacion-item');
                        if (itemAEliminar) {
                            itemAEliminar.remove();
                        }
                    } else {
                        console.error('Error al eliminar la notificación:', result.error);
                        alert('No se pudo eliminar la notificación: ' + result.error);
                    }
                } catch (error) {
                    console.error('Error al conectar con el servidor:', error);
                    alert('Hubo un problema al intentar eliminar la notificación.');
                }
            }
        }
    });
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
        const notificacionesOrdenadas = ordenarNotificaciones(data.notificaciones, criterioNotificaciones);
        renderizarNotificaciones(notificacionesOrdenadas);

    } catch (error) {
        console.error('Error al obtener notificaciones:', error);
        mostrarMensajeError("Hubo un problema de conexión. Por favor, verifica tu conexión a internet.");
    }
}


function ordenarNotificaciones(notificaciones, criterio) {
    // Creamos una copia del array para no modificar el original directamente.
    const notificacionesOrdenadas = [...notificaciones];
    if (criterio === 'reciente') {
        // Ordenamos en orden descendente (más recientes primero)
        notificacionesOrdenadas.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
    } else if (criterio === 'antiguo') {
        // Ordenamos en orden ascendente (más antiguos primero)
        notificacionesOrdenadas.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));
    }
    return notificacionesOrdenadas;
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
        
         // Asignar una clase CSS dependiendo del estado de 'leida'
        if (notificacion.leida) {
            divNotificacion.classList.add('leida');
        } else {
            divNotificacion.classList.add('nueva');
        }

        // Crear el cartelito "Nueva" si la notificación no ha sido leída
        const labelLeida = notificacion.leida 
            ? '' // Si está leída, el cartel está vacío
            : '<span class="label-nueva">Nueva</span>';
        
        divNotificacion.innerHTML = `
            <div class="notificacion-usuario">
                <span class="usuario-nombre">Notificación</span>
                ${labelLeida}
            </div>
            <div class="notificacion-contenido">
                <p>${notificacion.mensaje}</p>
            </div>
            <div class="notificacion-fecha">
                <span class="fecha">${new Date(notificacion.fecha).toLocaleString()}</span>
            </div>
            <button class="btn-eliminar" data-id="${notificacion.id_notif}">
            🗑️
            </button>
        `;
        const btnEliminar = divNotificacion.querySelector('.btn-eliminar');
        if (btnEliminar) {
            btnEliminar.addEventListener('click', async function() {
                const notifId = this.dataset.id;
                
                if (confirm("¿Estás seguro de que quieres eliminar esta notificación?")) {
                    try {
                        const response = await fetch(`/eliminar_notificacion/${notifId}`, {
                            method: 'DELETE'
                        });
                        const result = await response.json();
                        
                        if (result.success) {
                            // Eliminar el elemento del DOM
                            this.closest('.notificacion-item').remove();
                        } else {
                            console.error('Error al eliminar la notificación:', result.error);
                            alert('No se pudo eliminar la notificación: ' + result.error);
                        }
                    } catch (error) {
                        console.error('Error al conectar con el servidor:', error);
                        alert('Hubo un problema al intentar eliminar la notificación.');
                    }
                }
            });
        }
        contenedor.appendChild(divNotificacion);
    });
}

function mostrarMensajeError(mensaje) {
    const contenedor = document.getElementById('contenedor-notificaciones');
    contenedor.innerHTML = `<p class="error-mensaje">${mensaje}</p>`;
}