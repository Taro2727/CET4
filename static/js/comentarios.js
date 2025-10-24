
let criterioActual = 'reciente';
const IS_AUTHENTICATED = JSON.parse(document.querySelector('meta[name="is-authenticated"]').content);
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content')
const usuarioActual = parseInt(document.querySelector('meta[name="usuario-id"]').content);
const rolUsuarioActual = document.querySelector('meta[name="usuario-rol"]').content;

const IdusuarioActual = usuarioActual ? usuarioActual.content : null;
window.onload = async function () {
    const commentForm = document.getElementById('commentForm');
    if (!IS_AUTHENTICATED) {
        commentForm.style.display = 'none';
        // Opcional: Mostrar un mensaje para iniciar sesión
        const loginPrompt = document.createElement('p');
        loginPrompt.innerHTML = 'Debes <a href="/iniciarsesion">iniciar sesión</a> para publicar una pregunta.';
        commentForm.parentNode.insertBefore(loginPrompt, commentForm);
    }
    
    await cargarComentarios();

};

    const ordenarBtn = document.getElementById('ordenar-btn');
    const menuOrdenar = document.getElementById('menu-ordenar');

    if (ordenarBtn && menuOrdenar) {
        ordenarBtn.addEventListener('click', () => {
            menuOrdenar.classList.toggle('oculto');
        });

        menuOrdenar.addEventListener('click', (e) => {
            if (e.target.tagName === 'LI') {
                // Obtenemos el nuevo criterio del atributo data-orden
                const nuevoCriterio = e.target.dataset.orden;
                
                // Si el criterio es diferente al actual, recargamos
                if (nuevoCriterio !== criterioActual) {
                    criterioActual = nuevoCriterio;
                    cargarComentarios(); // Volvemos a llamar a la función para recargar y ordenar
                }
                
                menuOrdenar.classList.add('oculto'); // Ocultamos el menú
            }
        });
    }

        document.addEventListener('click', (e) => {
            if (!ordenarBtn.contains(e.target) && !menuOrdenar.contains(e.target)) {
                menuOrdenar.classList.add('oculto');
            }
        });

async function cargarComentarios() {
    const id_mat = document.getElementById('id_mat').value;
    const response = await fetch('/get_comentario?id_mat=' + encodeURIComponent(id_mat) + '&orden=' + encodeURIComponent(criterioActual) + '&t=' + Date.now());
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
        let botonesHTML = '';
       if (IS_AUTHENTICATED) {
        botonesHTML = `
            <button class="btn-responder" onclick="responder('${c.id_post}', '${c.usuario || "Anónimo"}')">Responder</button>
            <button class="btn-ver-respuestas" onclick="mostrarRespuestas('${c.id_post}')">Ver respuestas</button>
            <button class="btn-like ${c.likeado_por_usuario ? 'liked' : ''}" id="like-${c.id_post}">
                ${c.likeado_por_usuario ? '❤️' : '♡'}
            </button>
            <span id="contador-${c.id_post}" class="contador-likes">${c.cont_likes || 0}</span>
        `;
        } else {
            botonesHTML = `
                <button class="btn-ver-respuestas" onclick="mostrarRespuestas('${c.id_post}')">Ver respuestas</button>
                <button class="btn-like" id="like-${c.id_post}" disabled>♡</button>
                <span id="contador-${c.id_post}" class="contador-likes">${c.cont_likes || 0}</span>
            `;
        }
        console.log('Comparando:', Number(c.id_usu), Number(usuarioActual), rolUsuarioActual);
       div.innerHTML = `
        ${Number(c.id_usu) === Number(usuarioActual) || rolUsuarioActual == 'admin' ? `<button class="btn-eliminar" onclick="eliminarComentario('${c.id_post}')">🗑️</button>` : ''}
        <span class="usuario-comentario"><strong>${c.usuario || "Anónimo"}</strong>:</span>
        <br>
        <span class="titulo-comentario"><b>${tituloSeguro}</b></span>
        <span class="texto-comentario">${contenidoSeguro}</span>
        <br>
        ${botonesHTML}
        <div class="area-responder" id="area-responder-${c.id_post}"></div>
        <div class="respuestas" id="respuestas-${c.id_post}" style="display: none;"></div>
    `;
        
        section.appendChild(div);
        // Estas lineas de codigo hacen andar el corazon
        if (IS_AUTHENTICATED) {
            const btnLike = document.getElementById(`like-${c.id_post}`);
            const user_like = IdusuarioActual;
            btnLike.addEventListener('click', async () => {
                console.log("LIKE a enviar:", { comment_id: c.id_post, user_id: user_like });
                const res = await fetch('/api/like', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json', 
                        'X-CSRFToken': csrfToken 
                    },
                    body: JSON.stringify({ comment_id: c.id_post, user_id: user_like })
            });
            const data = await res.json();
            const contador = document.getElementById(`contador-${c.id_post}`);
            contador.textContent = data.total;
            btnLike.classList.toggle('liked', data.liked);
            btnLike.textContent = data.liked ? '❤️' : '♡';
    });
        }
    });
}


        //-----------------------------------------
        //esto iba abajo del 1er const
        // btnLike.addEventListener('click',() => {
        // btnLike.classList.toggle('liked');
        // btnLike.textContent = btnLike.textContent === '♡' ? '♡' : '♡';
        // linea corazoncito 
        //-------------------------------------------------

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
            // LÓGICA CONDICIONAL PARA BOTONES DE RESPUESTA
            let botonesRtaHTML = '';
            if (IS_AUTHENTICATED) {
                const puedeEliminarRta = r.id_usu == usuarioActual || rolUsuarioActual == 'admin';
                botonesRtaHTML = `
                    ${puedeEliminarRta ? `<button class="btn-eliminar" onclick="eliminarRespuesta('${r.id_com}')">🗑️</button>` : ''}
                    <button class="btn-like ${r.likeado_por_usuario ? 'liked' : ''}" id="like-resp-${r.id_com}">${r.likeado_por_usuario ? '❤️' : '♡'}</button>
                    <span id="contador-resp-${r.id_com}" class="contador-likes">${r.cont_likes || 0}</span>
                `;
            } else {
                botonesRtaHTML = `<span class="likes-info">❤️ ${r.cont_likes || 0}</span>`;
            }
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
    if (IS_AUTHENTICATED) {
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
       
        document.getElementById('commentForm').reset();
        await cargarComentarios();
    } else {
       console.log("error");
    }
});

