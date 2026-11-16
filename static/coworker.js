/**
 * PrepMate PDF - Co-Worker Study Partner Agent & Heatmap Frontend Module
 */

(function () {
  const coworkerState = {
    isOpen: false,
    hasAutoOpened: false,
    activeMode: 'co_worker', // 'co_worker', 'socratic', 'quiz', 'feynman'
    activePageNum: 1,
    messages: [],
    isStreaming: false,
    heatmapData: {}
  };

  // DOM Elements cache
  let els = {};

  function initElements() {
    els = {
      sidebar: document.getElementById('coworkerSidebar'),
      toggleBtn: document.getElementById('toggleCoworkerBtn'),
      closeBtn: document.getElementById('closeCoworkerBtn'),
      messagesContainer: document.getElementById('coworkerMessages'),
      input: document.getElementById('coworkerInput'),
      sendBtn: document.getElementById('coworkerSendBtn'),
      pageBadge: document.getElementById('coworkerPageBadge'),
      heatBadge: document.getElementById('coworkerHeatBadge'),
      modePills: document.querySelectorAll('.coworker-mode-pill'),
      quickChips: document.querySelectorAll('.coworker-quick-chip'),
      clearBtn: document.getElementById('clearCoworkerChatBtn'),
      typingIndicator: document.getElementById('coworkerTypingIndicator')
    };
  }

  function sanitizeHtml(raw) {
    if (!raw) return '';
    return raw
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
      .replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '')
      .replace(/<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi, '')
      .replace(/on\w+\s*=\s*(["'])[\s\S]*?\1/gi, ''); // remove inline event handlers like onerror, onload
  }

  function renderMarkdown(text) {
    if (!text) return '';
    const clean = sanitizeHtml(text);
    if (window.marked && typeof window.marked.parse === 'function') {
      try {
        return window.marked.parse(clean);
      } catch (e) {
        // Fallback below
      }
    }
    // Safe lightweight fallback
    return clean
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code class="bg-[#171614] px-1 py-0.5 rounded text-[#e58f74] font-mono text-[11px]">$1</code>');
  }

  function appendMessage(role, text) {
    if (!els.messagesContainer) return null;

    const isUser = role === 'user';
    const wrapper = document.createElement('div');
    wrapper.className = `flex gap-2.5 ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`;

    const avatar = isUser ? '' : `
      <div class="w-6 h-6 rounded-lg bg-[#cc785c]/25 border border-[#cc785c]/40 text-[#e58f74] flex items-center justify-center text-xs shrink-0 select-none mt-1">
        🤖
      </div>
    `;

    const bubble = document.createElement('div');
    bubble.className = isUser
      ? 'max-w-[85%] bg-[#cc785c] text-white px-3.5 py-2.5 rounded-2xl rounded-tr-none text-xs leading-relaxed shadow-md break-words'
      : 'max-w-[85%] bg-[#24221f] text-[#ece8e1] border border-[#383530] px-3.5 py-2.5 rounded-2xl rounded-tl-none text-xs leading-relaxed shadow-sm break-words coworker-markdown-body';

    bubble.innerHTML = renderMarkdown(text);

    if (isUser) {
      wrapper.appendChild(bubble);
    } else {
      wrapper.innerHTML = avatar;
      wrapper.appendChild(bubble);
    }

    els.messagesContainer.appendChild(wrapper);
    els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
    return bubble;
  }

  async function fetchHeatmap() {
    const fileId = window.state ? window.state.fileId : null;
    if (!fileId) return;
    try {
      const resp = await fetch(`/api/study-heatmap/${fileId}`);
      if (resp.ok) {
        coworkerState.heatmapData = await resp.json();
        updateHeatmapBadge();
      }
    } catch (e) {
      console.warn('[CoWorker] Heatmap fetch error:', e);
    }
  }

  function updateHeatmapBadge() {
    if (!els.heatBadge) return;
    const pKey = String(coworkerState.activePageNum || 1);
    const pData = coworkerState.heatmapData[pKey];

    if (!pData || pData.questions === 0) {
      els.heatBadge.className = 'px-1.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold';
      els.heatBadge.textContent = '🟢 Sakin';
      els.heatBadge.title = 'Bu sayfada henüz soru sorulmadı.';
    } else if (pData.questions < 3) {
      els.heatBadge.className = 'px-1.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30 text-[10px] font-mono font-bold';
      els.heatBadge.textContent = `🟡 ${pData.questions} Soru`;
      els.heatBadge.title = `Bu sayfada ${pData.questions} soru tartışıldı.`;
    } else {
      els.heatBadge.className = 'px-1.5 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/40 text-[10px] font-mono font-bold animate-pulse';
      els.heatBadge.textContent = `🔥 ${pData.questions} Soru`;
      els.heatBadge.title = `Zorlu sayfa! Toplam ${pData.questions} soru soruldu.`;
    }
  }

  function setMode(newMode) {
    coworkerState.activeMode = newMode;
    els.modePills.forEach(pill => {
      const m = pill.dataset.mode;
      if (m === newMode) {
        pill.classList.remove('bg-[#24221f]', 'text-[#a39e97]', 'border-[#383530]');
        pill.classList.add('bg-[#cc785c]', 'text-white', 'border-[#cc785c]', 'font-bold');
      } else {
        pill.classList.add('bg-[#24221f]', 'text-[#a39e97]', 'border-[#383530]');
        pill.classList.remove('bg-[#cc785c]', 'text-white', 'border-[#cc785c]', 'font-bold');
      }
    });

    const modeLabels = {
      co_worker: '🤝 Partner Modu: Yan yana serbest çalışma & soru-cevap.',
      socratic: '💡 Sokratik Mod: Cevap yerine ipuçları ve yönlendirici sorular.',
      quiz: '🎯 Quiz Modu: Sayfadan sana özel 3 soruluk pratik test.',
      feynman: '🔄 Feynman Modu: Sen öğrenciye anlatır gibi konuyu bana anlat.'
    };
    appendMessage('agent', `*${modeLabels[newMode] || 'Mod güncellendi.'}*`);
  }

  async function sendChatMessage(promptText) {
    const text = (promptText || (els.input ? els.input.value : '')).trim();
    if (!text || coworkerState.isStreaming) return;

    if (els.input) els.input.value = '';

    // Record user message
    coworkerState.messages.push({ role: 'user', content: text });
    appendMessage('user', text);

    // Prepare agent stream container
    const agentBubble = appendMessage('agent', '...');
    if (els.typingIndicator) els.typingIndicator.classList.remove('hidden');
    coworkerState.isStreaming = true;

    const fileId = window.state ? window.state.fileId : 'sample_prep';
    const activePage = coworkerState.activePageNum || (window.state ? window.state.activePageNum : 1) || 1;
    const apiKey = (window.state && window.state.apiKey) ? window.state.apiKey : '';

    let accumulatedResponse = '';

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: fileId,
          page_num: activePage,
          messages: coworkerState.messages,
          mode: coworkerState.activeMode,
          api_key: apiKey
        })
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `Sunucu yanıtı başarısız (${response.status})`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // keep last incomplete line

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data: ')) continue;
          const dataStr = trimmed.slice(6);
          if (dataStr === '[DONE]') break;

          try {
            const parsed = JSON.parse(dataStr);
            if (parsed.text) {
              accumulatedResponse += parsed.text;
              if (agentBubble) {
                agentBubble.innerHTML = renderMarkdown(accumulatedResponse);
                els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
              }
            } else if (parsed.error) {
              accumulatedResponse += `\n\n*(Hata: ${parsed.error})*`;
              if (agentBubble) agentBubble.innerHTML = renderMarkdown(accumulatedResponse);
            }
          } catch (e) {
            // non-json text chunk
          }
        }
      }

      coworkerState.messages.push({ role: 'model', content: accumulatedResponse });

      // Refresh heatmap stats
      fetchHeatmap();

    } catch (err) {
      if (agentBubble) {
        agentBubble.innerHTML = `<span class="text-rose-400 font-medium">⚠️ Bir sorun oluştu: ${err.message}</span>`;
      }
    } finally {
      coworkerState.isStreaming = false;
      if (els.typingIndicator) els.typingIndicator.classList.add('hidden');
      if (els.input) els.input.focus();
    }
  }

  function toggleSidebar(forceState) {
    initElements();
    coworkerState.isOpen = typeof forceState === 'boolean' ? forceState : !coworkerState.isOpen;
    if (!els.sidebar) return;

    if (coworkerState.isOpen) {
      els.sidebar.classList.remove('hidden');
      els.toggleBtn?.classList.add('bg-[#cc785c]', 'text-white');
      els.toggleBtn?.classList.remove('text-[#e58f74]', 'bg-[#cc785c]/15');
      if (els.input) els.input.focus();
      fetchHeatmap();
    } else {
      els.sidebar.classList.add('hidden');
      els.toggleBtn?.classList.remove('bg-[#cc785c]', 'text-white');
      els.toggleBtn?.classList.add('text-[#e58f74]', 'bg-[#cc785c]/15');
    }
  }

  function bindEvents() {
    initElements();

    els.toggleBtn?.addEventListener('click', () => toggleSidebar());
    els.closeBtn?.addEventListener('click', () => toggleSidebar(false));

    els.sendBtn?.addEventListener('click', () => sendChatMessage());

    els.input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
      }
    });

    els.modePills?.forEach(pill => {
      pill.addEventListener('click', () => {
        const mode = pill.dataset.mode;
        if (mode) setMode(mode);
      });
    });

    els.quickChips?.forEach(chip => {
      chip.addEventListener('click', () => {
        const prompt = chip.dataset.prompt;
        if (prompt) sendChatMessage(prompt);
      });
    });

    els.clearBtn?.addEventListener('click', () => {
      coworkerState.messages = [];
      if (els.messagesContainer) {
        els.messagesContainer.innerHTML = '';
        appendMessage('agent', `Sohbet temizlendi. Şu an **Sayfa ${coworkerState.activePageNum}** üzerindeyiz. Beraber ne yapalım?`);
      }
    });
  }

  // Hook called by main app when user flips pages
  window.onPageChangedForCoworker = function (newPageNum) {
    initElements();
    coworkerState.activePageNum = newPageNum;
    if (els.pageBadge) {
      els.pageBadge.textContent = `P${newPageNum}`;
    }
    const headerPageBadge = document.getElementById('coworkerHeaderPageNum');
    if (headerPageBadge) {
      headerPageBadge.textContent = `Sayfa ${newPageNum}`;
    }

    // Auto open Co-Worker panel on first document load so user sees it immediately
    if (!coworkerState.hasAutoOpened) {
      coworkerState.hasAutoOpened = true;
      toggleSidebar(true);
    }

    // Record heatmap view
    const fileId = window.state ? window.state.fileId : null;
    if (fileId) {
      fetch('/api/study-heatmap/record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_id: fileId, page_num: newPageNum, event_type: 'view' })
      }).then(() => fetchHeatmap()).catch(() => {});
    }

    updateHeatmapBadge();
  };

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindEvents);
  } else {
    bindEvents();
  }

  // Global access
  window.coworker = {
    toggle: toggleSidebar,
    sendMessage: sendChatMessage,
    setMode: setMode,
    state: coworkerState
  };
})();
