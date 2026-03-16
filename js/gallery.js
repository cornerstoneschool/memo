// ========================================
// MEMO PICS 2025 - GALLERY MANAGEMENT
// ========================================

const Gallery = {
    photos: [],
    filteredPhotos: [],
    categories: [],
    currentCategory: 'all',
    currentSort: 'newest',
    currentView: 'grid',
    photosPerPage: 12,
    currentPage: 1,

    async async init() {
        await this.loadData();
        this.setupEventListeners();
        this.render();
        this.renderCategories();
        this.updateStats();
        if(typeof this.renderFeatured === 'function') this.renderFeatured();
    },

    async loadData() {
        try {
            // Bypass cache to get latest photos
            const response = await fetch('./data/photos.json?v=' + new Date().getTime());
            if(response.ok) {
                const data = await response.json();
                this.photos = data.photos || [];
                if(data.categories && data.categories.length > 0) this.categories = data.categories;
            } else throw new Error("No JSON");
        } catch (error) {
            this.photos = Utils.storage.get('photos', []);
            this.categories = Utils.storage.get('categories', [
                { id: 'all', name: 'All Photos', icon: 'fa-th', teachersOnly: false },
                { id: 'teachers-only', name: 'Teachers Only', icon: 'fa-lock', teachersOnly: true }
            ]);
        }
    },

    setupEventListeners() {
        // Sort select
        document.getElementById('sortSelect').addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.render();
        });

        // View toggle
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentView = btn.dataset.view;
                this.updateGridView();
            });
        });

        // Search
        document.getElementById('searchInput').addEventListener('input', 
            Utils.debounce((e) => {
                this.search(e.target.value);
            }, 300)
        );
    },

    renderCategories() {
        const container = document.getElementById('categoryTabs');
        container.innerHTML = '';

        this.categories.forEach(cat => {
            // Skip teachers-only categories for non-teachers
            if (cat.teachersOnly && !Auth.canViewTeacherContent()) {
                return;
            }

            const btn = document.createElement('button');
            btn.className = `category-tab ${this.currentCategory === cat.id ? 'active' : ''}`;
            btn.dataset.category = cat.id;
            btn.innerHTML = `
                <i class="fas ${cat.icon}"></i>
                <span>${cat.name}</span>
                ${cat.teachersOnly ? '<i class="fas fa-lock lock-icon"></i>' : ''}
            `;
            btn.addEventListener('click', () => this.filterByCategory(cat.id));
            container.appendChild(btn);
        });
    },

    filterByCategory(categoryId) {
        // Check if user can access teachers-only category
        const category = this.categories.find(c => c.id === categoryId);
        if (category?.teachersOnly && !Auth.canViewTeacherContent()) {
            Toast.warning('Access Required', 'Please login as teacher to view this content');
            openLoginModal();
            return;
        }

        this.currentCategory = categoryId;
        this.currentPage = 1;
        
        // Update active tab
        document.querySelectorAll('.category-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.category === categoryId);
        });

        this.render();
    },

    getFilteredPhotos() {
        let photos = [...this.photos];

        // Filter out hidden photos (unless admin)
        if (!Auth.isSuperAdmin()) {
            photos = photos.filter(p => p.status !== 'hidden');
        }

        // Filter by category
        if (this.currentCategory !== 'all') {
            photos = photos.filter(p => p.category === this.currentCategory);
        }

        // Filter out teachers-only photos for non-teachers
        if (!Auth.canViewTeacherContent()) {
            photos = photos.filter(p => p.visibility !== 'teachers');
        }

        // Sort
        switch (this.currentSort) {
            case 'newest':
                photos.sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt));
                break;
            case 'oldest':
                photos.sort((a, b) => new Date(a.uploadedAt) - new Date(b.uploadedAt));
                break;
            case 'popular':
                photos.sort((a, b) => this.getTotalReactions(b) - this.getTotalReactions(a));
                break;
            case 'downloads':
                photos.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
                break;
        }

        return photos;
    },

    getTotalReactions(photo) {
        if (!photo.reactions) return 0;
        return Object.values(photo.reactions).reduce((a, b) => a + b, 0);
    },

    render() {
        const container = document.getElementById('photoGrid');
        const filteredPhotos = this.getFilteredPhotos();
        
        // Paginate
        const startIndex = 0;
        const endIndex = this.currentPage * this.photosPerPage;
        const photosToShow = filteredPhotos.slice(startIndex, endIndex);

        if (photosToShow.length === 0) {
            container.innerHTML = `
                <div class="no-photos" style="grid-column: 1/-1; text-align: center; padding: 3rem;">
                    <i class="fas fa-images" style="font-size: 4rem; color: var(--gold); margin-bottom: 1rem;"></i>
                    <h3>No Photos Found</h3>
                    <p style="color: var(--text-secondary);">
                        ${this.currentCategory === 'all' 
                            ? 'Photos will appear here once uploaded by the admin.' 
                            : 'No photos in this category yet.'}
                    </p>
                </div>
            `;
            document.getElementById('loadMore').classList.add('hidden');
            return;
        }

        container.innerHTML = photosToShow.map(photo => this.createPhotoCard(photo)).join('');

        // Show/hide load more button
        const loadMoreBtn = document.getElementById('loadMore');
        if (endIndex >= filteredPhotos.length) {
            loadMoreBtn.classList.add('hidden');
        } else {
            loadMoreBtn.classList.remove('hidden');
        }

        this.updateGridView();
    },

    createPhotoCard(photo) {
        const reactions = photo.reactions || {};
        const totalReactions = this.getTotalReactions(photo);
        const isTeachersOnly = photo.visibility === 'teachers';

        return `
            <div class="photo-card animate-fade-in" data-id="${photo.id}" onclick="Viewer.open('${photo.id}')">
                ${isTeachersOnly ? '<span class="teacher-badge"><i class="fas fa-lock"></i> Teachers</span>' : ''}
                <img src="${photo.src}" alt="${photo.name || 'Photo'}" loading="lazy">
                <div class="card-overlay">
                    <div class="card-reactions">
                        ${reactions.love ? `<span class="reaction">❤️ ${reactions.love}</span>` : ''}
                        ${reactions.laugh ? `<span class="reaction">😂 ${reactions.laugh}</span>` : ''}
                        ${reactions.fire ? `<span class="reaction">🔥 ${reactions.fire}</span>` : ''}
                        ${totalReactions === 0 ? '<span class="reaction" style="opacity: 0.5">No reactions yet</span>' : ''}
                    </div>
                    <div class="card-actions">
                        <button onclick="event.stopPropagation(); Gallery.downloadPhoto('${photo.id}')" title="Download">
                            <i class="fas fa-download"></i>
                        </button>
                        <button onclick="event.stopPropagation(); Gallery.sharePhoto('${photo.id}')" title="Share">
                            <i class="fas fa-share-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    updateGridView() {
        const grid = document.getElementById('photoGrid');
        if (this.currentView === 'masonry') {
            grid.classList.add('masonry');
        } else {
            grid.classList.remove('masonry');
        }
    },

    loadMore() {
        this.currentPage++;
        this.render();
    },

    search(query) {
        query = query.toLowerCase().trim();
        
        if (!query) {
            this.render();
            return;
        }

        const container = document.getElementById('photoGrid');
        const results = this.photos.filter(photo => {
            // Filter out teachers-only for non-teachers
            if (photo.visibility === 'teachers' && !Auth.canViewTeacherContent()) {
                return false;
            }
            
            return (
                (photo.name && photo.name.toLowerCase().includes(query)) ||
                (photo.category && photo.category.toLowerCase().includes(query)) ||
                (photo.tags && photo.tags.some(tag => tag.toLowerCase().includes(query)))
            );
        });

        if (results.length === 0) {
            container.innerHTML = `
                <div class="no-photos" style="grid-column: 1/-1; text-align: center; padding: 3rem;">
                    <i class="fas fa-search" style="font-size: 4rem; color: var(--gold); margin-bottom: 1rem;"></i>
                    <h3>No Results Found</h3>
                    <p style="color: var(--text-secondary);">Try a different search term</p>
                </div>
            `;
        } else {
            container.innerHTML = results.map(photo => this.createPhotoCard(photo)).join('');
        }

        document.getElementById('loadMore').classList.add('hidden');
    },

    // Photo management (for admin)
    addPhoto(photoData) {
        const photo = {
            id: Utils.generateId(),
            ...photoData,
            uploadedAt: new Date().toISOString(),
            reactions: {},
            downloads: 0,
            views: 0
        };

        this.photos.unshift(photo);
        this.savePhotos();
        this.render();
        this.updateStats();

        return photo;
    },

    deletePhoto(photoId) {
        this.photos = this.photos.filter(p => p.id !== photoId);
        this.savePhotos();
        this.render();
        this.updateStats();
    },

    updatePhoto(photoId, updates) {
        const index = this.photos.findIndex(p => p.id === photoId);
        if (index !== -1) {
            this.photos[index] = { ...this.photos[index], ...updates };
            this.savePhotos();
        }
    },

    savePhotos() {
        Utils.storage.set('photos', this.photos);
    },

    saveCategories() {
        Utils.storage.set('categories', this.categories);
    },

    // Download functionality
    downloadPhoto(photoId) {
        const photo = this.photos.find(p => p.id === photoId);
        if (!photo) return;

        // Increment download count
        photo.downloads = (photo.downloads || 0) + 1;
        this.savePhotos();
        this.updateStats();

        // Download the image
        Utils.downloadFile(photo.src, `memo-pics-2025-${photoId}.jpg`);
        Toast.success('Download Started', 'Your photo is being downloaded');
    },

    downloadAllVisible() {
        const photos = this.getFilteredPhotos();
        if (photos.length === 0) {
            Toast.warning('No Photos', 'No photos to download');
            return;
        }

        Toast.info('Downloading...', `Preparing ${photos.length} photos for download`);

        // Download each photo with a delay
        photos.forEach((photo, index) => {
            setTimeout(() => {
                Utils.downloadFile(photo.src, `memo-pics-2025-${index + 1}.jpg`);
                photo.downloads = (photo.downloads || 0) + 1;
            }, index * 500);
        });

        this.savePhotos();
        this.updateStats();
    },

    sharePhoto(photoId) {
        const photo = this.photos.find(p => p.id === photoId);
        if (!photo) return;

        // Open share modal
        Viewer.currentPhotoId = photoId;
        sharePhoto();
    },

    // Stats
    updateStats() {
        const totalPhotos = this.photos.length;
        const publicPhotos = this.photos.filter(p => p.visibility !== 'teachers').length;
        
        let totalReactions = 0;
        let totalDownloads = 0;

        this.photos.forEach(photo => {
            totalReactions += this.getTotalReactions(photo);
            totalDownloads += photo.downloads || 0;
        });

        // Update hero stats
        const heroPhotos = document.getElementById('heroPhotos');
        const heroReactions = document.getElementById('heroReactions');
        const heroDownloads = document.getElementById('heroDownloads');

        if (heroPhotos) Utils.animateCounter(heroPhotos, publicPhotos);
        if (heroReactions) Utils.animateCounter(heroReactions, totalReactions);
        if (heroDownloads) Utils.animateCounter(heroDownloads, totalDownloads);

        // Update admin stats
        const totalPhotosEl = document.getElementById('totalPhotos');
        const totalReactionsEl = document.getElementById('totalReactions');
        const totalDownloadsEl = document.getElementById('totalDownloads');

        if (totalPhotosEl) totalPhotosEl.textContent = totalPhotos;
        if (totalReactionsEl) totalReactionsEl.textContent = totalReactions;
        if (totalDownloadsEl) totalDownloadsEl.textContent = totalDownloads;
    },

    // Featured photos (most reactions)
    getFeaturedPhotos(limit = 10) {
        // First get photos marked as featured
        let featured = this.photos.filter(p => p.status === 'featured');

        // Filter by visibility
        featured = featured.filter(p => p.visibility !== 'teachers' || Auth.canViewTeacherContent());

        // If not enough featured, add most reacted
        if (featured.length < limit) {
            const remaining = this.photos
                .filter(p => p.status !== 'featured' && p.status !== 'hidden')
                .filter(p => p.visibility !== 'teachers' || Auth.canViewTeacherContent())
                .sort((a, b) => this.getTotalReactions(b) - this.getTotalReactions(a))
                .slice(0, limit - featured.length);

            featured = [...featured, ...remaining];
        }

        return featured.slice(0, limit);
    },

    renderFeatured() {
        const container = document.getElementById('featuredCarousel');
        const featured = this.getFeaturedPhotos();

        if (featured.length === 0) {
            container.innerHTML = `
                <div class="no-photos" style="padding: 2rem; text-align: center; width: 100%;">
                    <p style="color: var(--text-secondary);">Featured photos will appear here</p>
                </div>
            `;
            return;
        }

        container.innerHTML = featured.map(photo => `
            <div class="featured-card" data-id="${photo.id}" onclick="Featured.toggleSelect('${photo.id}')">
                <div class="select-checkbox">
                    <i class="fas fa-check"></i>
                </div>
                <img src="${photo.src}" alt="${photo.name || 'Featured Photo'}">
                <div class="card-overlay">
                    <div class="card-reactions">
                        <span>❤️ ${photo.reactions?.love || 0}</span>
                        <span>🔥 ${photo.reactions?.fire || 0}</span>
                    </div>
                    <button class="view-btn-small" onclick="event.stopPropagation(); Viewer.open('${photo.id}')">
                        <i class="fas fa-expand"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
};

