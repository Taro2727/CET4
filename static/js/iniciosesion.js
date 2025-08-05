document.getElementById("loginForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const mensajehtml = document.getElementById("mensaje")

  const regex = /^(?=.*[A-Z])(?=.*[0-9]).{8,}$/;

  if (!regex.test(password)) {
    mensajehtml.textContent = "Error: Contraseña muy corta.";
    return;
  }

  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  const respuesta = await fetch("/otp_login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    body: JSON.stringify({ email, password })
  });

  const resultado = await respuesta.json();

  if (resultado.success) {
    // Redirige a la página para ingresar el código OTP
    window.location.href = '/IngresarCodigo';
  } else {
    document.getElementById("mensaje").textContent = resultado.error || "No se pudo enviar el código OTP.";
  }
});