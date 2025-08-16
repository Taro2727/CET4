document.addEventListener('DOMContentLoaded', async () => {
    const misComentariosDiv = document.getElementById('mis-comentarios');

    if (!misComentariosDiv) {
        console.error("El elemento con id 'mis-comentarios' no fue encontrado.");
        return;
    }

    try {
        const response = await fetch('/get_mis_comentarios');
        const data = await response.json();

        if (data.success) {
            if (data.comentarios.length === 0) {
                misComentariosDiv.innerHTML = '<p>Aún no has hecho ningún comentario.</p>';
            } else {
                let htmlContent = '';
                data.comentarios.forEach(c => {
                    // Formato de fecha
                    const fecha = new Date(c.fecha);
                    const fechaFormato = `${fecha.getDate()}/${fecha.getMonth() + 1}/${fecha.getFullYear()}`;
                    
                    htmlContent += `
                        <div class="perfil-comentario-item">
                            <div class="perfil-comentario-header">
                                <span class="perfil-comentario-titulo">${c.titulo}</span>
                                <span class="perfil-comentario-materia"> en ${c.nom_mat}</span>
                            </div>
                            <div class="perfil-comentario-texto">
                            <p class="perfil-comentario-cont">${c.cont}</p>
                            <span class="perfil-comentario-fecha">Publicado el ${fechaFormato}</span>
                            </div>
                        </div>
                    `;
                });
                misComentariosDiv.innerHTML = htmlContent;
            }
        } else {
            misComentariosDiv.innerHTML = `<p class="error-cargando">Error: ${data.error}</p>`;
        }

    } catch (error) {
        console.error("Error al cargar comentarios del perfil:", error);
        misComentariosDiv.innerHTML = '<p class="error-cargando">Error de conexión al cargar tus comentarios.</p>';
    }
});

// document.addEventListener('DOMContentLoaded', () => {
//     // Obtiene los elementos del DOM
//     const modal = document.getElementById('myModal');
//     const btn = document.getElementById('openModalBtn');
//     const span = document.getElementsByClassName("close-btn")[0];

//     // Cuando el usuario hace clic en el botón, se abre el modal
//     btn.onclick = function() {
//         modal.style.display = "flex"; // Usa "flex" para centrar el modal
//     }

//     // Cuando el usuario hace clic en <span> (x), se cierra el modal
//     span.onclick = function() {
//         modal.style.display = "none";
//     }

//     // Cuando el usuario hace clic en cualquier lugar fuera del modal, se cierra
//     window.onclick = function(event) {
//         if (event.target == modal) {
//             modal.style.display = "none";
//         }
//     }
// });
