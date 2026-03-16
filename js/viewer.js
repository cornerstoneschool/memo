// ========================================
// MEMO PICS 2025 - PHOTO VIEWER
// ========================================

const Viewer = {
    currentPhotoId: null,
    currentIndex: 0,
    photos: [],

    init() {
        this.setupEventListeners();
    },

    setupEventListeners() {
        // Close on overlay click
        document.querySelector('.viewer-overlay').addEventListener('click', () => {
            this.close();
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!document.getElementById('photoViewer').classList.contains('active')) return;

            switch (e.key) {
                case 'Escape':
                    this.close();
                    break;
                case 'ArrowLeft':
                    this.navigate(-1);
                    break;
                case 'ArrowRight':
                    this.navigate(1);
                    break;
            }
        });

        // Swipe support for mobile
        let touchStartX = 0;
        const viewer = document.getElementById('photoViewer');

        viewer.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
        });

        viewer.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > 50) {
                if (diff > 0) {
                    this.navigate(1); // Swipe left - next
                } else {
                    this.navigate(-1); // Swipe right - prev
                }
            }
        });
    },

    open(photoId) {
        this.currentPhotoId = photoId;
        this.photos = Gallery.getFilteredPhotos();
        this.currentIndex = this.photos.findIndex(p => p.id === photoId);

        if (this.currentIndex === -1) return;

        this.updateView();
        document.getElementById('photoViewer').classList.add('active');
        document.body.style.overflow = 'hidden';

        // Increment view count
        const photo = this.getCurrentPhoto();
        if (photo) {
            photo.views = (photo.views || 0) + 1;
            Gallery.savePhotos();
        }
    },

    close() {
        document.getElementById('photoViewer').classList.remove('active');
        document.body.style.overflow = '';
    },

    navigate(direction) {
        this.currentIndex += direction;

        if (this.currentIndex < 0) {
            this.currentIndex = this.photos.length - 1;
        } else if (this.currentIndex >= this.photos.length) {
            this.currentIndex = 0;
        }

        this.currentPhotoId = this.photos[this.currentIndex].id;
        this.updateView();
    },

    updateView() {
        const photo = this.getCurrentPhoto();
        if (!photo) return;

        // Update image
        const img = document.getElementById('viewerImage');
        img.src = photo.src;
        img.alt = photo.name || 'Photo';

        // Update reactions
        Reactions.updateViewerReactions(photo);
    },

    getCurrentPhoto() {
        return this.photos[this.currentIndex];
    }
};

// Global functions
function closeViewer() {
    Viewer.close();
}

function navigatePhoto(direction) {
    Viewer.navigate(direction);
}

function downloadPhoto() {
    if (Viewer.currentPhotoId) {
        Gallery.downloadPhoto(Viewer.currentPhotoId);
    }
}

function sharePhoto() {
    const photo = Viewer.getCurrentPhoto();
    if (!photo) return;

    document.getElementById('shareLink').value = window.location.href + '?photo=' + photo.id;
    document.getElementById('shareModal').classList.add('active');
}

function closeShareModal() {
    document.getElementById('shareModal').classList.remove('active');
}

function shareToWhatsApp() {
    const photo = Viewer.getCurrentPhoto();
    const text = `Check out this photo from Memo Pics 2025! ${window.location.href}?photo=${photo.id}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
}

function shareToFacebook() {
    const url = window.location.href + '?photo=' + Viewer.currentPhotoId;
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
}

function shareToTwitter() {
    const text = 'Check out this photo from Memo Pics 2025!';
    const url = window.location.href + '?photo=' + Viewer.currentPhotoId;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
}

function shareToInstagram() {
    Toast.info('Instagram', 'Download the photo and share it on Instagram!');
    downloadPhoto();
}

function copyShareLink() {
    const input = document.getElementById('shareLink');
    Utils.copyToClipboard(input.value);
    Toast.success('Copied!', 'Link copied to clipboard');
}