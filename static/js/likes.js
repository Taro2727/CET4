document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_mis_likes")
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("commentsSection");
            container.innerHTML = "";

            if (!data.success || data.posts.length === 0) {
                container.innerHTML = "<p>No has dado like a ningún post.</p>";
                return;
            }

            data.posts.forEach(post => {
                const div = document.createElement("div");
                div.classList.add("post-likeado");
                div.innerHTML = `
                    <div class="comentarios-anteriores">
                    <div class="contenido-titulo">
                    <h3>${post.titulo}</h3>
                    </div>
                    <div class="contenido-texto">
                    <p>${post.cont}</p>
                    </div>

                    <div class="contenido-info">
                    <p><strong>Autor:</strong> ${post.nom_usu}</p>
                    <p><strong>Materia:</strong> ${post.nom_mat}</p>
                    <p><em>Fecha:</em> ${new Date(post.fecha).toLocaleString()}</p>
                    </div>
                    
                    </div>
                `;
                container.appendChild(div);
            });
        })
        .catch(err => {
            console.error("Error al cargar posts con like:", err);
            document.getElementById("mis-likes-container").innerHTML = "<p>Error al cargar los posts.</p>";
        });
});
