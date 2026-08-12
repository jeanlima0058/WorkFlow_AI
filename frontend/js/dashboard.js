const API_URL = "http://localhost:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "index.html";
}

async function loadUser() {

    try {

        const response = await fetch(`${API_URL}/auth/me`, {

            method: "GET",

            headers: {
                "Authorization": `Bearer ${token}`
            }

        });

        if (!response.ok) {

            localStorage.removeItem("access_token");

            window.location.href = "index.html";

            return;
        }

        const user = await response.json();

        document.getElementById("userName").textContent =
            user.nome;

        document.getElementById("userEmail").textContent =
            user.email;

    } catch (error) {

        console.error(error);
    }
}

document.getElementById("logout").addEventListener(
    "click",
    function () {

        localStorage.removeItem("access_token");

        window.location.href = "index.html";
    }
);

loadUser();