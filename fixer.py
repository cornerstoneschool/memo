import os
import re
import base64

def print_hdr(msg): print(f"\n\033[96m\033[1m=== {msg} ===\033[0m")
def print_ok(msg): print(f"\033[92m✅ {msg}\033[0m")
def print_err(msg): print(f"\033[91m❌ {msg}\033[0m")

print_hdr("MEMO PICS 2025 - CRYPTOGRAPHY HACK SETUP")
print("We are going to encrypt your GitHub token so it stays invisible to students.")

repo_owner = input("1. GitHub Username (e.g., cornerstoneschool): ").strip()
repo_name = input("2. Repository Name (e.g., memo2526): ").strip()
gh_token = input("3. Paste your GitHub PAT (ghp_...): ").strip()
admin_pwd = input("4. Type your Admin Password (e.g., MemoPics@2025): ").strip()

if not all([repo_owner, repo_name, gh_token, admin_pwd]):
    print_err("All fields are required!")
    exit(1)

# --- THE MAGIC: XOR ENCRYPTION ---
res = bytearray()
pwd_bytes = admin_pwd.encode('utf-8')
for i, char in enumerate(gh_token.encode('utf-8')):
    res.append(char ^ pwd_bytes[i % len(pwd_bytes)])
encrypted_token = base64.b64encode(res).decode('utf-8')

print_ok("Token encrypted successfully!")

# ==========================================
# 1. PATCH AUTH.JS (Inject Decryption Engine)
# ==========================================
try:
    with open('js/auth.js', 'r', encoding='utf-8') as f:
        auth = f.read()

    target = """            this.currentUser = {
                username: user.username,
                name: user.name,
                role: role,
                loginTime: Date.now()
            };"""

    replacement = f"""            this.currentUser = {{
                username: user.username,
                name: user.name,
                role: role,
                loginTime: Date.now()
            }};
            if (role === 'superAdmin') {{
                try {{
                    const enc = "{encrypted_token}";
                    const raw = atob(enc);
                    let dec = "";
                    for(let i=0; i<raw.length; i++) {{
                        dec += String.fromCharCode(raw.charCodeAt(i) ^ password.charCodeAt(i % password.length));
                    }}
                    this.currentUser.ghToken = dec;
                    this.currentUser.repoOwner = "{repo_owner}";
                    this.currentUser.repoName = "{repo_name}";
                }} catch(e) {{ console.error("Decryption failed"); }}
            }}"""

    if target in auth:
        auth = auth.replace(target, replacement)
        with open('js/auth.js', 'w', encoding='utf-8') as f:
            f.write(auth)
        print_ok("js/auth.js: Decryption engine injected.")
    elif "this.currentUser.ghToken" in auth:
        print_ok("js/auth.js: Already injected. Skipping.")
    else:
        print_err("js/auth.js: Target string not found!")
except Exception as e:
    print_err(f"Failed patching auth.js: {e}")

# ==========================================
# 2. PATCH ADMIN.JS (Live Upload Engine)
# ==========================================
try:
    with open('js/admin.js', 'r', encoding='utf-8') as f:
        admin = f.read()

    start_str = "uploadPhotos() {"
    end_str = "loadManageGrid() {"
    start_idx = admin.find(start_str)
    end_idx = admin.find(end_str)

    if start_idx != -1 and end_idx != -1:
        new_upload = """async uploadPhotos() {
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

    """
        admin = admin[:start_idx] + new_upload + admin[end_idx:]
        with open('js/admin.js', 'w', encoding='utf-8') as f:
            f.write(admin)
        print_ok("js/admin.js: Live upload engine injected.")
    else:
        print_err("js/admin.js: Injection point not found.")
except Exception as e:
    print_err(f"Failed patching admin.js: {e}")

# ==========================================
# 3. PATCH GALLERY.JS & APP.JS (Live JSON fetching)
# ==========================================
try:
    with open('js/gallery.js', 'r', encoding='utf-8') as f:
        gal = f.read()

    start_idx = gal.find("init() {")
    end_idx = gal.find("setupEventListeners() {")

    if start_idx != -1 and end_idx != -1:
        new_gal = f"""async init() {{
        await this.loadData();
        this.setupEventListeners();
        this.render();
        this.renderCategories();
        this.updateStats();
        if(typeof this.renderFeatured === 'function') this.renderFeatured();
    }},

    async loadData() {{
        try {{
            // Bypass cache to get latest photos
            const response = await fetch('./data/photos.json?v=' + new Date().getTime());
            if(response.ok) {{
                const data = await response.json();
                this.photos = data.photos || [];
                if(data.categories && data.categories.length > 0) this.categories = data.categories;
            }} else throw new Error("No JSON");
        }} catch (error) {{
            this.photos = Utils.storage.get('photos', []);
            this.categories = Utils.storage.get('categories', [
                {{ id: 'all', name: 'All Photos', icon: 'fa-th', teachersOnly: false }},
                {{ id: 'teachers-only', name: 'Teachers Only', icon: 'fa-lock', teachersOnly: true }}
            ]);
        }}
    }},

    """
        gal = gal[:start_idx] + new_gal + gal[end_idx:]
        with open('js/gallery.js', 'w', encoding='utf-8') as f:
            f.write(gal)
        print_ok("js/gallery.js: Wired to GitHub live database.")
except Exception as e:
    print_err(f"Failed patching gallery.js: {e}")

try:
    with open('js/app.js', 'r', encoding='utf-8') as f:
        app_js = f.read()
    app_js = app_js.replace("init() {", "async init() {").replace("Gallery.init();", "await Gallery.init();")
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(app_js)
    print_ok("js/app.js: Updated to async flow.")
except Exception as e:
    print_err(f"Failed patching app.js: {e}")

print_hdr("ALL DONE! PUSH TO GITHUB NOW")