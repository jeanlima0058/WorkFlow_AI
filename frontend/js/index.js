(function() {
  // ============================================
  // 1. FUNDO ANIMADO
  // ============================================
  const bgCanvas = document.querySelector('.bg-canvas');
  const tracks = [{ top: '28%' }, { top: '50%' }, { top: '72%' }];
  const fileIcons = ['description', 'picture_as_pdf', 'image', 'table_chart', 'text_snippet', 'folder_zip', 'insert_drive_file', 'dataset', 'analytics', 'receipt_long', 'article', 'code'];
  const dotColors = ['rgba(30, 92, 179, 0.4)', 'rgba(201, 162, 39, 0.4)', 'rgba(74, 142, 255, 0.4)', 'rgba(219, 185, 61, 0.35)', 'rgba(30, 92, 179, 0.25)'];

  function createTraveler() {
    const lane = tracks[Math.floor(Math.random() * tracks.length)];
    const el = document.createElement('div');
    const isGold = Math.random() > 0.65;
    const sizeClass = ['small', 'medium', 'medium', 'large'][Math.floor(Math.random() * 4)];

    el.className = `traveler ${sizeClass} ${isGold ? 'gold' : ''}`;
    const iconName = fileIcons[Math.floor(Math.random() * fileIcons.length)];
    el.innerHTML = `<span class="material-symbols-outlined">${iconName}</span>`;

    const baseTop = parseFloat(lane.top);
    const variation = (Math.random() - 0.5) * 6;
    el.style.top = `calc(${baseTop}% + ${variation}%)`;
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
    el.style.top = `calc(${baseTop}% + ${variation}%)`;
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

  // ============================================
  // 2. TRANSIÇÃO LOGIN → APP & VALIDAÇÃO
  // ============================================
  const screenLogin = document.getElementById('screenLogin');
  const screenApp = document.getElementById('screenApp');
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
  const logoutBtn = document.getElementById('logoutBtn');
  const appWelcomeTitle = document.getElementById('appWelcomeTitle');

  // Alternar visibilidade da senha
  togglePass.addEventListener('click', (e) => {
    e.preventDefault();
    const isPassword = loginPass.type === 'password';
    loginPass.type = isPassword ? 'text' : 'password';
    togglePassIcon.textContent = isPassword ? 'visibility_off' : 'visibility';
    togglePass.setAttribute('aria-label', isPassword ? 'Ocultar senha' : 'Mostrar senha');
    loginPass.focus();
  });

  // Limpar estado de erro nos inputs ao digitar
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

  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const user = loginUser.value.trim();
    const pass = loginPass.value.trim();

    if (!user) {
      showError('Informe o usuário', loginUser);
      loginUser.focus();
      return;
    }

    if (!pass) {
      showError('Informe a senha', loginPass);
      loginPass.focus();
      return;
    }

    if (pass.length < 4) {
      showError('A senha deve ter pelo menos 4 caracteres', loginPass);
      loginPass.focus();
      return;
    }

    goToApp(user);
  });

  function goToApp(username) {
    loginForm.querySelector('button[type="submit"]').disabled = true;
    screenLogin.classList.add('fading');

    if (appWelcomeTitle && username) {
      appWelcomeTitle.textContent = `Olá, ${username.charAt(0).toUpperCase() + username.slice(1)}`;
    }

    setTimeout(() => {
      screenLogin.classList.add('hidden');
      screenLogin.classList.remove('fading');
      screenApp.classList.remove('hidden');
      
      requestAnimationFrame(() => {
        screenApp.classList.add('visible');
      });

      loginForm.reset();
      loginForm.querySelector('button[type="submit"]').disabled = false;
      errorMsg.classList.remove('show');
    }, 500);
  }

  logoutBtn.addEventListener('click', () => {
    screenApp.classList.remove('visible');

    setTimeout(() => {
      screenApp.classList.add('hidden');
      screenLogin.classList.remove('hidden');
      
      requestAnimationFrame(() => {
        screenLogin.classList.remove('fading');
        loginUser.focus();
      });

      files = [];
      renderFiles();
      inputBarText.textContent = 'Anexar arquivo para análise...';
    }, 500);
  });

  document.getElementById('linkForgot').addEventListener('click', (e) => {
    e.preventDefault();
    showError('Funcionalidade em desenvolvimento');
  });

  document.getElementById('linkRegister').addEventListener('click', (e) => {
    e.preventDefault();
    showError('Cadastro disponível em breve');
  });

  // ============================================
  // 3. UPLOAD DE ARQUIVOS
  // ============================================
  const inputBar = document.getElementById('inputBar');
  const inputBarText = document.getElementById('inputBarText');
  const attachBtn = document.getElementById('attachBtn');
  const fileInput = document.getElementById('fileInput');
  const fileList = document.getElementById('fileList');
  const emptyState = document.getElementById('emptyState');
  const fileCount = document.getElementById('fileCount');

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
      pdf: 'picture_as_pdf',
      doc: 'description', docx: 'description',
      txt: 'text_snippet',
      png: 'image', jpg: 'image', jpeg: 'image', gif: 'image',
      csv: 'table_chart', xlsx: 'table_chart',
      zip: 'folder_zip',
      json: 'data_object',
      xml: 'code',
    };
    return map[ext] || 'insert_drive_file';
  }

  function renderFiles() {
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
      meta.innerHTML = `
        <span class="size-tag">${formatSize(file.size)}</span>
        <span>•</span>
        <span>${new Date(file.lastModified).toLocaleDateString('pt-BR')}</span>
      `;

      info.appendChild(name);
      info.appendChild(meta);

      const remove = document.createElement('button');
      remove.className = 'remove-btn';
      remove.setAttribute('aria-label', 'Remover');
      remove.innerHTML = '<span class="material-symbols-outlined">close</span>';
      remove.addEventListener('click', (e) => {
        e.stopPropagation();
        files.splice(index, 1);
        renderFiles();
      });

      item.appendChild(icon);
      item.appendChild(info);
      item.appendChild(remove);
      fileList.appendChild(item);
    });
  }

  function addFiles(newFiles) {
    const arr = Array.from(newFiles);
    let added = 0;
    arr.forEach(f => {
      const dup = files.some(existing => existing.name === f.name && existing.size === f.size);
      if (!dup) {
        files.push(f);
        added++;
      }
    });
    if (added > 0) {
      renderFiles();
      inputBarText.textContent = `${added} arquivo${added > 1 ? 's' : ''} anexado${added > 1 ? 's' : ''}!`;
      setTimeout(() => { inputBarText.textContent = 'Anexar arquivo para análise...'; }, 1800);
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

  document.addEventListener('dragover', (e) => e.preventDefault());
  document.addEventListener('drop', (e) => e.preventDefault());

  inputBar.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      openPicker();
    }
  });

  window.addEventListener('load', () => {
    setTimeout(() => loginUser.focus(), 400);
  });
})();