#!/usr/bin/env python3
"""
MEMO PICS 2025 - Auto Change Applier
=====================================
This script automatically applies all the required changes to your project files.
Run this from the ROOT folder of your project (where index.html is located).

Usage: python apply_changes.py
"""

import os
import sys
import re
import shutil
from datetime import datetime

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_skip(text):
    print(f"{Colors.YELLOW}⏭️  SKIPPED: {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ ERROR: {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def print_change(num, desc):
    print(f"{Colors.BLUE}{Colors.BOLD}[Change {num}]{Colors.END} {desc}")

def backup_file(filepath):
    """Create a backup of the file before modifying"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        return backup_path
    return None

def read_file(filepath):
    """Read file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print_error(f"File not found: {filepath}")
        return None
    except Exception as e:
        print_error(f"Error reading {filepath}: {e}")
        return None

def write_file(filepath, content):
    """Write content to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print_error(f"Error writing {filepath}: {e}")
        return False

def find_and_replace(content, find_text, replace_text, change_name):
    """Find and replace text, return (new_content, was_changed, was_skipped)"""
    # Normalize whitespace for comparison
    find_normalized = ' '.join(find_text.split())
    content_normalized = ' '.join(content.split())
    replace_normalized = ' '.join(replace_text.split())
    
    # Check if already applied (replacement text exists)
    if replace_normalized in content_normalized or replace_text.strip() in content:
        return content, False, True  # Skipped - already applied
    
    # Check if find text exists
    if find_text.strip() in content:
        new_content = content.replace(find_text.strip(), replace_text.strip())
        return new_content, True, False  # Changed
    
    # Try with normalized whitespace matching
    lines_to_find = [line.strip() for line in find_text.strip().split('\n') if line.strip()]
    if len(lines_to_find) > 0:
        first_line = lines_to_find[0]
        if first_line in content:
            # Find the block and replace
            start_idx = content.find(first_line)
            if start_idx != -1:
                # Find end of the block (approximate)
                last_line = lines_to_find[-1]
                end_idx = content.find(last_line, start_idx)
                if end_idx != -1:
                    end_idx += len(last_line)
                    old_block = content[start_idx:end_idx]
                    new_content = content[:start_idx] + replace_text.strip() + content[end_idx:]
                    return new_content, True, False
    
    return content, False, False  # Not found

def apply_change(content, find_text, replace_text, change_num, change_desc):
    """Apply a single change and report status"""
    print_change(change_num, change_desc)
    
    new_content, was_changed, was_skipped = find_and_replace(
        content, find_text, replace_text, change_desc
    )
    
    if was_skipped:
        print_skip(f"Already applied - {change_desc}")
        return content, 0, 1
    elif was_changed:
        print_success(f"Applied - {change_desc}")
        return new_content, 1, 0
    else:
        print_error(f"Could not find target text for: {change_desc}")
        return content, 0, 0

# ============================================================
# CHANGE DEFINITIONS
# ============================================================

CHANGES = {
    'css/styles.css': [],
    'index.html': [],
    'js/slideshow.js': [],
    'js/gallery.js': [],
    'js/admin.js': []
}

# ------------------------------------------------------------
# CHANGE 1: Fix Hero Padding (styles.css)
# ------------------------------------------------------------
CHANGES['css/styles.css'].append({
    'num': 1,
    'desc': 'Fix hero padding (Farewell 2025 visible)',
    'find': '''.hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: var(--spacing-xxl);
}''',
    'replace': '''.hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: var(--spacing-xxl);
    padding-top: 100px;
}'''
})

# ------------------------------------------------------------
# CHANGE 2: Featured Section Controls (index.html)
# ------------------------------------------------------------
CHANGES['index.html'].append({
    'num': 2,
    'desc': 'Add Featured section controls',
    'find': '''<!-- Featured Section -->
<section class="featured-section" id="featured">
    <div class="section-header">
        <h2><i class="fas fa-star"></i> Featured Moments</h2>
        <p>Most loved photos from the farewell</p>
    </div>
    <div class="featured-carousel" id="featuredCarousel"></div>
</section>''',
    'replace': '''<!-- Featured Section -->
<section class="featured-section" id="featured">
    <div class="section-header">
        <h2><i class="fas fa-star"></i> Featured Moments</h2>
        <p>Most loved photos from the farewell</p>
    </div>
    <div class="featured-controls glass-card">
        <button class="btn-gold" onclick="Featured.selectAll()">
            <i class="fas fa-check-double"></i> Select All
        </button>
        <button class="btn-gold" onclick="Featured.deselectAll()">
            <i class="fas fa-times"></i> Deselect All
        </button>
        <button class="btn-gold" onclick="Featured.addSelectedToSlideshow()">
            <i class="fas fa-film"></i> Add to Slideshow
        </button>
        <button class="btn-gold" onclick="Featured.downloadSelected()">
            <i class="fas fa-download"></i> Download Selected
        </button>
        <span class="selected-count">Selected: <span id="featuredSelectedCount">0</span></span>
    </div>
    <div class="featured-carousel" id="featuredCarousel"></div>
</section>'''
})

# ------------------------------------------------------------
# CHANGE 3: Featured Controls CSS (styles.css)
# ------------------------------------------------------------
CHANGES['css/styles.css'].append({
    'num': 3,
    'desc': 'Add featured controls styling',
    'find': '''/* ===== FEATURED CAROUSEL ===== */
.featured-carousel {
    display: flex;
    gap: var(--spacing-lg);''',
    'replace': '''/* ===== FEATURED CONTROLS ===== */
.featured-controls {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md) var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
    flex-wrap: wrap;
}

.featured-controls .selected-count {
    margin-left: auto;
    color: var(--gold);
    font-weight: 600;
}

.featured-card.selected {
    border: 3px solid var(--gold);
    box-shadow: var(--shadow-gold);
}

.featured-card .select-checkbox {
    position: absolute;
    top: var(--spacing-sm);
    left: var(--spacing-sm);
    width: 30px;
    height: 30px;
    background: rgba(0, 0, 0, 0.7);
    border: 2px solid var(--gold);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 10;
    transition: var(--transition-fast);
}

.featured-card .select-checkbox:hover {
    background: var(--gold);
    color: var(--black);
}

.featured-card.selected .select-checkbox {
    background: var(--gold);
    color: var(--black);
}

.featured-card .select-checkbox i {
    display: none;
}

.featured-card.selected .select-checkbox i {
    display: block;
}

/* ===== FEATURED CAROUSEL ===== */
.featured-carousel {
    display: flex;
    gap: var(--spacing-lg);'''
})

# ------------------------------------------------------------
# CHANGE 4: Slideshow Modal with Fullscreen (index.html)
# ------------------------------------------------------------
CHANGES['index.html'].append({
    'num': 4,
    'desc': 'New Slideshow Modal with fullscreen',
    'find': '''<!-- Slideshow Modal -->
<div id="slideshowModal" class="modal">
    <div class="modal-overlay"></div>
    <div class="modal-content glass-card slideshow-modal">
        <button class="modal-close" onclick="closeSlideshow()">&times;</button>
        <h2><i class="fas fa-film"></i> Memory Slideshow</h2>
        
        <div class="slideshow-container">
            <div class="slideshow-preview" id="slideshowPreview"></div>
            <div class="slideshow-controls">
                <button onclick="prevSlide()"><i class="fas fa-step-backward"></i></button>
                <button onclick="toggleSlideshow()" id="playPauseBtn">
                    <i class="fas fa-play"></i>
                </button>
                <button onclick="nextSlide()"><i class="fas fa-step-forward"></i></button>
            </div>
        </div>
        
        <div class="slideshow-settings">
            <div class="form-group">
                <label>Duration per slide</label>
                <input type="range" id="slideDuration" min="1" max="10" value="3">
                <span id="durationValue">3s</span>
            </div>
            <div class="form-group">
                <label>Transition</label>
                <select id="slideTransition">
                    <option value="fade">Fade</option>
                    <option value="slide">Slide</option>
                    <option value="zoom">Zoom</option>
                </select>
            </div>
        </div>
        
        <div class="slideshow-photos">
            <h3>Selected Photos (<span id="slideshowCount">0</span>)</h3>
            <div class="slideshow-photos-grid" id="slideshowPhotosGrid"></div>
        </div>
    </div>
</div>''',
    'replace': '''<!-- Slideshow Modal -->
<div id="slideshowModal" class="modal">
    <div class="modal-overlay"></div>
    <div class="modal-content glass-card slideshow-modal">
        <button class="modal-close" onclick="closeSlideshow()">&times;</button>
        <h2><i class="fas fa-film"></i> Memory Slideshow</h2>
        
        <div class="slideshow-settings">
            <div class="form-group">
                <label>Duration per slide</label>
                <input type="range" id="slideDuration" min="1" max="10" value="3">
                <span id="durationValue">3s</span>
            </div>
            <div class="form-group">
                <label>Transition</label>
                <select id="slideTransition">
                    <option value="fade">Fade</option>
                    <option value="slide">Slide</option>
                    <option value="zoom">Zoom</option>
                </select>
            </div>
        </div>
        
        <div class="slideshow-photos">
            <div class="slideshow-photos-header">
                <h3>Select Photos (<span id="slideshowCount">0</span> selected)</h3>
                <div class="slideshow-photo-actions">
                    <button class="btn-gold btn-sm" onclick="Slideshow.selectAll()">
                        <i class="fas fa-check-double"></i> Select All
                    </button>
                    <button class="btn-gold btn-sm" onclick="Slideshow.deselectAll()">
                        <i class="fas fa-times"></i> Deselect All
                    </button>
                    <button class="btn-gold btn-sm" onclick="Slideshow.removeSelected()">
                        <i class="fas fa-trash"></i> Remove Selected
                    </button>
                </div>
            </div>
            <div class="slideshow-photos-grid" id="slideshowPhotosGrid"></div>
        </div>

        <div class="slideshow-launch">
            <button class="btn-hero primary" onclick="Slideshow.launchFullscreen()">
                <i class="fas fa-expand"></i> Launch Fullscreen Slideshow
            </button>
        </div>
    </div>
</div>

<!-- Fullscreen Slideshow -->
<div id="fullscreenSlideshow" class="fullscreen-slideshow">
    <div class="fs-slide-container">
        <img id="fsSlideImage" src="" alt="Slideshow">
    </div>
    <div class="fs-overlay-top">
        <span class="fs-counter"><span id="fsCurrentSlide">1</span> / <span id="fsTotalSlides">0</span></span>
        <button class="fs-close-btn" onclick="Slideshow.exitFullscreen()">
            <i class="fas fa-times"></i>
        </button>
    </div>
    <div class="fs-overlay-bottom">
        <div class="fs-controls">
            <button onclick="Slideshow.prev()"><i class="fas fa-step-backward"></i></button>
            <button onclick="Slideshow.toggle()" id="fsPlayPauseBtn">
                <i class="fas fa-pause"></i>
            </button>
            <button onclick="Slideshow.next()"><i class="fas fa-step-forward"></i></button>
        </div>
        <div class="fs-progress">
            <div class="fs-progress-bar" id="fsProgressBar"></div>
        </div>
    </div>
</div>'''
})

# ------------------------------------------------------------
# CHANGE 5: Fullscreen Slideshow CSS (styles.css)
# ------------------------------------------------------------
CHANGES['css/styles.css'].append({
    'num': 5,
    'desc': 'Add fullscreen slideshow styling',
    'find': '''/* ===== SLIDESHOW MODAL ===== */
.slideshow-modal {
    max-width: 800px;
}''',
    'replace': '''/* ===== SLIDESHOW MODAL ===== */
.slideshow-modal {
    max-width: 900px;
}

.slideshow-photos-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.slideshow-photos-header h3 {
    margin: 0;
}

.slideshow-photo-actions {
    display: flex;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
}

.btn-sm {
    padding: var(--spacing-xs) var(--spacing-sm) !important;
    font-size: 0.85rem !important;
}

.slideshow-launch {
    margin-top: var(--spacing-xl);
    text-align: center;
}

/* ===== FULLSCREEN SLIDESHOW ===== */
.fullscreen-slideshow {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #000;
    z-index: 9999;
    display: none;
    flex-direction: column;
}

.fullscreen-slideshow.active {
    display: flex;
}

.fs-slide-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.fs-slide-container img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transition: all 0.5s ease;
}

.fs-slide-container img.fade-out {
    opacity: 0;
    transform: scale(0.95);
}

.fs-slide-container img.fade-in {
    opacity: 1;
    transform: scale(1);
}

.fs-slide-container img.slide-out-left {
    transform: translateX(-100%);
    opacity: 0;
}

.fs-slide-container img.slide-in-right {
    transform: translateX(0);
    opacity: 1;
}

.fs-slide-container img.zoom-out {
    transform: scale(0.5);
    opacity: 0;
}

.fs-slide-container img.zoom-in {
    transform: scale(1);
    opacity: 1;
}

.fs-overlay-top {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    padding: var(--spacing-lg) var(--spacing-xl);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(to bottom, rgba(0,0,0,0.7), transparent);
}

.fs-counter {
    color: var(--gold);
    font-size: 1.2rem;
    font-weight: 600;
}

.fs-close-btn {
    width: 50px;
    height: 50px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: var(--radius-full);
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    transition: var(--transition-normal);
}

.fs-close-btn:hover {
    background: var(--gold);
    color: var(--black);
    border-color: var(--gold);
}

.fs-overlay-bottom {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: var(--spacing-lg) var(--spacing-xl);
    background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
}

.fs-controls {
    display: flex;
    justify-content: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-md);
}

.fs-controls button {
    width: 60px;
    height: 60px;
    background: rgba(255, 215, 0, 0.2);
    border: 2px solid var(--gold);
    border-radius: var(--radius-full);
    color: var(--gold);
    font-size: 1.3rem;
    cursor: pointer;
    transition: var(--transition-normal);
}

.fs-controls button:hover {
    background: var(--gold);
    color: var(--black);
}

.fs-progress {
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
    overflow: hidden;
}

.fs-progress-bar {
    height: 100%;
    background: var(--gold-gradient);
    width: 0%;
    transition: width linear;
}'''
})

# ------------------------------------------------------------
# CHANGE 6: Featured Card Overlay CSS (styles.css)
# ------------------------------------------------------------
CHANGES['css/styles.css'].append({
    'num': 6,
    'desc': 'Add featured view button styling',
    'find': '''.featured-card .card-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: var(--spacing-lg);
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
}''',
    'replace': '''.featured-card .card-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: var(--spacing-lg);
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}

.featured-card .view-btn-small {
    width: 36px;
    height: 36px;
    background: rgba(255, 215, 0, 0.2);
    border: 1px solid var(--gold);
    border-radius: var(--radius-full);
    color: var(--gold);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: var(--transition-fast);
}

.featured-card .view-btn-small:hover {
    background: var(--gold);
    color: var(--black);
}'''
})

# ------------------------------------------------------------
# CHANGE 7: Manage Tab with Edit Options (index.html)
# ------------------------------------------------------------
CHANGES['index.html'].append({
    'num': 7,
    'desc': 'Admin manage tab with edit options',
    'find': '''<!-- Manage Tab -->
<div class="admin-tab-content" id="manageTab">
    <div class="manage-toolbar">
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="Search photos..." id="manageSearch">
        </div>
        <select id="manageFilter">
            <option value="all">All Categories</option>
        </select>
        <button class="btn-danger" onclick="deleteSelected()">
            <i class="fas fa-trash"></i> Delete Selected
        </button>
    </div>
    <div class="manage-grid" id="manageGrid"></div>
</div>''',
    'replace': '''<!-- Manage Tab -->
<div class="admin-tab-content" id="manageTab">
    <div class="manage-toolbar">
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="Search photos..." id="manageSearch">
        </div>
        <select id="manageFilter" onchange="Admin.filterByCategory(this.value)">
            <option value="all">All Categories</option>
        </select>
        <select id="manageStatusFilter" onchange="Admin.filterByStatus(this.value)">
            <option value="all">All Status</option>
            <option value="visible">Visible</option>
            <option value="hidden">Hidden</option>
            <option value="featured">Featured</option>
        </select>
    </div>
    <div class="manage-actions">
        <button class="btn-gold" onclick="Admin.selectAllPhotos()">
            <i class="fas fa-check-double"></i> Select All
        </button>
        <button class="btn-gold" onclick="Admin.deselectAllPhotos()">
            <i class="fas fa-times"></i> Deselect All
        </button>
        <button class="btn-gold" onclick="Admin.hideSelected()">
            <i class="fas fa-eye-slash"></i> Hide
        </button>
        <button class="btn-gold" onclick="Admin.showSelected()">
            <i class="fas fa-eye"></i> Show
        </button>
        <button class="btn-gold" onclick="Admin.featureSelected()">
            <i class="fas fa-star"></i> Feature
        </button>
        <button class="btn-gold" onclick="Admin.unfeatureSelected()">
            <i class="far fa-star"></i> Unfeature
        </button>
        <button class="btn-danger" onclick="deleteSelected()">
            <i class="fas fa-trash"></i> Delete
        </button>
    </div>
    <div class="manage-grid" id="manageGrid"></div>
    
    <!-- Edit Photo Modal -->
    <div id="editPhotoModal" class="edit-modal">
        <div class="edit-modal-content glass-card">
            <button class="modal-close" onclick="Admin.closeEditModal()">&times;</button>
            <h3><i class="fas fa-edit"></i> Edit Photo</h3>
            <div class="edit-preview">
                <img id="editPhotoPreview" src="" alt="Preview">
            </div>
            <div class="edit-form">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="editPhotoName" placeholder="Photo name">
                </div>
                <div class="form-group">
                    <label>Category</label>
                    <select id="editPhotoCategory"></select>
                </div>
                <div class="form-group">
                    <label>Visibility</label>
                    <select id="editPhotoVisibility">
                        <option value="public">Public</option>
                        <option value="teachers">Teachers Only</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <select id="editPhotoStatus">
                        <option value="visible">Visible</option>
                        <option value="hidden">Hidden</option>
                        <option value="featured">Featured</option>
                    </select>
                </div>
                <div class="edit-actions">
                    <button class="btn-gold" onclick="Admin.savePhotoEdit()">
                        <i class="fas fa-save"></i> Save
                    </button>
                    <button class="btn-danger" onclick="Admin.deleteCurrentPhoto()">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>'''
})

# ------------------------------------------------------------
# CHANGE 8: Manage Actions & Edit Modal CSS (styles.css)
# ------------------------------------------------------------
CHANGES['css/styles.css'].append({
    'num': 8,
    'desc': 'Add manage actions and edit modal styling',
    'find': '''.manage-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: var(--spacing-md);
    max-height: 300px;
    overflow-y: auto;
}''',
    'replace': '''.manage-actions {
    display: flex;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
    flex-wrap: wrap;
}

.manage-actions button {
    font-size: 0.85rem;
    padding: var(--spacing-xs) var(--spacing-sm);
}

.manage-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: var(--spacing-md);
    max-height: 400px;
    overflow-y: auto;
}

.manage-item {
    position: relative;
    border-radius: var(--radius-md);
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    transition: var(--transition-fast);
}

.manage-item:hover {
    border-color: var(--gold);
}

.manage-item.selected {
    border-color: var(--gold);
    box-shadow: var(--shadow-gold);
}

.manage-item img {
    width: 100%;
    height: 120px;
    object-fit: cover;
}

.manage-item .status-badge {
    position: absolute;
    bottom: 4px;
    right: 4px;
    padding: 2px 6px;
    font-size: 0.65rem;
    border-radius: var(--radius-sm);
    font-weight: 600;
}

.manage-item .status-badge.hidden {
    background: rgba(255, 68, 68, 0.9);
    color: white;
}

.manage-item .status-badge.featured {
    background: var(--gold);
    color: var(--black);
}

.manage-item .edit-btn {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 28px;
    height: 28px;
    background: rgba(0, 0, 0, 0.7);
    border: 1px solid var(--gold);
    border-radius: var(--radius-sm);
    color: var(--gold);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: var(--transition-fast);
}

.manage-item:hover .edit-btn {
    opacity: 1;
}

.manage-item .edit-btn:hover {
    background: var(--gold);
    color: var(--black);
}

/* Edit Modal */
.edit-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 250;
}

.edit-modal.active {
    display: flex;
}

.edit-modal-content {
    width: 90%;
    max-width: 450px;
    padding: var(--spacing-xl);
    position: relative;
}

.edit-modal-content h3 {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
    color: var(--gold);
}

.edit-preview {
    margin-bottom: var(--spacing-lg);
    border-radius: var(--radius-md);
    overflow: hidden;
}

.edit-preview img {
    width: 100%;
    max-height: 200px;
    object-fit: contain;
    background: var(--black-lighter);
}

.edit-form .form-group {
    margin-bottom: var(--spacing-md);
}

.edit-actions {
    display: flex;
    gap: var(--spacing-md);
    margin-top: var(--spacing-lg);
}

.edit-actions button {
    flex: 1;
}'''
})

# ============================================================
# NEW JS FILES - Complete Replacements
# ============================================================

NEW_SLIDESHOW_JS = '''// ========================================
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
'''

# ============================================================
# GALLERY.JS ADDITIONS (append to end of file)
# ============================================================

GALLERY_ADDITIONS = '''

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
'''

# ============================================================
# ADMIN.JS ADDITIONS
# ============================================================

ADMIN_ADDITIONS = '''
    // Additional Admin functions for photo management
    
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
            if (!this.selectedPhotos.includes(id)) {
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

    // Edit Modal
    openEditModal(photoId) {
        const photo = Gallery.photos.find(p => p.id === photoId);
        if (!photo) return;

        this.currentEditPhotoId = photoId;

        // Fill form
        const previewEl = document.getElementById('editPhotoPreview');
        const nameEl = document.getElementById('editPhotoName');
        const visibilityEl = document.getElementById('editPhotoVisibility');
        const statusEl = document.getElementById('editPhotoStatus');
        
        if (previewEl) previewEl.src = photo.src;
        if (nameEl) nameEl.value = photo.name || '';
        if (visibilityEl) visibilityEl.value = photo.visibility || 'public';
        if (statusEl) statusEl.value = photo.status || 'visible';

        // Fill category dropdown
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
'''

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print_header("MEMO PICS 2025 - AUTO CHANGE APPLIER")
    
    # Check if we're in the right directory
    if not os.path.exists('index.html'):
        print_error("index.html not found! Make sure you're in the project root folder.")
        print_info("Run this script from the same folder where index.html is located.")
        sys.exit(1)
    
    # Check required files exist
    required_files = ['index.html', 'css/styles.css', 'js/gallery.js', 'js/admin.js', 'js/slideshow.js']
    missing_files = []
    
    for f in required_files:
        if not os.path.exists(f):
            missing_files.append(f)
    
    if missing_files:
        print_error(f"Missing files: {', '.join(missing_files)}")
        print_info("Make sure all required files exist before running this script.")
        
        # Create directories if needed
        for f in missing_files:
            dir_path = os.path.dirname(f)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print_success(f"Created directory: {dir_path}")
        
        sys.exit(1)
    
    print_success("All required files found!")
    print_info("Creating backups...")
    
    # Backup all files
    for filepath in required_files:
        backup = backup_file(filepath)
        if backup:
            print_info(f"Backup: {backup}")
    
    # Statistics
    total_changes = 0
    total_skipped = 0
    total_errors = 0
    
    # Process each file
    print_header("APPLYING CHANGES")
    
    # ============================================================
    # CSS CHANGES
    # ============================================================
    print(f"\n{Colors.BOLD}📄 Processing: css/styles.css{Colors.END}")
    
    css_content = read_file('css/styles.css')
    if css_content:
        for change in CHANGES['css/styles.css']:
            css_content, changed, skipped = apply_change(
                css_content, 
                change['find'], 
                change['replace'], 
                change['num'], 
                change['desc']
            )
            total_changes += changed
            total_skipped += skipped
            if not changed and not skipped:
                total_errors += 1
        
        write_file('css/styles.css', css_content)
    
    # ============================================================
    # HTML CHANGES
    # ============================================================
    print(f"\n{Colors.BOLD}📄 Processing: index.html{Colors.END}")
    
    html_content = read_file('index.html')
    if html_content:
        for change in CHANGES['index.html']:
            html_content, changed, skipped = apply_change(
                html_content, 
                change['find'], 
                change['replace'], 
                change['num'], 
                change['desc']
            )
            total_changes += changed
            total_skipped += skipped
            if not changed and not skipped:
                total_errors += 1
        
        write_file('index.html', html_content)
    
    # ============================================================
    # SLIDESHOW.JS - COMPLETE REPLACEMENT
    # ============================================================
    print(f"\n{Colors.BOLD}📄 Processing: js/slideshow.js{Colors.END}")
    print_change(9, "Replace entire slideshow.js with new version")
    
    slideshow_content = read_file('js/slideshow.js')
    if slideshow_content:
        # Check if already updated (look for launchFullscreen)
        if 'launchFullscreen' in slideshow_content:
            print_skip("Already updated - slideshow.js")
            total_skipped += 1
        else:
            write_file('js/slideshow.js', NEW_SLIDESHOW_JS)
            print_success("Applied - Complete slideshow.js replacement")
            total_changes += 1
    
    # ============================================================
    # GALLERY.JS - ADD FEATURED HANDLER
    # ============================================================
    print(f"\n{Colors.BOLD}📄 Processing: js/gallery.js{Colors.END}")
    print_change(10, "Add Featured selection handler to gallery.js")
    
    gallery_content = read_file('js/gallery.js')
    if gallery_content:
        # Check if Featured already exists
        if 'const Featured = {' in gallery_content:
            print_skip("Already applied - Featured handler in gallery.js")
            total_skipped += 1
        else:
            # Add to end of file
            gallery_content = gallery_content.rstrip() + '\n' + GALLERY_ADDITIONS
            write_file('js/gallery.js', gallery_content)
            print_success("Applied - Added Featured handler to gallery.js")
            total_changes += 1
    
    # Update renderFeatured in gallery.js
    print_change(11, "Update renderFeatured function")
    
    gallery_content = read_file('js/gallery.js')
    if gallery_content:
        old_render = '''container.innerHTML = featured.map(photo => `
            <div class="featured-card" onclick="Viewer.open('${photo.id}')">
                <img src="${photo.src}" alt="${photo.name || 'Featured Photo'}">
                <div class="card-overlay">
                    <div class="card-reactions">
                        <span>❤️ ${photo.reactions?.love || 0}</span>
                        <span>🔥 ${photo.reactions?.fire || 0}</span>
                    </div>
                </div>
            </div>
        `).join('');'''
        
        new_render = '''container.innerHTML = featured.map(photo => `
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
        `).join('');'''
        
        if 'Featured.toggleSelect' in gallery_content:
            print_skip("Already applied - renderFeatured update")
            total_skipped += 1
        elif old_render.strip() in gallery_content:
            gallery_content = gallery_content.replace(old_render.strip(), new_render.strip())
            write_file('js/gallery.js', gallery_content)
            print_success("Applied - renderFeatured update")
            total_changes += 1
        else:
            print_error("Could not find renderFeatured target - may need manual update")
            total_errors += 1
    
    # Update getFilteredPhotos to filter hidden
    print_change(12, "Update getFilteredPhotos to filter hidden photos")
    
    gallery_content = read_file('js/gallery.js')
    if gallery_content:
        old_filter = '''getFilteredPhotos() {
        let photos = [...this.photos];

        // Filter by category
        if (this.currentCategory !== 'all') {
            photos = photos.filter(p => p.category === this.currentCategory);
        }

        // Filter out teachers-only photos for non-teachers
        if (!Auth.canViewTeacherContent()) {
            photos = photos.filter(p => p.visibility !== 'teachers');
        }'''
        
        new_filter = '''getFilteredPhotos() {
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
        }'''
        
        if "p.status !== 'hidden'" in gallery_content:
            print_skip("Already applied - hidden filter")
            total_skipped += 1
        elif 'getFilteredPhotos()' in gallery_content:
            gallery_content = gallery_content.replace(old_filter.strip(), new_filter.strip())
            write_file('js/gallery.js', gallery_content)
            print_success("Applied - hidden filter")
            total_changes += 1
        else:
            print_error("Could not find getFilteredPhotos - may need manual update")
            total_errors += 1
    
    # Update getFeaturedPhotos
    print_change(13, "Update getFeaturedPhotos to use status")
    
    gallery_content = read_file('js/gallery.js')
    if gallery_content:
        old_featured = '''getFeaturedPhotos(limit = 10) {
        return this.photos
            .filter(p => p.visibility !== 'teachers' || Auth.canViewTeacherContent())
            .sort((a, b) => this.getTotalReactions(b) - this.getTotalReactions(a))
            .slice(0, limit);
    },'''
        
        new_featured = '''getFeaturedPhotos(limit = 10) {
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
    },'''
        
        if "p.status === 'featured'" in gallery_content:
            print_skip("Already applied - getFeaturedPhotos update")
            total_skipped += 1
        elif 'getFeaturedPhotos(limit = 10)' in gallery_content:
            gallery_content = gallery_content.replace(old_featured.strip(), new_featured.strip())
            write_file('js/gallery.js', gallery_content)
            print_success("Applied - getFeaturedPhotos update")
            total_changes += 1
        else:
            print_error("Could not find getFeaturedPhotos - may need manual update")
            total_errors += 1
    
    # ============================================================
    # ADMIN.JS - ADD NEW FUNCTIONS
    # ============================================================
    print(f"\n{Colors.BOLD}📄 Processing: js/admin.js{Colors.END}")
    print_change(14, "Add currentEditPhotoId to Admin object")
    
    admin_content = read_file('js/admin.js')
    if admin_content:
        # Add currentEditPhotoId
        if 'currentEditPhotoId' in admin_content:
            print_skip("Already applied - currentEditPhotoId")
            total_skipped += 1
        else:
            admin_content = admin_content.replace(
                '''const Admin = {
    uploadQueue: [],
    selectedPhotos: [],

    init() {''',
                '''const Admin = {
    uploadQueue: [],
    selectedPhotos: [],
    currentEditPhotoId: null,

    init() {'''
            )
            write_file('js/admin.js', admin_content)
            print_success("Applied - Added currentEditPhotoId")
            total_changes += 1
    
    # Update loadManageGrid
    print_change(15, "Update loadManageGrid with status badges and edit button")
    
    admin_content = read_file('js/admin.js')
    if admin_content:
        old_manage = '''grid.innerHTML = photos.map(photo => `
            <div class="manage-item" data-id="${photo.id}">
                <input type="checkbox" onchange="Admin.togglePhotoSelection('${photo.id}')">
                <img src="${photo.src}" alt="${photo.name || 'Photo'}">
            </div>
        `).join('');'''
        
        if 'status-badge' in admin_content:
            print_skip("Already applied - loadManageGrid update")
            total_skipped += 1
        elif 'manage-item' in admin_content and old_manage.strip() in admin_content:
            new_manage = '''// Apply filters
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
        }).join('');'''
            
            admin_content = admin_content.replace(old_manage.strip(), new_manage.strip())
            write_file('js/admin.js', admin_content)
            print_success("Applied - loadManageGrid update")
            total_changes += 1
        else:
            print_error("Could not find loadManageGrid target - may need manual update")
            total_errors += 1
    
    # Add new admin functions
    print_change(16, "Add new Admin functions (select, hide, feature, edit modal)")
    
    admin_content = read_file('js/admin.js')
    if admin_content:
        if 'openEditModal' in admin_content:
            print_skip("Already applied - Admin functions")
            total_skipped += 1
        else:
            # Find a good place to insert - after filterManageGrid or before the closing of Admin object
            insert_marker = 'filterManageGrid(query) {'
            if insert_marker in admin_content:
                # Find the end of filterManageGrid function and insert after
                idx = admin_content.find(insert_marker)
                # Find the closing brace of this function
                brace_count = 0
                end_idx = idx
                started = False
                for i in range(idx, len(admin_content)):
                    if admin_content[i] == '{':
                        brace_count += 1
                        started = True
                    elif admin_content[i] == '}':
                        brace_count -= 1
                        if started and brace_count == 0:
                            end_idx = i + 1
                            break
                
                # Insert after this function
                admin_content = admin_content[:end_idx] + ',\n' + ADMIN_ADDITIONS + admin_content[end_idx:]
                write_file('js/admin.js', admin_content)
                print_success("Applied - Added new Admin functions")
                total_changes += 1
            else:
                print_error("Could not find insertion point - may need manual update")
                total_errors += 1
    
    # ============================================================
    # SUMMARY
    # ============================================================
    print_header("SUMMARY")
    
    print(f"{Colors.GREEN}{Colors.BOLD}✅ Changes Applied: {total_changes}{Colors.END}")
    print(f"{Colors.YELLOW}{Colors.BOLD}⏭️  Changes Skipped (already applied): {total_skipped}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}❌ Errors: {total_errors}{Colors.END}")
    
    if total_errors > 0:
        print(f"\n{Colors.YELLOW}⚠️  Some changes may need manual application.{Colors.END}")
        print(f"{Colors.YELLOW}   Check the error messages above for details.{Colors.END}")
    
    if total_changes > 0:
        print(f"\n{Colors.CYAN}📦 Don't forget to commit and push your changes:{Colors.END}")
        print(f"   git add .")
        print(f"   git commit -m 'Applied UI/UX improvements'")
        print(f"   git push")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Done!{Colors.END}\n")

if __name__ == '__main__':
    main()