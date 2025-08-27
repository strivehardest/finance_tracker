document.addEventListener("DOMContentLoaded", () => {
    const transactionsList = document.getElementById("transactions-list");
    fetch("/api/transactions/")
        .then(res => res.json())
        .then(data => {
            data.forEach(tx => {
                const row = `<tr>
                    <td>${tx.date}</td>
                    <td>${tx.category}</td>
                    <td>${tx.amount}</td>
                    <td>${tx.description}</td>
                </tr>`;
                transactionsList.innerHTML += row;
            });
        })
        .catch(err => console.error("Error loading transactions:", err));
});

document.addEventListener("DOMContentLoaded", () => {
    const transactionsList = document.getElementById("transactions-list");

    fetch("/api/transactions/", {
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
        transactionsList.innerHTML = "";
        data.forEach(tx => {
            const row = `<tr>
                <td>${tx.date}</td>
                <td>${tx.category.name}</td>
                <td>${tx.amount}</td>
                <td>${tx.description}</td>
            </tr>`;
            transactionsList.innerHTML += row;
        });
    })
    .catch(err => console.error("Error loading transactions:", err));
});
