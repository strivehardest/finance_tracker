document.addEventListener("DOMContentLoaded", () => {
    const categoryList = document.getElementById("category-list");
    fetch("/api/categories/")
        .then(res => res.json())
        .then(data => {
            data.forEach(cat => {
                const li = document.createElement("li");
                li.textContent = cat.name;
                categoryList.appendChild(li);
            });
        })
        .catch(err => console.error("Error loading categories:", err));
});

document.addEventListener("DOMContentLoaded", () => {
    const categoryList = document.getElementById("category-list");

    fetch("/api/categories/", {
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        }
    })
    .then(res => {
        if (res.status === 401) {
            alert("Session expired. Please log in again.");
            window.location.href = "/login/";
        }
        return res.json();
    })
    .then(data => {
        categoryList.innerHTML = "";
        data.forEach(cat => {
            const li = document.createElement("li");
            li.textContent = cat.name;
            categoryList.appendChild(li);
        });
    })
    .catch(err => console.error("Error loading categories:", err));
});
