const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content')
const usuarioActual = document.querySelector('meta[name="usuario-id"]').content;
const rolUsuarioActual = document.querySelector('meta[name="usuario-rol"]').content;
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
        const contenidoSeguro = DOMPurify.sanitize(c.cont);
        const tituloSeguro = DOMPurify.sanitize(c.titulo);
        const div = document.createElement('div');
        div.classList.add('comment');

        // Se agrega la separación de divs pero sin cambiar la estructura visible inicial
        div.innerHTML = `
        ${c.id_usu == usuarioActual || rolUsuarioActual == 'admin' ? `<button class="btn-eliminar" onclick="eliminarComentario('${c.id_post}')">🗑️</button>` : ''}
            <span class="usuario-comentario"><strong>${c.usuario || "Anónimo"}</strong>:</span>
            <br>
            <span class="titulo-comentario"><b>${tituloSeguro}</b></span>
            <span class="texto-comentario">${contenidoSeguro}</span>
            <br>
            <button class="btn-responder" onclick="responder('${c.id_post}', '${c.usuario || "Anónimo"}')">Responder</button>
            <button class="btn-ver-respuestas" onclick="mostrarRespuestas('${c.id_post}')">Ver respuestas</button>
            <button class="btn-like ${c.likeado_por_usuario ? 'liked' : ''}" id="like-${c.id_post}">${c.likeado_por_usuario ? '❤️' : '♡'}</button>
            <span id="contador-${c.id_post}" class="contador-likes">${c.cont_likes || 0}</span>
            <div class="area-responder" id="area-responder-${c.id_post}"></div>
            <div class="respuestas" id="respuestas-${c.id_post}" style="display: none;"></div>
            
        `  ;
        
        section.appendChild(div);
        // Estas lineas de codigo hacen andar el corazon
        const btnLike = document.getElementById(`like-${c.id_post}`);
        const user_like = usuarioActual;
        btnLike.addEventListener('click', async () => {
            console.log("LIKE a enviar:", { comment_id: c.id_post});//user_like no se esta usandoooo
            const res = await fetch('/api/like', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': csrfToken 
                },
                body: JSON.stringify({ comment_id: c.id_post, })
            });
            const data = await res.json();
            const contador = document.getElementById(`contador-${c.id_post}`);
            contador.textContent = data.total;
            btnLike.classList.toggle('liked', data.liked);
            btnLike.textContent = data.liked ? '❤️' : '♡';
    });


        //-----------------------------------------
        //esto iba abajo del 1er const
        // btnLike.addEventListener('click',() => {
        // btnLike.classList.toggle('liked');
        // btnLike.textContent = btnLike.textContent === '♡' ? '♡' : '♡';
        // linea corazoncito 
        //-------------------------------------------------

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
    
        let html = '';
    if (respuestas.length) {
        respuestas.forEach(r => {
            const textoRtaSeguro = DOMPurify.sanitize(r.cont);
            html += `
        <div class="respuesta-comentario">
            ${r.id_usu == usuarioActual || rolUsuarioActual == 'admin' ? `<button class="btn-eliminar" onclick="eliminarRespuesta('${r.id_com}')">🗑️</button>` : ''}
            <p class="usuario-rta">${r.usuario || "Anónimo"}:</p>
            <p class="texto-rta">${textoRtaSeguro}</p>
            <button class="btn-like ${r.likeado_por_usuario ? 'liked' : ''}" id="like-resp-${r.id_com}">${r.likeado_por_usuario ? '❤️' : '♡'}</button>
            <span id="contador-resp-${r.id_com}" class="contador-likes">${r.cont_likes || 0}</span>
        </div>
    `;
        });
    } else {
        html = '<div class="respuesta">No hay respuestas aún.</div>';
    }
        divRespuestas.innerHTML = html;
    setTimeout(() => {
        respuestas.forEach(r => {
            const btnLike = document.getElementById(`like-resp-${r.id_com}`);
            if (btnLike) {
                btnLike.onclick = async () => {
                    const res = await fetch('/api/like_respuesta', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ id_com: r.id_com })
                    });
                    const data = await res.json();
                    const contador = document.getElementById(`contador-resp-${r.id_com}`);
                    contador.textContent = data.total;
                    btnLike.classList.toggle('liked', data.liked);
                    btnLike.textContent = data.liked ? '❤️' : '♡';
                };
            }
        });
    }, 0);
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

//---FUNCIONES DE ELIMINACIÓN DE COMENTARIOS Y RESPUESTAS---
async function eliminarComentario(id_post) {
    if (!confirm("¿Seguro que quieres eliminar esta pregunta?")) return;
    const response = await fetch('/eliminar_comentario', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_post })
    });
    const result = await response.json();
    if (result.success) {
        await cargarComentarios();
    } else {
        alert(result.error || "No se pudo eliminar.");
}
}

async function eliminarRespuesta(id_com) {
    if (!confirm("¿Seguro que quieres eliminar esta respuesta?")) return;
    const response = await fetch('/eliminar_respuesta', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
         },
        body: JSON.stringify({ id_com })
    });
    const result = await response.json();
    if (result.success) {
        await cargarComentarios();
    } else {
        alert("No se pudo eliminar.");
    }
}