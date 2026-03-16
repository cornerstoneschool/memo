// ========================================
// MEMO PICS 2025 - WHATSAPP STICKER MAKER
// ========================================

const StickerMaker = {
    canvas: null,
    ctx: null,
    currentImage: null,
    stickerPack: [],
    currentTool: 'crop',

    init() {
        this.canvas = document.getElementById('stickerCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.stickerPack = Utils.storage.get('stickerPack', []);
        this.updatePackUI();
        this.setupEventListeners();
    },

    setupEventListeners() {
        // Tool buttons
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentTool = btn.dataset.tool;
            });
        });
    },

    open() {
        const photo = Viewer.getCurrentPhoto();
        if (!photo) {
            Toast.warning('No Photo', 'Please select a photo first');
            return;
        }

        this.loadImage(photo.src);
        document.getElementById('stickerMaker').classList.add('active');
    },

    close() {
        document.getElementById('stickerMaker').classList.remove('active');
    },

    loadImage(src) {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            this.currentImage = img;

            // Set canvas size (512x512 for WhatsApp stickers)
            const size = 512;
            this.canvas.width = size;
            this.canvas.height = size;

            // Calculate scaling to fit
            const scale = Math.min(size / img.width, size / img.height);
            const x = (size - img.width * scale) / 2;
            const y = (size - img.height * scale) / 2;

            this.ctx.fillStyle = 'transparent';
            this.ctx.clearRect(0, 0, size, size);
            this.ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
        };
        img.src = src;
    },

    addText(text, x, y) {
        if (!this.ctx) return;

        this.ctx.font = 'bold 32px Poppins';
        this.ctx.fillStyle = 'white';
        this.ctx.strokeStyle = 'black';
        this.ctx.lineWidth = 3;
        this.ctx.textAlign = 'center';
        
        this.ctx.strokeText(text, x || 256, y || 480);
        this.ctx.fillText(text, x || 256, y || 480);
    },

    makeCircular() {
        if (!this.currentImage) return;

        const size = 512;
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = size;
        tempCanvas.height = size;
        const tempCtx = tempCanvas.getContext('2d');

        // Create circular clip
        tempCtx.beginPath();
        tempCtx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
        tempCtx.closePath();
        tempCtx.clip();

        // Draw current canvas content
        tempCtx.drawImage(this.canvas, 0, 0);

        // Clear and redraw
        this.ctx.clearRect(0, 0, size, size);
        this.ctx.drawImage(tempCanvas, 0, 0);
    },

    download() {
        if (!this.canvas) return;

        const dataUrl = this.canvas.toDataURL('image/webp', 0.9);
        Utils.downloadFile(dataUrl, `sticker-${Date.now()}.webp`);
        Toast.success('Downloaded!', 'Sticker saved as WebP');
    },

    addToPack() {
        if (!this.canvas) return;

        if (this.stickerPack.length >= 30) {
            Toast.warning('Pack Full', 'Maximum 30 stickers per pack');
            return;
        }

        const dataUrl = this.canvas.toDataURL('image/webp', 0.9);
        this.stickerPack.push({
            id: Utils.generateId(),
            data: dataUrl,
            createdAt: Date.now()
        });

        Utils.storage.set('stickerPack', this.stickerPack);
        this.updatePackUI();
        Toast.success('Added!', 'Sticker added to pack');
    },

    removeFromPack(stickerId) {
        this.stickerPack = this.stickerPack.filter(s => s.id !== stickerId);
        Utils.storage.set('stickerPack', this.stickerPack);
        this.updatePackUI();
    },

    updatePackUI() {
        const grid = document.getElementById('stickerPackGrid');
        const count = document.getElementById('stickerCount');
        const exportBtn = document.getElementById('exportPackBtn');

        count.textContent = this.stickerPack.length;
        exportBtn.disabled = this.stickerPack.length < 3;

        grid.innerHTML = this.stickerPack.map(sticker => `
            <div class="sticker-pack-item">
                <img src="${sticker.data}" alt="Sticker">
                <button onclick="StickerMaker.removeFromPack('${sticker.id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    },

    exportPack() {
        if (this.stickerPack.length < 3) {
            Toast.warning('Not Enough', 'Need at least 3 stickers');
            return;
        }

        // Create a zip-like download of all stickers
        Toast.info('Exporting...', 'Preparing sticker pack');

        this.stickerPack.forEach((sticker, index) => {
            setTimeout(() => {
                Utils.downloadFile(sticker.data, `sticker-${index + 1}.webp`);
            }, index * 300);
        });

        Toast.success('Exported!', 'Import these stickers into WhatsApp Sticker Maker app');
    },

        clearPack() {
        if (confirm('Are you sure you want to clear all stickers?')) {
            this.stickerPack = [];
            Utils.storage.set('stickerPack', this.stickerPack);
            this.updatePackUI();
            Toast.info('Cleared', 'Sticker pack cleared');
        }
    }
};

// Global functions
function createSticker() {
    StickerMaker.open();
}

function closeStickerMaker() {
    StickerMaker.close();
}

function downloadSticker() {
    StickerMaker.download();
}

function addToStickerPack() {
    StickerMaker.addToPack();
}

function exportStickerPack() {
    StickerMaker.exportPack();
}