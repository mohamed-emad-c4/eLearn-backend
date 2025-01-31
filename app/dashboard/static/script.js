document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            try {
                const response = await fetch("http://127.0.0.1:8000/api/users/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: new URLSearchParams({ "username": email, "password": password })
                });
            
                const data = await response.json();
                console.log("Server Response:", data);  // ✅ Log the response
            
                if (response.ok) {
                    localStorage.setItem("token", data.access_token);
                    alert("✅ Login successful!");
                    window.location.href = "/dashboard";
                } else {
                    alert("❌ Error: " + (data.detail || "Unknown error"));
                }
            } catch (error) {
                console.error("⚠️ Server connection error:", error);
                alert("⚠️ Server connection error: " + error.message);
            }
            
        });
    }
});
