document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('#toggle');
    const elcostado = document.querySelector('.elcostado');
    const out = document.querySelector('#out');
    /* Detectar el rol del usuario */
    const rol = document.querySelector('meta[name="usuario-rol"]').content;

    /* Mostrar botón de admin si corresponde */
    if (rol === 'admin') {
        const adminBtn = document.createElement('a');
        adminBtn.classList.add('separador3');
        adminBtn.href = '/paneladmin';
        adminBtn.innerHTML = `<img src="/static/utils/img/iconoadmin.png"  class="opcion5">`;

        elcostado.insertBefore(adminBtn, elcostado.lastElementChild); // Lo pone antes de "cerrar sesión"
    }
    /*Abrir Barra lateral */
    toggle.addEventListener('click', () => {
        elcostado.classList.toggle('active');
    })
    /*Fin de la funcion abrir Barra lateral */

    /*Cerrar Barra lateral */
    out.addEventListener('click', () => {
        elcostado.classList.toggle('active');
    })
    /*Fin de la funcion Cerrar barra lateral*/
    });