// ========================================
// MEMO PICS 2025 - SLIDESHOW GENERATOR
// ========================================

const Slideshow = {
    photos: [],
    currentIndex: 0,
    isPlaying: false,
    interval: null,
    duration: 3000,
    transition: 'fade',

    init() {
        this.photos = Utils.storage.get('slideshowPhotos', []);
        this.setupEventListeners();
        this.updateUI();
    },

    setupEventListeners() {
        // Duration slider
        const durationSlider = document.getElementById('slideDuration');
        const durationValue = document.getElementById('durationValue');

        if (durationSlider) {
            durationSlider.addEventListener('input', (e) => {
                this.duration = parseInt(e.target.value) * 1000;
                durationValue.textContent = e.target.value + 's';
            });
        }

        // Transition select
        const transitionSelect = document.getElementById('slideTransition');
        if (transitionSelect) {
            transitionSelect.addEventListener('change', (e) => {
                this.transition = e.target.value;
            });
        }
    },

    open() {
        this.loadAvailablePhotos();
        document.getElementById('slideshowModal').classList.add('active');
    },

    close() {
        this.stop();
        document.getElementById('slideshowModal').classList.remove('active');
    },

    loadAvailablePhotos() {
        const grid = document.getElementById('slideshowPhotosGrid');
        const allPhotos = Gallery.getFilteredPhotos();

        grid.innerHTML = allPhotos.map((photo, index) => {
            const isSelected = this.photos.some(p => p.id === photo.id);
            const orderIndex = this.photos.findIndex(p => p.id === photo.id);

            return `
                <div class="slideshow-photo-item ${isSelected ? 'selected' : ''}" 
                     data-id="${photo.id}"
                     onclick="Slideshow.togglePhoto('${photo.id}')">
                    <img src="${photo.src}" alt="Photo ${index + 1}">
                    ${isSelected ? `<span class="order-badge">${orderIndex + 1}</span>` : ''}
                </div>
            `;
        }).join('');
    },

    togglePhoto(photoId) {
        const existingIndex = this.photos.findIndex(p => p.id === photoId);
        
        if (existingIndex !== -1) {
            this.photos.splice(existingIndex, 1);
        } else {
            const photo = Gallery.photos.find(p => p.id === photoId);
            if (photo) {
                this.photos.push(photo);
            }
        }

        Utils.storage.set('slideshowPhotos', this.photos);
        this.loadAvailablePhotos();
        this.updateUI();
    },

    updateUI() {
        const countEl = document.getElementById('slideshowCount');
        const previewEl = document.getElementById('slideshowPreview');

        if (countEl) {
            countEl.textContent = this.photos.length;
        }

        if (previewEl) {
            if (this.photos.length === 0) {
                previewEl.innerHTML = `
                    <div class="no-photos">
                        <i class="fas fa-images"></i>
                        <p>Select photos below to create a slideshow</p>
                    </div>
                `;
            } else {
                const currentPhoto = this.photos[this.currentIndex];
                previewEl.innerHTML = `<img src="${currentPhoto.src}" alt="Slideshow">`;
            }
        }
    },

    play() {
        if (this.photos.length === 0) {
            Toast.warning('No Photos', 'Please select photos for the slideshow');
            return;
        }

        this.isPlaying = true;
        this.updatePlayButton();

        this.interval = setInterval(() => {
            this.next();
        }, this.duration);
    },

    stop() {
        this.isPlaying = false;
        this.updatePlayButton();

        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    },

    toggle() {
        if (this.isPlaying) {
            this.stop();
        } else {
            this.play();
        }
    },

    next() {
        if (this.photos.length === 0) return;

        this.currentIndex = (this.currentIndex + 1) % this.photos.length;
        this.animateTransition();
    },

    prev() {
        if (this.photos.length === 0) return;

        this.currentIndex = (this.currentIndex - 1 + this.photos.length) % this.photos.length;
        this.animateTransition();
    },

    animateTransition() {
        const preview = document.getElementById('slideshowPreview');
        const img = preview.querySelector('img');
        
        if (!img) {
            this.updateUI();
            return;
        }

        switch (this.transition) {
            case 'fade':
                img.style.opacity = '0';
                setTimeout(() => {
                    img.src = this.photos[this.currentIndex].src;
                    img.style.opacity = '1';
                }, 300);
                break;

            case 'slide':
                img.style.transform = 'translateX(-100%)';
                setTimeout(() => {
                    img.src = this.photos[this.currentIndex].src;
                    img.style.transform = 'translateX(0)';
                }, 300);
                break;

            case 'zoom':
                img.style.transform = 'scale(0.5)';
                img.style.opacity = '0';
                setTimeout(() => {
                    img.src = this.photos[this.currentIndex].src;
                    img.style.transform = 'scale(1)';
                    img.style.opacity = '1';
                }, 300);
                break;

            default:
                img.src = this.photos[this.currentIndex].src;
        }
    },

    updatePlayButton() {
        const btn = document.getElementById('playPauseBtn');
        if (btn) {
            btn.innerHTML = this.isPlaying 
                ? '<i class="fas fa-pause"></i>' 
                : '<i class="fas fa-play"></i>';
        }
    },

    startFullscreen() {
        if (this.photos.length === 0) {
            Toast.warning('No Photos', 'Please select photos first');
            return;
        }

        // Create fullscreen slideshow
        const overlay = document.createElement('div');
        overlay.className = 'fullscreen-slideshow';
        overlay.innerHTML = `
            <div class="fs-content">
                <img src="${this.photos[0].src}" alt="Slideshow">
            </div>
            <button class="fs-close" onclick="Slideshow.exitFullscreen()">&times;</button>
            <div class="fs-controls">
                <button onclick="Slideshow.prev()"><i class="fas fa-chevron-left"></i></button>
                <button onclick="Slideshow.toggle()"><i class="fas fa-pause"></i></button>
                <button onclick="Slideshow.next()"><i class="fas fa-chevron-right"></i></button>
            </div>
        `;

        document.body.appendChild(overlay);
        this.currentIndex = 0;
        this.play();

        // Add fullscreen styles
        const style = document.createElement('style');
        style.id = 'fullscreen-style';
        style.textContent = `
            .fullscreen-slideshow {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #000;
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .fs-content img {
                max-width: 100%;
                max-height: 100%;
                transition: all 0.5s ease;
            }
            .fs-close {
                position: absolute;
                top: 20px;
                right: 20px;
                width: 50px;
                height: 50px;
                background: rgba(255,255,255,0.1);
                border: none;
                border-radius: 50%;
                color: white;
                font-size: 2rem;
                cursor: pointer;
            }
            .fs-controls {
                position: absolute;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 20px;
            }
            .fs-controls button {
                width: 60px;
                height: 60px;
                background: rgba(255,215,0,0.2);
                border: 1px solid rgba(255,215,0,0.5);
                border-radius: 50%;
                color: #FFD700;
                font-size: 1.5rem;
                cursor: pointer;
                transition: all 0.3s;
            }
            .fs-controls button:hover {
                background: #FFD700;
                color: #000;
            }
        `;
        document.head.appendChild(style);
    },

    exitFullscreen() {
        this.stop();
        const overlay = document.querySelector('.fullscreen-slideshow');
        const style = document.getElementById('fullscreen-style');
        
        if (overlay) overlay.remove();
        if (style) style.remove();
    },

    clearSelection() {
        this.photos = [];
        this.currentIndex = 0;
        Utils.storage.set('slideshowPhotos', []);
        this.loadAvailablePhotos();
        this.updateUI();
    }
};

// Global functions
function startSlideshow() {
    Slideshow.open();
}

function closeSlideshow() {
    Slideshow.close();
}

function toggleSlideshow() {
    Slideshow.toggle();
}

function nextSlide() {
    Slideshow.next();
}

function prevSlide() {
    Slideshow.prev();
}

function addToSlideshow() {
    const photo = Viewer.getCurrentPhoto();
    if (photo) {
        if (!Slideshow.photos.some(p => p.id === photo.id)) {
            Slideshow.photos.push(photo);
            Utils.storage.set('slideshowPhotos', Slideshow.photos);
            Toast.success('Added!', 'Photo added to slideshow');
        } else {
            Toast.info('Already Added', 'This photo is already in the slideshow');
        }
    }
}