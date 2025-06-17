window.onload = async function () { // (window onload)Al cargar la página, traemos los comentarios guardados. 
// async es para que podamos usar await dentro de la función
    const response = await fetch('/get_comments'); //respuesta espera a que fetch consulte la ruta '/get_comments'
    const comentarios = await response.json();// comentario espera a que  respuesta se convierta a JSON

    comentarios.forEach(c => { //foreach agarra el array de comentarios y los llama "c", cada uno se compone por lo q esta dentro de {}
        const div = document.createElement('div');
        div.classList.add('comment'); //a la division creada le damos la class 'comment' para ponerle style
        div.innerText = `${c.mensaje}`; //pone el texto dentro de la division creada, con el formato 'usuario: mensaje'
        // ` ${c.mensaje}` es una template string que permite insertar variables dentro de un string
        document.getElementById('commentsSection').appendChild(div);
    });
};
// archivo: static/script.js
document.getElementById('commentForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Evita recargar la página

    const comment = document.getElementById('comment').value;

    const response = await fetch('/comment', {
        method: 'POST', // método POST para enviar datos al servidor
        headers: {
            'Content-Type': 'application/json'// especifica que el cuerpo de la solicitud es JSON
        },
        body: JSON.stringify({ comment }) // convierte el objeto a una cadena JSON
    });

    const result = await response.json();
    if (result.success) {
        // Mostrar el nuevo comentario sin recargar
        const newComment = document.createElement('div');
        newComment.classList.add('comment');
        newComment.innerText = `${comment}`;
        document.getElementById('commentsSection').prepend(newComment);// agrega el nuevo comentario al inicio de la sección de comentarios
        document.getElementById('commentForm').reset();// resetea el formulario
    } else {
        alert("Error al enviar el comentario");
    }
});