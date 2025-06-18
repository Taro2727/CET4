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
    fetch ('/crearcuenta/registrar',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.text())
    .then(data => {
        alert(data); 
    });
});