const toggle = document.querySelector('#toggle');
const elcostado = document.querySelector('.elcostado');
const out = document.querySelector('#out');
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