function showConfirmModal(message, onConfirm, onCancel) {
    // Si ya existe, no crear otro
    if (document.getElementById('confirm-overlay')) return;
    const overlay = document.createElement('div');
    overlay.id = 'confirm-overlay';
    overlay.style = `
        position: fixed; inset: 0; background: rgba(0,0,0,0.45);
        display:flex; align-items:center; justify-content:center; z-index:9999;
    `;
    const box = document.createElement('div');
    box.style = 'background:#0f1724; color:#fff; padding:16px; border-radius:8px; max-width:90%; width:420px; text-align:left;';
    box.innerHTML = `
        <p style="margin:0 0 12px;">${message}</p>
        <div style="display:flex; gap:8px; justify-content:flex-end;">
            <button id="confirm-cancel" style="background:#444;color:#fff;border:none;padding:8px 12px;border-radius:6px;cursor:pointer;">Cancelar</button>
            <button id="confirm-ok" style="background:#0ea5a4;color:#062; border:none;padding:8px 12px;border-radius:6px;cursor:pointer;">Confirmar</button>
        </div>
    `;
    overlay.appendChild(box);
    document.body.appendChild(overlay);

    const cleanup = () => { const el = document.getElementById('confirm-overlay'); if (el) el.remove(); };
    document.getElementById('confirm-cancel').onclick = () => { cleanup(); if (onCancel) onCancel(); };
    document.getElementById('confirm-ok').onclick = () => { cleanup(); if (onConfirm) onConfirm(); };
}

//---FUNCIONES DE ELIMINACIÓN DE COMENTARIOS Y RESPUESTAS---
async function eliminarComentario(id_post) {
    showConfirmModal('¿Seguro que quieres eliminar esta pregunta?', async () => {
        try {
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
                console.log('Error al eliminar:', result.error || result);
                // opcional: mostrar un pequeño aviso en pantalla
            }
        } catch (err) {
            console.error('Fetch error eliminar_comentario:', err);
        }
    }, () => {
        // cancel callback (opcional)
    });
}

async function eliminarRespuesta(id_com) {
    showConfirmModal('¿Seguro que quieres eliminar esta respuesta?', async () => {
        try {
            const response = await fetch('/eliminar_respuesta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ id_com })
            });

            if (!response.ok) {
                const text = await response.text();
                console.error('Error eliminar_respuesta HTTP', response.status, text);
                return;
            }

            const result = await response.json();
            if (result && result.success) {
                await cargarComentarios();
            } else {
                console.error('Error al eliminar respuesta:', result && result.error ? result.error : result);
            }
        } catch (err) {
            console.error('Fetch error eliminar_respuesta:', err);
        }
    }, () => {
        // cancel callback (opcional)
    });
}