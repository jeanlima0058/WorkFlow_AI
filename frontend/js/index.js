(function() {
    const API_BASE_URL = "https://workflow-ai-lds3.onrender.com";

    async function apiFetch(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = sessionStorage.getItem('access_token');

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, { ...options, headers });

            if (response.status === 401) {
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('user_data');
                throw new Error('Sessão expirada. Faça login novamente.');
            }

            const contentType = response.headers.get('content-type');
            let data;
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                const message = data.detail || data.message || `Erro ${response.status}`;
                throw new Error(message);
            }

            return data;
        } catch (error) {
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                throw new Error('Erro de conexão. Verifique sua internet ou a URL da API.');
            }
            throw error;
        }
    }

    // Fundo animado (mesmo código)
    const bgCanvas = document.querySelector('.bg-canvas');
    const tracks = [{ top: '28%' }, { top: '50%' }, { top: '72%' }];
    const fileIcons = ['description', 'picture_as_pdf', 'image', 'table_chart', 'text_snippet', 'folder_zip', 'insert_drive_file', 'dataset', 'analytics', 'receipt_long', 'article', 'code'];
    const dotColors = ['rgba(30, 92, 179, 0.4)', 'rgba(201, 162, 39, 0.4)', 'rgba(74, 142, 255, 0.4)', 'rgba(219, 185, 61, 0.35)', 'rgba(30, 92, 179, 0.25)'];

    function createTraveler() {
        if (!bgCanvas) return;
        const lane = tracks[Math.floor(Math.random() * tracks.length)];
        const el = document.createElement('div');
        const isGold = Math.random() > 0.65;
        const sizeClass = ['small', 'medium', 'medium', 'large'][Math.floor(Math.random() * 4)];
        el.className = `traveler ${sizeClass} ${isGold ? 'gold' : ''}`;
        const iconName = fileIcons[Math.floor(Math.random() * fileIcons.length)];
        el.innerHTML = `<span class="material-symbols-outlined">${iconName}</span>`;
        const baseTop = parseFloat(lane.top);
        const variation = (Math.random() - 0.5) * 6;
        el.style.top = `calc(${baseTop}% + ${variation}px)`;
        el.style.left = '-100px';
        const duration = 14 + Math.random() * 16;
        const delay = Math.random() * -30;
        el.style.animationDuration = `${duration}s`;
        el.style.animationDelay = `${delay}s`;
        if (Math.random() > 0.6) el.style.animationName = 'travelWave';
        bgCanvas.appendChild(el);
        setTimeout(() => { if (el.parentNode) el.remove(); }, (duration + Math.abs(delay)) * 1000 + 2000);
    }

    function createDot() {
        if (!bgCanvas) return;
        const lane = tracks[Math.floor(Math.random() * tracks.length)];
        const el = document.createElement('div');
        el.className = 'dot';
        const size = 4 + Math.random() * 8;
        const color = dotColors[Math.floor(Math.random() * dotColors.length)];
        el.style.width = `${size}px`;
        el.style.height = `${size}px`;
        el.style.background = color;
        el.style.boxShadow = `0 0 ${size * 2}px ${color}`;
        const baseTop = parseFloat(lane.top);
        const variation = (Math.random() - 0.5) * 10;
        el.style.top = `calc(${baseTop}% + ${variation}px)`;
        el.style.left = '-50px';
        const duration = 10 + Math.random() * 15;
        const delay = Math.random() * -25;
        el.style.animationDuration = `${duration}s`;
        el.style.animationDelay = `${delay}s`;
        bgCanvas.appendChild(el);
        setTimeout(() => { if (el.parentNode) el.remove(); }, (duration + Math.abs(delay)) * 1000 + 2000);
    }

    function initBackground() {
        for (let i = 0; i < 14; i++) setTimeout(() => createTraveler(), i * 300);
        for (let i = 0; i < 20; i++) setTimeout(() => createDot(), i * 200);
        setInterval(() => createTraveler(), 1400);
        setInterval(() => createDot(), 700);
    }
    initBackground();

    // Elementos do DOM
    const screenLogin = document.getElementById('screenLogin');
    const loginForm = document.getElementById('loginForm');
    const loginUser = document.getElementById('loginUser');
    const loginPass = document.getElementById('loginPass');
    const fieldUserContainer = document.getElementById('fieldUserContainer');
    const fieldPassContainer = document.getElementById('fieldPassContainer');
    const loginCard = document.getElementById('loginCard');
    const errorMsg = document.getElementById('errorMsg');
    const errorText = document.getElementById('errorText');
    const togglePass = document.getElementById('togglePass');
    const togglePassIcon = document.getElementById('togglePassIcon');
    const loginBtn = document.getElementById('loginBtn');

    // Toggle visibilidade da senha
    togglePass.addEventListener('click', (e) => {
        e.preventDefault();
        const isPassword = loginPass.type === 'password';
        loginPass.type = isPassword ? 'text' : 'password';
        togglePassIcon.textContent = isPassword ? 'visibility_off' : 'visibility';
        togglePass.setAttribute('aria-label', isPassword ? 'Ocultar senha' : 'Mostrar senha');
        loginPass.focus();
    });

    // Limpar erros ao digitar
    [loginUser, loginPass].forEach(input => {
        input.addEventListener('input', () => {
            fieldUserContainer.classList.remove('invalid');
            fieldPassContainer.classList.remove('invalid');
            loginUser.removeAttribute('aria-invalid');
            loginPass.removeAttribute('aria-invalid');
            errorMsg.classList.remove('show');
        });
    });

    function showError(message, targetInput = null) {
        errorText.textContent = message;
        errorMsg.classList.add('show');
        if (targetInput === loginUser) {
            fieldUserContainer.classList.add('invalid');
            loginUser.setAttribute('aria-invalid', 'true');
        } else if (targetInput === loginPass) {
            fieldPassContainer.classList.add('invalid');
            loginPass.setAttribute('aria-invalid', 'true');
        } else {
            fieldUserContainer.classList.add('invalid');
            fieldPassContainer.classList.add('invalid');
            loginUser.setAttribute('aria-invalid', 'true');
            loginPass.setAttribute('aria-invalid', 'true');
        }
        loginCard.classList.remove('shake');
        void loginCard.offsetWidth;
        loginCard.classList.add('shake');
    }

    // Função para decidir a página de destino com base no tipo_usuario
    function getRedirectPage(userData) {
        const tipoUsuario = String(userData.tipo_usuario || '').toLowerCase().trim();
        if (tipoUsuario === 'admin') {
            return '/admin.html';
        }
        return '/dashboard.html';
    }

    // Submit do formulário de login
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const user = loginUser.value.trim();
        const pass = loginPass.value.trim();

        if (!user) { showError('Informe o usuário', loginUser); loginUser.focus(); return; }
        if (!pass) { showError('Informe a senha', loginPass); loginPass.focus(); return; }
        if (pass.length < 4) { showError('A senha deve ter pelo menos 4 caracteres', loginPass); loginPass.focus(); return; }

        loginBtn.disabled = true;
        loginBtn.innerHTML = '<span>Entrando...</span>';

        try {
            // 1. Fazer login
            const loginData = await apiFetch('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email: user, senha: pass }),
            });

            // 2. Salvar token
            sessionStorage.setItem('access_token', loginData.access_token);

            // 3. Buscar dados do usuário
            const userData = await apiFetch('/auth/me');

            // 4. Salvar dados do usuário
            sessionStorage.setItem('user_data', JSON.stringify(userData));

            // 5. Redirecionar com base no tipo_usuario
            window.location.href = getRedirectPage(userData);

        } catch (error) {
            showError(error.message);
            loginBtn.disabled = false;
            loginBtn.innerHTML = '<span>Entrar</span><span class="material-symbols-outlined">arrow_forward</span>';
        }
    });

    // Verificar se já está logado ao carregar a página
    async function checkExistingSession() {
        const token = sessionStorage.getItem('access_token');
        if (!token) return;

        try {
            // 1. Validar token e obter dados do usuário
            const userData = await apiFetch('/auth/me');
            
            // 2. Atualizar dados locais
            sessionStorage.setItem('user_data', JSON.stringify(userData));

            // 3. Redirecionar com base no tipo_usuario
            window.location.href = getRedirectPage(userData);
        } catch (error) {
            // Token inválido, limpar e continuar na tela de login
            sessionStorage.removeItem('access_token');
            sessionStorage.removeItem('user_data');
        }
    }

    checkExistingSession();

    // Focar no campo de usuário ao carregar
    window.addEventListener('load', () => {
        setTimeout(() => loginUser.focus(), 400);
    });

})();