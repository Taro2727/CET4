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
           ${ 
            u.rol==='normal' && (rolUsuarioActual==='moderador' || rolUsuarioActual==='admin')
                ? `<button class="btn-eliminar" onclick="eliminarUsuario('${u.id_usu}')">🗑️</button>`
                : u.rol==='moderador' && rolUsuarioActual==='admin'
                    ? `<button class="btn-eliminar" onclick="eliminarUsuario('${u.id_usu}')">🗑️</button>`
                    :u.rol==='admin' && rolUsuarioActual==='admin'
                        ? `<button class="btn-eliminar" onclick="eliminarUsuario('${u.id_usu}')">🗑️</button>`
                        :''
            }
            ${
                u.rol === 'normal' && (rolUsuarioActual === 'admin' || rolUsuarioActual === 'moderador')
                    ? `<button onclick="ascender('${u.id_usu}','${u.rol}','${u.email}')">↑</button>` 
                    : u.rol === 'moderador' && rolUsuarioActual === 'admin'
                        ? `<button onclick="ascender('${u.id_usu}','${u.rol}','${u.email}')">↑</button> <button onclick="down('${u.id_usu}','${u.rol}','${u.email}')">↓</button>` // Caso 2: Usuario moderador
                        : u.rol === 'admin' && rolUsuarioActual === 'admin'
                            ? `<button onclick="down('${u.id_usu}','${u.rol}','${u.email}')">↓</button>` 
                            : '' 
            }
           ${u.baneado
                ? (u.rol === 'normal' && (rolUsuarioActual === 'admin' || rolUsuarioActual === 'moderador')
                    ? `<button class="btn-eliminar" onclick="desbanear(${u.id_usu})">✅</button>`
                    :u.rol==='moderador' && rolUsuarioActual === 'admin'
                        ? `<button class="btn-eliminar" onclick="desbanear(${u.id_usu})">✅</button>`
                        :u.rol === 'admin' && rolUsuarioActual === 'admin'
                            ? `<button class="btn-eliminar" onclick="desbanear(${u.id_usu})">✅</button>`
                            :'')
                :(u.rol === 'normal' && (rolUsuarioActual === 'admin' || rolUsuarioActual === 'moderador')
                    ? `<button class="btn-eliminar" onclick="banear(${u.id_usu})">⛔</button>`
                    :u.rol==='moderador' && rolUsuarioActual === 'admin'
                        ? `<button class="btn-eliminar" onclick="banear(${u.id_usu})">⛔</button>`
                        :u.rol === 'admin' && rolUsuarioActual === 'admin'
                            ? `<button class="btn-eliminar" onclick="banear(${u.id_usu})">⛔</button>`
                            :'')
            }
            <span class="usuariooo"><strong>${u.nom_usu}</strong></span><br>
            <span class="usuariooo"><b>ID:</b> ${u.id_usu}</span><br>
            <span class="usuariooo"><b>Email:</b> ${u.email}</span><br>
            <span class="usuariooo"><b>Rol:</b> ${u.rol}</span><br>
            
            
            <div id="banForm-${u.id_usu}" class="ban-form-oculto">
                <h4>Detalles del Baneo</h4>
                <form onsubmit="formulariobaneo(event, '${u.id_usu}')">
                    <textarea name="motivo" placeholder="Motivo del baneo" required></textarea>
                    <input type="date" name="fecha_inicio" placeholder=" fecha de inicio" required>
                    <input type="date" name="fecha_fin" placeholder=" fecha de fin" required>
                    <div>
                        <button type="submit">Confirmar Baneo</button>
                        <button type="button" onclick="toggleBanForm('${u.id_usu}')">Cancelar</button>
                    </div>
                </form>
            </div>

            `;

            //EXPLICACION LINEAS 23 24 Y 25
            //    LINEA 23 "si el rol de usuario es NORMAL (? significa se cumple) entonces muetsra boton de upgradear"
            //    LINEA 24 pero si no cumple con la linea 23 (: significa else if )"si el rol del usuario es MODERADOR entonces muestra dos botones upgradear y degradar "
            //    LINEA 25 peeeero si no se cumple ninguna significa q es admin, entonces solo muestra boton de degradar

        section.appendChild(div);
    });
}
function toggleBanForm(userId) {
    const form = document.getElementById(`banForm-${userId}`);
    // Si el formulario ya está visible, lo oculta. Si no, lo muestra.
    form.style.display = form.style.display === 'block' ? 'none' : 'block';
}

// Nueva función para manejar el envío del formulario con fetch
async function formulariobaneo(event, userId) {
    event.preventDefault(); // Evita que el formulario se envíe de la forma tradicional

    const form = document.getElementById(`banForm-${userId}`);
    const motivo = form.querySelector('textarea[name="motivo"]').value;
    const fechaInicio = form.querySelector('input[name="fecha_inicio"]').value;
    const fechaFin = form.querySelector('input[name="fecha_fin"]').value;

    try {
        const response = await fetch('/ban', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                id_usuario: userId,
                motivo: motivo,
                fecha_inicio: fechaInicio,
                fecha_fin: fechaFin
            })
        });

        const result = await response.json();
        if (result.exito) {
            alert('Usuario baneado correctamente.');
            toggleBanForm(userId); // Oculta el formulario
            await cargar_usuarios(); // Recarga la lista
        } else {
            alert('Error al banear al usuario: ' + result.error);
        }
    } catch (e) {
        alert('Ocurrió un error en la comunicación con el servidor.');
    }
}



//---FUNCIONES DE ELIMINACIÓN DE COMENTARIOS Y RESPUESTAS---
async function eliminarUsuario(id_usuario,rol_usuario) {
    if (!confirm("¿Seguro que quieres eliminar este usuario?")) return;
    console.log({ id_usuario, rol_usuario });
    const response = await fetch('/otp_eliminar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_usuario,rol_usuario })
    });
    const result = await response.json();
    if (result.success) {
        alert('Código OTP enviado al mail');
        window.location.href = '/IngresarCodigo';
    } else {
        alert(result.error || "No se pudo eliminar.");
}
}
async function ascender(id_usuario,rol_usuario,mail_usuario) {
    if (!confirm("¿Seguro que quieres ascender este usuario?")) return;
    sessionStorage.setItem('id_usuario_up', id_usuario);
    sessionStorage.setItem('rol_usuario_up', rol_usuario);
    const response = await fetch('/otp_roles', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_usuario,rol_usuario,mail_usuario })
    });
    const result = await response.json();
    if (result.success) {
        alert('Código OTP enviado al mail');
        window.location.href = '/IngresarCodigo';
    } else {
        alert(result.error || "No se pudo upgradear.");
}
}
//falta agregar q le pase el rol para q dependiendo del rol haga una cosa o otra en el ap.py
async function down(id_usuario,rol_usuario,mail_usuario) {
    if (!confirm("¿Seguro que quieres degradar a este usuario?")) return;
    const response = await fetch('/otp_down', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_usuario,rol_usuario,mail_usuario })
    });
    const result = await response.json();
    if (result.success) {
        alert('Código OTP enviado al mail');
        window.location.href = '/IngresarCodigo';
    } else {
        alert(result.error || "No se pudo degradar.");
}
}

function banear(id_usuario){
    toggleBanForm(id_usuario);
}

async function desbanear(id_usuario) {
    if (!confirm("¿Seguro que quieres desbanear a este usuario?")) return;
    const response = await fetch('/unban', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ id_usuario,})
    });
    const result = await response.json();
    if (result.success) {
        alert('desbaneado ');
        window.location.href = '/paneladmin';
    } else {
        alert(result.error || "no se pudo desbanear.");
}
}

