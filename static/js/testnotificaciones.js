document.addEventListener('DOMContentLoaded', () => {
    const boton = document.getElementById('probar-notificacion');
    if (boton) {
        boton.addEventListener('click', () => {
            fetch('/test_notificacion')
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert("✅ Notificación enviada. Revisá tu escritorio.");
                    } else {
                        alert("❌ Error al enviar notificación: " + data.error);
                    }
                })
                .catch(err => {
                    console.error("Error en la solicitud:", err);
                    alert("❌ No se pudo conectar al servidor.");
                });
        });
    }
});
