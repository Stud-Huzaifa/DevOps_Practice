document.addEventListener('DOMContentLoaded', function() {
    const arcs = document.querySelectorAll('.arc');
    const searchInput = document.getElementById('arc-search');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const themeSwitcher = document.querySelector('.theme-switcher');
    const rootElement = document.documentElement;
    const navLinks = document.querySelectorAll('nav a');
    const sections = document.querySelectorAll('main section[id]');

    const applyTheme = (theme) => {
        if (theme === 'light') {
            rootElement.classList.add('light-theme');
            if (themeSwitcher) themeSwitcher.textContent = '☀️';
        } else {
            rootElement.classList.remove('light-theme');
            if (themeSwitcher) themeSwitcher.textContent = '🌙';
        }
        localStorage.setItem('site-theme', theme);
    };

    applyTheme(localStorage.getItem('site-theme') || 'dark');

    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', function() {
            const nextTheme = rootElement.classList.contains('light-theme') ? 'dark' : 'light';
            applyTheme(nextTheme);
        });
    }

    // Toggle expand for arc cards
    arcs.forEach(arc => {
        arc.addEventListener('click', function() {
            this.classList.toggle('expanded');
        });
    });

    // Sidebar toggle button
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            const isClosed = sidebar.classList.toggle('closed');
            this.setAttribute('aria-expanded', String(!isClosed));
        });
    }

    // Search filter for arcs and cards
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            arcs.forEach(arc => {
                const title = arc.querySelector('h3')?.textContent.toLowerCase() || '';
                const description = arc.querySelector('p')?.textContent.toLowerCase() || '';
                const match = title.includes(query) || description.includes(query);
                arc.classList.toggle('hidden', query.length > 0 && !match);
            });
        });
    }

    // Smooth scrolling for internal anchor links only
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (!href || (!href.startsWith('#') && !href.includes('index.html#'))) {
            return;
        }

        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').split('#').pop();
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Section observer for active sidebar link highlighting
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -40% 0px',
        threshold: 0.2,
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        document.querySelectorAll('nav a.active').forEach(link => link.classList.remove('active'));
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const id = entry.target.id;
            const activeLink = document.querySelector(`nav a[href$='${id}']`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        });
    }, observerOptions);

    sections.forEach(section => sectionObserver.observe(section));

    // Contact form toggle and submit
    const contactLink = document.getElementById('contact-link');
    const contactForm = document.getElementById('contact-form');
    const form = document.querySelector('#contact-form form');

    if (contactLink && contactForm) {
        contactLink.addEventListener('click', function(e) {
            e.preventDefault();
            const isHidden = contactForm.style.display === 'none' || !contactForm.style.display;
            contactForm.style.display = isHidden ? 'block' : 'none';
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your question! We\'ll get back to you soon.');
            form.reset();
            if (contactForm) contactForm.style.display = 'none';
        });
    }

    // Pirate-themed animation on load
    setTimeout(() => {
        const header = document.querySelector('header');
        if (header) {
            const treasure = document.createElement('div');
            treasure.className = 'treasure';
            treasure.textContent = '🏴‍☠️';
            header.appendChild(treasure);
            setTimeout(() => treasure.remove(), 3000);
        }
    }, 2000);
});