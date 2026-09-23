(function() {
    // =============================================
    // 1. CONFIGURAÇÃO E UTILITÁRIOS
    // =============================================
    const API_BASE_URL = "https://workflow-ai-lds3.onrender.com"; // Substitua pela URL real

    // Função centralizada para chamadas à API
    async function apiFetch(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = localStorage.getItem('access_token');

        const headers = {
            ...options.headers,
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Se for FormData, não definir Content-Type (o browser define automaticamente)
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(url, { ...options, headers });

            if (response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_data');
                window.location.href = 'index.html';
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
                throw new Error('Erro de conexão. Verifique sua internet.');
            }
            throw error;
        }
    }

    // =============================================
    // 2. VERIFICAÇÃO DE AUTENTICAÇÃO
    // =============================================
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
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

    // =============================================
    // 4. LÓGICA DE UPLOAD
    // =============================================
    const inputBar = document.getElementById('inputBar');
    const inputBarText = document.getElementById('inputBarText');
    const attachBtn = document.getElementById('attachBtn');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const emptyState = document.getElementById('emptyState');
    const fileCount = document.getElementById('fileCount');
    const profileBtn = document.getElementById('profileBtn');
    const historyBtn = document.getElementById('historyBtn');
    const aiResultPanel = document.getElementById('aiResultPanel');
    const aiResultContent = document.getElementById('aiResultContent');
    const closeResultBtn = document.getElementById('closeResultBtn');

    let files = [];

    function formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    function iconFor(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const map = {
            pdf: 'picture_as_pdf', doc: 'description', docx: 'description',
            txt: 'text_snippet', png: 'image', jpg: 'image', jpeg: 'image', gif: 'image',
            csv: 'table_chart', xlsx: 'table_chart', zip: 'folder_zip',
            json: 'data_object', xml: 'code',
        };
        return map[ext] || 'insert_drive_file';
    }

    function render() {
        fileCount.textContent = files.length;
        if (files.length === 0) {
            fileList.innerHTML = '';
            fileList.appendChild(emptyState);
            emptyState.style.display = 'flex';
            return;
        }
        emptyState.style.display = 'none';
        fileList.innerHTML = '';
        files.forEach((file, index) => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.style.animationDelay = `${index * 0.05}s`;

            const icon = document.createElement('div');
            icon.className = 'file-icon';
            icon.innerHTML = `<span class="material-symbols-outlined">${iconFor(file.name)}</span>`;

            const info = document.createElement('div');
            info.className = 'file-info';

            const name = document.createElement('div');
            name.className = 'file-name';
            name.textContent = file.name;
            name.title = file.name;

            const meta = document.createElement('div');
            meta.className = 'file-meta';
            meta.innerHTML = `<span class="size-tag">${formatSize(file.size)}</span> <span>•</span> <span>${new Date(file.lastModified).toLocaleDateString('pt-BR')}</span>`;

            info.appendChild(name);
            info.appendChild(meta);

            const remove = document.createElement('button');
            remove.className = 'remove-btn';
            remove.setAttribute('aria-label', 'Remover');
            remove.innerHTML = '<span class="material-symbols-outlined">close</span>';
            remove.addEventListener('click', (e) => {
                e.stopPropagation();
                files.splice(index, 1);
                render();
            });

            item.appendChild(icon);
            item.appendChild(info);
            item.appendChild(remove);
            fileList.appendChild(item);
        });
    }

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('arquivo', file);

        const data = await apiFetch('/documents/upload', {
            method: 'POST',
            body: formData,
        });

        return data; // Retorna o documento criado com id
    }

    async function processDocument(documentId) {
        // 1. OCR
        showAiResult(`
            <div class="ai-loading">
                <div class="spinner"></div>
                <span>Extraindo texto do documento (OCR)...</span>
            </div>
        `);

        try {
            await apiFetch(`/ocr/process/${documentId}`, { method: 'POST' });
        } catch (error) {
            throw new Error(`Falha no OCR: ${error.message}`);
        }

        // 2. Análise de IA
        showAiResult(`
            <div class="ai-loading">
                <div class="spinner"></div>
                <span>Analisando documento com IA...</span>
            </div>
        `);

        try {
            const result = await apiFetch(`/ai/analyze/${documentId}`, { method: 'POST' });
            return result;
        } catch (error) {
            throw new Error(`Falha na análise de IA: ${error.message}`);
        }
    }

    function showAiResult(html) {
        aiResultContent.innerHTML = html;
        aiResultPanel.classList.add('visible');
    }

    function renderAiResult(data) {
        const html = `
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">category</span> Tipo do Documento</div>
                <div class="result-value">${data.tipo_documento || 'Não informado'}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">label</span> Categoria</div>
                <div class="result-value">${data.categoria || 'Não informada'}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">summarize</span> Resumo</div>
                <div class="result-value">${data.resumo || 'Nenhum resumo disponível.'}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">info</span> Informações Principais</div>
                <div class="result-value">${data.informacoes_principais || 'Nenhuma informação disponível.'}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">lightbulb</span> Insights</div>
                <div class="result-value">${data.insights || 'Nenhum insight disponível.'}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">recommend</span> Recomendações</div>
                <div class="result-value">${data.recomendacoes || 'Nenhuma recomendação disponível.'}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">key</span> Palavras-chave</div>
                <div class="result-value">${data.palavras_chave || 'Nenhuma palavra-chave.'}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">warning</span> Alertas</div>
                <div class="result-value highlight">${data.alertas || 'Nenhum alerta.'}</div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">verified</span> Confiança</div>
                <div class="confidence-bar">
                    <div class="bar">
                        <div class="fill" style="width: ${(data.confianca || 0) * 100}%"></div>
                    </div>
                    <span class="value">${((data.confianca || 0) * 100).toFixed(0)}%</span>
                </div>
            </div>
            <div class="result-section">
                <div class="result-label"><span class="material-symbols-outlined">calendar_today</span> Data da Análise</div>
                <div class="result-value">${data.data_processamento ? new Date(data.data_processamento).toLocaleString('pt-BR') : 'Data não disponível'}</div>
            </div>
        `;
        showAiResult(html);
    }

    function showAiError(message) {
        showAiResult(`
            <div class="ai-error">
                <span class="material-symbols-outlined">error</span>
                <span>${message}</span>
            </div>
        `);
    }

    async function addFiles(newFiles) {
        const arr = Array.from(newFiles);
        let added = 0;

        for (const f of arr) {
            const dup = files.some(existing => existing.name === f.name && existing.size === f.size);
            if (!dup) {
                files.push(f);
                added++;
            }
        }

        if (added > 0) {
            render();
            inputBarText.textContent = `${added} arquivo${added > 1 ? 's' : ''} anexado${added > 1 ? 's' : ''}`;
            setTimeout(() => { inputBarText.textContent = 'Anexar arquivo para análise...'; }, 1800);

            // Fazer upload do primeiro arquivo adicionado (ou de todos, um por um)
            for (const file of arr) {
                try {
                    const doc = await uploadFile(file);
                    // Após upload, processar OCR e IA
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

    function openPicker(e) {
        if (e) e.preventDefault();
        fileInput.click();
    }

    attachBtn.addEventListener('click', openPicker);
    inputBar.addEventListener('click', (e) => {
        if (e.target.closest('.attach-btn')) return;
        openPicker(e);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            addFiles(e.target.files);
            fileInput.value = '';
        }
    });

    inputBar.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        inputBar.classList.add('drag-over');
    });
    inputBar.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        inputBar.classList.remove('drag-over');
    });
    inputBar.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        inputBar.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            addFiles(e.dataTransfer.files);
        }
    });

    inputBar.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openPicker();
        }
    });

    closeResultBtn.addEventListener('click', () => {
        aiResultPanel.classList.remove('visible');
    });

    // =============================================
    // 5. MODAL DE PERFIL
    // =============================================
    const profileModalOverlay = document.getElementById('profileModalOverlay');
    const closeProfileModal = document.getElementById('closeProfileModal');
    const profileModalBody = document.getElementById('profileModalBody');
    const logoutModalBtn = document.getElementById('logoutModalBtn');

    async function openProfileModal() {
        profileModalOverlay.classList.add('active');
        profileModalBody.innerHTML = `
            <div class="ai-loading">
                <div class="spinner"></div>
                <span>Carregando perfil...</span>
            </div>
        `;

        try {
            const user = await apiFetch('/auth/me');
            profileModalBody.innerHTML = `
                <div class="profile-field">
                    <label>Nome</label>
                    <span>${user.nome || 'Não informado'}</span>
                </div>
                <div class="profile-field">
                    <label>E-mail</label>
                    <span>${user.email || 'Não informado'}</span>
                </div>
                <div class="profile-field">
                    <label>Tipo de Usuário</label>
                    <span>${user.tipo_usuario || 'Não informado'}</span>
                </div>
                <div class="profile-field">
                    <label>Data de Criação</label>
                    <span>${user.data_criacao ? new Date(user.data_criacao).toLocaleString('pt-BR') : 'Não informada'}</span>
                </div>
            `;
        } catch (error) {
            profileModalBody.innerHTML = `
                <div class="ai-error">
                    <span class="material-symbols-outlined">error</span>
                    <span>Erro ao carregar perfil: ${error.message}</span>
                </div>
            `;
        }
    }

    function closeProfileModalFn() {
        profileModalOverlay.classList.remove('active');
    }

    profileBtn.addEventListener('click', openProfileModal);
    closeProfileModal.addEventListener('click', closeProfileModalFn);
    profileModalOverlay.addEventListener('click', (e) => {
        if (e.target === profileModalOverlay) closeProfileModalFn();
    });

    logoutModalBtn.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        window.location.href = 'index.html';
    });

    // =============================================
    // 6. MODAL DE HISTÓRICO
    // =============================================
    const historyModalOverlay = document.getElementById('historyModalOverlay');
    const closeHistoryModal = document.getElementById('closeHistoryModal');
    const historyModalBody = document.getElementById('historyModalBody');

    async function openHistoryModal() {
        historyModalOverlay.classList.add('active');
        historyModalBody.innerHTML = `
            <div class="ai-loading">
                <div class="spinner"></div>
                <span>Carregando histórico...</span>
            </div>
        `;

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
                const statusLabel = doc.status || 'PENDENTE';
                html += `
                    <div class="history-item" data-doc-id="${doc.id}">
                        <div class="history-item-icon">
                            <span class="material-symbols-outlined">${iconFor(doc.nome_arquivo || 'file')}</span>
                        </div>
                        <div class="history-item-info">
                            <div class="history-item-name">${doc.nome_arquivo || 'Documento sem nome'}</div>
                            <div class="history-item-meta">
                                <span>${doc.tipo_arquivo || 'N/A'}</span>
                                <span>•</span>
                                <span>${doc.tamanho ? formatSize(doc.tamanho) : 'N/A'}</span>
                                <span>•</span>
                                <span>${doc.data_upload ? new Date(doc.data_upload).toLocaleDateString('pt-BR') : 'N/A'}</span>
                            </div>
                        </div>
                        <span class="history-item-status ${statusClass}">${statusLabel}</span>
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
                        showAiError('Este documento ainda não possui uma análise.');
                    }
                });
            });

        } catch (error) {
            historyModalBody.innerHTML = `
                <div class="ai-error">
                    <span class="material-symbols-outlined">error</span>
                    <span>Erro ao carregar histórico: ${error.message}</span>
                </div>
            `;
        }
    }

    function closeHistoryModalFn() {
        historyModalOverlay.classList.remove('active');
    }

    historyBtn.addEventListener('click', openHistoryModal);
    closeHistoryModal.addEventListener('click', closeHistoryModalFn);
    historyModalOverlay.addEventListener('click', (e) => {
        if (e.target === historyModalOverlay) closeHistoryModalFn();
    });

    // Fechar modais com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeProfileModalFn();
            closeHistoryModalFn();
        }
    });

    // =============================================
    // 7. INICIALIZAÇÃO
    // =============================================
    render();

})();