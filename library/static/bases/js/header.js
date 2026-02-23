// Header JavaScript
// Theme Toggle Logic
const currentTheme = localStorage.getItem('theme') ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
document.documentElement.setAttribute('data-theme', currentTheme);

const themeIcon = document.getElementById('themeIcon');
if (currentTheme === 'dark') {
    themeIcon.textContent = 'light_mode';
} else {
    themeIcon.textContent = 'dark_mode';
}

function toggleTheme() {
    let theme = document.documentElement.getAttribute('data-theme');
    let newTheme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    if (newTheme === 'dark') {
        themeIcon.textContent = 'light_mode';
    } else {
        themeIcon.textContent = 'dark_mode';
    }
}

// Mobile Menu Logic
function toggleMobileMenu() {
    const nav = document.getElementById('navMenu');
    nav.classList.toggle('open');
}

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    const nav = document.getElementById('navMenu');
    const menuBtn = document.querySelector('.mobile-menu-btn');
    if (!nav.contains(e.target) && !menuBtn.contains(e.target) && nav.classList.contains('open')) {
        nav.classList.remove('open');
    }
});


const searchInput = document.getElementById("search-input");
const searchForm = document.getElementById("search-form");

searchInput.addEventListener('keypress', (event) =>{
    if (event.key === "Enter") {
        searchForm.submit();
    }
});


    // Profile Menu Logic
    function toggleProfileMenu() {
        const profileMenu = document.querySelector('.profile-menu .profile-dropdown');
        profileMenu.classList.toggle('open');
    }