window.onload = async function () { // (window onload)Al cargar la página, traemos los comentarios guardados. 
 // async es para que podamos usar await dentro de la función
    const response = await fetch('/get_comentario'); //respuesta espera a que fetch consulte la ruta '/get_comentario'
    const comentarios = await response.json();// comentario espera a que  respuesta se convierta a JSON

    comentarios.forEach(c => { //foreach agarra el array de comentarios y los llama "c", cada uno se compone por lo q esta dentro de {}
        const div = document.createElement('div');
        div.classList.add('comment'); //a la division creada le damos la class 'comment' para ponerle style
       div.innerHTML = `
            <strong>${c.usuario || "Anónimo"}:</strong> ${c.cont}
            <button onclick="responder('${c.id_post}', '${c.usuario || "Anónimo"}')">Responder</button>
            <div class="respuestas" id="respuestas-${c.id_post}"></div>
        `;
        document.getElementById('commentsSection').appendChild(div);
    });
};

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
        body: JSON.stringify({ id_comentario: id, respuesta: respuesta })
    });
    const result = await response.json();
    if (result.success) {
        location.reload(); // Recarga para ver la respuesta
    }
}

async function mostrarRespuestas(id_post) {
    const res = await fetch('/get_respuestas/' + id_post);
    const respuestas = await res.json();
    const div = document.getElementById('respuestas-' + id_post);
    div.classList.add('comment'); 
    div.innerHTML = respuestas.map(r => `<div class="respuesta"><b>${r.usuario || "Anónimo"}:</b> ${r.cont}</div>`).join('');
}

// archivo: static/script.js
document.getElementById('commentForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Evita recargar la página

    const titulo = document.getElementById('titulo').value;
    const comment = document.getElementById('comentario').value;
    const id_mat= document.getElementById('id_mat').value;
    const response = await fetch('/comentario', {
        method: 'POST', // método POST para enviar datos al servidor
        headers: {
            'Content-Type': 'application/json'// especifica que el cuerpo de la solicitud es JSON
        },
        body: JSON.stringify({ titulo, comment, id_mat }) // convierte el objeto a una cadena JSON
    });
    const result = await response.json();
    if (result.success) {
        alert("¡Pregunta enviada!");
        document.getElementById('commentForm').reset();
    } else {
        alert("Error al enviar la pregunta");
    }
});
    