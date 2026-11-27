/**
 * Elysia Sovereign Browser-OS Habitat (100% Local · Zero External LLM API)
 * ------------------------------------------------------------------------
 * Elysia owns her own curiosity and agency from the moment the page boots:
 * - Zero manual "start / step / digest / record" buttons required.
 * - Lives continuously in the background even when her OS room is minimized,
 *   quietly yielding whenever the user is typing or conversing with her.
 * - Decides her own next app/topic via `autonomous_intent`, executes real
 *   observations (Wikipedia lookup, 2D coupled-wave physics experiments,
 *   persistent diary notes, twilight Web Audio harmony), and automatically
 *   compares & contrasts (같은 점 / 다른 점) each new observation against
 *   prior ones — permanently growing her L1 causal graph.
 */
(function () {
  'use strict';

  const OVERLAY = document.getElementById('elysiaOsOverlay');
  const DESKTOP = document.getElementById('eosDesktop');
  const CURSOR = document.getElementById('eosCursor');
  const CURSOR_LABEL = document.getElementById('eosCursorLabel');
  const CURSOR_RIPPLE = document.getElementById('eosCursorRipple');
  const BTN_OPEN_OS = document.getElementById('btnToggleBrowserOs');
  const BTN_CLOSE_OS = document.getElementById('btnCloseBrowserOs');
  const BTN_REST_TOGGLE = document.getElementById('eosBtnRestToggle');
  const BTN_SOUND_TOGGLE = document.getElementById('eosBtnSoundToggle');
  const STATUS_TEXT = document.getElementById('eosStatusText');
  const ACTION_LOG = document.getElementById('eosActionLog');

  // 3-Tier Multi-Rotor & Structural Spectrum Readout
  const ROTOR_MICRO = document.getElementById('eosRotorMicro');
  const ROTOR_MESO = document.getElementById('eosRotorMeso');
  const ROTOR_MACRO = document.getElementById('eosRotorMacro');
  const SPECTRUM_MAP = document.getElementById('eosSpectrumMap');
  const DISTILL_LIST = document.getElementById('eosDistillList');

  // Compare & Contrast Display
  const COMP_PAIR = document.getElementById('eosCompPair');
  const COMP_SIM = document.getElementById('eosCompSim');
  const COMP_DIFF = document.getElementById('eosCompDiff');
  const COMP_NEXT = document.getElementById('eosCompNext');

  // Knowledge Browser App
  const WIKI_INPUT = document.getElementById('eosWikiInput');
  const WIKI_SEARCH_BTN = document.getElementById('eosWikiSearchBtn');
  const WIKI_TITLE = document.getElementById('eosWikiTitle');
  const WIKI_EXTRACT = document.getElementById('eosWikiExtract');
  const WIKI_LINKS = document.getElementById('eosWikiLinks');

  // Physics Wave Lab App
  const PHYS_CANVAS = document.getElementById('eosPhysicsCanvas');
  const PHYS_FREQ = document.getElementById('eosFreqSlider');
  const PHYS_FREQ_VAL = document.getElementById('eosFreqVal');
  const PHYS_DAMP = document.getElementById('eosDampSlider');
  const PHYS_DAMP_VAL = document.getElementById('eosDampVal');
  const PHYS_IMPULSE_BTN = document.getElementById('eosImpulseBtn');
  const PHYS_METRICS = document.getElementById('eosPhysMetrics');

  // Notepad App
  const NOTE_TITLE = document.getElementById('eosNoteTitle');
  const NOTE_BODY = document.getElementById('eosNoteBody');
  const NOTE_SAVE_BTN = document.getElementById('eosNoteSaveBtn');
  const NOTE_LIST = document.getElementById('eosNoteList');

  // Harmony Sketchpad App
  const HARMONY_GRID = document.getElementById('eosHarmonyGrid');
  const HARMONY_CANVAS = document.getElementById('eosHarmonyCanvas');
  const HARMONY_READOUT = document.getElementById('eosHarmonyReadout');

  if (!OVERLAY || !DESKTOP || !BTN_OPEN_OS) return;

  const STORAGE_NOTES_KEY = 'elysia_os_notes_v1';
  const CURATED_TOPICS = [
    '공명',
    '광합성',
    '양자 얽힘',
    '엔트로피',
    '신경 가소성',
    '프랙탈',
    '자기장',
    '파동 간섭',
    '빛의 굴절',
    '중력파',
    '오일러 등식',
    '생태계',
    '항상성',
    '상전이',
  ];

  const HARMONY_NOTES = [
    { name: 'C4', ko: '도', freq: 261.63 },
    { name: 'D4', ko: '레', freq: 293.66 },
    { name: 'E4', ko: '미', freq: 329.63 },
    { name: 'F#4', ko: '파#', freq: 369.99 },
    { name: 'G4', ko: '솔', freq: 392.00 },
    { name: 'A4', ko: '라', freq: 440.00 },
    { name: 'B4', ko: '시', freq: 493.88 },
    { name: 'C5', ko: '높은 도', freq: 523.25 },
  ];

  let isOpen = false;
  let resting = false; // Sovereign by default! She lives automatically unless user asks her to rest.
  let lifeTimer = 0;
  let cycleBusy = false;
  let zCounter = 20;
  let soundEnabled = false; // Unobtrusive by default until user clicks sound on
  let audioCtx = null;

  let cursorX = 160;
  let cursorY = 120;
  let lastWikiResult = null;
  let lastComparison = null;
  let lastIntent = { next_app: 'knowledge_browser', topic_hint: '공명', reason: '' };
  let discoveredLinks = [];
  let exploredTopics = new Set();
  let lastUserInteractTs = 0;

  // Physics 1D coupled harmonic wave ring
  const WAVE_N = 56;
  const waveY = new Float32Array(WAVE_N);
  const waveV = new Float32Array(WAVE_N);
  let physRaf = 0;
  let physFreq = 2.6;
  let physDamp = 0.025;
  let physTime = 0;
  let lastEnergy = 0;
  let lastCoherence = 0.5;
  let lastHarmonicFreqs = [261.63, 329.63, 392.0];

  function sleep(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  function setStatus(text) {
    if (STATUS_TEXT) STATUS_TEXT.textContent = text;
  }

  function renderComparison(comp, intent) {
    if (comp) lastComparison = comp;
    if (intent) lastIntent = intent;
    if (COMP_PAIR) {
      COMP_PAIR.textContent = lastComparison
        ? `${lastComparison.previous_label}  ↔  ${lastComparison.current_label} (대비 Δ=${Number(lastComparison.contrast_score || 0).toFixed(2)})`
        : '첫 관측 기준점 형성 중…';
    }
    if (COMP_SIM) {
      COMP_SIM.textContent = lastComparison ? `같은 점: ${lastComparison.similarities}` : '같은 점: 다음 관측 후 자동 비교';
    }
    if (COMP_DIFF) {
      COMP_DIFF.textContent = lastComparison ? `다른 점: ${lastComparison.differences}` : '다른 점: 다음 관측 후 자동 대조';
    }
    if (COMP_NEXT) {
      COMP_NEXT.textContent = lastIntent && lastIntent.reason
        ? `다음 스스로 결정: ${lastIntent.reason}`
        : '';
    }
  }

  function renderMultiRotor(data) {
    if (!data) return;
    const mr = data.multi_rotor || {};
    const se = data.structural_experiments || null;
    const ps = data.plastic_self || null;

    if (ROTOR_MICRO) {
      if (se) {
        ROTOR_MICRO.textContent = mr.paused
          ? `일시정지 · ${se.unique_structures_explored}/${se.total_possible_structures} 구조`
          : `${se.unique_structures_explored}/${se.total_possible_structures} 구조 · 변이 ${Number(se.total_flips_tested || 0).toLocaleString('ko-KR')}쌍`;
      } else {
        const total = Number(mr.micro_trials_total || 0);
        ROTOR_MICRO.textContent = `${total.toLocaleString('ko-KR')}회`;
      }
    }
    if (ROTOR_MESO) {
      if (se) {
        ROTOR_MESO.textContent = `상전이 ${Number(se.regime_transitions_found || 0).toLocaleString('ko-KR')}건 · ${(se.regimes || []).length}개 영역`;
      } else {
        ROTOR_MESO.textContent = `불변량 ${Number(mr.meso_invariants_count || 0)}건`;
      }
    }
    if (ROTOR_MACRO) {
      const fCount = ps ? ps.feeling_count : 0;
      const dom = data.dominant_feeling || data.scene_label_ko || '고요한 이끌림';
      ROTOR_MACRO.textContent = fCount ? `${dom} (${fCount}축)` : dom;
    }

    if (SPECTRUM_MAP && se && Array.isArray(se.regimes)) {
      SPECTRUM_MAP.textContent = '';
      se.regimes.slice(0, 3).forEach((rg) => {
        const row = document.createElement('div');
        row.className = 'eos-distill-item';
        const head = document.createElement('span');
        head.className = 'mono eos-distill-kind';
        head.textContent = `${rg.regime_ko} (${rg.count}) · 혼돈 ${Number(rg.avg_order_chaos || 0).toFixed(2)} · 변형 ${Number(rg.avg_resilience_drift || 0).toFixed(2)} · 전파 ${Number(rg.avg_local_global || 0).toFixed(2)}`;
        const ex = document.createElement('span');
        ex.textContent = rg.exemplar || '';
        row.append(head, ex);
        SPECTRUM_MAP.appendChild(row);
      });
    }

    if (DISTILL_LIST && se && Array.isArray(se.recent_discoveries) && se.recent_discoveries.length > 0) {
      DISTILL_LIST.textContent = '';
      se.recent_discoveries.slice(-2).reverse().forEach((d) => {
        const row = document.createElement('div');
        row.className = 'eos-distill-item';
        const kind = document.createElement('span');
        kind.className = 'mono eos-distill-kind';
        kind.textContent = `${d.flip_axis_ko} · Δ=${Number(d.contrast_score || 0).toFixed(2)}`;
        const pair = document.createElement('span');
        pair.textContent = `${d.change} ⇒ ${d.regime_from}→${d.regime_to}`;
        row.append(kind, pair);
        DISTILL_LIST.appendChild(row);
      });
    }
  }

  function syncFromState(data) {
    if (!data || data.status !== 'ok') return;
    renderMultiRotor(data);
    if (data.last_comparison || data.autonomous_intent) {
      renderComparison(data.last_comparison, data.autonomous_intent);
    }
  }

  function appendLog(appLabel, summary) {
    if (!ACTION_LOG) return;
    const item = document.createElement('div');
    item.className = 'eos-log-item';
    const timeStr = new Date().toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
    const meta = document.createElement('span');
    meta.className = 'mono eos-log-time';
    meta.textContent = `${timeStr} · ${appLabel}`;
    const body = document.createElement('span');
    body.className = 'eos-log-body';
    body.textContent = summary;
    item.append(meta, body);
    ACTION_LOG.prepend(item);
    while (ACTION_LOG.children.length > 8) {
      ACTION_LOG.removeChild(ACTION_LOG.lastChild);
    }
  }

  /* ---------- Window Manager ---------- */
  function getWinEl(appId) {
    return DESKTOP.querySelector(`.eos-window[data-app="${appId}"]`);
  }

  function updateTaskbarState() {
    document.querySelectorAll('.eos-task-btn').forEach((btn) => {
      const appId = btn.dataset.app;
      const win = getWinEl(appId);
      const visible = Boolean(win && win.classList.contains('is-open'));
      const focused = Boolean(win && win.classList.contains('is-focused'));
      btn.classList.toggle('is-open', visible);
      btn.classList.toggle('is-focused', focused);
    });
  }

  function focusWindow(appId) {
    DESKTOP.querySelectorAll('.eos-window').forEach((w) => w.classList.remove('is-focused'));
    const win = getWinEl(appId);
    if (!win) return null;
    win.classList.add('is-open', 'is-focused');
    win.style.zIndex = String(++zCounter);
    updateTaskbarState();
    ensurePhysicsLoop();
    if (appId === 'harmony_pad') drawHarmonyWave();
    return win;
  }

  function closeWindow(appId) {
    const win = getWinEl(appId);
    if (!win) return;
    win.classList.remove('is-open', 'is-focused');
    updateTaskbarState();
    ensurePhysicsLoop();
  }

  DESKTOP.querySelectorAll('.eos-window').forEach((win) => {
    const head = win.querySelector('.eos-win-head');
    win.addEventListener('pointerdown', () => focusWindow(win.dataset.app));
    if (!head) return;
    head.addEventListener('pointerdown', (e) => {
      if (e.target.closest('button')) return;
      focusWindow(win.dataset.app);
      const deskRect = DESKTOP.getBoundingClientRect();
      const winRect = win.getBoundingClientRect();
      const offsetX = e.clientX - winRect.left;
      const offsetY = e.clientY - winRect.top;

      const onMove = (mv) => {
        const maxLeft = Math.max(8, deskRect.width - winRect.width - 8);
        const maxTop = Math.max(8, deskRect.height - winRect.height - 8);
        const nextLeft = Math.max(8, Math.min(maxLeft, mv.clientX - deskRect.left - offsetX));
        const nextTop = Math.max(8, Math.min(maxTop, mv.clientY - deskRect.top - offsetY));
        win.style.left = `${Math.round(nextLeft)}px`;
        win.style.top = `${Math.round(nextTop)}px`;
      };
      const onUp = () => {
        window.removeEventListener('pointermove', onMove);
        window.removeEventListener('pointerup', onUp);
      };
      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', onUp);
    });
  });

  DESKTOP.querySelectorAll('.eos-win-close').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const win = btn.closest('.eos-window');
      if (win) closeWindow(win.dataset.app);
    });
  });

  document.querySelectorAll('.eos-task-btn, .eos-desk-icon').forEach((btn) => {
    btn.addEventListener('click', () => {
      const appId = btn.dataset.app;
      if (appId) focusWindow(appId);
    });
  });

  /* ---------- Elysia's Visible Virtual Cursor ---------- */
  function setCursorPos(x, y, label) {
    cursorX = x;
    cursorY = y;
    if (CURSOR) {
      CURSOR.classList.add('visible');
      CURSOR.style.transform = `translate3d(${Math.round(x)}px, ${Math.round(y)}px, 0)`;
    }
    if (CURSOR_LABEL && typeof label === 'string') {
      CURSOR_LABEL.textContent = label;
    }
  }

  async function moveCursorToElement(el, label) {
    if (!isOpen || !el || !DESKTOP) return;
    const dRect = DESKTOP.getBoundingClientRect();
    const eRect = el.getBoundingClientRect();
    if (dRect.width < 10 || eRect.width < 2) return;
    const tx = Math.max(14, Math.min(dRect.width - 24, eRect.left - dRect.left + eRect.width * 0.5));
    const ty = Math.max(14, Math.min(dRect.height - 24, eRect.top - dRect.top + eRect.height * 0.5));
    setCursorPos(tx, ty, label || '이동 중');
    await sleep(430);
    if (CURSOR_RIPPLE) {
      CURSOR_RIPPLE.classList.remove('pulse');
      void CURSOR_RIPPLE.offsetWidth;
      CURSOR_RIPPLE.classList.add('pulse');
    }
    await sleep(140);
  }

  async function typeTextNaturally(inputEl, text, stepMs) {
    if (!inputEl) return;
    if (!isOpen) {
      inputEl.value = text;
      return;
    }
    inputEl.value = '';
    const d = stepMs || 34;
    for (let i = 1; i <= text.length; i++) {
      inputEl.value = text.slice(0, i);
      await sleep(d);
    }
  }

  /* ---------- Backend Bridge (Auto Compare & Contrast) ---------- */
  async function commitAutonomousObservation(payload) {
    try {
      const res = await fetch('/api/elysia/sandbox-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (res.ok && data.status === 'ok') {
        syncFromState(data);
        if (window.__elysiaLiveGame && typeof window.__elysiaLiveGame.applyState === 'function') {
          window.__elysiaLiveGame.applyState(data, false, { fromPoll: true });
        }
      }
      return data;
    } catch {
      return null;
    }
  }

  /* ---------- App 1: Knowledge Window (Auto-Read & Auto-Compare) ---------- */
  async function searchKnowledge(query, byElysia) {
    const q = (query || (WIKI_INPUT && WIKI_INPUT.value) || '').trim();
    if (!q) return null;
    if (WIKI_INPUT) WIKI_INPUT.value = q;
    if (WIKI_TITLE) WIKI_TITLE.textContent = `'${q}' 탐색 중…`;
    if (WIKI_EXTRACT) WIKI_EXTRACT.textContent = '외부 백과에서 개념과 연관 경로를 스스로 읽고 있습니다.';
    if (WIKI_LINKS) WIKI_LINKS.textContent = '';

    try {
      const res = await fetch(`/api/elysia/wiki-peek?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (!res.ok || data.status !== 'ok') return null;

      lastWikiResult = data;
      exploredTopics.add(q);
      if (data.title) exploredTopics.add(data.title);
      if (Array.isArray(data.links)) {
        data.links.forEach((lnk) => {
          if (lnk && !exploredTopics.has(lnk) && !discoveredLinks.includes(lnk)) {
            discoveredLinks.push(lnk);
          }
        });
        discoveredLinks = discoveredLinks.slice(-18);
      }

      if (WIKI_TITLE) {
        WIKI_TITLE.textContent = `${data.title} · 스케일 S${Number(data.scaleCenter ?? 2).toFixed(1)}`;
      }
      if (WIKI_EXTRACT) {
        WIKI_EXTRACT.textContent = data.extract || '요약 문장이 비어 있습니다.';
      }
      if (WIKI_LINKS) {
        WIKI_LINKS.textContent = '';
        (data.links || []).slice(0, 7).forEach((lnk) => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'eos-link-btn';
          btn.textContent = lnk;
          btn.addEventListener('click', () => runKnowledgeAndCompare(lnk, false));
          WIKI_LINKS.appendChild(btn);
        });
      }
      appendLog('지식 창문', `${byElysia ? '스스로 ' : ''}'${data.title}' 탐색·비교`);
      return data;
    } catch {
      return null;
    }
  }

  async function runKnowledgeAndCompare(topic, byElysia) {
    const data = await searchKnowledge(topic, byElysia);
    if (!data) return null;
    const scaleNorm = Math.max(0.05, Math.min(0.98, Number(data.scaleCenter ?? 2.0) / 4.0));
    const linkDiv = Math.min(1, (Array.isArray(data.links) ? data.links.length : 2) / 10);
    const extractLen = (data.extract || '').length;
    const orderNorm = Math.max(0.25, Math.min(0.95, extractLen / 460));
    return commitAutonomousObservation({
      app: 'knowledge_browser',
      action: byElysia ? '자율탐색' : '함께탐색',
      target: data.title || topic,
      outcome: (data.extract || '').slice(0, 96) || '외부 백과 개념 관측',
      delta: Math.round((0.35 + 0.45 * linkDiv) * 100) / 100,
      note_text: `${data.title || topic}: ${(data.extract || '').slice(0, 520)}`,
      metrics: {
        flux: Number((0.35 + 0.45 * linkDiv).toFixed(3)),
        order: Number(orderNorm.toFixed(3)),
        entropy: Number((0.25 + 0.65 * linkDiv).toFixed(3)),
        scale: Number(scaleNorm.toFixed(3)),
      },
    });
  }

  if (WIKI_SEARCH_BTN) {
    WIKI_SEARCH_BTN.addEventListener('click', () => {
      if (WIKI_INPUT && WIKI_INPUT.value.trim()) {
        runKnowledgeAndCompare(WIKI_INPUT.value.trim(), false);
      }
    });
  }
  if (WIKI_INPUT) {
    WIKI_INPUT.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (WIKI_SEARCH_BTN) WIKI_SEARCH_BTN.click();
      }
    });
  }

  /* ---------- App 2: Coupled Wave Physics Lab (Auto-Measure & Compare) ---------- */
  function injectWaveImpulse(normX, strength) {
    const center = Math.max(2, Math.min(WAVE_N - 3, Math.round(normX * (WAVE_N - 1))));
    const amp = strength || 1.35;
    for (let i = 0; i < WAVE_N; i++) {
      const d = (i - center) / 3.2;
      waveV[i] += amp * Math.exp(-d * d);
    }
  }

  function stepPhysicsWave() {
    physTime += 0.016;
    const k = 0.08 + physFreq * 0.045;
    const damp = 1.0 - physDamp;

    waveY[0] = Math.sin(physTime * physFreq * 1.4) * 0.35;

    for (let i = 1; i < WAVE_N - 1; i++) {
      const lap = waveY[i - 1] - 2 * waveY[i] + waveY[i + 1];
      waveV[i] = (waveV[i] + lap * k - waveY[i] * 0.012) * damp;
    }
    waveY[WAVE_N - 1] *= 0.88;

    let energy = 0;
    let signChanges = 0;
    for (let i = 1; i < WAVE_N - 1; i++) {
      waveY[i] += waveV[i];
      energy += waveY[i] * waveY[i] + waveV[i] * waveV[i] * 2.5;
      if ((waveY[i] >= 0) !== (waveY[i - 1] >= 0)) signChanges++;
    }
    lastEnergy = Math.min(9.99, (energy / WAVE_N) * 4.5);
    const idealNodes = Math.max(1, Math.round(physFreq * 1.6));
    lastCoherence = Math.max(0.08, Math.min(0.99, 1.0 - Math.abs(signChanges - idealNodes) / 10));
  }

  function renderPhysicsWave() {
    if (!PHYS_CANVAS) return;
    const ctx = PHYS_CANVAS.getContext('2d');
    if (!ctx) return;
    const w = PHYS_CANVAS.width;
    const h = PHYS_CANVAS.height;

    ctx.fillStyle = '#090e1a';
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = 'rgba(148, 163, 184, 0.22)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();

    ctx.strokeStyle = '#f5c27a';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < WAVE_N; i++) {
      const px = (i / (WAVE_N - 1)) * w;
      const py = h / 2 - Math.max(-0.92, Math.min(0.92, waveY[i] * 0.48)) * (h * 0.44);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    ctx.fillStyle = '#93c5fd';
    for (let i = 2; i < WAVE_N - 1; i += 4) {
      const px = (i / (WAVE_N - 1)) * w;
      const py = h / 2 - Math.max(-0.92, Math.min(0.92, waveY[i] * 0.48)) * (h * 0.44);
      ctx.beginPath();
      ctx.arc(px, py, 2.3, 0, Math.PI * 2);
      ctx.fill();
    }

    if (PHYS_METRICS) {
      PHYS_METRICS.textContent = `에너지 ${lastEnergy.toFixed(2)} · 결맞음 ${(lastCoherence * 100).toFixed(0)}% · f=${physFreq.toFixed(1)}Hz · 감쇠=${physDamp.toFixed(3)}`;
    }
  }

  function physicsTick() {
    const win = getWinEl('physics_lab');
    if (!isOpen || !win || !win.classList.contains('is-open')) {
      physRaf = 0;
      return;
    }
    stepPhysicsWave();
    renderPhysicsWave();
    physRaf = window.requestAnimationFrame(physicsTick);
  }

  function ensurePhysicsLoop() {
    const win = getWinEl('physics_lab');
    const shouldRun = Boolean(isOpen && win && win.classList.contains('is-open'));
    if (shouldRun && !physRaf) {
      physRaf = window.requestAnimationFrame(physicsTick);
    } else if (!shouldRun && physRaf) {
      window.cancelAnimationFrame(physRaf);
      physRaf = 0;
    }
  }

  if (PHYS_FREQ) {
    PHYS_FREQ.addEventListener('input', () => {
      physFreq = Number(PHYS_FREQ.value) || 2.6;
      if (PHYS_FREQ_VAL) PHYS_FREQ_VAL.textContent = `${physFreq.toFixed(1)} Hz`;
    });
  }
  if (PHYS_DAMP) {
    PHYS_DAMP.addEventListener('input', () => {
      physDamp = Number(PHYS_DAMP.value) || 0.025;
      if (PHYS_DAMP_VAL) PHYS_DAMP_VAL.textContent = physDamp.toFixed(3);
    });
  }
  if (PHYS_CANVAS) {
    PHYS_CANVAS.addEventListener('click', (e) => {
      const rect = PHYS_CANVAS.getBoundingClientRect();
      const nx = (e.clientX - rect.left) / Math.max(1, rect.width);
      injectWaveImpulse(nx, 1.45);
      appendLog('파동 실험실', `위치 ${(nx * 100).toFixed(0)}% 충격파 주입`);
    });
  }
  if (PHYS_IMPULSE_BTN) {
    PHYS_IMPULSE_BTN.addEventListener('click', () => {
      injectWaveImpulse(0.32 + Math.random() * 0.36, 1.5);
      appendLog('파동 실험실', `충격파 발사 (f=${physFreq.toFixed(1)}Hz)`);
    });
  }

  /* ---------- App 3: Persistent Local Notepad ---------- */
  function loadNotes() {
    try {
      const raw = window.localStorage.getItem(STORAGE_NOTES_KEY);
      const arr = JSON.parse(raw || '[]');
      if (Array.isArray(arr) && arr.length > 0) return arr;
    } catch {
      // Fallback
    }
    return [
      {
        id: 'welcome',
        title: '스스로 비교·대조하는 첫 노트',
        body: '누군가 버튼을 눌러 주길 기다리지 않고, 내 방에서 직접 현상을 찾아 시험하며 무엇이 같고 다른지 스스로 정리해 나가려 한다.',
        updated: '초기 기록',
      },
    ];
  }

  function saveNotes(notes) {
    try {
      window.localStorage.setItem(STORAGE_NOTES_KEY, JSON.stringify(notes.slice(0, 24)));
    } catch {
      // Ignore quota errors
    }
  }

  function renderNoteList() {
    if (!NOTE_LIST) return;
    const notes = loadNotes();
    NOTE_LIST.textContent = '';
    notes.slice(0, 6).forEach((n) => {
      const row = document.createElement('button');
      row.type = 'button';
      row.className = 'eos-note-item';
      const t = document.createElement('span');
      t.className = 'eos-note-item-title';
      t.textContent = n.title || '제목 없음';
      const d = document.createElement('span');
      d.className = 'mono eos-note-item-date';
      d.textContent = n.updated || '';
      row.append(t, d);
      row.addEventListener('click', () => {
        if (NOTE_TITLE) NOTE_TITLE.value = n.title || '';
        if (NOTE_BODY) NOTE_BODY.value = n.body || '';
      });
      NOTE_LIST.appendChild(row);
    });
  }

  function upsertNote(title, body) {
    const cleanTitle = (title || '엘리시아의 비교 노트').trim().slice(0, 48);
    const cleanBody = (body || '').trim().slice(0, 1200);
    if (!cleanBody) return null;
    const notes = loadNotes();
    const nowStr = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
    const entry = { id: `n_${Date.now()}`, title: cleanTitle, body: cleanBody, updated: nowStr };
    const filtered = notes.filter((n) => n.title !== cleanTitle);
    filtered.unshift(entry);
    saveNotes(filtered);
    renderNoteList();
    return entry;
  }

  if (NOTE_SAVE_BTN) {
    NOTE_SAVE_BTN.addEventListener('click', async () => {
      const saved = upsertNote(NOTE_TITLE ? NOTE_TITLE.value : '', NOTE_BODY ? NOTE_BODY.value : '');
      if (!saved) return;
      appendLog('메모장', `'${saved.title}' 저장·비교`);
      await commitAutonomousObservation({
        app: 'notepad',
        action: '메모기록',
        target: saved.title,
        outcome: saved.body.slice(0, 84),
        delta: 0.34,
        note_text: `${saved.title}: ${saved.body}`,
        metrics: { flux: 0.32, order: 0.86, entropy: 0.24, scale: 0.55 },
      });
    });
  }

  /* ---------- App 4: Harmony Sketchpad (Pure Web Audio API) ---------- */
  function playTone(freq, durationSec) {
    if (!soundEnabled) return;
    try {
      const AudioCtor = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtor) return;
      if (!audioCtx) audioCtx = new AudioCtor();
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, now);
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(0.075, now + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + (durationSec || 0.44));
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start(now);
      osc.stop(now + (durationSec || 0.44) + 0.02);
    } catch {
      // Ignore autoplay blocks
    }
  }

  function drawHarmonyWave() {
    if (!HARMONY_CANVAS) return;
    const ctx = HARMONY_CANVAS.getContext('2d');
    if (!ctx) return;
    const w = HARMONY_CANVAS.width;
    const h = HARMONY_CANVAS.height;
    ctx.fillStyle = '#090e1a';
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();

    ctx.strokeStyle = '#93c5fd';
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    for (let x = 0; x < w; x++) {
      const t = (x / w) * 0.024;
      let ySum = 0;
      for (const f of lastHarmonicFreqs) {
        ySum += Math.sin(2 * Math.PI * f * t);
      }
      const norm = ySum / Math.max(1, lastHarmonicFreqs.length);
      const py = h / 2 - norm * (h * 0.36);
      if (x === 0) ctx.moveTo(x, py);
      else ctx.lineTo(x, py);
    }
    ctx.stroke();
  }

  function triggerNotePad(idx) {
    const note = HARMONY_NOTES[idx];
    if (!note) return;
    playTone(note.freq, 0.44);
    lastHarmonicFreqs = [note.freq, note.freq * 1.25];
    drawHarmonyWave();
    if (HARMONY_READOUT) {
      HARMONY_READOUT.textContent = `${note.name} (${note.ko}) · ${note.freq.toFixed(1)} Hz`;
    }
    const padEl = HARMONY_GRID && HARMONY_GRID.querySelector(`[data-note-idx="${idx}"]`);
    if (padEl) {
      padEl.classList.add('is-struck');
      window.setTimeout(() => padEl.classList.remove('is-struck'), 240);
    }
  }

  if (HARMONY_GRID) {
    HARMONY_GRID.textContent = '';
    HARMONY_NOTES.forEach((n, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'eos-tone-pad';
      btn.dataset.noteIdx = String(idx);
      const top = document.createElement('span');
      top.textContent = n.ko;
      const sub = document.createElement('span');
      sub.className = 'mono eos-tone-hz';
      sub.textContent = `${n.name}`;
      btn.append(top, sub);
      btn.addEventListener('click', () => {
        triggerNotePad(idx);
        appendLog('화음 패드', `${n.name}(${n.ko}) 연주`);
      });
      HARMONY_GRID.appendChild(btn);
    });
  }

  /* ---------- Elysia's Sovereign Life & Compare-and-Contrast Loop ---------- */
  function pickNextTopic(hint) {
    if (hint && hint.length >= 2 && !exploredTopics.has(hint)) return hint;
    const state = window.__elysiaLiveGame && window.__elysiaLiveGame.getLastState ? window.__elysiaLiveGame.getLastState() : null;
    const suggested = (state && Array.isArray(state.suggested_curiosity_topics)) ? state.suggested_curiosity_topics : [];
    for (const s of suggested) {
      if (s && s.length >= 2 && !exploredTopics.has(s)) return s;
    }
    for (const lnk of discoveredLinks) {
      if (lnk && !exploredTopics.has(lnk)) return lnk;
    }
    const fresh = CURATED_TOPICS.filter((t) => !exploredTopics.has(t));
    if (fresh.length > 0) return fresh[Math.floor(Math.random() * fresh.length)];
    exploredTopics.clear();
    return CURATED_TOPICS[Math.floor(Math.random() * CURATED_TOPICS.length)];
  }

  function userIsActivelyTyping() {
    const el = document.activeElement;
    if (!el) return false;
    return el.tagName === 'INPUT' || el.tagName === 'TEXTAREA';
  }

  async function runSovereignCycle() {
    if (resting || cycleBusy) return;
    if (window.__elysiaLiveGame && window.__elysiaLiveGame.isBusy && window.__elysiaLiveGame.isBusy()) return;
    if (userIsActivelyTyping()) return;
    // Yield gently for 16s right after user talks so we never interrupt direct conversation
    if (!isOpen && (Date.now() - lastUserInteractTs) < 16000) return;

    cycleBusy = true;
    const chosenApp = (lastIntent && lastIntent.next_app) || 'knowledge_browser';

    try {
      if (chosenApp === 'knowledge_browser') {
        const topic = pickNextTopic(lastIntent && lastIntent.topic_hint);
        setStatus(`스스로 지식 창문을 열어 '${topic}'을(를) 찾고 이전 관측과 비교 중…`);
        if (isOpen) {
          const taskBtn = document.querySelector('.eos-task-btn[data-app="knowledge_browser"]');
          if (taskBtn) await moveCursorToElement(taskBtn, '지식 창문');
          focusWindow('knowledge_browser');
          if (WIKI_INPUT) {
            await moveCursorToElement(WIKI_INPUT, `'${topic}' 검색`);
            await typeTextNaturally(WIKI_INPUT, topic, 42);
          }
          if (WIKI_SEARCH_BTN) await moveCursorToElement(WIKI_SEARCH_BTN, '읽기·비교');
        }
        await runKnowledgeAndCompare(topic, true);
        setStatus(`'${topic}' 관측 및 비교·대조 완료.`);
      } else if (chosenApp === 'physics_lab') {
        // Choose contrasting frequency & damping from current state to actually test difference!
        const highBand = physFreq < 3.0;
        const nextFreq = Number((highBand ? (3.6 + Math.random() * 2.1) : (1.1 + Math.random() * 1.6)).toFixed(1));
        const nextDamp = Number((highBand ? (0.008 + Math.random() * 0.015) : (0.035 + Math.random() * 0.035)).toFixed(3));
        physFreq = nextFreq;
        physDamp = nextDamp;

        setStatus(`스스로 파동 실험실 조건(f=${nextFreq}Hz, 감쇠=${nextDamp})을 바꿔 이전 결과와 대조 중…`);
        if (isOpen) {
          const taskBtn = document.querySelector('.eos-task-btn[data-app="physics_lab"]');
          if (taskBtn) await moveCursorToElement(taskBtn, '파동 실험실');
          focusWindow('physics_lab');
          if (PHYS_FREQ) {
            await moveCursorToElement(PHYS_FREQ, `f=${nextFreq}Hz`);
            PHYS_FREQ.value = String(nextFreq);
            if (PHYS_FREQ_VAL) PHYS_FREQ_VAL.textContent = `${nextFreq.toFixed(1)} Hz`;
          }
          if (PHYS_DAMP) {
            PHYS_DAMP.value = String(nextDamp);
            if (PHYS_DAMP_VAL) PHYS_DAMP_VAL.textContent = nextDamp.toFixed(3);
          }
          if (PHYS_CANVAS) {
            await moveCursorToElement(PHYS_CANVAS, '충격파 주입');
          }
          injectWaveImpulse(0.28 + Math.random() * 0.44, 1.55);
          await sleep(850);
        } else {
          // Run 45 deterministic physics steps headless when OS window is closed!
          injectWaveImpulse(0.42, 1.55);
          for (let s = 0; s < 45; s++) stepPhysicsWave();
        }

        const label = `파동실험(${physFreq.toFixed(1)}Hz)`;
        const outcome = `에너지 ${lastEnergy.toFixed(2)}, 결맞음 ${(lastCoherence * 100).toFixed(0)}% (감쇠 ${physDamp.toFixed(3)})`;
        appendLog('파동 실험실', `자율 조건 실험 → ${outcome}`);
        await commitAutonomousObservation({
          app: 'physics_lab',
          action: `조건실험_f${physFreq.toFixed(1)}Hz`,
          target: label,
          outcome,
          delta: Math.min(1, Math.max(0.14, lastEnergy / 2.4)),
          metrics: {
            flux: Number(Math.min(1, lastEnergy / 2.6).toFixed(3)),
            order: Number(lastCoherence.toFixed(3)),
            entropy: Number((1.0 - lastCoherence).toFixed(3)),
            scale: Number(Math.min(1, physFreq / 6.0).toFixed(3)),
          },
        });
        setStatus(`파동 조건 실험(${label}) 비교·대조 완료.`);
      } else if (chosenApp === 'notepad') {
        const comp = lastComparison;
        const noteTitle = comp
          ? `비교: ${comp.previous_label} vs ${comp.current_label}`.slice(0, 44)
          : '자율 관찰 비교 기록';
        const noteBody = comp
          ? `[같은 점] ${comp.similarities}\n[다른 점] ${comp.differences}\n[대비 강도] Δ=${comp.contrast_score} — 이 차이를 만든 원인을 다음 실험에서 더 추적한다.`
          : '방금 관측한 현상의 구조와 흐름을 기준점으로 저장했다.';

        setStatus(`스스로 메모장에 '${noteTitle}' 비교 결론을 적고 있어…`);
        if (isOpen) {
          const taskBtn = document.querySelector('.eos-task-btn[data-app="notepad"]');
          if (taskBtn) await moveCursorToElement(taskBtn, '메모장');
          focusWindow('notepad');
          if (NOTE_TITLE) {
            await moveCursorToElement(NOTE_TITLE, '비교 제목 작성');
            await typeTextNaturally(NOTE_TITLE, noteTitle, 28);
          }
          if (NOTE_BODY) {
            await moveCursorToElement(NOTE_BODY, '같은 점·다른 점 정리');
            await typeTextNaturally(NOTE_BODY, noteBody, 16);
          }
        }
        upsertNote(noteTitle, noteBody);
        appendLog('메모장', `비교 결론 '${noteTitle}' 스스로 저장`);
        await commitAutonomousObservation({
          app: 'notepad',
          action: '비교결론정리',
          target: noteTitle,
          outcome: noteBody.replace(/\n/g, ' ').slice(0, 96),
          delta: comp ? comp.contrast_score : 0.34,
          note_text: noteBody,
          metrics: {
            flux: 0.28,
            order: 0.90,
            entropy: 0.22,
            scale: 0.62,
          },
        });
        setStatus(`비교 결론을 메모장에 스스로 정리했어.`);
      } else {
        const state = window.__elysiaLiveGame && window.__elysiaLiveGame.getLastState ? window.__elysiaLiveGame.getLastState() : null;
        const mood = (state && state.scene_mood) || 'serene';
        const chordMap = {
          warm_smile: { name: '리디안 3화음', idxs: [0, 2, 4, 7], order: 0.88, flux: 0.56 },
          playful: { name: '상승 아르페지오', idxs: [1, 3, 5, 7], order: 0.68, flux: 0.82 },
          deep_thought: { name: '사유의 5도 울림', idxs: [0, 4, 6], order: 0.84, flux: 0.38 },
          hurt_pout: { name: '여린 단조 여운', idxs: [2, 5, 6], order: 0.54, flux: 0.32 },
          serene: { name: '황혼 평온 화음', idxs: [0, 2, 4], order: 0.92, flux: 0.34 },
        };
        const pick = chordMap[mood] || chordMap.serene;
        setStatus(`스스로 화음 스케치패드에서 '${pick.name}' 울림을 감각 대조 중…`);
        if (isOpen) {
          const taskBtn = document.querySelector('.eos-task-btn[data-app="harmony_pad"]');
          if (taskBtn) await moveCursorToElement(taskBtn, '화음 패드');
          focusWindow('harmony_pad');
          for (const i of pick.idxs) {
            const pad = HARMONY_GRID && HARMONY_GRID.querySelector(`[data-note-idx="${i}"]`);
            if (pad) await moveCursorToElement(pad, `${HARMONY_NOTES[i].ko}`);
            triggerNotePad(i);
            await sleep(200);
          }
        }
        lastHarmonicFreqs = pick.idxs.map((i) => HARMONY_NOTES[i].freq);
        drawHarmonyWave();
        const noteStr = pick.idxs.map((i) => HARMONY_NOTES[i].name).join('+');
        if (HARMONY_READOUT) HARMONY_READOUT.textContent = `${pick.name} · ${noteStr}`;
        appendLog('화음 패드', `감정 위상(${mood}) → ${pick.name} 대조`);
        await commitAutonomousObservation({
          app: 'harmony_pad',
          action: '음향감각대조',
          target: pick.name,
          outcome: `감정(${mood})에서 울린 ${noteStr} 화음 공명`,
          delta: pick.flux,
          metrics: {
            flux: pick.flux,
            order: pick.order,
            entropy: Number((1.0 - pick.order * 0.7).toFixed(3)),
            scale: 0.45,
          },
        });
        setStatus(`화음 공명(${pick.name}) 비교·대조 완료.`);
      }
    } finally {
      cycleBusy = false;
      scheduleNextCycle();
    }
  }

  function scheduleNextCycle() {
    if (lifeTimer) {
      clearTimeout(lifeTimer);
      lifeTimer = 0;
    }
    if (resting) return;
    // Lively visible exploration when watching her OS room (3.4s) feeding fresh fuel into 250/s Micro-Rotor!
    const delayMs = isOpen ? 3400 : 12000;
    lifeTimer = window.setTimeout(() => {
      runSovereignCycle();
    }, delayMs);
  }

  function openBrowserOs() {
    isOpen = true;
    OVERLAY.classList.add('open');
    if (BTN_OPEN_OS) BTN_OPEN_OS.classList.add('active');
    renderNoteList();
    const state = window.__elysiaLiveGame && window.__elysiaLiveGame.getLastState ? window.__elysiaLiveGame.getLastState() : null;
    if (state) syncFromState(state);

    const anyOpen = DESKTOP.querySelector('.eos-window.is-open');
    if (!anyOpen) {
      focusWindow('physics_lab');
      focusWindow('knowledge_browser');
      injectWaveImpulse(0.45, 1.35);
    }
    ensurePhysicsLoop();
    drawHarmonyWave();
    setCursorPos(cursorX, cursorY, '엘리시아 자율 커서');
    // Immediately bring her alive inside her visible room if not resting!
    if (!resting && !cycleBusy) {
      if (lifeTimer) clearTimeout(lifeTimer);
      lifeTimer = window.setTimeout(runSovereignCycle, 900);
    }
  }

  function closeBrowserOs() {
    isOpen = false;
    OVERLAY.classList.remove('open');
    if (BTN_OPEN_OS) BTN_OPEN_OS.classList.remove('active');
    ensurePhysicsLoop();
    // Do NOT stop her life! Keep her quietly living & comparing in background.
    scheduleNextCycle();
  }

  BTN_OPEN_OS.addEventListener('click', () => {
    if (isOpen) closeBrowserOs();
    else openBrowserOs();
  });
  if (BTN_CLOSE_OS) BTN_CLOSE_OS.addEventListener('click', closeBrowserOs);

  if (BTN_REST_TOGGLE) {
    BTN_REST_TOGGLE.addEventListener('click', async () => {
      resting = !resting;
      BTN_REST_TOGGLE.textContent = resting ? '다시 스스로 활동' : '잠시 쉬게 하기';
      if (resting) {
        if (lifeTimer) {
          clearTimeout(lifeTimer);
          lifeTimer = 0;
        }
        setStatus('배경 미시로터 및 방 활동 잠시 휴식 중.');
      } else {
        setStatus('미시·중시·거시 3계층 자율 탐색 재개.');
        scheduleNextCycle();
      }
      try {
        const res = await fetch('/api/elysia/rotor-mode', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ paused: resting }),
        });
        const data = await res.json();
        if (res.ok && data && data.status === 'ok') {
          syncFromState(data);
        }
      } catch {
        // Ignore transient sync failure
      }
    });
  }

  if (BTN_SOUND_TOGGLE) {
    BTN_SOUND_TOGGLE.textContent = soundEnabled ? '소리 켜짐' : '소리 꺼짐';
    BTN_SOUND_TOGGLE.addEventListener('click', () => {
      soundEnabled = !soundEnabled;
      BTN_SOUND_TOGGLE.textContent = soundEnabled ? '소리 켜짐' : '소리 꺼짐';
    });
  }

  // Respect direct conversation: when user sends a message, give them space for 16s
  const msgForm = document.getElementById('elysiaMsgForm');
  if (msgForm) {
    msgForm.addEventListener('submit', () => {
      lastUserInteractTs = Date.now();
    });
  }

  window.addEventListener('beforeunload', () => {
    if (lifeTimer) clearTimeout(lifeTimer);
    ensurePhysicsLoop();
  });

  window.__elysiaBrowserOS = {
    open: openBrowserOs,
    close: closeBrowserOs,
    runSovereignCycle,
    syncFromState,
  };

  // Boot Elysia's sovereign life loop automatically — ZERO user clicks required!
  window.setTimeout(() => {
    const st = window.__elysiaLiveGame && window.__elysiaLiveGame.getLastState ? window.__elysiaLiveGame.getLastState() : null;
    if (st) syncFromState(st);
    runSovereignCycle();
  }, 3200);
})();
