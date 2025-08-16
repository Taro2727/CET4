// static/js/notificaciones.js

document.addEventListener('DOMContentLoaded', () => {
    const pushToggleBtn = document.getElementById('push-toggle-btn');
    const emailToggle = document.getElementById('email-toggle');

    // Comprobar si el navegador soporta notificaciones y service workers
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Notificaciones Push no soportadas.');
        if (pushToggleBtn) {
            pushToggleBtn.disabled = true; // Deshabilitar el botón si no hay soporte
        }
        return;
    }

    // Registrar el Service Worker
    navigator.serviceWorker.register('/sw.js')
        .then(swReg => {
            console.log('Service Worker registrado', swReg);
        })
        .catch(error => console.error('Error al registrar Service Worker', error));

    // Cargar estado inicial de los interruptores
    loadInitialStatus();

    // ---- MANEJADOR PARA EL INTERRUPTOR PUSH ----
    if (pushToggleBtn) {
        pushToggleBtn.addEventListener('change', async () => {
            const isEnabled = pushToggleBtn.checked;
            try {
                if (isEnabled) {
                    console.log('Activando notificaciones push...');
                    await subscribeUser();
                } else {
                    console.log('Desactivando notificaciones push...');
                    await unsubscribeUser();
                }
                // Actualizar preferencia en el backend
                await updatePushPreference(isEnabled);
            } catch (error) {
                console.error('Error al cambiar el estado de las notificaciones push:', error);
                // Revertir el estado visual si falla
                pushToggleBtn.checked = !isEnabled;
                setSwitchState('push', !isEnabled);
                alert('Hubo un error al procesar tu solicitud.');
            }
        });
    }
    
    // ---- MANEJADOR PARA EL INTERRUPTOR EMAIL ----
    if (emailToggle) {
        emailToggle.addEventListener('change', async () => {
            const isEnabled = emailToggle.checked;
            try {
                await updateEmailPreference(isEnabled);
                setSwitchState('email', isEnabled);
            } catch (error) {
                console.error('Error al cambiar las notificaciones por email:', error);
                alert('Hubo un error al guardar tu preferencia de email.');
            }
        });
    }
});

// ---- FUNCIONES AUXILIARES ----

function setSwitchState(type, enabled) {
    const statusEl = document.getElementById(type + '-status');
    if (!statusEl) return;

    if (enabled) {
        statusEl.textContent = 'Activadas';
        statusEl.classList.remove('status-off');
        statusEl.classList.add('status-on');
    } else {
        statusEl.textContent = 'Desactivadas';
        statusEl.classList.remove('status-on');
        statusEl.classList.add('status-off');
    }
}

async function loadInitialStatus() {
    try {
        const response = await fetch('/mis-preferencias-notif');
        const data = await response.json();
        if (data.success && data.prefs) {
            const pushToggleBtn = document.getElementById('push-toggle-btn');
            const emailToggle = document.getElementById('email-toggle');

            if (pushToggleBtn) {
                pushToggleBtn.checked = data.prefs.notif_push;
                setSwitchState('push', data.prefs.notif_push);
            }
            if (emailToggle) {
                emailToggle.checked = data.prefs.notif_email;
                setSwitchState('email', data.prefs.notif_email);
            }
        }
    } catch (error) {
        console.error('No se pudieron cargar las preferencias de notificación:', error);
    }
}

async function subscribeUser() {
    const swReg = await navigator.serviceWorker.ready;

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

    // 4. Enviar suscripción al backend para guardarla
    await saveSubscription(subscription);
    alert('¡Notificaciones Push activadas!');
}

async function unsubscribeUser() {
    const swReg = await navigator.serviceWorker.ready;
    const subscription = await swReg.pushManager.getSubscription();

    if (subscription) {
        // Desuscribir en el navegador
        await subscription.unsubscribe();
        console.log('Suscripción local cancelada.');

        // Avisar al backend para que la elimine
        await deleteSubscription(subscription);
        alert('Notificaciones Push desactivadas.');
    } else {
        console.log('No había suscripción activa para cancelar.');
    }
}

// ---- LLAMADAS A LA API ----

async function saveSubscription(subscription) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const response = await fetch('/guardarsuscripcion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify(subscription)
    });

    if (!response.ok) {
        throw new Error('No se pudo guardar la suscripción en el servidor.');
    }
}

async function deleteSubscription(subscription) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    await fetch('/eliminar-suscripcion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ endpoint: subscription.endpoint }) // Enviamos solo el endpoint
    });
}

async function updatePushPreference(enabled) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    await fetch('/toggle-push-notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ enable: enabled })
    });
    setSwitchState('push', enabled);
}

async function updateEmailPreference(enabled) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    await fetch('/toggle-email-notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ enable: enabled })
    });
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