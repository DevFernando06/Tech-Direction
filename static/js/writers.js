function filterWriters(query) {
    const term = query.toLowerCase();
    const rows = document.querySelectorAll('.writer-row');
    rows.forEach((row) => {
        const name = (row.getAttribute('data-name') || '').toLowerCase();
        const login = (row.getAttribute('data-login') || '').toLowerCase();
        const email = (row.getAttribute('data-email') || '').toLowerCase();
        const match = name.includes(term) || login.includes(term) || email.includes(term);
        row.style.display = match ? '' : 'none';
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchWriter');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => filterWriters(e.target.value));
    }
});

