window.onload = async function () {
    // Se mantiene la carga inicial de comentarios
    await cargarComentarios();
};

async function cargarComentarios() {
    const id_mat = document.getElementById('id_mat').value;
    const response = await fetch('/get_comentario?id_mat='+encodeURIComponent(id_mat)+ '&t=' + Date.now());
    const comentarios = await response.json();
    const section = document.getElementById('commentsSection');
    section.innerHTML = ''; // Limpia la sección antes de recargar

    comentarios.forEach(c => {
        // Se mantiene la clase original del contenedor principal: "comment"
        const div = document.createElement('div');
        div.classList.add('comment');

        // Se agrega la separación de divs pero sin cambiar la estructura visible inicial
        div.innerHTML = `
            <span class="usuario-comentario"><strong>${c.usuario || "Anónimo"}</strong>:</span>
            <br>
            <span class="titulo-comentario"><b>${c.titulo}</b></span>
            <span class="texto-comentario">${c.cont}</span>
            <br>
            <button class="btn-responder" onclick="responder('${c.id_post}', '${c.usuario || "Anónimo"}')">Responder</button>
            <button class="btn-ver-respuestas" onclick="mostrarRespuestas('${c.id_post}')">Ver respuestas</button>
            <div  br class="area-responder" id="area-responder-${c.id_post}"></div>
            <div class="respuestas" id="respuestas-${c.id_post}" style="display: none;"></div>
        `  ;
        
        section.appendChild(div);
    });
}

// Se mantiene el nombre original de la función: "responder"
function responder(id, usuario) {
    const areaResponder = document.getElementById(`area-responder-${id}`);

    // Si el formulario ya está ahí, lo quita. Si no, lo pone.
    if (areaResponder.innerHTML !== '') {
        areaResponder.innerHTML = '';
        return;
    }

    // Se crea el formulario dentro de su propia caja para poder estilizarla
    areaResponder.innerHTML = `
        <div class="caja-responder">
            <textarea id="texto-respuesta-${id}" placeholder="Responder a ${usuario}..."></textarea>
            <button onclick="enviarRespuesta('${id}')">Enviar</button>
        </div>
    `;
}

// Se mantiene el nombre original de la función: "enviarRespuesta"
async function enviarRespuesta(id) {
    const respuesta = document.getElementById(`texto-respuesta-${id}`).value;
    const response = await fetch('/responder', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
         },

        body: JSON.stringify({ id_post: id, respuesta: respuesta })
    });
    const result = await response.json();
    if (result.success) {
        // Limpia el área del formulario y muestra la lista de respuestas actualizada
        document.getElementById(`area-responder-${id}`).innerHTML = '';
        await cargarComentarios(); // Recarga todos los comentarios para mostrar la nueva respuesta
        setTimeout(() => {
            mostrarRespuestas(id, true);
        }, 200); // forzarApertura = true
    }
}

// Se mantiene el nombre original de la función: "mostrarRespuestas"
async function mostrarRespuestas(id_post, forzarApertura = false) {
    if (!id_post) return;
    // Apunta al contenedor de la lista de respuestas
    const divRespuestas = document.getElementById('respuestas-' + id_post);
const estaVisible = divRespuestas.style.display === 'block';
if (estaVisible && !forzarApertura) {
        // Si ya está visible y no se fuerza la apertura, lo oculta
        divRespuestas.style.display = 'none';
        return;
    }   
    divRespuestas.style.display = 'block';

    const res = await fetch('/get_respuestas/' + id_post + '?t=' + Date.now());
    const respuestas = await res.json();
    
    // Se mantiene la clase original para cada respuesta individual: "respuesta"
    divRespuestas.innerHTML = respuestas.length
        ? respuestas.map(r => `<div class="respuesta-comentario"><p class="usuario-rta">${r.usuario || "Anónimo"}:</p> <p class="texto-rta">${r.cont}</p> </div>`).join('')
        : '<div class="respuesta">No hay respuestas aún.</div>';
}


// Se mantiene sin cambios el formulario de envío de preguntas
document.getElementById('commentForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const titulo = document.getElementById('titulo').value;
    const comment = document.getElementById('comentario').value;
    const id_mat = document.getElementById('id_mat').value;
    const response = await fetch('/comentario/materias', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ titulo, comment, id_mat })
    });
    const result = await response.json();
    if (result.success) {
        alert("¡Pregunta enviada!");
        document.getElementById('commentForm').reset();
        await cargarComentarios();
    } else {
        alert("Error al enviar la pregunta");
    }
});