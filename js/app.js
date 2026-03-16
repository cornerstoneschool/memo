// ========================================
// MEMO PICS 2025 - MAIN APPLICATION
// ========================================

const App = {
    init() {
        // Hide loader after everything is ready
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.getElementById('loader').classList.add('hidden');
            }, 1000);
        });

        // Initialize all modules
        Toast.init();
        Auth.init();
        Gallery.init();
        Viewer.init();
        Reactions.init();
        StickerMaker.init();
        Slideshow.init();
        Admin.init();

        // Setup UI
        this.setupNavigation();
        this.setupHero();
        this.setupSearch();
        this.checkUrlParams();

        // Render initial content
        Gallery.renderFeatured();
        Gallery.updateStats();

        console.log('✨ Memo Pics 2025 Initialized');
    },

    setupNavigation() {
        // Nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                const section = link.dataset.section;
                
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                switch (section) {
                    case 'home':
                        Utils.scrollToElement(document.getElementById('hero'), 0);
                        break;
                    case 'gallery':
                        Utils.scrollToElement(document.getElementById('gallery'), 80);
                        break;
                    case 'slideshow':
                        Slideshow.open();
                        break;
                }
            });
        });

        // Update active nav on scroll
        window.addEventListener('scroll', Utils.throttle(() => {
            const sections = ['hero', 'gallery'];
            const scrollPos = window.scrollY + 100;

            sections.forEach(sectionId => {
                const section = document.getElementById(sectionId);
                if (!section) return;

                const top = section.offsetTop;
                const height = section.offsetHeight;

                if (scrollPos >= top && scrollPos < top + height) {
                    document.querySelectorAll('.nav-link').forEach(link => {
                        link.classList.toggle('active', 
                            link.dataset.section === (sectionId === 'hero' ? 'home' : sectionId)
                        );
                    });
                }
            });
        }, 100));

        // Close modals on overlay click
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', () => {
                overlay.parentElement.classList.remove('active');
            });
        });

        // Close modals on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal.active').forEach(modal => {
                    modal.classList.remove('active');
                });
            }
        });
    },

    setupHero() {
        // Create particles
        const particleContainer = document.getElementById('heroParticles');
        if (particleContainer) {
            Utils.createParticles(particleContainer, 50);
        }

        // Animate stats on scroll
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    Gallery.updateStats();
                    observer.unobserve(entry.target);
                }
            });
        });

        const heroStats = document.querySelector('.hero-stats');
        if (heroStats) {
            observer.observe(heroStats);
        }
    },

    setupSearch() {
        const searchBar = document.getElementById('searchBar');
        let searchOpen = false;

        window.toggleSearch = () => {
            searchOpen = !searchOpen;
            searchBar.classList.toggle('active', searchOpen);

            if (searchOpen) {
                document.getElementById('searchInput').focus();
            }
        };

        window.clearSearch = () => {
            document.getElementById('searchInput').value = '';
            Gallery.render();
            toggleSearch();
        };

        // Close search on click outside
        document.addEventListener('click', (e) => {
            if (searchOpen && !searchBar.contains(e.target) && !e.target.closest('.search-btn')) {
                toggleSearch();
            }
        });
    },

    checkUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const photoId = params.get('photo');

        if (photoId) {
            // Open specific photo
            setTimeout(() => {
                Viewer.open(photoId);
            }, 1500);
        }
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Service Worker for PWA (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // navigator.serviceWorker.register('/sw.js')
        //     .then(reg => console.log('SW registered'))
        //     .catch(err => console.log('SW registration failed'));
    });
}