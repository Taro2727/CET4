// esto funca para el registro de la pág
//guardamo el formulario de registro en regi
let regi = document.getElementById('registro');
regi.addEventListener('submit',async function (event){
    //cuando apretas el boton de registrarte (cndo haces submit) va a pasar esto: (event)
    event.preventDefault(); 
    //agarra los datos del formulario (email,Contra)
    const email = document.getElementById('email').value;
    const contra = document.getElementById('password').value;
    const confirmcontra = document.getElementById('confirm').value;
})
fetch ('\n')