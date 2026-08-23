const CATEGORY_ICONS = [
    { code: 'fa-money-bill-wave', name: 'Salary' },
    { code: 'fa-wallet', name: 'Wallet' },
    { code: 'fa-laptop', name: 'Freelance' },
    { code: 'fa-building', name: 'Business' },
    { code: 'fa-chart-line', name: 'Investment' },
    { code: 'fa-gift', name: 'Gift' },
    { code: 'fa-undo', name: 'Refund' },
    { code: 'fa-utensils', name: 'Food' },
    { code: 'fa-coffee', name: 'Coffee' },
    { code: 'fa-shopping-basket', name: 'Groceries' },
    { code: 'fa-car', name: 'Car' },
    { code: 'fa-bus', name: 'Bus' },
    { code: 'fa-gas-pump', name: 'Fuel' },
    { code: 'fa-plane', name: 'Travel' },
    { code: 'fa-home', name: 'Housing' },
    { code: 'fa-bolt', name: 'Utilities' },
    { code: 'fa-wifi', name: 'Internet' },
    { code: 'fa-mobile-alt', name: 'Phone' },
    { code: 'fa-film', name: 'Entertainment' },
    { code: 'fa-gamepad', name: 'Games' },
    { code: 'fa-music', name: 'Music' },
    { code: 'fa-heartbeat', name: 'Health' },
    { code: 'fa-pills', name: 'Medicine' },
    { code: 'fa-shopping-bag', name: 'Shopping' },
    { code: 'fa-tshirt', name: 'Clothes' },
    { code: 'fa-graduation-cap', name: 'Education' },
    { code: 'fa-paw', name: 'Pets' },
    { code: 'fa-heart', name: 'Family' },
    { code: 'fa-credit-card', name: 'Cards' },
    { code: 'fa-ellipsis-h', name: 'Other' }
];

function initIconPicker(inputId) {
    const input = document.getElementById(inputId);
    const grid = document.getElementById('icon-grid');
    const search = document.getElementById('icon-search');
    if (!input || !grid) return;

    function render(filter) {
        grid.innerHTML = '';
        CATEGORY_ICONS.filter(function (icon) {
            return !filter || icon.name.toLowerCase().includes(filter.toLowerCase()) || icon.code.includes(filter);
        }).forEach(function (icon) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.innerHTML = '<i class="fas ' + icon.code + '"></i>';
            btn.title = icon.name;
            if (input.value === icon.code) btn.classList.add('active');
            btn.addEventListener('click', function () {
                input.value = icon.code;
                grid.querySelectorAll('button').forEach(function (el) { el.classList.remove('active'); });
                btn.classList.add('active');
            });
            grid.appendChild(btn);
        });
    }
    render('');
    if (search) search.addEventListener('input', function () { render(search.value); });
}
