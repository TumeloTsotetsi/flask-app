// CipherSense — Main JS

// Animate cards on scroll
const cards = document.querySelectorAll('.article-card, .comparison-card, .stat');
if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
        entries.forEach((e, i) => {
            if (e.isIntersecting) {
                setTimeout(() => {
                    e.target.style.opacity = '1';
                    e.target.style.transform = 'translateY(0)';
                }, i * 60);
                io.unobserve(e.target);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        io.observe(card);
    });
}

// Terminal typewriter on hero
const terminalLines = document.querySelectorAll('.t-line');
terminalLines.forEach((line, i) => {
    line.style.opacity = '0';
    setTimeout(() => {
        line.style.transition = 'opacity 0.3s ease';
        line.style.opacity = '1';
    }, 300 + i * 200);
});

// Article card click-through
document.querySelectorAll('.article-card').forEach(card => {
    const link = card.querySelector('.card-link');
    if (link) {
        card.addEventListener('click', () => {
            window.location.href = link.href;
        });
    }
});

// Active nav link highlight
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath ||
        (currentPath.startsWith('/category') && link.href.includes(currentPath.split('/')[2]))) {
        link.style.color = 'var(--accent-green)';
        link.style.borderColor = 'var(--accent-green)';
        link.style.background = 'rgba(0, 255, 159, 0.06)';
    }
});
