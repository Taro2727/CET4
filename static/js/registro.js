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
    //Me faltaba hacer una cte llamada datos, esa dps se va a usar para el fetch (diccionario de py)
    const datos={
        email: email,
        contra: contra,
        confirmcontra: confirmcontra
    };
    //OBLIGATORIO QUE EL FETCH ESTÉ ADENTRO DEL EVENT LISTENER
    //para mandar un json a py:
fetch ('/crearcuenta/registrar',{
    method: 'POST',
    headers: {
        'Content-Type': 'aplication/json'
    },
    body: JSON.stringify(datos)
    //convierte todo lo anterior en un json (diccionario para py) llamado "datos"
})
})
