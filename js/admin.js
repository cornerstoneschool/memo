// ========================================
// MEMO PICS 2025 - ADMIN PANEL
// ========================================

const Admin = {
    uploadQueue: [],
    selectedPhotos: [],
    currentEditPhotoId: null,

    init() {
        this.setupEventListeners();
        this.loadManageGrid();
        this.loadCategories();
        this.loadModerators();
    },

    setupEventListeners() {
        // Admin tabs
        document.querySelectorAll('.admin-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.admin-tab-content').forEach(c => c.classList.remove('active'));
                
                tab.classList.add('active');
                document.getElementById(tab.dataset.tab + 'Tab').classList.add('active');
            });
        });

        // Upload zone drag & drop
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');

        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Manage search
        document.getElementById('manageSearch')?.addEventListener('input', 
            Utils.debounce((e) => {
                this.filterManageGrid(e.target.value);
            }, 300)
        );
    },

    async handleFiles(files) {
        const preview = document.getElementById('uploadPreview');
        
        for (const file of files) {
            if (!file.type.startsWith('image/')) continue;

            try {
                const base64 = await Utils.compressImage(file, 1920, 0.85);
                const dimensions = await Utils.getImageDimensions(base64);
                
                const id = Utils.generateId();
                this.uploadQueue.push({
                    id,
                    file,
                    src: base64,
                    name: file.name,
                    dimensions
                });

                const previewItem = document.createElement('div');
                previewItem.className = 'upload-preview-item';
                previewItem.id = `preview-${id}`;
                previewItem.innerHTML = `
                    <img src="${base64}" alt="${file.name}">
                    <button onclick="Admin.removeFromQueue('${id}')">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                preview.appendChild(previewItem);
            } catch (error) {
                console.error('Error processing file:', error);
                Toast.error('Error', `Failed to process ${file.name}`);
            }
        }

        if (this.uploadQueue.length > 0) {
            Toast.info('Ready', `${this.uploadQueue.length} photo(s) ready to upload`);
        }
    },

    removeFromQueue(id) {
        this.uploadQueue = this.uploadQueue.filter(item => item.id !== id);
        document.getElementById(`preview-${id}`)?.remove();
    },

    async async uploadPhotos() {
        if (!Auth.isSuperAdmin() || !Auth.currentUser.ghToken) {
            Toast.error('Access Denied', 'Missing GitHub Token or Admin access.');
            return;
        }
        if (this.uploadQueue.length === 0) {
            Toast.warning('No Photos', 'Please select photos to upload');
            return;
        }

        const category = document.getElementById('uploadCategory').value;
        const visibility = document.getElementById('uploadVisibility').value;
        const uploadBtn = document.querySelector('.btn-upload');
        
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Pushing to GitHub...';
        Toast.info('Uploading...', 'Do not close this page.');

        const token = Auth.currentUser.ghToken;
        const owner = Auth.currentUser.repoOwner;
        const repo = Auth.currentUser.repoName;
        let uploaded = 0;

        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        try {
            // 1. Fetch JSON Database
            let fileSha = null;
            let currentData = { photos: Gallery.photos, categories: Gallery.categories };
            try {
                const getResp = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/data/photos.json`, { headers });
                if (getResp.ok) {
                    const getJson = await getResp.json();
                    fileSha = getJson.sha;
                    const decodedStr = decodeURIComponent(escape(atob(getJson.content)));
                    const parsed = JSON.parse(decodedStr);
                    if(parsed.photos) currentData.photos = parsed.photos;
                    if(parsed.categories && parsed.categories.length > 0) currentData.categories = parsed.categories;
                }
            } catch(e) { console.log("Creating new JSON"); }

            // 2. Upload Images
            for (const item of this.uploadQueue) {
                const safeName = "pic_" + Utils.generateId() + ".jpg";
                const path = `assets/images/${safeName}`;
                const base64Data = item.src.split(',')[1];
                
                const imgResp = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${path}`, {
                    method: 'PUT',
                    headers: headers,
                    body: JSON.stringify({ message: `Upload ${safeName}`, content: base64Data, branch: 'main' })
                });

                if (!imgResp.ok) throw new Error(`Upload failed for ${safeName}`);

                currentData.photos.unshift({
                    id: Utils.generateId(),
                    src: path,
                    name: item.name.split('.')[0] || "Photo",
                    category: category,
                    visibility: visibility,
                    status: 'visible',
                    uploadedAt: new Date().toISOString(),
                    reactions: {},
                    downloads: 0,
                    views: 0
                });
                uploaded++;
            }

            // 3. Update JSON
            const updatedJsonStr = JSON.stringify(currentData, null, 4);
            const encodedJson = btoa(unescape(encodeURIComponent(updatedJsonStr)));
            
            const jsonBody = {
                message: `Database update: ${uploaded} new photos`,
                content: encodedJson,
                branch: 'main'
            };
            if (fileSha) jsonBody.sha = fileSha;

            const jsonResp = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/data/photos.json`, {
                method: 'PUT',
                headers: headers,
                body: JSON.stringify(jsonBody)
            });

            if (!jsonResp.ok) throw new Error("Failed to update JSON");

            // Success cleanup
            this.uploadQueue = [];
            document.getElementById('uploadPreview').innerHTML = '';
            document.getElementById('fileInput').value = '';
            Gallery.photos = currentData.photos;
            Utils.storage.set('photos', Gallery.photos);
            this.loadManageGrid();
            Gallery.render();
            Gallery.updateStats();
            if(typeof Gallery.renderFeatured === 'function') Gallery.renderFeatured();
            
            Toast.success('Live!', `${uploaded} photos pushed to GitHub!`);

        } catch (error) {
            console.error(error);
            Toast.error("Error", error.message);
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-upload"></i> Upload Photos';
        }
    },

    loadManageGrid() {
    const grid = document.getElementById('manageGrid');
    if (!grid) return;

    let photos = [...Gallery.photos];

    if (photos.length === 0) {
        grid.innerHTML = '<p style="grid-column:1/-1; text-align:center; color:var(--text-muted);">No photos uploaded yet</p>';
        return;
    }

    // Apply filters
    const statusFilter = document.getElementById('manageStatusFilter')?.value || 'all';
    const categoryFilter = document.getElementById('manageFilter')?.value || 'all';

    if (statusFilter !== 'all') {
        photos = photos.filter(p => p.status === statusFilter);
    }

        if (categoryFilter !== 'all') {
            photos = photos.filter(p => p.category === categoryFilter);
        }

        if (photos.length === 0) {
            grid.innerHTML = '<p style="grid-column:1/-1; text-align:center; color:var(--text-muted);">No photos found</p>';
            return;
        }

        grid.innerHTML = photos.map(photo => {
            const isSelected = this.selectedPhotos.includes(photo.id);
            const status = photo.status || 'visible';
            let statusBadge = '';

            if (status === 'hidden') {
                statusBadge = '<span class="status-badge hidden">Hidden</span>';
            } else if (status === 'featured') {
                statusBadge = '<span class="status-badge featured">★ Featured</span>';
            }

            return `
                <div class="manage-item ${isSelected ? 'selected' : ''}" data-id="${photo.id}">
                    <input type="checkbox" ${isSelected ? 'checked' : ''} 
                           onclick="event.stopPropagation();" 
                           onchange="Admin.togglePhotoSelection('${photo.id}')">
                    <img src="${photo.src}" alt="${photo.name || 'Photo'}" 
                         onclick="Admin.openEditModal('${photo.id}')">
                    <button class="edit-btn" onclick="event.stopPropagation(); Admin.openEditModal('${photo.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${statusBadge}
                </div>
            `;
        }).join('');
    },

    filterManageGrid(query) {
        const items = document.querySelectorAll('.manage-item');
        query = query.toLowerCase();

        items.forEach(item => {
            const photoId = item.dataset.id;
            const photo = Gallery.photos.find(p => p.id === photoId);
            
            if (!photo) return;

            const matches = (
                (photo.name && photo.name.toLowerCase().includes(query)) ||
                (photo.category && photo.category.toLowerCase().includes(query))
            );

            item.style.display = matches || !query ? '' : 'none';
        });
    },
        filterByStatus(status) {
        this.loadManageGrid();
    },

    filterByCategory(category) {
        this.loadManageGrid();
    },

    selectAllPhotos() {
        const visiblePhotos = document.querySelectorAll('.manage-item');
        visiblePhotos.forEach(item => {
            const id = item.dataset.id;
            if (id && !this.selectedPhotos.includes(id)) {
                this.selectedPhotos.push(id);
            }
            item.classList.add('selected');
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox) checkbox.checked = true;
        });
        Toast.success('Selected', `${this.selectedPhotos.length} photos selected`);
    },

    deselectAllPhotos() {
        this.selectedPhotos = [];
        document.querySelectorAll('.manage-item').forEach(item => {
            item.classList.remove('selected');
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox) checkbox.checked = false;
        });
        Toast.info('Deselected', 'All photos deselected');
    },

    hideSelected() {
        if (this.selectedPhotos.length === 0) {
            Toast.warning('None Selected', 'Please select photos first');
            return;
        }

        this.selectedPhotos.forEach(id => {
            const photo = Gallery.photos.find(p => p.id === id);
            if (photo) photo.status = 'hidden';
        });

        Gallery.savePhotos();
        this.loadManageGrid();
        Gallery.render();
        Toast.success('Hidden', `${this.selectedPhotos.length} photos hidden`);
    },

    showSelected() {
        if (this.selectedPhotos.length === 0) {
            Toast.warning('None Selected', 'Please select photos first');
            return;
        }

        this.selectedPhotos.forEach(id => {
            const photo = Gallery.photos.find(p => p.id === id);
            if (photo) photo.status = 'visible';
        });

        Gallery.savePhotos();
        this.loadManageGrid();
        Gallery.render();
        Toast.success('Visible', `${this.selectedPhotos.length} photos now visible`);
    },

    featureSelected() {
        if (this.selectedPhotos.length === 0) {
            Toast.warning('None Selected', 'Please select photos first');
            return;
        }

        this.selectedPhotos.forEach(id => {
            const photo = Gallery.photos.find(p => p.id === id);
            if (photo) photo.status = 'featured';
        });

        Gallery.savePhotos();
        this.loadManageGrid();
        Gallery.renderFeatured();
        Toast.success('Featured', `${this.selectedPhotos.length} photos marked as featured`);
    },

    unfeatureSelected() {
        if (this.selectedPhotos.length === 0) {
            Toast.warning('None Selected', 'Please select photos first');
            return;
        }

        this.selectedPhotos.forEach(id => {
            const photo = Gallery.photos.find(p => p.id === id);
            if (photo && photo.status === 'featured') {
                photo.status = 'visible';
            }
        });

        Gallery.savePhotos();
        this.loadManageGrid();
        Gallery.renderFeatured();
        Toast.success('Unfeatured', 'Selected photos unfeatured');
    },

    openEditModal(photoId) {
        const photo = Gallery.photos.find(p => p.id === photoId);
        if (!photo) return;

        this.currentEditPhotoId = photoId;

        const previewEl = document.getElementById('editPhotoPreview');
        const nameEl = document.getElementById('editPhotoName');
        const visibilityEl = document.getElementById('editPhotoVisibility');
        const statusEl = document.getElementById('editPhotoStatus');
        
        if (previewEl) previewEl.src = photo.src;
        if (nameEl) nameEl.value = photo.name || '';
        if (visibilityEl) visibilityEl.value = photo.visibility || 'public';
        if (statusEl) statusEl.value = photo.status || 'visible';

        const categorySelect = document.getElementById('editPhotoCategory');
        if (categorySelect) {
            categorySelect.innerHTML = Gallery.categories.map(cat => `
                <option value="${cat.id}" ${photo.category === cat.id ? 'selected' : ''}>${cat.name}</option>
            `).join('');
        }

        document.getElementById('editPhotoModal').classList.add('active');
    },

    closeEditModal() {
        document.getElementById('editPhotoModal').classList.remove('active');
        this.currentEditPhotoId = null;
    },

    savePhotoEdit() {
        if (!this.currentEditPhotoId) return;

        const photo = Gallery.photos.find(p => p.id === this.currentEditPhotoId);
        if (!photo) return;

        const nameEl = document.getElementById('editPhotoName');
        const categoryEl = document.getElementById('editPhotoCategory');
        const visibilityEl = document.getElementById('editPhotoVisibility');
        const statusEl = document.getElementById('editPhotoStatus');

        if (nameEl) photo.name = nameEl.value;
        if (categoryEl) photo.category = categoryEl.value;
        if (visibilityEl) photo.visibility = visibilityEl.value;
        if (statusEl) photo.status = statusEl.value;

        Gallery.savePhotos();
        this.loadManageGrid();
        Gallery.render();
        Gallery.renderFeatured();
        this.closeEditModal();

        Toast.success('Saved', 'Photo updated successfully');
    },

    deleteCurrentPhoto() {
        if (!this.currentEditPhotoId) return;

        if (!confirm('Are you sure you want to delete this photo?')) return;

        Gallery.deletePhoto(this.currentEditPhotoId);
        this.closeEditModal();
        this.loadManageGrid();

        Toast.success('Deleted', 'Photo deleted successfully');
    },
    togglePhotoSelection(photoId) {
        const index = this.selectedPhotos.indexOf(photoId);
        if (index !== -1) {
            this.selectedPhotos.splice(index, 1);
        } else {
            this.selectedPhotos.push(photoId);
        }
    },

    deleteSelected() {
        if (!Auth.isSuperAdmin()) {
            Toast.error('Access Denied', 'Only Super Admins can delete photos');
            return;
        }

        if (this.selectedPhotos.length === 0) {
            Toast.warning('None Selected', 'Please select photos to delete');
            return;
        }

        if (!confirm(`Are you sure you want to delete ${this.selectedPhotos.length} photo(s)?`)) {
            return;
        }

        this.selectedPhotos.forEach(id => {
            Gallery.deletePhoto(id);
        });

        Toast.success('Deleted', `${this.selectedPhotos.length} photo(s) deleted`);
        this.selectedPhotos = [];
        this.loadManageGrid();
    },

    // Categories Management
    loadCategories() {
        const list = document.getElementById('categoriesList');
        if (!list) return;

        const categories = Gallery.categories.filter(c => c.id !== 'all');

        list.innerHTML = categories.map(cat => `
            <div class="category-item">
                <div class="category-info">
                    <i class="fas ${cat.icon}"></i>
                    <span>${cat.name}</span>
                    ${cat.teachersOnly ? '<span class="teacher-only-badge">Teachers Only</span>' : ''}
                </div>
                ${cat.id !== 'candid' && cat.id !== 'stage' && cat.id !== 'group' ? `
                    <button onclick="Admin.deleteCategory('${cat.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </div>
        `).join('');
    },

    addCategory() {
        const name = document.getElementById('newCategoryName').value.trim();
        const icon = document.getElementById('newCategoryIcon').value.trim() || 'fa-folder';
        const teachersOnly = document.getElementById('categoryTeachersOnly').checked;

        if (!name) {
            Toast.warning('Required', 'Please enter a category name');
            return;
        }

        const id = name.toLowerCase().replace(/\s+/g, '-');

        if (Gallery.categories.some(c => c.id === id)) {
            Toast.error('Exists', 'Category already exists');
            return;
        }

        Gallery.categories.push({
            id,
            name,
            icon: icon.startsWith('fa-') ? icon : `fa-${icon}`,
            teachersOnly
        });

        Gallery.saveCategories();
        Gallery.renderCategories();
        this.loadCategories();
        this.updateCategoryDropdown();

        // Clear form
        document.getElementById('newCategoryName').value = '';
        document.getElementById('newCategoryIcon').value = '';
        document.getElementById('categoryTeachersOnly').checked = false;

        Toast.success('Added', `Category "${name}" created`);
    },

    deleteCategory(categoryId) {
        if (!confirm('Delete this category? Photos will be moved to "All".')) {
            return;
        }

        // Move photos to 'all'
        Gallery.photos.forEach(photo => {
            if (photo.category === categoryId) {
                photo.category = 'all';
            }
        });
        Gallery.savePhotos();

        // Remove category
        Gallery.categories = Gallery.categories.filter(c => c.id !== categoryId);
        Gallery.saveCategories();
        Gallery.renderCategories();
        this.loadCategories();
        this.updateCategoryDropdown();

        Toast.success('Deleted', 'Category deleted');
    },

    updateCategoryDropdown() {
        const select = document.getElementById('uploadCategory');
        if (!select) return;

        select.innerHTML = Gallery.categories.map(cat => `
            <option value="${cat.id}">${cat.name}</option>
        `).join('');
    },

    // Moderators/Teachers Management
    loadModerators() {
        const list = document.getElementById('moderatorsList');
        if (!list) return;

        const teachers = Auth.getTeachers();

        if (teachers.length === 0) {
            list.innerHTML = '<p style="color:var(--text-muted);">No teachers added yet</p>';
            return;
        }

        list.innerHTML = teachers.map(teacher => `
            <div class="moderator-item">
                <div class="mod-info">
                    <i class="fas fa-user-tie"></i>
                    <span>${teacher.name}</span>
                    <span class="role-badge">Teacher</span>
                </div>
                <button onclick="Admin.removeModerator('${teacher.username}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');
    },

    addModerator() {
        const username = document.getElementById('modUsername').value.trim();
        const password = document.getElementById('modPassword').value;
        const role = document.getElementById('modRole').value;

        if (!username || !password) {
            Toast.warning('Required', 'Please fill all fields');
            return;
        }

        if (password.length < 6) {
            Toast.warning('Weak Password', 'Password must be at least 6 characters');
            return;
        }

        const success = Auth.addTeacher(username, password, username);

        if (success) {
            this.loadModerators();
            document.getElementById('modUsername').value = '';
            document.getElementById('modPassword').value = '';
        }
    },

    removeModerator(username) {
        if (!confirm('Remove this teacher?')) return;
        
        Auth.removeTeacher(username);
        this.loadModerators();
    },

    // Settings
    getSettings() {
        return Utils.storage.get('settings', {
            animations: true,
            reactions: true,
            downloads: true,
            watermark: false
        });
    },

    saveSetting(key, value) {
        const settings = this.getSettings();
        settings[key] = value;
        Utils.storage.set('settings', settings);
    },

    loadSettings() {
        const settings = this.getSettings();
        
        document.getElementById('settingAnimations').checked = settings.animations;
        document.getElementById('settingReactions').checked = settings.reactions;
        document.getElementById('settingDownloads').checked = settings.downloads;
        document.getElementById('settingWatermark').checked = settings.watermark;

        // Add change listeners
        ['Animations', 'Reactions', 'Downloads', 'Watermark'].forEach(setting => {
            const el = document.getElementById('setting' + setting);
            if (el) {
                el.addEventListener('change', (e) => {
                    this.saveSetting(setting.toLowerCase(), e.target.checked);
                });
            }
        });
    },

    // Data management
    exportData() {
        const data = {
            photos: Gallery.photos,
            categories: Gallery.categories,
            teachers: Auth.credentials.teachers,
            settings: this.getSettings(),
            exportedAt: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        Utils.downloadFile(url, `memo-pics-backup-${Date.now()}.json`);
        URL.revokeObjectURL(url);

        Toast.success('Exported', 'Backup file downloaded');
    },

    importData() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';

        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);

                    if (data.photos) {
                        Gallery.photos = data.photos;
                        Gallery.savePhotos();
                    }

                    if (data.categories) {
                        Gallery.categories = data.categories;
                        Gallery.saveCategories();
                    }

                    if (data.teachers) {
                        Auth.credentials.teachers = data.teachers;
                        Utils.storage.set('teachers', data.teachers);
                    }

                    if (data.settings) {
                        Utils.storage.set('settings', data.settings);
                    }

                    Toast.success('Imported', 'Data restored successfully');
                    
                    // Refresh UI
                    Gallery.render();
                    Gallery.renderCategories();
                    Gallery.renderFeatured();
                    this.loadManageGrid();
                    this.loadCategories();
                    this.loadModerators();

                } catch (error) {
                    Toast.error('Error', 'Invalid backup file');
                    console.error('Import error:', error);
                }
            };
            reader.readAsText(file);
        };

        input.click();
    },

    clearAllData() {
        if (!confirm('⚠️ This will delete ALL data including photos, categories, and settings. Continue?')) {
            return;
        }

        if (!confirm('Are you REALLY sure? This cannot be undone!')) {
            return;
        }

        Utils.storage.clear();
        Toast.success('Cleared', 'All data has been cleared. Refreshing...');

        setTimeout(() => {
            location.reload();
        }, 1500);
    }
};

// Global functions
function openAdminPanel() {
    if (!Auth.isSuperAdmin()) {
        Toast.error('Access Denied', 'Super Admin access required');
        return;
    }

    document.getElementById('adminPanel').classList.add('active');
    document.getElementById('adminName').textContent = Auth.currentUser.name;
    
    Admin.loadManageGrid();
    Admin.loadCategories();
    Admin.loadModerators();
    Admin.loadSettings();
    Admin.updateCategoryDropdown();
    Gallery.updateStats();
}

function closeAdminPanel() {
    document.getElementById('adminPanel').classList.remove('active');
}

function uploadPhotos() {
    Admin.uploadPhotos();
}

function deleteSelected() {
    Admin.deleteSelected();
}

function addCategory() {
    Admin.addCategory();
}

function addModerator() {
    Admin.addModerator();
}

function exportData() {
    Admin.exportData();
}

function importData() {
    Admin.importData();
}

function clearAllData() {
    Admin.clearAllData();
}