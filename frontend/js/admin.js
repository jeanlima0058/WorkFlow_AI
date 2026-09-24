(function() {
    const API_BASE_URL = "COLOCAR_AQUI_URL_DO_RENDER";
    
    const token = sessionStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/';
        return;
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
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Erro na requisição');
            return data;
        } catch (error) {
            if (error.name === 'TypeError') throw new Error('Erro de conexão.');
            throw error;
        }
    }

    // Elementos
    const statsGrid = document.getElementById('statsGrid');
    const usersTableContainer = document.getElementById('usersTableContainer');
    const logsTableContainer = document.getElementById('logsTableContainer');
    const newUserBtn = document.getElementById('newUserBtn');
    const userModalOverlay = document.getElementById('userModalOverlay');
    const closeUserModal = document.getElementById('closeUserModal');
    const newUserForm = document.getElementById('newUserForm');
    const backBtn = document.getElementById('backBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    // Navegação
    backBtn.addEventListener('click', () => window.location.href = '/dashboard.html');
    logoutBtn.addEventListener('click', () => {
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('user_data');
        window.location.href = '/';
    });

    // Carregar Estatísticas
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
            const typeLabels = Object.keys(docTypes);
            const typeValues = Object.values(docTypes);

            new ApexCharts(document.querySelector("#chartDocTypes"), {
                chart: { type: 'bar', height: 250, toolbar: { show: false }, fontFamily: 'Inter' },
                series: [{ name: 'Documentos', data: typeValues }],
                xaxis: { categories: typeLabels },
                colors: ['#1e5cb3'],
                plotOptions: { bar: { borderRadius: 6, columnWidth: '50%' } },
                dataLabels: { enabled: false },
                grid: { borderColor: 'rgba(30, 92, 179, 0.08)' }
            }).render();

            // Gráfico de Status
            const statusCounts = stats.status_counts || {};
            const statusLabels = Object.keys(statusCounts);
            const statusValues = Object.values(statusCounts);

            new ApexCharts(document.querySelector("#chartStatus"), {
                chart: { type: 'donut', height: 250, fontFamily: 'Inter' },
                series: statusValues,
                labels: statusLabels,
                colors: ['#1e5cb3', '#c9a227', '#16a34a', '#d53f3f', '#7b98b3'],
                legend: { position: 'bottom' },
                dataLabels: { enabled: true }
            }).render();

        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    }

    // Carregar Usuários
    async function loadUsers() {
        try {
            const users = await apiFetch('/admin/users');
            let html = `
                <table>
                    <thead><tr><th>Nome</th><th>E-mail</th><th>Tipo</th><th>Data Criação</th></tr></thead>
                    <tbody>
            `;
            users.forEach(user => {
                const tipoClass = user.tipo_usuario === 'ADMIN' ? 'admin' : 'user';
                html += `
                    <tr>
                        <td>${user.nome}</td>
                        <td>${user.email}</td>
                        <td><span class="status-badge ${tipoClass}">${user.tipo_usuario}</span></td>
                        <td>${new Date(user.data_criacao).toLocaleDateString('pt-BR')}</td>
                    </tr>
                `;
            });
            html += `</tbody></table>`;
            usersTableContainer.innerHTML = html;
        } catch (error) {
            usersTableContainer.innerHTML = `<div style="padding:20px; color:#d53f3f;">Erro ao carregar usuários: ${error.message}</div>`;
        }
    }

    // Carregar Logs
    async function loadLogs() {
        try {
            const logs = await apiFetch('/admin/logs');
            let html = `
                <table>
                    <thead><tr><th>Data/Hora</th><th>Usuário</th><th>Ação</th><th>Descrição</th></tr></thead>
                    <tbody>
            `;
            logs.forEach(log => {
                html += `
                    <tr>
                        <td>${new Date(log.data).toLocaleString('pt-BR')}</td>
                        <td>${log.usuario_email || 'Sistema'}</td>
                        <td><strong>${log.acao}</strong></td>
                        <td>${log.descricao}</td>
                    </tr>
                `;
            });
            html += `</tbody></table>`;
            logsTableContainer.innerHTML = html;
        } catch (error) {
            logsTableContainer.innerHTML = `<div style="padding:20px; color:#d53f3f;">Erro ao carregar logs: ${error.message}</div>`;
        }
    }

    // Modal de Novo Usuário
    newUserBtn.addEventListener('click', () => userModalOverlay.classList.add('active'));
    closeUserModal.addEventListener('click', () => userModalOverlay.classList.remove('active'));
    userModalOverlay.addEventListener('click', (e) => { if (e.target === userModalOverlay) userModalOverlay.classList.remove('active'); });

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
            userModalOverlay.classList.remove('active');
            newUserForm.reset();
            loadUsers(); // Recarrega a lista
        } catch (error) {
            alert('Erro ao cadastrar usuário: ' + error.message);
        }
    });

    // Inicialização
    loadStats();
    loadUsers();
    loadLogs();

})();