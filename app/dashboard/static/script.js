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
document.addEventListener("DOMContentLoaded", function () {
    const token = localStorage.getItem("token");
    if (!token && window.location.pathname !== "/login") {
        window.location.href = "/login";
    }
});


document.addEventListener("DOMContentLoaded", function () {
    console.log("Dashboard JS Loaded ✅");
});

// Show Update Course Form & Fill Fields
// Show Update Course Form & Fill Fields
function showUpdateForm(id, name, level, description, category, language, image_url, status) {
    document.getElementById("update-course-id").value = id;
    document.getElementById("update-course-name").value = name;
    document.getElementById("update-course-level").value = level;
    document.getElementById("update-course-description").value = description;
    document.getElementById("update-course-category").value = category;
    document.getElementById("update-course-language").value = language;
    document.getElementById("update-course-image").value = image_url;
    document.getElementById("update-course-status").value = status;

    // ✅ Set correct form action dynamically
    document.getElementById("updateCourseForm").action = `/update_course/${id}`;

    document.getElementById("updateCourseContainer").style.display = "block";
}


// Hide Update Course Form
function hideUpdateForm() {
    document.getElementById("updateCourseContainer").style.display = "none";
}


document.getElementById("updateCourseForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(this);

    fetch("/update_course/" + document.getElementById("update-course-id").value, {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert("✅ Course updated successfully!");
        window.location.reload();
    })
    .catch(error => console.error("❌ Error updating course:", error));
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", function () {
            showUpdateForm(
                this.dataset.id,
                this.dataset.name,
                this.dataset.level,
                this.dataset.description,
                this.dataset.category,
                this.dataset.language,
                this.dataset.image,
                this.dataset.status
            );
        });
    });
});




