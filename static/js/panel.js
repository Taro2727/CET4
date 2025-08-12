const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content')
const usuarioActual = document.querySelector('meta[name="usuario-id"]').content;
const rolUsuarioActual = document.querySelector('meta[name="usuario-rol"]').content;
window.onload = async function () {
    // Se mantiene la carga inicial de comentarios
    await cargar_usuarios();
};
//cargar_usuarios
async function cargar_usuarios() {
    const response = await fetch('/api/users?t=' + Date.now());
    const usuario = await response.json();
    const section = document.getElementById('adminPanel');
    section.innerHTML = ''; // Limpia la sección antes de recargar

    usuario.forEach(u => {
        // Se mantiene la clase original del contenedor principal: "comment"
        const div = document.createElement('div');
        div.classList.add('comment');

        // Se agrega la separación de divs pero sin cambiar la estructura visible inicial
        div.innerHTML = `
            <button class="btn-eliminar" onclick="eliminarUsuario('${u.id_usu}')">🗑️</button>
            ${u.rol == 'normal'  ? `<button class="usuariooo" onclick="ascender('${u.id_usu}','${u.rol}')">ascender</button>` : `<button class="usuariooo" onclick="down('${u.id_usu}','${u.rol}')">down</button>`}
            <span class="usuariooo"><strong>${u.nom_usu}</strong></span><br>
            <span class="usuariooo"><b>ID:</b> ${u.id_usu}</span><br>
            <span class="usuariooo"><b>Email:</b> ${u.email}</span><br>
            <span class="usuariooo"><b>Rol:</b> ${u.rol}</span><br>
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
//<<<<<<<<<<<<<<<<<<<<<<<<<<AHIIIII<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
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
async function eliminarUsuario(id_usuario,rol_usuario) {
    if (!confirm("¿Seguro que quieres eliminar este usuario?")) return;
    const response = await fetch('/eliminar_usuario', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_usuario,rol_usuario })
    });
    const result = await response.json();
    if (result.success) {
        await cargar_usuarios();
    } else {
        alert(result.error || "No se pudo eliminar.");
}
}
async function ascender(id_usuario,rol_usuario) {
    if (!confirm("¿Seguro que quieres ascemnder este usuario?")) return;
    const response = await fetch('/upgradear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_usuario,rol_usuario })
    });
    const result = await response.json();
    if (result.success) {
        await cargar_usuarios();
    } else {
        alert(result.error || "No se pudo upgradear.");
}
}
//falta agregar q le pase el rol para q dependiendo del rol haga una cosa o otra en el ap.py
async function degradar(id_usuario) {
    if (!confirm("¿Seguro que quieres degradar a este usuario?")) return;
    const response = await fetch('/down', {
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
        alert(result.error || "No se pudo degradar.");
}
}
