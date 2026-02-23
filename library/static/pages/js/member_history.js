// Pagination Logic

document.addEventListener('DOMContentLoaded', function () {
    // Items per page for each section
    const itemsPerPage = 6;

    // Initialize pagination for borrows
    initPagination('borrows', itemsPerPage);

    // Initialize pagination for reservations
    initPagination('reservations', itemsPerPage);
});

function initPagination(section, itemsPerPage) {
    const grid = document.getElementById(`${section}-grid`);
    const items = grid.querySelectorAll('.history-card');

    // Skip if no items or only empty state
    if (items.length === 0) {
        return;
    }

    // Calculate total pages
    const totalPages = Math.ceil(items.length / itemsPerPage);

    // Store current page in data attribute
    grid.dataset.currentPage = 1;
    grid.dataset.totalPages = totalPages;
    grid.dataset.itemsPerPage = itemsPerPage;

    // Initial display
    displayItems(section, 1);

    // Update pagination controls
    updatePaginationControls(section);
}

function displayItems(section, page) {
    const grid = document.getElementById(`${section}-grid`);
    const items = grid.querySelectorAll('.history-card');
    const itemsPerPage = parseInt(grid.dataset.itemsPerPage);

    // Hide all items
    items.forEach(item => {
        item.style.display = 'none';
    });

    // Calculate start and end indices
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;

    // Show items for current page
    for (let i = startIndex; i < endIndex && i < items.length; i++) {
        items[i].style.display = 'flex';
    }

    // Update current page
    grid.dataset.currentPage = page;

    // Update pagination controls
    updatePaginationControls(section);
}

function updatePaginationControls(section) {
    const grid = document.getElementById(`${section}-grid`);
    const currentPage = parseInt(grid.dataset.currentPage);
    const totalPages = parseInt(grid.dataset.totalPages);

    // Update prev/next buttons
    const prevBtn = document.getElementById(`${section}-prev`);
    const nextBtn = document.getElementById(`${section}-next`);

    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;

    // Update page numbers
    const pageNumbersContainer = document.getElementById(`${section}-page-numbers`);
    pageNumbersContainer.innerHTML = '';

    // Determine which page numbers to show
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);

    // Adjust if we're near the end
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }

    // Add page numbers
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `pagination-btn ${i === currentPage ? 'pagination-current' : ''}`;
        pageBtn.textContent = i;
        pageBtn.onclick = function () {
            changePage(section, i - currentPage);
        };
        pageNumbersContainer.appendChild(pageBtn);
    }
}

function changePage(section, offset) {
    const grid = document.getElementById(`${section}-grid`);
    const currentPage = parseInt(grid.dataset.currentPage);
    const totalPages = parseInt(grid.dataset.totalPages);

    // Calculate new page
    let newPage;
    if (typeof offset === 'number') {
        // Previous/next button
        newPage = currentPage + offset;
    } else {
        // Direct page number
        newPage = offset;
    }

    // Ensure valid page
    newPage = Math.max(1, Math.min(totalPages, newPage));

    // Display items for new page
    displayItems(section, newPage);
}
