const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content')
const usuarioActual = document.querySelector('meta[name="usuario-id"]').content;
const rolUsuarioActual = document.querySelector('meta[name="usuario-rol"]').content;
window.onload = async function () {
    // Se mantiene la carga inicial de comentarios
    await cargarComentarios();
};
//cargar_usuarios
async function cargar_usuarios() {
    const response = await fetch('/get_usuario?t=' + Date.now());
    const usuario = await response.json();
    const section = document.getElementById('adminPanel');
    section.innerHTML = ''; // Limpia la sección antes de recargar

    usuario.forEach(u => {
        // Se mantiene la clase original del contenedor principal: "comment"
        const div = document.createElement('div');
        div.classList.add('comment');

        // Se agrega la separación de divs pero sin cambiar la estructura visible inicial
        div.innerHTML = `
            <button class="btn-eliminar" onclick="eliminarUsuario('${u.id}')">🗑️</button>
            <span class="usuario-comentario"><strong>${u.nombre}</strong></span><br>
            <span><b>ID:</b> ${u.id}</span><br>
            <span><b>Email:</b> ${u.email}</span><br>
            <span><b>Rol:</b> ${u.rol}</span><br>
            <button class="btn-editar" onclick="editarRol('${u.id}', '${u.rol}')">Editar Rol</button>
            
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
// document.getElementById('commentForm').addEventListener('submit', async function(e) {
//     e.preventDefault();

//     const titulo = document.getElementById('titulo').value;
//     const comment = document.getElementById('comentario').value;
//     const id_mat = document.getElementById('id_mat').value;
//     const response = await fetch('/comentario/materias', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': csrfToken
//         },
//         body: JSON.stringify({ titulo, comment, id_mat })
//     });
//     const result = await response.json();
//     if (result.success) {
//         alert("¡Pregunta enviada!");
//         document.getElementById('commentForm').reset();
//         await cargarComentarios();
//     } else {
//         alert("Error al enviar la pregunta");
//     }
// });

//---FUNCIONES DE ELIMINACIÓN DE COMENTARIOS Y RESPUESTAS---
async function eliminarUsuario(id_usuario) {
    if (!confirm("¿Seguro que quieres eliminar este usuario?")) return;
    const response = await fetch('/eliminar_usuario', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_usuario })
    });
    const result = await response.json();
    if (result.success) {
        await cargar_usuarios();
    } else {
        alert(result.error || "No se pudo eliminar.");
}
}

