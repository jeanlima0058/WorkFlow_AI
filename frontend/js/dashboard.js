(function() {
    // =============================================
    // 1. CONFIGURAÇÃO
    // =============================================
    const API_BASE_URL = "https://workflow-ai-lds3.onrender.com";

    // Função para escapar HTML (Segurança contra XSS)
    function escapeHTML(str) {
        if (str === null || str === undefined) return '';
        return String(str).replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    // Função centralizada para chamadas à API
    async function apiFetch(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = sessionStorage.getItem('access_token');

        const headers = { ...options.headers };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';

        try {
            const response = await fetch(url, { ...options, headers });

            // Tratamento de 401 - Sessão expirada
            if (response.status === 401) {
                sessionStorage.removeItem('access_token');
                sessionStorage.removeItem('user_data');
                window.location.href = '/';
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
                // Extrai a mensagem de erro da API
                const message = data.detail || data.message || `Erro ${response.status}`;
                const error = new Error(message);
                error.status = response.status;
                throw error;
            }

            return data;
        } catch (error) {
            // Erro de conexão
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                const connError = new Error('Não foi possível conectar à API. Verifique sua internet.');
                connError.status = 0;
                throw connError;
            }
            throw error;
        }
    }

    // =============================================
    // 2. VERIFICAÇÃO DE AUTENTICAÇÃO
    // =============================================
    const token = sessionStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    // =============================================
    // 3. FUNDO ANIMADO
    // =============================================
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
        el.style.width = `${size}px`; el.style.height = `${size}px`;
        el.style.background = color; el.style.boxShadow = `0 0 ${size * 2}px ${color}`;
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

    // =============================================
    // 4. ELEMENTOS DO DOM
    // =============================================
    const inputBar = document.getElementById('inputBar');
    const inputBarText = document.getElementById('inputBarText');
    const attachBtn = document.getElementById('attachBtn');
    const fileInput = document.getElementById('fileInput');
    const fileTags = document.getElementById('fileTags');
    const emptyStateTag = document.getElementById('emptyStateTag');
    const profileBtn = document.getElementById('profileBtn');
    const historyBtn = document.getElementById('historyBtn');
    const searchBtn = document.getElementById('searchBtn');
    const aiResultPanel = document.getElementById('aiResultPanel');
    const aiResultContent = document.getElementById('aiResultContent');
    const closeResultBtn = document.getElementById('closeResultBtn');

    let files = [];

    // =============================================
    // 5. FUNÇÕES AUXILIARES
    // =============================================
    function formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function iconFor(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const map = { pdf: 'picture_as_pdf', doc: 'description', docx: 'description', txt: 'text_snippet', png: 'image', jpg: 'image', jpeg: 'image', gif: 'image', csv: 'table_chart', xlsx: 'table_chart', zip: 'folder_zip', json: 'data_object', xml: 'code' };
        return map[ext] || 'insert_drive_file';
    }

    // =============================================
    // 6. RENDERIZAÇÃO DE ARQUIVOS ANEXADOS
    // =============================================
    function renderFileTags() {
        if (files.length === 0) {
            fileTags.innerHTML = '';
            fileTags.appendChild(emptyStateTag);
            emptyStateTag.style.display = 'flex';
            return;
        }
        emptyStateTag.style.display = 'none';
        fileTags.innerHTML = '';
        files.forEach((file, index) => {
            const tag = document.createElement('div');
            tag.className = 'file-tag';
            tag.title = file.name;
            tag.innerHTML = `
                <span class="material-symbols-outlined">${iconFor(file.name)}</span>
                <span class="file-tag-name">${escapeHTML(file.name)}</span>
                <button class="remove-tag" data-index="${index}"><span class="material-symbols-outlined">close</span></button>
            `;
            fileTags.appendChild(tag);
        });

        fileTags.querySelectorAll('.remove-tag').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.dataset.index);
                files.splice(idx, 1);
                renderFileTags();
            });
        });
    }

    // =============================================
    // 7. UPLOAD E PROCESSAMENTO
    // =============================================
    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('arquivo', file);
        return await apiFetch('/documents/upload', { method: 'POST', body: formData });
    }

    async function processDocument(documentId) {
        showAiResult(`<div class="ai-loading"><div class="spinner"></div><span>Extraindo texto (OCR)...</span></div>`);
        try {
            await apiFetch(`/ocr/process/${documentId}`, { method: 'POST' });
        } catch (error) {
            throw new Error(`Falha no OCR: ${error.message}`);
        }

        showAiResult(`<div class="ai-loading"><div class="spinner"></div><span>Analisando com IA...</span></div>`);
        try {
            const result = await apiFetch(`/ai/analyze/${documentId}`, { method: 'POST' });
            return result;
        } catch (error) {
            throw new Error(`Falha na análise: ${error.message}`);
        }
    }

    function showAiResult(html) {
        aiResultContent.innerHTML = html;
        aiResultPanel.classList.add('visible');
    }

    function renderAiResult(data, isInsight = false) {
        const insightClass = isInsight ? 'insight-match' : '';
        const insightBadge = isInsight ? '<span class="history-item-status" style="background: rgba(201,162,39,0.15); color: #b8901a;">INSIGHT</span>' : '';

        const html = `
            <div class="result-section ${insightClass}">
                ${insightBadge}
                <div class="result-label"><span class="material-symbols-outlined">category</span> Tipo do Documento</div>
                <div class="result-value">${escapeHTML(data.tipo_documento || 'Não informado')}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">label</span> Categoria</div>
                <div class="result-value">${escapeHTML(data.categoria || 'Não informada')}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">summarize</span> Resumo</div>
                <div class="result-value">${escapeHTML(data.resumo || 'Nenhum resumo.')}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">info</span> Informações Principais</div>
                <div class="result-value">${escapeHTML(data.informacoes_principais || 'Nenhuma informação.')}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">lightbulb</span> Insights</div>
                <div class="result-value">${escapeHTML(data.insights || 'Nenhum insight.')}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">recommend</span> Recomendações</div>
                <div class="result-value">${escapeHTML(data.recomendacoes || 'Nenhuma recomendação.')}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">key</span> Palavras-chave</div>
                <div class="result-value">${escapeHTML(data.palavras_chave || 'Nenhuma.')}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">warning</span> Alertas</div>
                <div class="result-value highlight">${escapeHTML(data.alertas || 'Nenhum alerta.')}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">verified</span> Confiança</div>
                <div class="confidence-bar">
                    <div class="bar"><div class="fill" style="width: ${(data.confianca || 0) * 100}%"></div></div>
                    <span class="value">${((data.confianca || 0) * 100).toFixed(0)}%</span>
                </div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">calendar_today</span> Data da Análise</div>
                <div class="result-value">${data.data_processamento ? new Date(data.data_processamento).toLocaleString('pt-BR') : 'Não disponível'}</div>
            </div>
        `;
        showAiResult(html);
    }

    function showAiError(message) {
        showAiResult(`<div class="ai-error"><span class="material-symbols-outlined">error</span><span>${escapeHTML(message)}</span></div>`);
    }

    async function addFiles(newFiles) {
        const arr = Array.from(newFiles);
        let added = 0;
        for (const f of arr) {
            if (!files.some(existing => existing.name === f.name && existing.size === f.size)) {
                files.push(f);
                added++;
            }
        }
        if (added > 0) {
            renderFileTags();
            inputBarText.textContent = `${added} arquivo(s) anexado(s)`;
            setTimeout(() => { inputBarText.textContent = 'Anexar arquivo para análise...'; }, 1800);

            for (const file of arr) {
                try {
                    const doc = await uploadFile(file);
                    if (doc && doc.id) {
                        await processDocument(doc.id);
                    }
                } catch (error) {
                    showAiError(error.message);
                }
            }
        } else {
            inputBarText.textContent = 'Arquivo já anexado';
            setTimeout(() => { inputBarText.textContent = 'Anexar arquivo para análise...'; }, 1500);
        }
    }

    // =============================================
    // 8. EVENTOS DE UPLOAD
    // =============================================
    // Clicar na barra inteira abre o seletor de arquivos
    inputBar.addEventListener('click', (e) => {
        // Se clicou no botão específico, deixa o botão cuidar
        if (e.target.closest('.attach-btn')) return;
        fileInput.click();
    });

    // Botão específico também abre o seletor
    attachBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) { 
            addFiles(e.target.files); 
            fileInput.value = ''; 
        }
    });

    // Drag and drop
    inputBar.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); inputBar.classList.add('drag-over'); });
    inputBar.addEventListener('dragleave', (e) => { e.preventDefault(); e.stopPropagation(); inputBar.classList.remove('drag-over'); });
    inputBar.addEventListener('drop', (e) => { 
        e.preventDefault(); 
        e.stopPropagation(); 
        inputBar.classList.remove('drag-over'); 
        if (e.dataTransfer.files.length > 0) addFiles(e.dataTransfer.files); 
    });

    // Teclado
    inputBar.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInput.click();
        }
    });

    closeResultBtn.addEventListener('click', () => aiResultPanel.classList.remove('visible'));

    // =============================================
    // 9. MODAL DE PERFIL (CORRIGIDO)
    // =============================================
    const profileModalOverlay = document.getElementById('profileModalOverlay');
    const closeProfileModal = document.getElementById('closeProfileModal');
    const profileModalBody = document.getElementById('profileModalBody');
    const logoutModalBtn = document.getElementById('logoutModalBtn');

    async function openProfileModal() {
        profileModalOverlay.classList.add('active');
        profileModalBody.innerHTML = `<div class="ai-loading"><div class="spinner"></div><span>Carregando perfil...</span></div>`;

        let apiUser = null;
        let localUser = null;

        // Tenta buscar dados locais primeiro (fallback)
        try {
            const stored = sessionStorage.getItem('user_data');
            if (stored) localUser = JSON.parse(stored);
        } catch (e) { /* ignora */ }

        // Tenta buscar da API
        try {
            apiUser = await apiFetch('/auth/me');
            // Atualiza o localStorage com os dados mais recentes
            sessionStorage.setItem('user_data', JSON.stringify(apiUser));
        } catch (error) {
            // Se for 401, o apiFetch já redirecionou
            if (error.status === 401) return;
            
            // Se for erro de conexão ou outro, usa fallback
            if (!localUser) {
                profileModalBody.innerHTML = `
                    <div class="ai-error">
                        <span class="material-symbols-outlined">error</span>
                        <span>${escapeHTML(error.message)}</span>
                    </div>
                `;
                return;
            }
        }

        // Mescla dados: API tem prioridade, fallback para local
        const user = {
            nome: apiUser?.nome || localUser?.nome || null,
            email: apiUser?.email || localUser?.email || null,
            tipo_usuario: apiUser?.tipo_usuario || localUser?.tipo_usuario || null,
            data_criacao: apiUser?.data_criacao || localUser?.data_criacao || null
        };

        profileModalBody.innerHTML = `
            <div class="profile-field">
                <label>Nome</label>
                <span>${user.nome ? escapeHTML(user.nome) : 'Não informado'}</span>
            </div>
            <div class="profile-field">
                <label>E-mail</label>
                <span>${user.email ? escapeHTML(user.email) : 'Não informado'}</span>
            </div>
            <div class="profile-field">
                <label>Tipo de Usuário</label>
                <span>${user.tipo_usuario ? escapeHTML(user.tipo_usuario) : 'Não informado'}</span>
            </div>
            <div class="profile-field">
                <label>Data de Criação</label>
                <span>${user.data_criacao ? new Date(user.data_criacao).toLocaleString('pt-BR') : 'Não informada'}</span>
            </div>
        `;
    }

    function closeProfileModalFn() { profileModalOverlay.classList.remove('active'); }
    profileBtn.addEventListener('click', openProfileModal);
    closeProfileModal.addEventListener('click', closeProfileModalFn);
    profileModalOverlay.addEventListener('click', (e) => { if (e.target === profileModalOverlay) closeProfileModalFn(); });

    logoutModalBtn.addEventListener('click', () => {
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('user_data');
        window.location.href = '/';
    });

    // =============================================
    // 10. MODAL DE HISTÓRICO (CORRIGIDO)
    // =============================================
    const historyModalOverlay = document.getElementById('historyModalOverlay');
    const closeHistoryModal = document.getElementById('closeHistoryModal');
    const historyModalBody = document.getElementById('historyModalBody');

    async function openHistoryModal() {
        historyModalOverlay.classList.add('active');
        historyModalBody.innerHTML = `<div class="ai-loading"><div class="spinner"></div><span>Carregando histórico...</span></div>`;

        try {
            const documents = await apiFetch('/documents/');
            
            if (!documents || documents.length === 0) {
                historyModalBody.innerHTML = `
                    <div class="empty-state">
                        <span class="material-symbols-outlined">inbox</span>
                        <span>Nenhum documento encontrado.</span>
                    </div>
                `;
                return;
            }

            let html = '';
            documents.forEach(doc => {
                const statusClass = doc.status ? doc.status.toLowerCase() : '';
                html += `
                    <div class="history-item" data-doc-id="${escapeHTML(doc.id)}">
                        <div class="history-item-icon"><span class="material-symbols-outlined">${iconFor(doc.nome_arquivo || 'file')}</span></div>
                        <div class="history-item-info">
                            <div class="history-item-name">${escapeHTML(doc.nome_arquivo || 'Sem nome')}</div>
                            <div class="history-item-meta">
                                <span>${escapeHTML(doc.tipo_arquivo || 'N/A')}</span>
                                <span>•</span>
                                <span>${doc.tamanho ? formatSize(doc.tamanho) : 'N/A'}</span>
                                <span>•</span>
                                <span>${doc.data_upload ? new Date(doc.data_upload).toLocaleDateString('pt-BR') : 'N/A'}</span>
                            </div>
                        </div>
                        <span class="history-item-status ${statusClass}">${escapeHTML(doc.status || 'PENDENTE')}</span>
                    </div>
                `;
            });
            historyModalBody.innerHTML = html;

            // Adicionar evento de clique em cada item
            historyModalBody.querySelectorAll('.history-item').forEach(item => {
                item.addEventListener('click', async () => {
                    const docId = item.dataset.docId;
                    historyModalOverlay.classList.remove('active');
                    
                    try {
                        const result = await apiFetch(`/ai/result/${docId}`);
                        renderAiResult(result);
                    } catch (error) {
                        // Diferencia os tipos de erro
                        if (error.status === 404) {
                            showAiError('Este documento ainda não possui uma análise de IA.');
                        } else if (error.status === 401) {
                            // apiFetch já redirecionou
                            return;
                        } else if (error.status === 0) {
                            showAiError('Não foi possível conectar à API. Verifique sua internet.');
                        } else {
                            showAiError(`Erro ao buscar análise: ${error.message}`);
                        }
                    }
                });
            });

        } catch (error) {
            // Diferencia os tipos de erro na listagem
            if (error.status === 401) {
                // apiFetch já redirecionou
                return;
            } else if (error.status === 0) {
                historyModalBody.innerHTML = `
                    <div class="ai-error">
                        <span class="material-symbols-outlined">error</span>
                        <span>Não foi possível conectar à API. Verifique sua internet.</span>
                    </div>
                `;
            } else if (error.status === 403) {
                historyModalBody.innerHTML = `
                    <div class="ai-error">
                        <span class="material-symbols-outlined">error</span>
                        <span>Acesso negado. Você não tem permissão para ver este histórico.</span>
                    </div>
                `;
            } else if (error.status === 404) {
                historyModalBody.innerHTML = `
                    <div class="empty-state">
                        <span class="material-symbols-outlined">inbox</span>
                        <span>Nenhum documento encontrado.</span>
                    </div>
                `;
            } else {
                historyModalBody.innerHTML = `
                    <div class="ai-error">
                        <span class="material-symbols-outlined">error</span>
                        <span>Erro ao carregar histórico: ${escapeHTML(error.message)}</span>
                    </div>
                `;
            }
        }
    }

    function closeHistoryModalFn() { historyModalOverlay.classList.remove('active'); }
    historyBtn.addEventListener('click', openHistoryModal);
    closeHistoryModal.addEventListener('click', closeHistoryModalFn);
    historyModalOverlay.addEventListener('click', (e) => { if (e.target === historyModalOverlay) closeHistoryModalFn(); });

    // =============================================
    // 11. MODAL DE PESQUISA
    // =============================================
    const searchModalOverlay = document.getElementById('searchModalOverlay');
    const closeSearchModal = document.getElementById('closeSearchModal');
    const searchInput = document.getElementById('searchInput');
    const searchSubmitBtn = document.getElementById('searchSubmitBtn');
    const searchResults = document.getElementById('searchResults');

    function openSearchModal() {
        searchModalOverlay.classList.add('active');
        searchInput.focus();
    }

    function closeSearchModalFn() { searchModalOverlay.classList.remove('active'); }

    searchBtn.addEventListener('click', openSearchModal);
    closeSearchModal.addEventListener('click', closeSearchModalFn);
    searchModalOverlay.addEventListener('click', (e) => { if (e.target === searchModalOverlay) closeSearchModalFn(); });

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            searchResults.innerHTML = `<div class="empty-state"><span class="material-symbols-outlined">search_off</span><span>Digite um termo para pesquisar.</span></div>`;
            return;
        }

        searchResults.innerHTML = `<div class="ai-loading"><div class="spinner"></div><span>Pesquisando...</span></div>`;

        try {
            const results = await apiFetch(`/documents/search?q=${encodeURIComponent(query)}`);
            if (!results || results.length === 0) {
                searchResults.innerHTML = `<div class="empty-state"><span class="material-symbols-outlined">search_off</span><span>Nenhum documento encontrado.</span></div>`;
                return;
            }

            let html = '';
            results.forEach(doc => {
                const isInsight = doc.match_type === 'insight';
                const matchClass = isInsight ? 'insight-match' : '';
                const matchLabel = isInsight ? '<span class="history-item-status" style="background: rgba(201,162,39,0.15); color: #b8901a;">INSIGHT</span>' : '<span class="history-item-status" style="background: rgba(30,92,179,0.08); color: #1e5cb3;">PALAVRA-CHAVE</span>';
                
                let snippet = '';
                if (isInsight && doc.insight_snippet) {
                    const highlighted = escapeHTML(doc.insight_snippet).replace(
                        new RegExp(`(${escapeHTML(query)})`, 'gi'), 
                        '<span class="insight-highlight">$1</span>'
                    );
                    snippet = `<div style="font-size:0.75rem; color:#4a6f8f; margin-top:4px; font-style:italic;">"...${highlighted}..."</div>`;
                } else if (doc.palavras_chave) {
                    snippet = `<div style="font-size:0.75rem; color:#7b98b3; margin-top:4px;">Palavras-chave: ${escapeHTML(doc.palavras_chave)}</div>`;
                }

                html += `
                    <div class="history-item ${matchClass}" data-doc-id="${escapeHTML(doc.id)}">
                        <div class="history-item-icon"><span class="material-symbols-outlined">${iconFor(doc.nome_arquivo || 'file')}</span></div>
                        <div class="history-item-info">
                            <div class="history-item-name">${escapeHTML(doc.nome_arquivo || 'Sem nome')}</div>
                            <div class="history-item-meta">
                                <span>${doc.data_upload ? new Date(doc.data_upload).toLocaleDateString('pt-BR') : 'N/A'}</span>
                                ${matchLabel}
                            </div>
                            ${snippet}
                        </div>
                    </div>
                `;
            });
            searchResults.innerHTML = html;

            searchResults.querySelectorAll('.history-item').forEach(item => {
                item.addEventListener('click', async () => {
                    const docId = item.dataset.docId;
                    closeSearchModalFn();
                    try {
                        const result = await apiFetch(`/ai/result/${docId}`);
                        renderAiResult(result, true);
                    } catch (error) {
                        if (error.status === 404) {
                            showAiError('Este documento ainda não possui uma análise de IA.');
                        } else if (error.status === 0) {
                            showAiError('Não foi possível conectar à API.');
                        } else {
                            showAiError(`Erro: ${error.message}`);
                        }
                    }
                });
            });

        } catch (error) {
            if (error.status === 0) {
                searchResults.innerHTML = `<div class="ai-error"><span class="material-symbols-outlined">error</span><span>Não foi possível conectar à API.</span></div>`;
            } else {
                searchResults.innerHTML = `<div class="ai-error"><span class="material-symbols-outlined">error</span><span>${escapeHTML(error.message)}</span></div>`;
            }
        }
    }

    searchSubmitBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') performSearch(); });

    // Fechar modais com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeProfileModalFn();
            closeHistoryModalFn();
            closeSearchModalFn();
        }
    });

    // =============================================
    // 12. INICIALIZAÇÃO
    // =============================================
    renderFileTags();
})();