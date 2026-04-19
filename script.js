document.addEventListener('DOMContentLoaded', function() {
    // Add click event to each arc
    const arcs = document.querySelectorAll('.arc');
    arcs.forEach(arc => {
        arc.addEventListener('click', function() {
            this.classList.toggle('expanded');
        });
    });

    // Contact link toggle
    const contactLink = document.getElementById('contact-link');
    const contactForm = document.getElementById('contact-form');
    contactLink.addEventListener('click', function(e) {
        e.preventDefault();
        contactForm.style.display = contactForm.style.display === 'none' ? 'block' : 'none';
    });

    // Form submission (basic, just alert for now)
    const form = document.querySelector('#contact-form form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        alert('Thank you for your question! We\'ll get back to you soon.');
        form.reset();
        contactForm.style.display = 'none';
    });

    // Smooth scrolling for nav links
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            targetElement.scrollIntoView({ behavior: 'smooth' });
        });
    });

    // Add some pirate-themed interactions
    // Random treasure chest animation on load
    setTimeout(() => {
        const header = document.querySelector('header');
        header.innerHTML += '<div class="treasure">🏴‍☠️</div>';
        setTimeout(() => {
            document.querySelector('.treasure').remove();
        }, 3000);
    }, 2000);
});