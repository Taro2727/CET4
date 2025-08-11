const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content')
const usuarioActual = document.querySelector('meta[name="usuario-id"]').content;
const rolUsuarioActual = document.querySelector('meta[name="usuario-rol"]').content;
window.onload = async function () {
    // Se mantiene la carga inicial de comentarios
    await cargarComentarios();
};
//cargar_usuarios
async function cargar_usuarios() {
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
                
          
            <div class="area-responder" id="area-responder-${c.id_post}"></div>
            <div class="respuestas" id="respuestas-${c.id_post}" style="display: none;"></div>
            
        `  ;
        
        section.appendChild(div);
        // Estas lineas de codigo hacen andar el corazon
       


        //-----------------------------------------
        //esto iba abajo del 1er const
        // btnLike.addEventListener('click',() => {
        // btnLike.classList.toggle('liked');
        // btnLike.textContent = btnLike.textContent === '♡' ? '♡' : '♡';
        // linea corazoncito 
        //-------------------------------------------------

    });
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

