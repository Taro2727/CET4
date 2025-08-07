// Espera a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    // URL de tu API de usuarios
    const API_URL = '/api/users';

    // Función asincrónica para obtener los usuarios
    const fetchUsers = async () => {
        try {
            // Realiza la petición GET al endpoint
            const response = await fetch(API_URL);
            
            // Verifica si la respuesta es exitosa
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Parsea el JSON de la respuesta
            const users = await response.json();
            
            // Muestra los usuarios en la tabla
            renderUsers(users);
            
        } catch (error) {
            console.error('Error al obtener los usuarios:', error);
            // Podrías mostrar un mensaje de error en el UI
            const tableBody = document.querySelector('#users-table tbody');
            tableBody.innerHTML = `<tr><td colspan="3" class="text-center text-red-500">Error al cargar los usuarios.</td></tr>`;
        }
    };

    // Función para renderizar los usuarios en la tabla
    const renderUsers = (users) => {
        const tableBody = document.querySelector('#users-table tbody');
        tableBody.innerHTML = ''; // Limpia el cuerpo de la tabla antes de agregar nuevos datos

        if (users.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="3" class="text-center text-gray-500">No hay usuarios para mostrar.</td></tr>`;
            return;
        }

        users.forEach(user => {
            const row = document.createElement('tr');
            row.className = 'border-b hover:bg-gray-50';
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${user.id}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.email}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.rol}</td>
            `;
            tableBody.appendChild(row);
        });
    };

    // Llama a la función para obtener los usuarios cuando se carga la página
    fetchUsers();
});
