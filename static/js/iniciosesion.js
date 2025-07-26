document.getElementById("loginForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  const respuesta = await fetch("/verificar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    body: JSON.stringify({ email, password })
  });

  const resultado = await respuesta.json();

  if (resultado.exito) {
    window.location.href = '/indexhomeoinicio';
  } else {
    document.getElementById("mensaje").textContent = "Usuario o contraseña incorrectos.";
  }
});
