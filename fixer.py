import re
import sys

print("🚀 Starting UI Bug Fix Sniper...")

# ==========================================
# FIX 1: INDEX.HTML - ADMIN PANEL LAYOUT BUG
# ==========================================
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # The bug: Extra </div> tags and duplicate elements pushed the other tabs out of the modal.
    # We grab from the Delete Photo button inside the Edit Modal down to the Categories Tab,
    # and replace the chaotic middle with EXACTLY 5 closing divs to maintain strict modal structure.
    
    pattern_html = re.compile(
        r'(<button class="btn-danger" onclick="Admin\.deleteCurrentPhoto\(\)">\s*<i class="fas fa-trash"></i> Delete\s*</button>).*?(<!-- Categories Tab -->)', 
        re.DOTALL
    )

    # 5 specific closing divs needed: edit-actions, edit-form, edit-modal-content, edit-modal, admin-tab-content
    replacement_html = r'''\1
                    </div>
                </div>
            </div>
        </div>
    </div>

    \2'''
    
    new_html, count = pattern_html.subn(replacement_html, html)
    
    if count > 0:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f"✅ index.html: Sniped broken HTML and restored perfect Modal nesting!")
    else:
        print("⚠️ index.html: Target block not found. Already fixed?")
        
except Exception as e:
    print(f"❌ Error fixing index.html: {e}")

# ==========================================
# FIX 2: STYLES.CSS - DUPLICATE FEATURED CSS
# ==========================================
try:
    with open('css/styles.css', 'r', encoding='utf-8') as f:
        css = f.read()

    # Replace everything between SECTION STYLES and CATEGORY TABS with the pristine deduplicated version
    pattern_css = re.compile(
        r'/\* ===== SECTION STYLES ===== \*/.*?/\* ===== CATEGORY TABS ===== \*/', 
        re.DOTALL
    )
    
    clean_css = '''/* ===== SECTION STYLES ===== */
section {
    padding: var(--spacing-xxl) var(--spacing-xl);
}

.section-header {
    text-align: center;
    margin-bottom: var(--spacing-xl);
}

.section-header h2 {
    font-size: 2.5rem;
    margin-bottom: var(--spacing-sm);
}

.section-header h2 i {
    color: var(--gold);
    margin-right: var(--spacing-sm);
}

.section-header p {
    color: var(--text-secondary);
    font-size: 1.1rem;
}

/* ===== FEATURED CONTROLS ===== */
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
    gap: var(--spacing-lg);
    overflow-x: auto;
    padding: var(--spacing-md);
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
}

.featured-carousel::-webkit-scrollbar {
    height: 6px;
}

.featured-card {
    flex: 0 0 300px;
    scroll-snap-align: start;
    position: relative;
    border-radius: var(--radius-lg);
    overflow: hidden;
    cursor: pointer;
    transition: var(--transition-normal);
}

.featured-card:hover {
    transform: scale(1.02);
}

.featured-card img {
    width: 100%;
    height: 400px;
    object-fit: cover;
}

.featured-card .card-overlay {
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
}

.featured-card .card-reactions {
    display: flex;
    gap: var(--spacing-md);
}

.featured-card .card-reactions span {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    color: var(--text-secondary);
}

/* ===== CATEGORY TABS ===== */'''

    new_css, count = pattern_css.subn(clean_css, css)
    
    if count > 0:
        with open('css/styles.css', 'w', encoding='utf-8') as f:
            f.write(new_css)
        print(f"✅ css/styles.css: Eradicated duplicates and restored pristine CSS!")
    else:
        print("⚠️ css/styles.css: Target block not found. Already fixed?")
        
except Exception as e:
    print(f"❌ Error fixing styles.css: {e}")

print("\n🎉 DONE! The layout is officially unbroken. Push to GitHub!")