// static/js/notificaciones.js

document.addEventListener('DOMContentLoaded', () => {
    const enableNotificationsBtn = document.getElementById('enable-notifications-btn');

    // Comprobar si el navegador soporta notificaciones y service workers
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Notificaciones Push no soportadas.');
        if(enableNotificationsBtn) enableNotificationsBtn.style.display = 'none';
        return;
    }

    // Registrar el Service Worker
    navigator.serviceWorker.register('/sw.js')
        .then(swReg => {
            console.log('Service Worker registrado', swReg);
            if(enableNotificationsBtn) enableNotificationsBtn.addEventListener('click', () => {
                askPermissionAndSubscribe(swReg);
            });
        })
        .catch(error => console.error('Error al registrar Service Worker', error));
});

async function guardarsuscripcion(subscription) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const response = await fetch('/guardarsuscripcion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(subscription)
    });

    if (!response.ok) {
        throw new Error('No se pudo guardar la suscripción en el servidor.');
    }
    return response.json();
}

async function askPermissionAndSubscribe(swReg) {
    try {
        // 1. Pedir permiso al usuario
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            throw new Error('Permiso de notificación no concedido.');
        }

        // 2. Obtener la clave pública VAPID del servidor
        const response = await fetch('/vapid_key_publica');
        const data = await response.json();
        const vapidPublicKey = data.public_key;
        
        const options = {
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
        };
        
        // 3. Suscribir al usuario
        const subscription = await swReg.pushManager.subscribe(options);
        console.log('Usuario suscrito:', subscription);

        // 4. Enviar suscripción al backend
        await guardarsuscripcion(subscription);
        alert('¡Suscripción a notificaciones activada!');
        document.getElementById('enable-notifications-btn').style.display = 'none';

    } catch (error) {
        console.error('Fallo al suscribir al usuario: ', error);
        alert('Error al activar las notificaciones.');
    }
}


// Función auxiliar para convertir la clave VAPID
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}