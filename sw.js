// sw.js (EN LA RAÍZ DEL PROYECTO)

self.addEventListener('push', event => {
    const data = event.data.json();
    console.log('Push Recibido:', data);

    const title = data.title;
    const options = {
        body: data.body,
        icon: '/static/utils/img/campana-img2.png', // Un ícono para la notificación
        badge: '/static/utils/img/campana-img2.png' // Ícono para la barra de estado (Android)
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

// Opcional: Manejar click en la notificación para abrir la web
self.addEventListener('notificationclick', event => {
    event.notification.close(); // Cierra la notificación
    // Abre la página de inicio o una página específica de notificaciones
    event.waitUntil(
        clients.openWindow('/indexhomeoinicio') 
    );
});