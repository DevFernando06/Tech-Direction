/**
 * Tech Direction - Gestão e Pesquisa de Posts
 */

function filterPosts() {
    const searchInput = document.getElementById('searchPost');
    const statusSelect = document.getElementById('filterStatus');
    const noResults = document.getElementById('noResults');

    const term = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const selectedStatus = statusSelect ? statusSelect.value.toLowerCase() : 'all';

    const rows = document.querySelectorAll('.post-row');
    let visibleCount = 0;

    rows.forEach((row) => {
        const title = (row.getAttribute('data-title') || '').toLowerCase();
        const status = (row.getAttribute('data-status') || '').toLowerCase();

        const matchesText = !term || title.includes(term);
        const matchesStatus = selectedStatus === 'all' || status === selectedStatus;

        const isVisible = matchesText && matchesStatus;
        row.style.display = isVisible ? '' : 'none';

        if (isVisible) {
            visibleCount++;
        }
    });

    const countDisplay = document.getElementById('visiblePostsCount');
    if (countDisplay) {
        countDisplay.textContent = visibleCount;
    }

    if (noResults) {
        noResults.classList.toggle('hidden', visibleCount > 0);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchPost');
    if (searchInput) {
        searchInput.addEventListener('input', filterPosts);
    }

    const statusSelect = document.getElementById('filterStatus');
    if (statusSelect) {
        statusSelect.addEventListener('change', filterPosts);
    }

    const btnClearFilters = document.getElementById('btnClearFilters');
    if (btnClearFilters) {
        btnClearFilters.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            if (statusSelect) statusSelect.value = 'all';
            filterPosts();
        });
    }
});
