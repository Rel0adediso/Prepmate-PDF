// Ödevmatik AI - Frontend Application
document.addEventListener('DOMContentLoaded', () => {
  // App State
  const state = {
    fileId: null,
    fileName: null,
    totalPages: 0,
    selectedPages: [],
    currentPageIndex: 0, // index in selectedPages
    isTwoPageMode: true,
    activePageNum: null,
    pagesData: {}, // { [pageNum]: [ { id, answer, box_2d: [ymin, xmin, ymax, xmax], font_size, explanation } ] }
    pagesStatus: {}, // { [pageNum]: 'idle' | 'solving' | 'done' | 'error' }
    apiKey: localStorage.getItem('gemini_api_key') || '',
    keyCount: 1,
    isDetailedMode: false,
    activeAnnotationEl: null
  };

  // DOM Elements
  const apiKeyBtn = document.getElementById('apiKeyBtn');
  const apiKeyBtnText = document.getElementById('apiKeyBtnText');
  const apiKeyStatusDot = document.getElementById('apiKeyStatusDot');
  const apiKeyModal = document.getElementById('apiKeyModal');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
  const closeApiModalBtn = document.getElementById('closeApiModalBtn');

  // Mode Elements
  const fastModeBtn = document.getElementById('fastModeBtn');
  const detailedModeBtn = document.getElementById('detailedModeBtn');
  const editorFastModeBtn = document.getElementById('editorFastModeBtn');
  const editorDetailedModeBtn = document.getElementById('editorDetailedModeBtn');
  const modeTitle = document.getElementById('modeTitle');
  const modeDesc = document.getElementById('modeDesc');
  const modeBadge = document.getElementById('modeBadge');
  const modeIcon = document.getElementById('modeIcon');

  const uploadSection = document.getElementById('uploadSection');
  const editorSection = document.getElementById('editorSection');
  const dropZone = document.getElementById('dropZone');
  const pdfFileInput = document.getElementById('pdfFileInput');
  const fileMetaCard = document.getElementById('fileMetaCard');
  const fileNameDisplay = document.getElementById('fileNameDisplay');
  const totalPagesDisplay = document.getElementById('totalPagesDisplay');
  const changeFileBtn = document.getElementById('changeFileBtn');
  const pageRangeInput = document.getElementById('pageRangeInput');
  const startSolveBtn = document.getElementById('startSolveBtn');

  const prevPageBtn = document.getElementById('prevPageBtn');
  const nextPageBtn = document.getElementById('nextPageBtn');
  const pageSelectDropdown = document.getElementById('pageSelectDropdown');
  const twoPageViewBtn = document.getElementById('twoPageViewBtn');
  const singlePageViewBtn = document.getElementById('singlePageViewBtn');
  const addTextBoxBtn = document.getElementById('addTextBoxBtn');
  const fontSizeSelect = document.getElementById('fontSizeSelect');
  const reSolveBtn = document.getElementById('reSolveBtn');
  const backToUploadBtn = document.getElementById('backToUploadBtn');
  const exportGroup = document.getElementById('exportGroup');
  const downloadHwBtn = document.getElementById('downloadHwBtn');
  const downloadFullBtn = document.getElementById('downloadFullBtn');

  const leftPageContainer = document.getElementById('leftPageContainer');
  const leftPageImage = document.getElementById('leftPageImage');
  const leftAnnotationsLayer = document.getElementById('leftAnnotationsLayer');

  const rightPageContainer = document.getElementById('rightPageContainer');
  const rightPageImage = document.getElementById('rightPageImage');
  const rightAnnotationsLayer = document.getElementById('rightAnnotationsLayer');

  const pageLoadingOverlay = document.getElementById('pageLoadingOverlay');
  const loadingStatusText = document.getElementById('loadingStatusText');
  const toastNotification = document.getElementById('toastNotification');
  const toastMessage = document.getElementById('toastMessage');

  // Progress Sidebar Elements
  const progressSidebar = document.getElementById('progressSidebar');
  const toggleProgressSidebarBtn = document.getElementById('toggleProgressSidebarBtn');
  const closeProgressSidebarBtn = document.getElementById('closeProgressSidebarBtn');
  const progressSummaryBadge = document.getElementById('progressSummaryBadge');
  const overallPercentBadge = document.getElementById('overallPercentBadge');
  const progressStatusSubtitle = document.getElementById('progressStatusSubtitle');
  const overallProgressBar = document.getElementById('overallProgressBar');
  const completedPagesCount = document.getElementById('completedPagesCount');
  const totalSelectedPagesCount = document.getElementById('totalSelectedPagesCount');
  const progressPagesList = document.getElementById('progressPagesList');

  // Add More Pages Modal Elements
  const addPagesBtn = document.getElementById('addPagesBtn');
  const addPagesSidebarBtn = document.getElementById('addPagesSidebarBtn');
  const addPagesModal = document.getElementById('addPagesModal');
  const closeAddPagesModalBtn = document.getElementById('closeAddPagesModalBtn');
  const cancelAddPagesBtn = document.getElementById('cancelAddPagesBtn');
  const confirmAddPagesBtn = document.getElementById('confirmAddPagesBtn');
  const addPageRangeInput = document.getElementById('addPageRangeInput');
  const currentPagesListDisplay = document.getElementById('currentPagesListDisplay');

  // Initialize Config Check
  checkConfig();

  async function checkConfig() {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      if (data.key_count) state.keyCount = data.key_count;
      if (data.has_env_key && !state.apiKey) {
        state.apiKey = 'ENV_KEY_ACTIVE';
        updateApiKeyUI(true, data.key_type ? `${data.key_type} Aktif` : 'Sistem Anahtarı Aktif');
      } else if (state.apiKey) {
        const keys = state.apiKey.split(/[\r\n,;]+/).map(k => k.trim()).filter(Boolean);
        state.keyCount = keys.length || 1;
        const lbl = keys.length > 1 ? `${keys.length} Hesap / Anahtar` : (state.apiKey.startsWith('sk-or-') ? 'OpenRouter Aktif' : 'Gemini 3.8 Aktif');
        updateApiKeyUI(true, lbl);
      } else {
        updateApiKeyUI(false, 'AI Anahtarı Gir');
      }
    } catch (e) {
      if (state.apiKey) {
        const keys = state.apiKey.split(/[\r\n,;]+/).map(k => k.trim()).filter(Boolean);
        state.keyCount = keys.length || 1;
        const lbl = keys.length > 1 ? `${keys.length} Hesap / Anahtar` : (state.apiKey.startsWith('sk-or-') ? 'OpenRouter Aktif' : 'Gemini 3.8 Aktif');
        updateApiKeyUI(true, lbl);
      }
    }
  }

  function updateApiKeyUI(active, text) {
    apiKeyBtnText.textContent = text;
    apiKeyStatusDot.className = active 
      ? 'w-2 h-2 rounded-full bg-emerald-400' 
      : 'w-2 h-2 rounded-full bg-amber-400';
  }

  function showToast(msg, isError = false) {
    toastMessage.textContent = msg;
    document.getElementById('toastIcon').textContent = isError ? '⚠️' : '✅';
    toastNotification.classList.remove('translate-y-24', 'opacity-0');
    setTimeout(() => {
      toastNotification.classList.add('translate-y-24', 'opacity-0');
    }, 3500);
  }

  // API Key Modal Events
  apiKeyBtn.addEventListener('click', () => {
    apiKeyInput.value = state.apiKey === 'ENV_KEY_ACTIVE' ? '' : state.apiKey;
    apiKeyModal.classList.remove('hidden');
    apiKeyInput.focus();
  });

  closeApiModalBtn.addEventListener('click', () => {
    apiKeyModal.classList.add('hidden');
  });

  saveApiKeyBtn.addEventListener('click', () => {
    const val = apiKeyInput.value.trim();
    if (val) {
      state.apiKey = val;
      localStorage.setItem('gemini_api_key', val);
      const keys = val.split(/[\r\n,;]+/).map(k => k.trim()).filter(Boolean);
      state.keyCount = keys.length || 1;
      const lbl = keys.length > 1 ? `${keys.length} Hesap / Anahtar` : (val.startsWith('sk-or-') ? 'OpenRouter Aktif' : 'Gemini 3.8 Aktif');
      updateApiKeyUI(true, lbl);
      showToast(keys.length > 1 ? `${keys.length} API Anahtarı kaydedildi! Kota doldukça otomatik geçiş yapılacak.` : 'API Anahtarı başarıyla kaydedildi.');
    } else {
      state.apiKey = '';
      state.keyCount = 1;
      localStorage.removeItem('gemini_api_key');
      updateApiKeyUI(false, 'AI Anahtarı Gir');
    }
    apiKeyModal.classList.add('hidden');
  });

  // Mode Selection Logic (Fast vs Detailed)
  function setSolveMode(detailed) {
    state.isDetailedMode = detailed;
    if (detailed) {
      fastModeBtn.className = 'px-2.5 py-1 rounded text-slate-400 hover:text-white transition';
      detailedModeBtn.className = 'px-2.5 py-1 rounded bg-amber-600 text-white font-semibold transition shadow-sm';
      if (editorFastModeBtn) editorFastModeBtn.className = 'px-2 py-0.5 rounded text-slate-400 hover:text-white transition';
      if (editorDetailedModeBtn) editorDetailedModeBtn.className = 'px-2 py-0.5 rounded bg-amber-600 text-white font-semibold transition shadow-sm';
      if (modeIcon) modeIcon.textContent = '💡';
      if (modeTitle) modeTitle.textContent = 'Detaylı / Açıklamalı Mod';
      if (modeBadge) {
        modeBadge.textContent = 'Cevap Mantığı';
        modeBadge.className = 'text-[10px] bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded font-medium';
      }
      if (modeDesc) modeDesc.textContent = 'Cevapların yanında hoca sorarsa diye Türkçe kural/gerekçe açıklamaları eklenir.';
      showToast('Detaylı Mod aktif: Cevap gerekçeleri ve açıklamalar eklenecek.');
    } else {
      fastModeBtn.className = 'px-3 py-1 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold transition shadow-sm';
      detailedModeBtn.className = 'px-3 py-1 rounded-lg text-slate-400 hover:text-white transition';
      if (editorFastModeBtn) editorFastModeBtn.className = 'px-2.5 py-1 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold transition shadow-sm';
      if (editorDetailedModeBtn) editorDetailedModeBtn.className = 'px-2.5 py-1 rounded-lg text-slate-400 hover:text-white transition';
      if (modeIcon) modeIcon.textContent = '⚡';
      if (modeTitle) modeTitle.textContent = 'Hızlı Mod (Önerilen)';
      if (modeBadge) {
        modeBadge.textContent = 'Paralel Çözüm';
        modeBadge.className = 'text-[10px] bg-violet-500/20 text-violet-300 border border-violet-500/30 px-1.5 py-0.5 rounded font-medium';
      }
      if (modeDesc) modeDesc.textContent = 'Doğrudan net cevaplar, maksimum hız ve paralel worker\'lar.';
      showToast('Hızlı Mod aktif: Maksimum hız ve paralel çözüm.');
    }
  }

  if (fastModeBtn) fastModeBtn.addEventListener('click', () => setSolveMode(false));
  if (detailedModeBtn) detailedModeBtn.addEventListener('click', () => setSolveMode(true));
  if (editorFastModeBtn) editorFastModeBtn.addEventListener('click', () => setSolveMode(false));
  if (editorDetailedModeBtn) editorDetailedModeBtn.addEventListener('click', () => setSolveMode(true));

  // Drag & Drop Upload
  dropZone.addEventListener('click', () => pdfFileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-violet-500', 'bg-violet-500/10');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-violet-500', 'bg-violet-500/10');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-violet-500', 'bg-violet-500/10');
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  pdfFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  const demoPdfBtn = document.getElementById('demoPdfBtn');

  changeFileBtn.addEventListener('click', () => {
    dropZone.classList.remove('hidden');
    if (demoPdfBtn) demoPdfBtn.classList.remove('hidden');
    fileMetaCard.classList.add('hidden');
    startSolveBtn.disabled = true;
    pdfFileInput.value = '';
    state.fileId = null;
  });

  if (demoPdfBtn) {
    demoPdfBtn.addEventListener('click', async () => {
      demoPdfBtn.disabled = true;
      demoPdfBtn.innerHTML = '<span>⏳ Örnek PDF Hazırlanıyor...</span>';
      try {
        const res = await fetch('/api/load-sample', { method: 'POST' });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Örnek dosya yüklenemedi');

        state.fileId = data.file_id;
        state.fileName = data.filename;
        state.totalPages = data.total_pages;

        fileNameDisplay.textContent = data.filename;
        totalPagesDisplay.textContent = `Toplam: ${data.total_pages} Sayfa`;

        dropZone.classList.add('hidden');
        demoPdfBtn.classList.add('hidden');
        fileMetaCard.classList.remove('hidden');
        pageRangeInput.value = '1-2';
        startSolveBtn.disabled = false;
        showToast('Örnek ödev yüklendi! "Sayfaları Getir" butonuna basarak deneyebilirsin.');
      } catch (err) {
        showToast(err.message, true);
      } finally {
        demoPdfBtn.disabled = false;
        demoPdfBtn.innerHTML = '<span>🎯 Örnek İngilizce Ödev ile Hemen Dene</span><span class="text-[10px] bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded">Tek Tıkla Başla</span>';
      }
    });
  }

  async function handleFileSelected(file) {
    if (demoPdfBtn) demoPdfBtn.classList.add('hidden');
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      showToast('Lütfen sadece PDF dosyası yükleyin.', true);
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    document.getElementById('dropZoneText').textContent = 'PDF yükleniyor...';

    try {
      const res = await fetch('/api/upload', { method: 'POST', body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Yükleme başarısız');

      state.fileId = data.file_id;
      state.fileName = data.filename;
      state.totalPages = data.total_pages;

      fileNameDisplay.textContent = data.filename;
      totalPagesDisplay.textContent = `Toplam: ${data.total_pages} Sayfa`;

      dropZone.classList.add('hidden');
      fileMetaCard.classList.remove('hidden');
      startSolveBtn.disabled = false;

      if (data.total_pages > 5) {
        pageRangeInput.placeholder = `Örn: 15-20 (Maks: ${data.total_pages})`;
      } else {
        pageRangeInput.value = `1-${data.total_pages}`;
      }

      showToast(`PDF başarıyla yüklendi (${data.total_pages} sayfa)`);
    } catch (err) {
      showToast(err.message, true);
      document.getElementById('dropZoneText').textContent = 'PDF dosyasını buraya sürükleyin veya tıklayıp seçin';
    }
  }

  function parseRangeString(str, max) {
    const pages = new Set();
    const parts = str.split(',').map(s => s.trim()).filter(Boolean);
    for (const part of parts) {
      if (part.includes('-')) {
        const [start, end] = part.split('-').map(n => parseInt(n.trim(), 10));
        if (!isNaN(start) && !isNaN(end)) {
          const s = Math.max(1, Math.min(start, end));
          const e = Math.min(max, Math.max(start, end));
          for (let p = s; p <= e; p++) pages.add(p);
        }
      } else {
        const p = parseInt(part, 10);
        if (!isNaN(p) && p >= 1 && p <= max) pages.add(p);
      }
    }
    return Array.from(pages).sort((a, b) => a - b);
  }

  // View Mode Toggles
  twoPageViewBtn.addEventListener('click', () => {
    state.isTwoPageMode = true;
    twoPageViewBtn.className = 'px-2.5 py-1 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold transition flex items-center gap-1 shadow-sm';
    singlePageViewBtn.className = 'px-2.5 py-1 rounded-lg text-slate-400 hover:text-white font-medium transition flex items-center gap-1';
    rebuildDropdown();
    renderCurrentSpread();
  });

  singlePageViewBtn.addEventListener('click', () => {
    state.isTwoPageMode = false;
    singlePageViewBtn.className = 'px-2.5 py-1 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold transition flex items-center gap-1 shadow-sm';
    twoPageViewBtn.className = 'px-2.5 py-1 rounded-lg text-slate-400 hover:text-white font-medium transition flex items-center gap-1';
    rebuildDropdown();
    renderCurrentSpread();
  });

  // Start Solving
  startSolveBtn.addEventListener('click', () => {
    if (!state.fileId) return;

    if (!state.apiKey) {
      apiKeyModal.classList.remove('hidden');
      showToast('Lütfen önce Gemini API anahtarınızı girin.', true);
      return;
    }

    const rangeStr = pageRangeInput.value.trim() || '1-1';
    const pages = parseRangeString(rangeStr, state.totalPages);

    if (pages.length === 0) {
      showToast(`Lütfen geçerli bir sayfa aralığı girin (1-${state.totalPages})`, true);
      return;
    }

    state.selectedPages = pages;
    state.currentPageIndex = 0;
    state.isTwoPageMode = pages.length > 1;

    if (state.isTwoPageMode) {
      twoPageViewBtn.className = 'px-2.5 py-1 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold transition flex items-center gap-1 shadow-sm';
      singlePageViewBtn.className = 'px-2.5 py-1 rounded-lg text-slate-400 hover:text-white font-medium transition flex items-center gap-1';
    } else {
      singlePageViewBtn.className = 'px-2.5 py-1 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold transition flex items-center gap-1 shadow-sm';
      twoPageViewBtn.className = 'px-2.5 py-1 rounded-lg text-slate-400 hover:text-white font-medium transition flex items-center gap-1';
    }

    uploadSection.classList.add('hidden');
    editorSection.classList.remove('hidden');
    exportGroup.classList.remove('hidden');

    // Initialize progress status for selected pages
    pages.forEach(p => {
      if (!state.pagesStatus[p]) state.pagesStatus[p] = 'idle';
    });
    if (progressSidebar) progressSidebar.classList.remove('collapsed');
    updateProgressSidebarUI();

    rebuildDropdown();
    renderCurrentSpread();

    // Background solve for all selected pages
    solveAllPagesInBackground(pages);
  });

  backToUploadBtn.addEventListener('click', () => {
    editorSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    exportGroup.classList.add('hidden');
  });

  // Add More Pages Modal Handlers (Mevcut listeye sonradan sayfa ekleme)
  function openAddPagesModal() {
    if (!state.fileId) return;
    if (currentPagesListDisplay) {
      if (state.selectedPages.length <= 6) {
        currentPagesListDisplay.textContent = state.selectedPages.join(', ');
      } else {
        currentPagesListDisplay.textContent = `${state.selectedPages[0]}-${state.selectedPages[state.selectedPages.length - 1]} (${state.selectedPages.length} sayfa)`;
      }
    }
    const lastPage = state.selectedPages[state.selectedPages.length - 1] || 1;
    const nextStart = Math.min(state.totalPages, lastPage + 1);
    const nextEnd = Math.min(state.totalPages, nextStart + 4);
    if (addPageRangeInput) {
      addPageRangeInput.placeholder = `Örn: ${nextStart}-${nextEnd} (Maks: ${state.totalPages})`;
      addPageRangeInput.value = '';
    }
    if (addPagesModal) addPagesModal.classList.remove('hidden');
    if (addPageRangeInput) addPageRangeInput.focus();
  }

  function closeAddPagesModal() {
    if (addPagesModal) addPagesModal.classList.add('hidden');
  }

  if (addPagesBtn) addPagesBtn.addEventListener('click', openAddPagesModal);
  if (addPagesSidebarBtn) addPagesSidebarBtn.addEventListener('click', openAddPagesModal);
  if (closeAddPagesModalBtn) closeAddPagesModalBtn.addEventListener('click', closeAddPagesModal);
  if (cancelAddPagesBtn) cancelAddPagesBtn.addEventListener('click', closeAddPagesModal);

  if (confirmAddPagesBtn) {
    confirmAddPagesBtn.addEventListener('click', () => {
      const val = addPageRangeInput.value.trim();
      if (!val) {
        showToast('Lütfen eklenecek sayfa aralığını girin.', true);
        return;
      }
      const parsed = parseRangeString(val, state.totalPages);
      if (parsed.length === 0) {
        showToast(`Geçerli bir sayfa aralığı girin (1-${state.totalPages})`, true);
        return;
      }

      const newPagesToAdd = parsed.filter(p => !state.selectedPages.includes(p));
      if (newPagesToAdd.length === 0) {
        showToast('Belirttiğiniz sayfalar zaten mevcut listede bulunuyor.', true);
        return;
      }

      // Merge and sort selected pages
      state.selectedPages = Array.from(new Set([...state.selectedPages, ...newPagesToAdd])).sort((a, b) => a - b);

      // Initialize status for new pages
      newPagesToAdd.forEach(p => {
        state.pagesStatus[p] = 'idle';
      });

      closeAddPagesModal();
      rebuildDropdown();
      updateProgressSidebarUI();

      showToast(`${newPagesToAdd.length} yeni sayfa eklendi ve çözülüyor: ${newPagesToAdd.join(', ')}`);

      // Solve only the newly added pages in background!
      solveAllPagesInBackground(newPagesToAdd);
    });
  }

  function rebuildDropdown() {
    pageSelectDropdown.innerHTML = '';
    const step = state.isTwoPageMode ? 2 : 1;

    for (let i = 0; i < state.selectedPages.length; i += step) {
      const opt = document.createElement('option');
      opt.value = i;
      if (state.isTwoPageMode && i + 1 < state.selectedPages.length) {
        opt.textContent = `${state.selectedPages[i]} - ${state.selectedPages[i + 1]}`;
      } else {
        opt.textContent = `${state.selectedPages[i]}`;
      }
      pageSelectDropdown.appendChild(opt);
    }
  }

  // Render Current Spread (1 or 2 pages)
  function renderCurrentSpread() {
    const leftIndex = state.currentPageIndex;
    const leftPage = state.selectedPages[leftIndex];
    state.activePageNum = leftPage;

    // Update Dropdown Selection
    const step = state.isTwoPageMode ? 2 : 1;
    const dropdownVal = Math.floor(leftIndex / step) * step;
    pageSelectDropdown.value = dropdownVal;

    // Prev / Next button state
    prevPageBtn.disabled = leftIndex <= 0;
    if (state.isTwoPageMode) {
      nextPageBtn.disabled = leftIndex + 2 >= state.selectedPages.length && leftIndex + 1 >= state.selectedPages.length;
    } else {
      nextPageBtn.disabled = leftIndex + 1 >= state.selectedPages.length;
    }

    // Render Left Page
    renderSinglePageContainer(leftPage, leftPageContainer, leftPageImage, leftAnnotationsLayer);

    // Render Right Page if 2-page mode
    const rightIndex = leftIndex + 1;
    if (state.isTwoPageMode && rightIndex < state.selectedPages.length) {
      const rightPage = state.selectedPages[rightIndex];
      rightPageContainer.classList.remove('hidden');
      leftPageContainer.classList.remove('single-mode');
      renderSinglePageContainer(rightPage, rightPageContainer, rightPageImage, rightAnnotationsLayer);
    } else {
      rightPageContainer.classList.add('hidden');
      leftPageContainer.classList.add('single-mode');
    }

    // Refresh progress sidebar active spread indicator
    updateProgressSidebarUI();
  }

  function syncContainerDimensions(containerEl, imgEl) {
    if (imgEl.naturalWidth && imgEl.naturalHeight) {
      const ratio = imgEl.naturalWidth / imgEl.naturalHeight;
      const h = containerEl.clientHeight || (window.innerHeight - 120);
      containerEl.style.width = `${Math.round(h * ratio)}px`;
    }
  }

  function renderSinglePageContainer(pageNum, containerEl, imgEl, layerEl) {
    layerEl.innerHTML = '';

    imgEl.onload = () => {
      syncContainerDimensions(containerEl, imgEl);
      if (state.pagesData[pageNum]) {
        renderAnnotationsForPage(pageNum, layerEl, containerEl);
      }
    };

    imgEl.src = `/api/page-image/${state.fileId}/${pageNum}`;

    containerEl.onclick = () => {
      state.activePageNum = pageNum;
    };

    if (state.pagesData[pageNum]) {
      syncContainerDimensions(containerEl, imgEl);
      renderAnnotationsForPage(pageNum, layerEl, containerEl);
    } else {
      solveSinglePage(pageNum);
    }
  }

  window.addEventListener('resize', () => {
    syncContainerDimensions(leftPageContainer, leftPageImage);
    if (state.isTwoPageMode && !rightPageContainer.classList.contains('hidden')) {
      syncContainerDimensions(rightPageContainer, rightPageImage);
    }
  });

  // Background Solver with Concurrent Worker Pool
  async function solveAllPagesInBackground(pages) {
    const queue = pages.filter(p => !state.pagesData[p] && state.pagesStatus[p] !== 'solving');
    if (queue.length === 0) return;

    // Concurrency: 3 parallel workers per API key (e.g. 2 keys = 6 parallel workers!)
    const keyMultiplier = Math.max(1, state.keyCount || 1);
    const concurrency = Math.min(queue.length, Math.max(3, keyMultiplier * 3));
    let index = 0;

    async function worker() {
      while (index < queue.length) {
        const pageNum = queue[index++];
        await solveSinglePage(pageNum);
      }
    }

    const workers = Array.from({ length: concurrency }, () => worker());
    await Promise.all(workers);
  }

  async function solveSinglePage(pageNum) {
    if (state.pagesStatus[pageNum] === 'solving') return;
    state.pagesStatus[pageNum] = 'solving';
    updateProgressSidebarUI();

    // Arka planda çözerken ekranı karartıp kullanıcıyı engellemiyoruz!
    // Kullanıcı sayfaları serbestçe gezebilir; sayfa hazır olunca cevaplar anında oturur.

    try {
      const res = await fetch('/api/solve-page', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: state.fileId,
          page_num: pageNum,
          api_key: state.apiKey === 'ENV_KEY_ACTIVE' ? '' : state.apiKey,
          detailed: !!state.isDetailedMode
        })
      });

      let data;
      const text = await res.text();
      try {
        data = JSON.parse(text);
      } catch (e) {
        throw new Error(text || `Sunucu yanıt veremedi (HTTP ${res.status})`);
      }

      if (!res.ok) throw new Error(data.detail || `Sayfa çözülemedi (HTTP ${res.status})`);

      state.pagesData[pageNum] = data.annotations || [];
      state.pagesStatus[pageNum] = 'done';
      updateProgressSidebarUI();

      // Re-render if visible
      if (pageNum === state.selectedPages[state.currentPageIndex]) {
        renderAnnotationsForPage(pageNum, leftAnnotationsLayer, leftPageContainer);
      } else if (state.isTwoPageMode && pageNum === state.selectedPages[state.currentPageIndex + 1]) {
        renderAnnotationsForPage(pageNum, rightAnnotationsLayer, rightPageContainer);
      }

      showToast(`Sayfa ${pageNum} başarıyla çözüldü!`);
    } catch (err) {
      state.pagesStatus[pageNum] = 'error';
      updateProgressSidebarUI();
      showToast(`Sayfa ${pageNum}: ${err.message}`, true);
    } finally {
      pageLoadingOverlay.classList.add('hidden');
      updateProgressSidebarUI();
    }
  }

  // Progress Sidebar UI Controller
  function updateProgressSidebarUI() {
    if (!state.selectedPages || state.selectedPages.length === 0) return;

    const total = state.selectedPages.length;
    let completed = 0;
    let solvingCount = 0;
    let errorCount = 0;

    state.selectedPages.forEach(p => {
      const st = state.pagesStatus[p];
      if (st === 'done') completed++;
      else if (st === 'solving') solvingCount++;
      else if (st === 'error') errorCount++;
    });

    const percent = Math.round((completed / total) * 100);
    if (overallProgressBar) overallProgressBar.style.width = `${percent}%`;
    if (overallPercentBadge) overallPercentBadge.textContent = `${percent}%`;
    if (completedPagesCount) completedPagesCount.textContent = `${completed} tamamlandı`;
    if (totalSelectedPagesCount) totalSelectedPagesCount.textContent = `${total} sayfa`;
    if (progressSummaryBadge) progressSummaryBadge.textContent = `${completed}/${total}`;

    if (progressStatusSubtitle) {
      if (solvingCount > 0) {
        progressStatusSubtitle.textContent = `Yapay zeka çözüyor... (${completed}/${total})`;
      } else if (completed === total) {
        progressStatusSubtitle.textContent = `Tüm ödev sayfaları hazır! 🎉`;
      } else if (errorCount > 0) {
        progressStatusSubtitle.textContent = `${errorCount} sayfada hata oluştu`;
      } else {
        progressStatusSubtitle.textContent = `${completed}/${total} sayfa hazır`;
      }
    }

    if (!progressPagesList) return;
    progressPagesList.innerHTML = '';

    const currentLeft = state.selectedPages[state.currentPageIndex];
    const currentRight = state.isTwoPageMode ? state.selectedPages[state.currentPageIndex + 1] : null;

    state.selectedPages.forEach(p => {
      const status = state.pagesStatus[p] || 'idle';
      const annotations = state.pagesData[p] || [];
      const isVisible = p === currentLeft || p === currentRight;

      const card = document.createElement('div');
      card.className = `progress-page-card bg-white/[0.03] hover:bg-white/[0.07] border border-white/10 rounded-2xl p-3 cursor-pointer transition-all duration-200 flex items-center justify-between group ${isVisible ? 'active-spread ring-1 ring-violet-500/50 bg-violet-500/10' : ''}`;
      card.dataset.page = p;

      let badgeHtml = '';
      let statusDesc = '';

      if (status === 'done') {
        badgeHtml = `<div class="w-7 h-7 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-sm shrink-0 shadow-sm">✓</div>`;
        statusDesc = `<span class="text-emerald-400 font-medium">${annotations.length} boşluk dolduruldu</span>`;
      } else if (status === 'solving') {
        badgeHtml = `<div class="w-7 h-7 rounded-xl bg-violet-500/20 text-violet-400 border border-violet-500/30 flex items-center justify-center shrink-0 shadow-sm"><div class="w-3.5 h-3.5 border-2 border-violet-400 border-t-transparent rounded-full animate-spin"></div></div>`;
        statusDesc = `<span class="text-violet-300 font-medium animate-pulse">Çözülüyor...</span>`;
      } else if (status === 'error') {
        badgeHtml = `<div class="w-7 h-7 rounded-xl bg-red-500/20 text-red-400 border border-red-500/30 flex items-center justify-center font-bold text-sm shrink-0">✕</div>`;
        statusDesc = `<span class="text-red-400 font-medium">Hata oluştu</span>`;
      } else {
        badgeHtml = `<div class="w-7 h-7 rounded-xl bg-white/[0.05] text-slate-400 border border-white/10 flex items-center justify-center font-bold text-xs shrink-0">⏱</div>`;
        statusDesc = `<span class="text-slate-400">Sırada bekliyor</span>`;
      }

      card.innerHTML = `
        <div class="flex items-center space-x-3 overflow-hidden">
          ${badgeHtml}
          <div class="truncate">
            <div class="text-xs font-semibold text-white flex items-center gap-1.5">
              <span>Sayfa ${p}</span>
              ${isVisible ? '<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-violet-500/20 text-violet-300 font-semibold border border-violet-500/30">Açık</span>' : ''}
            </div>
            <div class="text-[11px] truncate mt-0.5">${statusDesc}</div>
          </div>
        </div>
        <button class="resolve-card-btn opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-white/[0.08] text-slate-400 hover:text-amber-400 transition" title="Yeniden Çöz">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
        </button>
      `;

      card.addEventListener('click', (e) => {
        if (e.target.closest('.resolve-card-btn')) return;
        const targetIdx = state.selectedPages.indexOf(p);
        const step = state.isTwoPageMode ? 2 : 1;
        state.currentPageIndex = Math.floor(targetIdx / step) * step;
        state.activePageNum = p;
        renderCurrentSpread();
      });

      const reSolveCardBtn = card.querySelector('.resolve-card-btn');
      if (reSolveCardBtn) {
        reSolveCardBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          state.pagesData[p] = null;
          solveSinglePage(p);
        });
      }

      progressPagesList.appendChild(card);
    });
  }

  // Sidebar Open / Close Toggle Buttons
  if (toggleProgressSidebarBtn) {
    toggleProgressSidebarBtn.addEventListener('click', () => {
      progressSidebar.classList.toggle('collapsed');
      setTimeout(() => {
        syncContainerDimensions(leftPageContainer, leftPageImage);
        if (state.isTwoPageMode && !rightPageContainer.classList.contains('hidden')) {
          syncContainerDimensions(rightPageContainer, rightPageImage);
        }
      }, 320);
    });
  }

  if (closeProgressSidebarBtn) {
    closeProgressSidebarBtn.addEventListener('click', () => {
      progressSidebar.classList.add('collapsed');
      setTimeout(() => {
        syncContainerDimensions(leftPageContainer, leftPageImage);
        if (state.isTwoPageMode && !rightPageContainer.classList.contains('hidden')) {
          syncContainerDimensions(rightPageContainer, rightPageImage);
        }
      }, 320);
    });
  }

  reSolveBtn.addEventListener('click', () => {
    if (confirm(`Sayfa ${state.activePageNum} tekrar çözülsün mü?`)) {
      state.pagesData[state.activePageNum] = null;
      solveSinglePage(state.activePageNum);
    }
  });

  prevPageBtn.addEventListener('click', () => {
    const step = state.isTwoPageMode ? 2 : 1;
    state.currentPageIndex = Math.max(0, state.currentPageIndex - step);
    renderCurrentSpread();
  });

  nextPageBtn.addEventListener('click', () => {
    const step = state.isTwoPageMode ? 2 : 1;
    if (state.currentPageIndex + step < state.selectedPages.length) {
      state.currentPageIndex += step;
      renderCurrentSpread();
    }
  });

  pageSelectDropdown.addEventListener('change', (e) => {
    state.currentPageIndex = parseInt(e.target.value, 10);
    renderCurrentSpread();
  });

  // Render Annotations
  function renderAnnotationsForPage(pageNum, layerEl, containerEl) {
    layerEl.innerHTML = '';
    const annotations = state.pagesData[pageNum] || [];

    annotations.forEach((item, index) => {
      createAnnotationElement(item, index, pageNum, layerEl, containerEl);
    });
  }

  function attachExplanationTooltip(targetEl, explanation) {
    if (!explanation) return;
    const pill = document.createElement('div');
    pill.className = 'explanation-pill';
    pill.title = 'Hoca sorarsa: Açıklamayı gör';
    pill.textContent = '💡';
    const tip = document.createElement('div');
    tip.className = 'explanation-tooltip';
    tip.innerHTML = `
      <div class="tooltip-header">💡 Hoca Sorarsa / Neden?</div>
      <div class="tooltip-body">${escapeHtml(explanation)}</div>
    `;
    targetEl.appendChild(pill);
    targetEl.appendChild(tip);
  }

  function createAnnotationElement(item, index, pageNum, layerEl, containerEl) {
    const [ymin, xmin, ymax, xmax] = item.box_2d || [100, 100, 150, 300];

    const el = document.createElement('div');
    el.dataset.id = item.id || index;
    el.dataset.page = pageNum;

    if (item.type === 'highlight') {
      el.className = 'acrobat-highlight-annotation';
      el.style.left = `${(xmin / 10).toFixed(2)}%`;
      el.style.top = `${(ymin / 10).toFixed(2)}%`;
      el.style.width = `${((xmax - xmin) / 10).toFixed(2)}%`;
      el.style.height = `${((ymax - ymin) / 10).toFixed(2)}%`;
      el.title = item.answer || 'Vurgulanan Seçenek';

      el.innerHTML = `
        <div class="delete-btn" title="Kaldır">&times;</div>
      `;

      el.querySelector('.delete-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        el.remove();
        const list = state.pagesData[pageNum] || [];
        state.pagesData[pageNum] = list.filter(a => a !== item);
      });

      el.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('delete-btn')) return;
        document.querySelectorAll('.acrobat-annotation, .acrobat-highlight-annotation').forEach(a => a.classList.remove('active'));
        el.classList.add('active');
        state.activeAnnotationEl = el;
        state.activePageNum = pageNum;
      });

      attachExplanationTooltip(el, item.explanation);
      makeDraggable(el, item, containerEl);
      layerEl.appendChild(el);
      return;
    }

    if (item.type === 'correction') {
      el.className = 'acrobat-correction-annotation';
      el.style.left = `${(xmin / 10).toFixed(2)}%`;
      el.style.top = `${(ymin / 10).toFixed(2)}%`;
      el.style.width = `${((xmax - xmin) / 10).toFixed(2)}%`;
      el.style.height = `${((ymax - ymin) / 10).toFixed(2)}%`;
      el.title = `Hata: ${item.wrong_word || ''} -> Düzeltme: ${item.answer || ''}`;

      el.innerHTML = `
        <div class="delete-btn" title="Kaldır">&times;</div>
        <div class="strike-line"></div>
        <div class="correction-text" contenteditable="true" spellcheck="false">${escapeHtml(item.answer || '')}</div>
      `;

      const textEl = el.querySelector('.correction-text');
      textEl.addEventListener('input', () => {
        item.answer = textEl.innerText.trim();
      });

      el.querySelector('.delete-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        el.remove();
        const list = state.pagesData[pageNum] || [];
        state.pagesData[pageNum] = list.filter(a => a !== item);
      });

      el.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('correction-text') && document.activeElement === e.target) return;
        if (e.target.classList.contains('delete-btn')) return;
        document.querySelectorAll('.acrobat-annotation, .acrobat-highlight-annotation, .acrobat-correction-annotation').forEach(a => a.classList.remove('active'));
        el.classList.add('active');
        state.activeAnnotationEl = el;
        state.activePageNum = pageNum;
      });

      attachExplanationTooltip(el, item.explanation);
      makeDraggable(el, item, containerEl);
      layerEl.appendChild(el);
      return;
    }

    el.className = 'acrobat-annotation';

    // Snug inline positioning: matches exact vector baseline and left alignment
    el.style.left = `${(xmin / 10).toFixed(2)}%`;
    el.style.top = `${(ymin / 10).toFixed(2)}%`;
    
    const boxWidthNorm = (xmax - xmin) / 10;
    if (boxWidthNorm > 20) {
      el.style.maxWidth = `${Math.min(96, (boxWidthNorm * 1.05)).toFixed(2)}%`;
      el.style.width = 'auto';
    } else {
      el.style.minWidth = `${Math.max(25, boxWidthNorm * 6)}px`;
    }
    el.style.fontSize = `${item.font_size || 11}pt`;

    el.innerHTML = `
      <div class="delete-btn" title="Kaldır">&times;</div>
      <div class="text-content" contenteditable="true" spellcheck="false">${escapeHtml(item.answer || '')}</div>
    `;

    const textEl = el.querySelector('.text-content');
    textEl.addEventListener('input', () => {
      item.answer = textEl.innerText.trim();
    });

    el.querySelector('.delete-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      el.remove();
      const list = state.pagesData[pageNum] || [];
      state.pagesData[pageNum] = list.filter(a => a !== item);
    });

    el.addEventListener('mousedown', (e) => {
      if (e.target.classList.contains('delete-btn')) return;
      document.querySelectorAll('.acrobat-annotation, .acrobat-highlight-annotation, .acrobat-correction-annotation').forEach(a => a.classList.remove('active'));
      el.classList.add('active');
      state.activeAnnotationEl = el;
      state.activePageNum = pageNum;
      fontSizeSelect.value = item.font_size || 11;
    });

    attachExplanationTooltip(el, item.explanation);
    makeDraggable(el, item, containerEl);
    layerEl.appendChild(el);
  }

  function makeDraggable(el, item, containerEl) {
    let isDragging = false;
    let startX = 0, startY = 0;
    let initialLeft = 0, initialTop = 0;

    el.addEventListener('mousedown', (e) => {
      if (e.target.classList.contains('text-content') && document.activeElement === e.target) {
        return;
      }
      if (e.target.classList.contains('delete-btn')) return;
      if (e.target.classList.contains('explanation-pill') || e.target.closest('.explanation-tooltip')) return;

      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;

      const rect = el.getBoundingClientRect();
      const parentRect = containerEl.getBoundingClientRect();

      initialLeft = ((rect.left - parentRect.left) / parentRect.width) * 1000;
      initialTop = ((rect.top - parentRect.top) / parentRect.height) * 1000;

      const onMouseMove = (ev) => {
        if (!isDragging) return;
        const dx = ev.clientX - startX;
        const dy = ev.clientY - startY;

        const deltaNormX = (dx / parentRect.width) * 1000;
        const deltaNormY = (dy / parentRect.height) * 1000;

        const newX = Math.max(0, Math.min(960, initialLeft + deltaNormX));
        const newY = Math.max(0, Math.min(980, initialTop + deltaNormY));

        el.style.left = `${(newX / 10).toFixed(2)}%`;
        el.style.top = `${(newY / 10).toFixed(2)}%`;

        const boxWidth = item.box_2d[3] - item.box_2d[1];
        const boxHeight = item.box_2d[2] - item.box_2d[0];
        item.box_2d = [
          Math.round(newY),
          Math.round(newX),
          Math.round(newY + boxHeight),
          Math.round(newX + boxWidth)
        ];
      };

      const onMouseUp = () => {
        isDragging = false;
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
      };

      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    });
  }

  // Add Custom Text Box Tool
  addTextBoxBtn.addEventListener('click', () => {
    const pageNum = state.activePageNum || state.selectedPages[state.currentPageIndex];
    if (!pageNum) return;

    const newItem = {
      id: Date.now(),
      answer: 'Metin',
      box_2d: [150, 400, 180, 550],
      font_size: parseInt(fontSizeSelect.value, 10) || 11
    };

    if (!state.pagesData[pageNum]) state.pagesData[pageNum] = [];
    state.pagesData[pageNum].push(newItem);

    const isLeft = pageNum === state.selectedPages[state.currentPageIndex];
    const targetLayer = isLeft ? leftAnnotationsLayer : rightAnnotationsLayer;
    const targetContainer = isLeft ? leftPageContainer : rightPageContainer;

    createAnnotationElement(newItem, state.pagesData[pageNum].length - 1, pageNum, targetLayer, targetContainer);
    showToast(`Sayfa ${pageNum}'e yeni metin kutusu eklendi.`);
  });

  // Font Size Change Event
  fontSizeSelect.addEventListener('change', () => {
    const newSize = parseInt(fontSizeSelect.value, 10);
    if (state.activeAnnotationEl) {
      state.activeAnnotationEl.style.fontSize = `${newSize}pt`;
      const id = state.activeAnnotationEl.dataset.id;
      const pageNum = state.activeAnnotationEl.dataset.page;
      const list = state.pagesData[pageNum] || [];
      const target = list.find(x => String(x.id) === String(id));
      if (target) target.font_size = newSize;
    }
  });

  // Export Buttons
  downloadHwBtn.addEventListener('click', () => triggerExport('only_homework'));
  downloadFullBtn.addEventListener('click', () => triggerExport('full_book'));

  async function triggerExport(mode) {
    if (!state.fileId) return;

    const btn = mode === 'only_homework' ? downloadHwBtn : downloadFullBtn;
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span class="animate-spin mr-1">⏳</span> Hazırlanıyor...`;
    btn.disabled = true;

    try {
      const res = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: state.fileId,
          mode: mode,
          selected_pages: state.selectedPages,
          pages_annotations: state.pagesData
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Dışa aktarma başarısız');

      const link = document.createElement('a');
      link.href = data.download_url;
      link.download = data.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      showToast(`PDF başarıyla indirildi: ${data.filename}`);
    } catch (err) {
      showToast(err.message, true);
    } finally {
      btn.innerHTML = originalText;
      btn.disabled = false;
    }
  }

  // Desktop Keyboard Shortcuts (← / → for page navigation, Del to delete annotation)
  document.addEventListener('keydown', (e) => {
    const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) ||
      document.activeElement.isContentEditable;

    if (e.key === 'Escape') {
      if (state.activeAnnotationEl) {
        state.activeAnnotationEl.classList.remove('active');
        state.activeAnnotationEl = null;
      }
      apiKeyModal?.classList.add('hidden');
      return;
    }

    if (isTyping) return;

    if (e.key === 'ArrowLeft' && !editorSection.classList.contains('hidden')) {
      e.preventDefault();
      prevPageBtn.click();
    } else if (e.key === 'ArrowRight' && !editorSection.classList.contains('hidden')) {
      e.preventDefault();
      nextPageBtn.click();
    } else if ((e.key === 'Delete' || e.key === 'Backspace') && state.activeAnnotationEl) {
      e.preventDefault();
      const deleteBtn = state.activeAnnotationEl.querySelector('.delete-btn');
      if (deleteBtn) deleteBtn.click();
    }
  });

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
  }
});
