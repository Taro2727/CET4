document.getElementById("loginForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const usuario = document.getElementById("email").value;
  const contrasena = document.getElementById("password").value;

  const respuesta = await fetch("/verificar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ usuario, contrasena })
  });

  const resultado = await respuesta.json();

  if (resultado.exito) {
    window.location.href = "url('https://www.youtube.com/')";
  } else {
    document.getElementById("mensaje").textContent = "Usuario o contraseña incorrectos.";
  }
});