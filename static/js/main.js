document.addEventListener("DOMContentLoaded", () => {
    const ctx = document.getElementById('summaryChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Income', 'Expenses'],
                datasets: [{
                    label: 'Amount',
                    data: [5000, 3000],
                    backgroundColor: ['green', 'red']
                }]
            }
        });
    }
});
