(function() {
    const API_BASE_URL = "https://workflow-ai-lds3.onrender.com";
    
    const token = sessionStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    function escapeHTML(str) {
        if (str === null || str === undefined) return '';
        return String(str).replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }

    async function apiFetch(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = { ...options.headers };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';

        try {
            const response = await fetch(url, { ...options, headers });
            if (response.status === 401 || response.status === 403) {
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('user_data');
                window.location.href = '/';
                throw new Error('Acesso negado.');
            }
            const contentType = response.headers.get('content-type');
            let data;
            if (contentType && contentType.includes('application/json')) data = await response.json();
            else data = await response.text();
            if (!response.ok) {
                const message = data.detail || data.message || `Erro ${response.status}`;
                const error = new Error(message);
                error.status = response.status;
                throw error;
            }
            return data;
        } catch (error) {
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                const connError = new Error('Não foi possível conectar à API.');
                connError.status = 0;
                throw connError;
            }
            throw error;
        }
    }

    // =============================================
    // ELEMENTOS DO DOM
    // =============================================
    const statsGrid = document.getElementById('statsGrid');
    const adminUserName = document.getElementById('adminUserName');
    const logoutBtn = document.getElementById('logoutBtn');

    const usersCard = document.getElementById('usersCard');
    const logsCard = document.getElementById('logsCard');

    // Modal de usuários
    const usersModalOverlay = document.getElementById('usersModalOverlay');
    const closeUsersModalBtn = document.getElementById('closeUsersModal');
    const usersListContainer = document.getElementById('usersListContainer');
    const userSearchInput = document.getElementById('userSearchInput');
    const userTypeFilter = document.getElementById('userTypeFilter');
    const newUserBtn = document.getElementById('newUserBtn');

    // Modal de novo usuário
    const newUserModalOverlay = document.getElementById('newUserModalOverlay');
    const closeNewUserModalBtn = document.getElementById('closeNewUserModal');
    const newUserForm = document.getElementById('newUserForm');

    // Modal de logs
    const logsModalOverlay = document.getElementById('logsModalOverlay');
    const closeLogsModalBtn = document.getElementById('closeLogsModal');
    const logsListContainer = document.getElementById('logsListContainer');
    const logStartDate = document.getElementById('logStartDate');
    const logEndDate = document.getElementById('logEndDate');
    const filterLogsBtn = document.getElementById('filterLogsBtn');
    const clearLogsFilterBtn = document.getElementById('clearLogsFilterBtn');

    let allUsers = [];
    let allLogs = [];
    let currentUserFilter = 'all';

    // =============================================
    // LOGOUT
    // =============================================
    logoutBtn.addEventListener('click', () => {
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('user_data');
        window.location.href = '/';
    });

    // =============================================
    // CARREGAR DADOS DO USUÁRIO ADMIN
    // =============================================
    async function loadAdminUser() {
        try {
            const stored = sessionStorage.getItem('user_data');
            if (stored) {
                const user = JSON.parse(stored);
                adminUserName.textContent = user.nome || user.email || 'Admin';
            }
        } catch (e) { /* ignora */ }
    }

    // =============================================
    // CARREGAR ESTATÍSTICAS
    // =============================================
    async function loadStats() {
        try {
            const stats = await apiFetch('/admin/stats');
            
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="icon material-symbols-outlined">group</div>
                    <div class="label">Total de Usuários</div>
                    <div class="value">${stats.total_users}</div>
                </div>
                <div class="stat-card">
                    <div class="icon material-symbols-outlined">description</div>
                    <div class="label">Total de Documentos</div>
                    <div class="value">${stats.total_docs}</div>
                </div>
                <div class="stat-card">
                    <div class="icon material-symbols-outlined">analytics</div>
                    <div class="label">Documentos Analisados</div>
                    <div class="value">${stats.analyzed_docs}</div>
                </div>
                <div class="stat-card">
                    <div class="icon material-symbols-outlined">auto_awesome</div>
                    <div class="label">Total de Análises</div>
                    <div class="value">${stats.total_analyses}</div>
                </div>
            `;

            // Gráfico de Tipos de Documentos
            const docTypes = stats.doc_types || {};
            new ApexCharts(document.querySelector("#chartDocTypes"), {
                chart: { type: 'bar', height: 280, toolbar: { show: false }, fontFamily: 'Inter' },
                series: [{ name: 'Documentos', data: Object.values(docTypes) }],
                xaxis: { categories: Object.keys(docTypes) },
                colors: ['#1e5cb3'],
                plotOptions: { bar: { borderRadius: 6, columnWidth: '50%' } },
                dataLabels: { enabled: false },
                grid: { borderColor: 'rgba(30, 92, 179, 0.08)' }
            }).render();

            // Gráfico de Status
            const statusCounts = stats.status_counts || {};
            new ApexCharts(document.querySelector("#chartStatus"), {
                chart: { type: 'donut', height: 280, fontFamily: 'Inter' },
                series: Object.values(statusCounts),
                labels: Object.keys(statusCounts),
                colors: ['#1e5cb3', '#c9a227', '#16a34a', '#d53f3f', '#7b98b3'],
                legend: { position: 'bottom' },
                dataLabels: { enabled: true }
            }).render();

            // Gráfico de Timeline
            new ApexCharts(document.querySelector("#chartTimeline"), {
                chart: { type: 'area', height: 280, toolbar: { show: false }, fontFamily: 'Inter' },
                series: [{ name: 'Análises', data: [0, 0, 0, 0, 0, 0, stats.total_analyses] }],
                xaxis: { categories: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'] },
                colors: ['#c9a227'],
                fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.1 } },
                dataLabels: { enabled: false },
                grid: { borderColor: 'rgba(30, 92, 179, 0.08)' }
            }).render();

        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    }

    // =============================================
    // MODAL DE USUÁRIOS
    // =============================================
    async function openUsersModal() {
        usersModalOverlay.classList.add('active');
        usersListContainer.innerHTML = `<div class="ai-loading"><div class="spinner"></div><span>Carregando usuários...</span></div>`;
        
        try {
            allUsers = await apiFetch('/admin/users');
            renderUsersList();
        } catch (error) {
            usersListContainer.innerHTML = `<div class="ai-error"><span class="material-symbols-outlined">error</span><span>${escapeHTML(error.message)}</span></div>`;
        }
    }

    function renderUsersList() {
        const searchTerm = userSearchInput.value.trim().toLowerCase();
        let filtered = allUsers;

        if (currentUserFilter === 'admin') {
            filtered = filtered.filter(u => String(u.tipo_usuario || '').toLowerCase() === 'admin');
        } else if (currentUserFilter === 'usuario') {
            filtered = filtered.filter(u => String(u.tipo_usuario || '').toLowerCase() === 'usuario');
        }

        if (searchTerm) {
            filtered = filtered.filter(u => String(u.nome || '').toLowerCase().includes(searchTerm));
        }

        if (filtered.length === 0) {
            usersListContainer.innerHTML = `<div class="empty-state"><span class="material-symbols-outlined">person_off</span><span>Nenhum usuário encontrado.</span></div>`;
            return;
        }

        let html = '';
        filtered.forEach(user => {
            const isAdmin = String(user.tipo_usuario || '').toLowerCase() === 'admin';
            const badgeClass = isAdmin ? 'admin' : '';
            const initial = (user.nome || 'U').charAt(0).toUpperCase();
            
            html += `
                <div class="user-item">
                    <div class="user-item-icon">${initial}</div>
                    <div class="user-item-info">
                        <div class="user-item-name">${escapeHTML(user.nome || 'Sem nome')}</div>
                        <div class="user-item-email">${escapeHTML(user.email || 'Sem e-mail')}</div>
                        <div class="user-item-meta">Criado em ${user.data_criacao ? new Date(user.data_criacao).toLocaleDateString('pt-BR') : 'N/A'}</div>
                    </div>
                    <span class="user-item-badge ${badgeClass}">${isAdmin ? 'Admin' : 'Usuário'}</span>
                </div>
            `;
        });
        usersListContainer.innerHTML = html;
    }

    function closeUsersModalFn() { usersModalOverlay.classList.remove('active'); }

    usersCard.addEventListener('click', openUsersModal);
    closeUsersModalBtn.addEventListener('click', closeUsersModalFn);
    usersModalOverlay.addEventListener('click', (e) => { if (e.target === usersModalOverlay) closeUsersModalFn(); });

    userSearchInput.addEventListener('input', renderUsersList);

    userTypeFilter.addEventListener('click', (e) => {
        const btn = e.target.closest('.filter-btn');
        if (!btn) return;
        userTypeFilter.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentUserFilter = btn.dataset.filter;
        renderUsersList();
    });

    // =============================================
    // MODAL DE NOVO USUÁRIO
    // =============================================
    function openNewUserModal() {
        newUserModalOverlay.classList.add('active');
    }
    function closeNewUserModalFn() {
        newUserModalOverlay.classList.remove('active');
    }

    newUserBtn.addEventListener('click', openNewUserModal);
    closeNewUserModalBtn.addEventListener('click', closeNewUserModalFn);
    newUserModalOverlay.addEventListener('click', (e) => { if (e.target === newUserModalOverlay) closeNewUserModalFn(); });

    newUserForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userData = {
            nome: document.getElementById('newUserName').value,
            email: document.getElementById('newUserEmail').value,
            senha: document.getElementById('newUserPass').value,
            tipo_usuario: document.getElementById('newUserType').value
        };

        try {
            await apiFetch('/admin/users', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            closeNewUserModalFn();
            newUserForm.reset();
            // Recarregar lista
            allUsers = await apiFetch('/admin/users');
            renderUsersList();
        } catch (error) {
            alert('Erro ao cadastrar usuário: ' + error.message);
        }
    });

    // =============================================
    // MODAL DE LOGS
    // =============================================
    async function openLogsModal() {
        logsModalOverlay.classList.add('active');
        logsListContainer.innerHTML = `<div class="ai-loading"><div class="spinner"></div><span>Carregando logs...</span></div>`;
        
        try {
            allLogs = await apiFetch('/admin/logs');
            renderLogs(allLogs.slice(0, 15)); // Mostrar apenas os 15 mais recentes
        } catch (error) {
            logsListContainer.innerHTML = `<div class="ai-error"><span class="material-symbols-outlined">error</span><span>${escapeHTML(error.message)}</span></div>`;
        }
    }

    function renderLogs(logs) {
        if (!logs || logs.length === 0) {
            logsListContainer.innerHTML = `<div class="empty-state"><span class="material-symbols-outlined">receipt_long</span><span>Nenhum log encontrado.</span></div>`;
            return;
        }

        const iconMap = {
            'LOGIN': 'login',
            'LOGOUT': 'logout',
            'UPLOAD': 'upload_file',
            'OCR': 'document_scanner',
            'AI_ANALYSIS': 'auto_awesome',
            'CADASTRO_USUARIO': 'person_add'
        };

        let html = '';
        logs.forEach(log => {
            const icon = iconMap[log.acao] || 'info';
            html += `
                <div class="log-item">
                    <div class="log-item-icon"><span class="material-symbols-outlined">${icon}</span></div>
                    <div class="log-item-info">
                        <div class="log-item-action">${escapeHTML(log.acao || 'AÇÃO')}</div>
                        <div class="log-item-desc">${escapeHTML(log.descricao || '')}</div>
                        <div class="log-item-meta">
                            <span>${log.data ? new Date(log.data).toLocaleString('pt-BR') : 'N/A'}</span>
                            ${log.usuario_email ? `<span>• ${escapeHTML(log.usuario_email)}</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        logsListContainer.innerHTML = html;
    }

    function closeLogsModalFn() { logsModalOverlay.classList.remove('active'); }

    logsCard.addEventListener('click', openLogsModal);
    closeLogsModalBtn.addEventListener('click', closeLogsModalFn);
    logsModalOverlay.addEventListener('click', (e) => { if (e.target === logsModalOverlay) closeLogsModalFn(); });

    // Filtro por data
    filterLogsBtn.addEventListener('click', () => {
        const startDate = logStartDate.value;
        const endDate = logEndDate.value;

        if (!startDate && !endDate) {
            renderLogs(allLogs.slice(0, 15));
            return;
        }

        let filtered = allLogs;
        if (startDate) {
            const start = new Date(startDate);
            start.setHours(0, 0, 0, 0);
            filtered = filtered.filter(log => new Date(log.data) >= start);
        }
        if (endDate) {
            const end = new Date(endDate);
            end.setHours(23, 59, 59, 999);
            filtered = filtered.filter(log => new Date(log.data) <= end);
        }

        if (filtered.length === 0) {
            logsListContainer.innerHTML = `<div class="empty-state"><span class="material-symbols-outlined">event_busy</span><span>Não foram encontrados logs para o período informado.</span></div>`;
        } else {
            renderLogs(filtered);
        }
    });

    clearLogsFilterBtn.addEventListener('click', () => {
        logStartDate.value = '';
        logEndDate.value = '';
        renderLogs(allLogs.slice(0, 15));
    });

    // =============================================
    // FECHAR MODAIS COM ESC
    // =============================================
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeUsersModalFn();
            closeNewUserModalFn();
            closeLogsModalFn();
        }
    });

    // =============================================
    // INICIALIZAÇÃO
    // =============================================
    loadAdminUser();
    loadStats();
})();