// ========================================
// MEMO PICS 2025 - REACTIONS SYSTEM
// ========================================

const Reactions = {
    types: ['love', 'laugh', 'emotional', 'fire', 'clap', 'star'],
    userReactions: {}, // Track user reactions per photo

    init() {
        this.userReactions = Utils.storage.get('userReactions', {});
    },

    addReaction(type) {
        const photo = Viewer.getCurrentPhoto();
        if (!photo) return;

        const photoId = photo.id;

        // Initialize user reactions for this photo
        if (!this.userReactions[photoId]) {
            this.userReactions[photoId] = [];
        }

        // Initialize photo reactions
        if (!photo.reactions) {
            photo.reactions = {};
        }

        // Check if user already reacted with this type
        const existingIndex = this.userReactions[photoId].indexOf(type);

        if (existingIndex !== -1) {
            // Remove reaction
            this.userReactions[photoId].splice(existingIndex, 1);
            photo.reactions[type] = Math.max(0, (photo.reactions[type] || 0) - 1);
        } else {
            // Add reaction
            this.userReactions[photoId].push(type);
            photo.reactions[type] = (photo.reactions[type] || 0) + 1;
        }

        // Save
        Utils.storage.set('userReactions', this.userReactions);
        Gallery.savePhotos();

        // Update UI
        this.updateViewerReactions(photo);
        this.animateReaction(type);
    },

    updateViewerReactions(photo) {
        const reactions = photo.reactions || {};
        const userReacted = this.userReactions[photo.id] || [];

        this.types.forEach(type => {
            const countEl = document.getElementById(`count-${type}`);
            const btnEl = document.querySelector(`.reaction-btn[data-reaction="${type}"]`);

            if (countEl) {
                countEl.textContent = reactions[type] || 0;
            }

            if (btnEl) {
                btnEl.classList.toggle('active', userReacted.includes(type));
            }
        });
    },

    animateReaction(type) {
        const btn = document.querySelector(`.reaction-btn[data-reaction="${type}"]`);
        if (!btn) return;

        btn.style.transform = 'scale(1.3)';
        setTimeout(() => {
            btn.style.transform = '';
        }, 200);

        // Create floating emoji
        const emoji = btn.querySelector('.reaction-emoji').textContent;
        const floatingEmoji = document.createElement('span');
        floatingEmoji.textContent = emoji;
        floatingEmoji.style.cssText = `
            position: fixed;
            font-size: 2rem;
            pointer-events: none;
            z-index: 1000;
            animation: floatUp 1s ease-out forwards;
        `;

        const rect = btn.getBoundingClientRect();
        floatingEmoji.style.left = rect.left + rect.width / 2 + 'px';
        floatingEmoji.style.top = rect.top + 'px';

        document.body.appendChild(floatingEmoji);

        setTimeout(() => {
            floatingEmoji.remove();
        }, 1000);
    }
};

// Add float animation
const style = document.createElement('style');
style.textContent = `
    @keyframes floatUp {
        0% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
        100% {
            opacity: 0;
            transform: translateY(-100px) scale(1.5);
        }
    }
`;
document.head.appendChild(style);

// Global function
function addReaction(type) {
    Reactions.addReaction(type);
}