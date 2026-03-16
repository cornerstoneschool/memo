// ========================================
// MEMO PICS 2025 - AUTHENTICATION
// ========================================

const Auth = {
    // Predefined credentials (In production, use secure methods)
    credentials: {
        superAdmin: [
            { username: 'admin1', password: 'MemoPics@2025', name: 'Super Admin 1' },
            { username: 'admin2', password: 'MemoPics@2025', name: 'Super Admin 2' }
        ],
        teachers: [] // Will be loaded from storage
    },

    currentUser: null,
    loginType: 'teacher', // 'teacher' or 'admin'

    init() {
        // Load teachers from storage
        this.credentials.teachers = Utils.storage.get('teachers', [
            { username: 'teacher', password: 'Teacher@2025', name: 'Teacher' }
        ]);

        // Check for existing session
        const session = Utils.storage.get('session');
        if (session) {
            this.currentUser = session;
            this.updateUI();
        }

        this.setupEventListeners();
    },

    setupEventListeners() {
        // Login tabs
        document.querySelectorAll('.login-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.login-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.loginType = tab.dataset.tab;
            });
        });

        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });
    },

    login() {
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;
        const errorEl = document.getElementById('loginError');

        errorEl.textContent = '';

        let user = null;
        let role = null;

        if (this.loginType === 'admin') {
            // Check super admin credentials
            user = this.credentials.superAdmin.find(
                u => u.username === username && u.password === password
            );
            role = 'superAdmin';
        } else {
            // Check teacher credentials
            user = this.credentials.teachers.find(
                u => u.username === username && u.password === password
            );
            role = 'teacher';
        }

        if (user) {
            this.currentUser = {
                username: user.username,
                name: user.name,
                role: role,
                loginTime: Date.now()
            };

            Utils.storage.set('session', this.currentUser);
            this.updateUI();
            closeLoginModal();
            
            Toast.success('Welcome!', `Logged in as ${user.name}`);

            // Refresh gallery to show teacher-only content if applicable
            if (typeof Gallery !== 'undefined') {
                Gallery.render();
            }
        } else {
            errorEl.textContent = 'Invalid username or password';
            document.getElementById('loginPassword').value = '';
        }
    },

    logout() {
        this.currentUser = null;
        Utils.storage.remove('session');
        this.updateUI();
        closeAdminPanel();
        Toast.info('Logged Out', 'You have been logged out');

        // Refresh gallery to hide teacher-only content
        if (typeof Gallery !== 'undefined') {
            Gallery.render();
        }
    },

    updateUI() {
        const loginBtn = document.getElementById('loginBtn');
        const adminBtn = document.getElementById('adminBtn');

        if (this.currentUser) {
            loginBtn.innerHTML = `
                <i class="fas fa-user-check"></i>
                <span>${this.currentUser.name}</span>
            `;
            loginBtn.onclick = () => this.showUserMenu();

            if (this.currentUser.role === 'superAdmin') {
                adminBtn.classList.remove('hidden');
            } else {
                adminBtn.classList.add('hidden');
            }
        } else {
            loginBtn.innerHTML = `
                <i class="fas fa-user"></i>
                <span>Login</span>
            `;
            loginBtn.onclick = openLoginModal;
            adminBtn.classList.add('hidden');
        }
    },

    showUserMenu() {
        // Simple logout for now
        if (confirm('Do you want to logout?')) {
            this.logout();
        }
    },

    isLoggedIn() {
        return this.currentUser !== null;
    },

    isSuperAdmin() {
        return this.currentUser?.role === 'superAdmin';
    },

    isTeacher() {
        return this.currentUser?.role === 'teacher' || this.currentUser?.role === 'superAdmin';
    },

    canViewTeacherContent() {
        return this.isTeacher();
    },

    // Moderator management (for super admin)
    addTeacher(username, password, name) {
        if (!this.isSuperAdmin()) {
            Toast.error('Access Denied', 'Only super admins can add teachers');
            return false;
        }

        // Check if username exists
        if (this.credentials.teachers.some(t => t.username === username)) {
            Toast.error('Error', 'Username already exists');
            return false;
        }

        this.credentials.teachers.push({ username, password, name });
        Utils.storage.set('teachers', this.credentials.teachers);
        Toast.success('Success', `Teacher "${name}" added successfully`);
        return true;
    },

    removeTeacher(username) {
        if (!this.isSuperAdmin()) {
            Toast.error('Access Denied', 'Only super admins can remove teachers');
            return false;
        }

        this.credentials.teachers = this.credentials.teachers.filter(
            t => t.username !== username
        );
        Utils.storage.set('teachers', this.credentials.teachers);
        Toast.success('Success', 'Teacher removed successfully');
        return true;
    },

    getTeachers() {
        return this.credentials.teachers.map(t => ({
            username: t.username,
            name: t.name
        }));
    }
};

// Global functions for modal control
function openLoginModal() {
    document.getElementById('loginModal').classList.add('active');
    document.getElementById('loginUsername').focus();
}

function closeLoginModal() {
    document.getElementById('loginModal').classList.remove('active');
    document.getElementById('loginForm').reset();
    document.getElementById('loginError').textContent = '';
}

function togglePassword() {
    const input = document.getElementById('loginPassword');
    const icon = document.querySelector('.password-toggle i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

function logout() {
    Auth.logout();
}