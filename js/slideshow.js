// ========================================
// MEMO PICS 2025 - SLIDESHOW GENERATOR
// ========================================

const Slideshow = {
    photos: [],
    selectedIds: [],
    currentIndex: 0,
    isPlaying: false,
    interval: null,
    progressInterval: null,
    duration: 3000,
    transition: 'fade',

    init() {
        this.photos = Utils.storage.get('slideshowPhotos', []);
        this.selectedIds = this.photos.map(p => p.id);
        this.setupEventListeners();
        this.updateUI();
    },

    setupEventListeners() {
        const durationSlider = document.getElementById('slideDuration');
        const durationValue = document.getElementById('durationValue');

        if (durationSlider) {
            durationSlider.addEventListener('input', (e) => {
                this.duration = parseInt(e.target.value) * 1000;
                durationValue.textContent = e.target.value + 's';
            });
        }

        const transitionSelect = document.getElementById('slideTransition');
        if (transitionSelect) {
            transitionSelect.addEventListener('change', (e) => {
                this.transition = e.target.value;
            });
        }

        // Keyboard controls for fullscreen
        document.addEventListener('keydown', (e) => {
            const fs = document.getElementById('fullscreenSlideshow');
            if (!fs || !fs.classList.contains('active')) return;

            switch (e.key) {
                case 'Escape':
                    this.exitFullscreen();
                    break;
                case 'ArrowLeft':
                    this.prev();
                    break;
                case 'ArrowRight':
                    this.next();
                    break;
                case ' ':
                    e.preventDefault();
                    this.toggle();
                    break;
            }
        });
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
        if (!grid) return;
        
        const allPhotos = Gallery.getFilteredPhotos();

        grid.innerHTML = allPhotos.map((photo, index) => {
            const isSelected = this.selectedIds.includes(photo.id);
            const orderIndex = this.selectedIds.indexOf(photo.id);

            return `
                <div class="slideshow-photo-item ${isSelected ? 'selected' : ''}" 
                     data-id="${photo.id}"
                     onclick="Slideshow.togglePhoto('${photo.id}')">
                    <img src="${photo.src}" alt="Photo ${index + 1}">
                    ${isSelected ? `<span class="order-badge">${orderIndex + 1}</span>` : ''}
                </div>
            `;
        }).join('');

        this.updateCount();
    },

    togglePhoto(photoId) {
        const existingIndex = this.selectedIds.indexOf(photoId);
        
        if (existingIndex !== -1) {
            this.selectedIds.splice(existingIndex, 1);
            this.photos = this.photos.filter(p => p.id !== photoId);
        } else {
            const photo = Gallery.photos.find(p => p.id === photoId);
            if (photo) {
                this.selectedIds.push(photoId);
                this.photos.push(photo);
            }
        }

        this.savePhotos();
        this.loadAvailablePhotos();
    },

    selectAll() {
        const allPhotos = Gallery.getFilteredPhotos();
        this.photos = [...allPhotos];
        this.selectedIds = allPhotos.map(p => p.id);
        this.savePhotos();
        this.loadAvailablePhotos();
        Toast.success('Selected All', `${this.photos.length} photos selected`);
    },

    deselectAll() {
        this.photos = [];
        this.selectedIds = [];
        this.savePhotos();
        this.loadAvailablePhotos();
        Toast.info('Deselected', 'All photos deselected');
    },

    removeSelected() {
        if (this.selectedIds.length === 0) {
            Toast.warning('None Selected', 'No photos to remove');
            return;
        }

        const count = this.selectedIds.length;
        this.photos = [];
        this.selectedIds = [];
        this.savePhotos();
        this.loadAvailablePhotos();
        Toast.success('Removed', `${count} photos removed from slideshow`);
    },

    savePhotos() {
        Utils.storage.set('slideshowPhotos', this.photos);
    },

    updateCount() {
        const countEl = document.getElementById('slideshowCount');
        if (countEl) {
            countEl.textContent = this.selectedIds.length;
        }
    },

    updateUI() {
        this.updateCount();
    },

    // Fullscreen Slideshow
    launchFullscreen() {
        if (this.photos.length === 0) {
            Toast.warning('No Photos', 'Please select photos for the slideshow');
            return;
        }

        // Close modal
        document.getElementById('slideshowModal').classList.remove('active');

        // Open fullscreen
        const fs = document.getElementById('fullscreenSlideshow');
        fs.classList.add('active');
        document.body.style.overflow = 'hidden';

        this.currentIndex = 0;
        this.updateFullscreenSlide();
        this.updateSlideCounter();

        // Auto-play
        setTimeout(() => {
            this.play();
        }, 500);
    },

    exitFullscreen() {
        this.stop();
        const fs = document.getElementById('fullscreenSlideshow');
        if (fs) {
            fs.classList.remove('active');
        }
        document.body.style.overflow = '';
    },

    updateFullscreenSlide() {
        const img = document.getElementById('fsSlideImage');
        const currentPhoto = this.photos[this.currentIndex];

        if (!currentPhoto || !img) return;

        // Apply transition
        const outClass = this.getOutClass();
        const inClass = this.getInClass();

        img.classList.add(outClass);

        setTimeout(() => {
            img.src = currentPhoto.src;
            img.classList.remove(outClass);
            img.classList.add(inClass);

            setTimeout(() => {
                img.classList.remove(inClass);
            }, 500);
        }, 300);

        this.updateSlideCounter();
    },

    getOutClass() {
        switch (this.transition) {
            case 'slide': return 'slide-out-left';
            case 'zoom': return 'zoom-out';
            default: return 'fade-out';
        }
    },

    getInClass() {
        switch (this.transition) {
            case 'slide': return 'slide-in-right';
            case 'zoom': return 'zoom-in';
            default: return 'fade-in';
        }
    },

    updateSlideCounter() {
        const currentEl = document.getElementById('fsCurrentSlide');
        const totalEl = document.getElementById('fsTotalSlides');
        if (currentEl) currentEl.textContent = this.currentIndex + 1;
        if (totalEl) totalEl.textContent = this.photos.length;
    },

    play() {
        if (this.photos.length === 0) return;

        this.isPlaying = true;
        this.updatePlayButton();
        this.startProgress();

        this.interval = setInterval(() => {
            this.next();
            this.startProgress();
        }, this.duration);
    },

    stop() {
        this.isPlaying = false;
        this.updatePlayButton();
        this.stopProgress();

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
        this.updateFullscreenSlide();
    },

    prev() {
        if (this.photos.length === 0) return;
        this.currentIndex = (this.currentIndex - 1 + this.photos.length) % this.photos.length;
        this.updateFullscreenSlide();
    },

    startProgress() {
        const progressBar = document.getElementById('fsProgressBar');
        if (!progressBar) return;

        progressBar.style.transition = 'none';
        progressBar.style.width = '0%';

        setTimeout(() => {
            progressBar.style.transition = `width ${this.duration}ms linear`;
            progressBar.style.width = '100%';
        }, 50);
    },

    stopProgress() {
        const progressBar = document.getElementById('fsProgressBar');
        if (progressBar) {
            progressBar.style.transition = 'none';
            progressBar.style.width = '0%';
        }
    },

    updatePlayButton() {
        const btn = document.getElementById('fsPlayPauseBtn');
        const modalBtn = document.getElementById('playPauseBtn');

        const icon = this.isPlaying ? 'fa-pause' : 'fa-play';

        if (btn) btn.innerHTML = `<i class="fas ${icon}"></i>`;
        if (modalBtn) modalBtn.innerHTML = `<i class="fas ${icon}"></i>`;
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
        if (!Slideshow.selectedIds.includes(photo.id)) {
            Slideshow.photos.push(photo);
            Slideshow.selectedIds.push(photo.id);
            Slideshow.savePhotos();
            Toast.success('Added!', 'Photo added to slideshow');
        } else {
            Toast.info('Already Added', 'This photo is already in the slideshow');
        }
    }
}
