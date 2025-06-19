window.onload = async function () {
    await cargarComentarios();
};

async function cargarComentarios() {
    const response = await fetch('/get_comentario');
    const comentarios = await response.json();
    const section = document.getElementById('commentsSection');
    section.innerHTML = '';
    comentarios.forEach(c => {
        const div = document.createElement('div');
        div.classList.add('comment');
        div.innerHTML = `
            <strong>${c.usuario || "Anónimo"}</strong>: <b>${c.titulo}</b><br>
            ${c.cont}
            <button onclick="responder('${c.id_post}', '${c.usuario || "Anónimo"}')">Responder</button>
            <button onclick="mostrarRespuestas('${c.id_post}')">Ver respuestas</button>
            <div class="respuestas" id="respuestas-${c.id_post}"></div>
        `;
        section.appendChild(div);
    });
}

function responder(id, usuario) {
    const div = document.getElementById(`respuestas-${id}`);
    div.innerHTML = `
        <textarea id="respuesta-${id}" placeholder="Responder a ${usuario}..."></textarea>
        <button onclick="enviarRespuesta('${id}')">Enviar</button>
    `;
}

async function enviarRespuesta(id) {
    const respuesta = document.getElementById(`respuesta-${id}`).value;
    const response = await fetch('/responder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_post: id, respuesta: respuesta }) // <-- nombre correcto
    });
    const result = await response.json();
    if (result.success) {
        mostrarRespuestas(id); // Muestra las respuestas actualizadas
    }
}

async function mostrarRespuestas(id_post) {
    if (!id_post)return;
    const res = await fetch('/get_respuestas/' + id_post);
    const respuestas = await res.json();
    const div = document.getElementById('respuestas-' + id_post);
    div.innerHTML = respuestas.length
        ? respuestas.map(r => `<div class="respuesta"><b>${r.usuario || "Anónimo"}:</b> ${r.cont}</div>`).join('')
        : '<div class="respuesta">No hay respuestas aún.</div>';
}

// Envío de nuevo comentario/pregunta
document.getElementById('commentForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const titulo = document.getElementById('titulo').value;
    const comment = document.getElementById('comentario').value;
    const id_mat = document.getElementById('id_mat').value;
    const response = await fetch('/comentario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo, comment, id_mat })
    });
    const result = await response.json();
    if (result.success) {
        alert("¡Pregunta enviada!");
        document.getElementById('commentForm').reset();
        await cargarComentarios(); // Recarga la lista de comentarios
    } else {
        alert("Error al enviar la pregunta");
    }
});
    