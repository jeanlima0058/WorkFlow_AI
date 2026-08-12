const API_URL = "http://localhost:8000";

const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    message.textContent = "Entrando...";

    try {

        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                senha: senha
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Erro ao realizar login");
        }

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        window.location.href = "dashboard.html";

    } catch (error) {

        message.textContent = error.message;
    }
});