// Global functions
function loadMorePhotos() {
    Gallery.loadMore();
}

function downloadAllVisible() {
    Gallery.downloadAllVisible();
}

function scrollToGallery() {
    const gallery = document.getElementById('gallery');
    Utils.scrollToElement(gallery, 80);
}


// Featured Photos Selection Handler
const Featured = {
    selectedIds: [],

    toggleSelect(photoId) {
        const card = document.querySelector(`.featured-card[data-id="${photoId}"]`);
        const index = this.selectedIds.indexOf(photoId);

        if (index !== -1) {
            this.selectedIds.splice(index, 1);
            if (card) card.classList.remove('selected');
        } else {
            this.selectedIds.push(photoId);
            if (card) card.classList.add('selected');
        }

        this.updateCount();
    },

    selectAll() {
        const featured = Gallery.getFeaturedPhotos();
        this.selectedIds = featured.map(p => p.id);

        document.querySelectorAll('.featured-card').forEach(card => {
            card.classList.add('selected');
        });

        this.updateCount();
        Toast.success('Selected All', `${this.selectedIds.length} photos selected`);
    },

    deselectAll() {
        this.selectedIds = [];

        document.querySelectorAll('.featured-card').forEach(card => {
            card.classList.remove('selected');
        });

        this.updateCount();
        Toast.info('Deselected', 'All photos deselected');
    },

    updateCount() {
        const countEl = document.getElementById('featuredSelectedCount');
        if (countEl) {
            countEl.textContent = this.selectedIds.length;
        }
    },

    addSelectedToSlideshow() {
        if (this.selectedIds.length === 0) {
            Toast.warning('None Selected', 'Please select photos first');
            return;
        }

        let added = 0;
        this.selectedIds.forEach(id => {
            const photo = Gallery.photos.find(p => p.id === id);
            if (photo && !Slideshow.selectedIds.includes(id)) {
                Slideshow.photos.push(photo);
                Slideshow.selectedIds.push(id);
                added++;
            }
        });

        Slideshow.savePhotos();
        Toast.success('Added!', `${added} photos added to slideshow`);
    },

    downloadSelected() {
        if (this.selectedIds.length === 0) {
            Toast.warning('None Selected', 'Please select photos first');
            return;
        }

        Toast.info('Downloading...', `Preparing ${this.selectedIds.length} photos`);

        this.selectedIds.forEach((id, index) => {
            const photo = Gallery.photos.find(p => p.id === id);
            if (photo) {
                setTimeout(() => {
                    Utils.downloadFile(photo.src, `featured-${index + 1}.jpg`);
                }, index * 500);
            }
        });
    }
};
