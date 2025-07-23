let regi = document.getElementById('registro');
regi.addEventListener('submit',async function (event){
    event.preventDefault(); 
    const nombre = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const contra = document.getElementById('password').value;
    const confirmcontra = document.getElementById('confirm').value;
    const datos={
        name:nombre,
        email: email,
        contra: contra,
        confcontra: confirmcontra
    };

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/crearcuenta/registrar', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(datos)
})

    .then(async response =>{
        const text = await response.text();
        if(!response.ok) {
            alert("error " + text);
        }else{
            alert(text);
        }
    });
    });
//el 1er }); cierra el .then y el 2do cierra el eventlistener