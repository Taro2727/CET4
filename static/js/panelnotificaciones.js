
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
        `;
        
        contenedor.appendChild(divNotificacion);
    });
}

function mostrarMensajeError(mensaje) {
    const contenedor = document.getElementById('contenedor-notificaciones');
    contenedor.innerHTML = `<p class="error-mensaje">${mensaje}</p>`;
}