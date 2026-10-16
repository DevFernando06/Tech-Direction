/**
 * Tech Direction - Gestão e Pesquisa de Trilhas Criadas
 */

function filterTrails() {
    const searchInput = document.getElementById('searchTrail');
    const statusSelect = document.getElementById('filterStatus');
    const categorySelect = document.getElementById('filterCategory');
    const noResults = document.getElementById('noResults');

    const term = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const selectedStatus = statusSelect ? statusSelect.value.toLowerCase() : 'all';
    const selectedCategory = categorySelect ? categorySelect.value : 'all';

    const rows = document.querySelectorAll('.trail-row');
    let visibleCount = 0;

    rows.forEach((row) => {
        const title = (row.getAttribute('data-title') || '').toLowerCase();
        const author = (row.getAttribute('data-author') || '').toLowerCase();
        const category = row.getAttribute('data-category') || '';
        const status = (row.getAttribute('data-status') || '').toLowerCase();

        const matchesText = !term || title.includes(term) || author.includes(term) || category.toLowerCase().includes(term);
        const matchesStatus = selectedStatus === 'all' || status === selectedStatus;
        const matchesCategory = selectedCategory === 'all' || category === selectedCategory;

        const isVisible = matchesText && matchesStatus && matchesCategory;
        row.style.display = isVisible ? '' : 'none';

        if (isVisible) {
            visibleCount++;
        }
    });

    const countDisplay = document.getElementById('visibleTrailsCount');
    if (countDisplay) {
        countDisplay.textContent = visibleCount;
    }

    if (noResults) {
        if (visibleCount === 0) {
            noResults.classList.remove('hidden');
        } else {
            noResults.classList.add('hidden');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchTrail');
    if (searchInput) {
        searchInput.addEventListener('input', filterTrails);
    }

    const statusSelect = document.getElementById('filterStatus');
    if (statusSelect) {
        statusSelect.addEventListener('change', filterTrails);
    }

    const categorySelect = document.getElementById('filterCategory');
    if (categorySelect) {
        categorySelect.addEventListener('change', filterTrails);
    }

    const btnClearFilters = document.getElementById('btnClearFilters');
    if (btnClearFilters) {
        btnClearFilters.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            if (statusSelect) statusSelect.value = 'all';
            if (categorySelect) categorySelect.value = 'all';
            filterTrails();
        });
    }
});
