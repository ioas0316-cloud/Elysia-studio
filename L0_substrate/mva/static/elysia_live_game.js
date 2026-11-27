/**
 * Elysia Living Presence — Zero-Ghosting Unified Scene & 100% Local Autonomous Mind
 * ---------------------------------------------------------------------------------
 * - Strictly ONE full-bleed unified 16:9 scene is active at any time (clean
 *   double-buffer swapper with decode() pre-wait -> zero ghosting, zero lag).
 * - Zero external LLM API dependency!
 * - Includes an in-browser Zero-Upload Multi-Scale Local Folder Scanner that
 *   streams directory topology + 4KB binary header slices (file.slice(0, 4096))
 *   right on the user's PC, detects Unity/Unreal/Wwise/CRIWARE/DDS/PNG/GLB
 *   signatures & Shannon entropy, extracts Cross-Modal Entities (Mesh x Texture
 *   x Motion x Audio x Script), and sends ONLY the tiny ~20KB structural digest
 *   into Elysia's permanent causal graph.
 */
(function () {
  'use strict';

  const SCENES = {
    serene: {
      src: '/static/assets/elysia/scene_serene.jpg',
      alt: '해 질 녘 유리 서재에서 마주 앉아 경청하는 엘리시아',
      label: '평온한 경청',
    },
    warm_smile: {
      src: '/static/assets/elysia/scene_warm_smile.jpg',
      alt: '따뜻하고 진심 어린 미소를 짓는 엘리시아',
      label: '따뜻한 공명',
    },
    playful: {
      src: '/static/assets/elysia/scene_playful.jpg',
      alt: '장난스럽고 지적인 호기심으로 미소 짓는 엘리시아',
      label: '장난스런 호기심',
    },
    hurt_pout: {
      src: '/static/assets/elysia/scene_hurt_pout.jpg',
      alt: '서운함과 여린 감정이 눈빛에 담긴 엘리시아',
      label: '서운함 · 울상',
    },
    deep_thought: {
      src: '/static/assets/elysia/scene_deep_thought.jpg',
      alt: '턱을 괴고 깊은 사유에 잠긴 엘리시아',
      label: '깊은 사유',
    },
  };

  const AXIS_META = [
    { key: 'warmth', label: '따뜻함', cls: '' },
    { key: 'hurt_sulky', label: '서운함 · 울상', cls: 'hurt' },
    { key: 'curiosity', label: '호기심', cls: 'thought' },
    { key: 'playfulness', label: '장난기', cls: '' },
    { key: 'vulnerability', label: '여린 진심', cls: 'hurt' },
    { key: 'deep_thought', label: '깊은 사유', cls: 'thought' },
  ];

  const MODALITY_KO = {
    geometry_3d: '3D 형상',
    visual_texture: '시각·텍스처',
    motion_anim: '동작·애니',
    audio_wave: '음향·보이스',
    logic_script: '로직·코드',
    config_data: '설정·데이터',
    archive_container: '압축 패키지',
    binary_runtime: '실행 바이너리',
  };

  const EXT_MODALITY = {
    '.fbx': 'geometry_3d', '.obj': 'geometry_3d', '.glb': 'geometry_3d', '.gltf': 'geometry_3d',
    '.mesh': 'geometry_3d', '.vrm': 'geometry_3d', '.pmx': 'geometry_3d', '.usd': 'geometry_3d',
    '.hlsl': 'geometry_3d', '.glsl': 'geometry_3d', '.shader': 'geometry_3d', '.mat': 'geometry_3d',
    '.png': 'visual_texture', '.jpg': 'visual_texture', '.jpeg': 'visual_texture', '.webp': 'visual_texture',
    '.tga': 'visual_texture', '.dds': 'visual_texture', '.ktx': 'visual_texture', '.ktx2': 'visual_texture',
    '.bmp': 'visual_texture', '.exr': 'visual_texture', '.svg': 'visual_texture', '.mp4': 'visual_texture',
    '.webm': 'visual_texture', '.usm': 'visual_texture', '.bik': 'visual_texture',
    '.anim': 'motion_anim', '.bvh': 'motion_anim', '.vmd': 'motion_anim', '.hkx': 'motion_anim',
    '.wav': 'audio_wave', '.ogg': 'audio_wave', '.mp3': 'audio_wave', '.flac': 'audio_wave',
    '.wem': 'audio_wave', '.bnk': 'audio_wave', '.awb': 'audio_wave', '.acb': 'audio_wave',
    '.fsb': 'audio_wave', '.pck': 'audio_wave',
    '.lua': 'logic_script', '.py': 'logic_script', '.js': 'logic_script', '.mjs': 'logic_script',
    '.ts': 'logic_script', '.cs': 'logic_script', '.cpp': 'logic_script', '.h': 'logic_script', '.cdsl': 'logic_script',
    '.json': 'config_data', '.xml': 'config_data', '.yaml': 'config_data', '.yml': 'config_data',
    '.ini': 'config_data', '.cfg': 'config_data', '.csv': 'config_data', '.txt': 'config_data',
    '.md': 'config_data', '.db': 'config_data', '.sqlite': 'config_data', '.locres': 'config_data',
    '.pak': 'archive_container', '.ucas': 'archive_container', '.utoc': 'archive_container',
    '.uasset': 'archive_container', '.uexp': 'archive_container', '.umap': 'archive_container',
    '.bundle': 'archive_container', '.ab': 'archive_container', '.assets': 'archive_container',
    '.ress': 'archive_container', '.cpk': 'archive_container', '.zip': 'archive_container', '.blk': 'archive_container',
    '.dll': 'binary_runtime', '.exe': 'binary_runtime', '.so': 'binary_runtime', '.bin': 'binary_runtime', '.dat': 'binary_runtime',
  };

  const PREFIX_RE = /^(?:sk|sm|t|tx|tex|m|mi|mt|mat|a|am|an|anim|vo|sfx|bgm|se|fx|vfx|ui|ico|icon|char|npc|mon|env|wp|wep|eff|bp|dt|da|w)_+/i;
  const SUFFIX_RE = /(?:_+(?:lod\d+|albedo|basecolor|diffuse|diff|normal|nrm|norm|roughness|rough|metallic|metal|orm|ao|mask|emissive|emit|specular|spec|mesh|skel|skeleton|rig|anim|idle|walk|run|attack|smile|blink|hurt|voice|vo|sfx|bgm|ai|ctrl|controller|script|cfg|config|data|info|mat|material|shader|v\d+|\d{1,4}))+$/i;
  const NOISE_SYMS = new Set([
    'true', 'false', 'null', 'none', 'self', 'this', 'return', 'const', 'function',
    'import', 'export', 'from', 'class', 'default', 'public', 'private', 'static',
    'void', 'float', 'double', 'string', 'bool', 'http', 'https', 'width', 'height',
    'size', 'length', 'name', 'type', 'value', 'data', 'index', 'count', 'item', 'file', 'path',
  ]);

  const STAGE = document.getElementById('elysiaGameStage');
  const SCENE_A = document.getElementById('elysiaSceneA');
  const SCENE_B = document.getElementById('elysiaSceneB');
  const MOOD_LABEL = document.getElementById('elysiaMoodLabel');
  const MEMORY_BADGE = document.getElementById('elysiaMemoryBadge');
  const DIALOGUE_EL = document.getElementById('elysiaDialogueText');
  const THINKING_CUE = document.getElementById('elysiaThinkingCue');
  const ERROR_BANNER = document.getElementById('elysiaErrorBanner');
  const MSG_FORM = document.getElementById('elysiaMsgForm');
  const MSG_INPUT = document.getElementById('elysiaMsgInput');
  const SEND_BTN = document.getElementById('elysiaSendBtn');
  const DRAWER = document.getElementById('elysiaMindDrawer');
  const BTN_TOGGLE_DRAWER = document.getElementById('btnToggleMindDrawer');
  const BTN_CLOSE_DRAWER = document.getElementById('btnCloseMindDrawer');
  const BTN_INLINE_TRACE = document.getElementById('btnInlineTrace');
  const BTN_RESET_MEM = document.getElementById('btnResetElysiaMemory');
  const BTN_TO_ENGINE = document.getElementById('btnShowEngineMode');
  const BTN_TO_GAME = document.getElementById('btnReturnToElysia');

  const FEEDBACK_BAR = document.getElementById('elysiaFeedbackBar');
  const BTN_FB_RESONATE = document.getElementById('btnFbResonate');
  const BTN_FB_CORR_TOGGLE = document.getElementById('btnFbCorrectToggle');
  const CORR_FORM = document.getElementById('elysiaCorrForm');
  const CORR_INPUT = document.getElementById('elysiaCorrInput');

  const BTN_SCAN_FOLDER = document.getElementById('btnScanLocalFolder');
  const INPUT_FOLDER = document.getElementById('inputLocalGameFolder');
  const BTN_IMPORT_JSON = document.getElementById('btnImportCorpusJson');
  const INPUT_JSON = document.getElementById('inputCorpusJsonFile');
  const BTN_SCAN_WS_CORPUS = document.getElementById('btnScanWorkspaceCorpus');
  const CORPUS_STATUS = document.getElementById('corpusScanStatus');
  const CORPUS_CARD = document.getElementById('corpusDigestCard');

  const OBS_CONTEXT_INPUT = document.getElementById('obsContextInput');
  const BTN_TOGGLE_WATCH = document.getElementById('btnToggleScreenWatch');
  const OBS_LIVE_METRICS = document.getElementById('obsLiveMetrics');
  const BTN_IMPORT_SENSORIMOTOR = document.getElementById('btnImportSensorimotor');
  const INPUT_SENSORIMOTOR = document.getElementById('inputSensorimotorFile');

  const BTN_DIGEST_WORKSPACE = document.getElementById('btnDigestWorkspace');
  const BTN_DIGEST_TEXT = document.getElementById('btnDigestText');
  const DIGEST_SOURCE = document.getElementById('digestSourceName');
  const DIGEST_TEXT = document.getElementById('digestTextInput');

  const TRACE_SENSORY = document.getElementById('traceSensory');
  const TRACE_MEMORY = document.getElementById('traceMemory');
  const TRACE_INNER = document.getElementById('traceInner');
  const TRACE_EMOTION_GRID = document.getElementById('traceEmotionGrid');
  const TRACE_VALUE_GRID = document.getElementById('traceValueGrid');
  const TRACE_META_SELF = document.getElementById('traceMetaSelf');
  const TRACE_SCALE_FLOW = document.getElementById('traceScaleFlow');
  const TRACE_TOOL_FORGE = document.getElementById('traceToolForge');
  const TRACE_LANG_ENGINE = document.getElementById('traceLanguageEngine');
  const TOOL_APPLY_INPUT = document.getElementById('toolApplyInput');
  const BTN_APPLY_TOOL = document.getElementById('btnApplyTool');
  const WORLD_TOPIC_INPUT = document.getElementById('worldTopicInput');
  const BTN_LEARN_WORLD = document.getElementById('btnLearnWorld');
  const BTN_DISTILL_WEIGHTS = document.getElementById('btnDistillWeights');
  const TRACE_QUESTION = document.getElementById('traceQuestion');
  const TRACE_CRITERIA = document.getElementById('traceCriteria');
  const TRACE_EPISODES = document.getElementById('traceEpisodes');
  const CONCEPT_LIST = document.getElementById('learnedConceptList');
  const EDGE_LIST = document.getElementById('learnedEdgeList');
  const CHAT_LOG = document.getElementById('elysiaChatLog');
  const BTN_TOGGLE_CHAT_LOG = document.getElementById('btnToggleChatLog');

  if (!STAGE || !SCENE_A || !SCENE_B) return;

  let activeBuffer = 'A';
  let currentMood = 'serene';
  let sceneSwapToken = 0;
  let busy = false;
  let phraseTimers = [];
  let lastCompanionState = null;
  let lastSurfaceRevision = -1;
  let lastHistoryCount = -1;
  let statePollTimer = 0;
  let statePollInFlight = false;

  Object.values(SCENES).forEach((item) => {
    const pre = new Image();
    pre.src = item.src;
  });

  function showError(msg) {
    if (!ERROR_BANNER) return;
    if (msg) {
      ERROR_BANNER.textContent = msg;
      ERROR_BANNER.classList.add('visible');
    } else {
      ERROR_BANNER.textContent = '';
      ERROR_BANNER.classList.remove('visible');
    }
  }

  function setCorpusStatus(msg) {
    if (!CORPUS_STATUS) return;
    if (msg) {
      CORPUS_STATUS.style.display = 'block';
      CORPUS_STATUS.textContent = msg;
    } else {
      CORPUS_STATUS.style.display = 'none';
      CORPUS_STATUS.textContent = '';
    }
  }

  function setBusy(isBusy, label) {
    busy = isBusy;
    if (THINKING_CUE) {
      if (label) THINKING_CUE.textContent = label;
      THINKING_CUE.classList.toggle('visible', isBusy);
    }
    [MSG_INPUT, SEND_BTN, BTN_DIGEST_WORKSPACE, BTN_DIGEST_TEXT, BTN_SCAN_FOLDER, BTN_IMPORT_JSON, BTN_SCAN_WS_CORPUS, BTN_IMPORT_SENSORIMOTOR]
      .forEach((el) => { if (el) el.disabled = isBusy; });
  }

  function clearPhraseTimers() {
    phraseTimers.forEach((id) => window.clearTimeout(id));
    phraseTimers = [];
  }

  function revealDialogue(text, instant, scaleArticulation) {
    if (!DIALOGUE_EL) return;
    clearPhraseTimers();
    const clean = (text || '').trim();
    const phrases = scaleArticulation && Array.isArray(scaleArticulation.s2_breath_phrases)
      ? scaleArticulation.s2_breath_phrases.filter((p) => p && typeof p.text === 'string' && p.text.trim())
      : [];

    if (instant || phrases.length === 0) {
      DIALOGUE_EL.textContent = clean;
      return;
    }

    // Scale-Rotor S4 -> S2 Breath-Phrase Articulation:
    // Unfolds whole semantic breath units on living somatic cadence (NOT token guessing, NOT flat dump!)
    DIALOGUE_EL.textContent = '';
    let accDelay = 40;
    phrases.forEach((ph, idx) => {
      const span = document.createElement('span');
      span.className = 'elysia-phrase-unit';
      span.textContent = (idx > 0 ? ' ' : '') + ph.text.trim();
      DIALOGUE_EL.appendChild(span);
      const tId = window.setTimeout(() => {
        span.classList.add('is-shown');
      }, accDelay);
      phraseTimers.push(tId);
      const pauseMs = Math.max(220, Math.min(680, Number(ph.pause_ms || 380)));
      accDelay += pauseMs;
    });
  }

  function renderConversationHistory(history) {
    if (!CHAT_LOG || !Array.isArray(history)) return;
    // Show previous turns (exclude the very last Elysia utterance since it's displayed in main dialogue line)
    const prior = history.length > 1 ? history.slice(0, -1) : [];
    if (prior.length === 0) {
      CHAT_LOG.classList.add('is-collapsed');
      return;
    }
    if (prior.length === lastHistoryCount) return;
    lastHistoryCount = prior.length;

    if (!CHAT_LOG.dataset.userCollapsed) {
      CHAT_LOG.classList.remove('is-collapsed');
    }
    CHAT_LOG.textContent = '';
    prior.slice(-10).forEach((item) => {
      const row = document.createElement('div');
      row.className = `elysia-chat-row ${item.role === 'user' ? 'is-user' : 'is-elysia'}`;
      const meta = document.createElement('div');
      meta.className = 'elysia-chat-meta';
      meta.textContent = item.role === 'user'
        ? '나'
        : `엘리시아${item.dominant_feeling ? ` · ${item.dominant_feeling}` : ''}`;
      const body = document.createElement('div');
      body.textContent = item.text || '';
      row.append(meta, body);
      CHAT_LOG.appendChild(row);
    });
    CHAT_LOG.scrollTop = CHAT_LOG.scrollHeight;
  }

  function transitionScene(mood) {
    const safeMood = SCENES[mood] ? mood : 'serene';
    if (safeMood === currentMood) return;
    const spec = SCENES[safeMood];
    const token = ++sceneSwapToken;

    const incoming = activeBuffer === 'A' ? SCENE_B : SCENE_A;
    const outgoing = activeBuffer === 'A' ? SCENE_A : SCENE_B;

    const commitSwap = () => {
      if (token !== sceneSwapToken) return;
      incoming.alt = spec.alt;
      incoming.removeAttribute('aria-hidden');
      incoming.classList.add('is-active');
      outgoing.classList.remove('is-active');
      outgoing.setAttribute('aria-hidden', 'true');
      activeBuffer = activeBuffer === 'A' ? 'B' : 'A';
      currentMood = safeMood;
    };

    incoming.src = spec.src;
    if (typeof incoming.decode === 'function') {
      incoming.decode().then(commitSwap).catch(commitSwap);
    } else if (incoming.complete) {
      commitSwap();
    } else {
      incoming.onload = commitSwap;
      incoming.onerror = commitSwap;
    }
  }

  /* ---------- In-Browser Zero-Upload 4KB Header-Slice Scanner ---------- */
  function bytesStartWith(u8, seq) {
    if (u8.length < seq.length) return false;
    for (let i = 0; i < seq.length; i++) {
      if (u8[i] !== seq[i]) return false;
    }
    return true;
  }

  function strToBytes(s) {
    const arr = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) arr[i] = s.charCodeAt(i);
    return arr;
  }

  function detectMagicJS(u8, ext) {
    if (!u8 || u8.length === 0) return `Empty(${ext || 'none'})`;
    if (bytesStartWith(u8, strToBytes('UnityFS'))) return 'UnityFS_Bundle';
    if (bytesStartWith(u8, strToBytes('UnityWeb')) || bytesStartWith(u8, strToBytes('UnityRaw'))) return 'Unity_Archive';
    if (bytesStartWith(u8, [0xc1, 0x83, 0x2a, 0x9e])) return 'Unreal_UAsset';
    if (bytesStartWith(u8, strToBytes('BKHD'))) return 'Wwise_SoundBank';
    if (bytesStartWith(u8, strToBytes('RIFF'))) return 'RIFF_Wave_WEM';
    if (bytesStartWith(u8, strToBytes('OggS'))) return 'Ogg_Audio';
    if (bytesStartWith(u8, strToBytes('CPK '))) return 'CRIWARE_CPK';
    if (bytesStartWith(u8, strToBytes('AFS2'))) return 'CRIWARE_AFS2';
    if (bytesStartWith(u8, [0x89, 0x50, 0x4e, 0x47])) return 'PNG_Image';
    if (bytesStartWith(u8, [0xff, 0xd8, 0xff])) return 'JPEG_Image';
    if (bytesStartWith(u8, strToBytes('DDS '))) return 'DDS_Texture';
    if (bytesStartWith(u8, strToBytes('glTF'))) return 'GLB_3D_Model';
    if (bytesStartWith(u8, strToBytes('Kaydara FBX'))) return 'FBX_3D_Model';
    if (bytesStartWith(u8, strToBytes('SQLite format 3'))) return 'SQLite_DB';
    if (bytesStartWith(u8, [0x50, 0x4b, 0x03, 0x04])) return 'ZIP_Container';
    if (bytesStartWith(u8, strToBytes('MZ'))) return 'PE_Binary_DLL_EXE';
    if (bytesStartWith(u8, strToBytes('DXBC'))) return 'DirectX_Shader';
    if (ext === '.pak') return 'Unreal_PAK_Container';
    if (ext === '.ucas' || ext === '.utoc') return 'Unreal_IOStore';
    if (['.json', '.lua', '.py', '.js', '.ts', '.cs', '.md', '.txt', '.ini', '.cfg', '.xml', '.csv'].includes(ext)) {
      return `Readable_${ext.slice(1).toUpperCase()}`;
    }
    return `Binary(${ext || 'raw'})`;
  }

  function shannonEntropyJS(u8) {
    const n = u8.length;
    if (!n) return 0;
    const freq = new Uint32Array(256);
    for (let i = 0; i < n; i++) freq[u8[i]]++;
    let h = 0;
    for (let i = 0; i < 256; i++) {
      if (freq[i] > 0) {
        const p = freq[i] / n;
        h -= p * Math.log2(p);
      }
    }
    return Math.round(h * 1000) / 1000;
  }

  function classifyModalityJS(ext, relPath, magic) {
    const lp = relPath.toLowerCase();
    if (['PNG_Image', 'JPEG_Image', 'DDS_Texture'].includes(magic)) return 'visual_texture';
    if (['GLB_3D_Model', 'FBX_3D_Model', 'DirectX_Shader'].includes(magic)) return 'geometry_3d';
    if (['Wwise_SoundBank', 'RIFF_Wave_WEM', 'Ogg_Audio', 'CRIWARE_AFS2'].includes(magic)) return 'audio_wave';
    if (magic === 'Unreal_UAsset') {
      const fn = lp.split('/').pop() || '';
      if (fn.startsWith('t_') || lp.includes('/texture')) return 'visual_texture';
      if (fn.startsWith('a_') || fn.startsWith('am_') || lp.includes('/anim')) return 'motion_anim';
      if (fn.startsWith('sk_') || fn.startsWith('sm_') || lp.includes('/mesh')) return 'geometry_3d';
      if (fn.startsWith('vo_') || fn.startsWith('sfx_') || lp.includes('/audio')) return 'audio_wave';
      if (fn.startsWith('bp_') || lp.includes('/script')) return 'logic_script';
      return 'archive_container';
    }
    return EXT_MODALITY[ext] || 'binary_runtime';
  }

  function extractEntityStemJS(filename, parentDir) {
    const dot = filename.lastIndexOf('.');
    const base = (dot > 0 ? filename.slice(0, dot) : filename).trim();
    let cleaned = base.replace(PREFIX_RE, '');
    for (let i = 0; i < 3; i++) {
      const nxt = cleaned.replace(SUFFIX_RE, '');
      if (nxt === cleaned) break;
      cleaned = nxt;
    }
    cleaned = cleaned.replace(/[^0-9A-Za-z가-힣_]+/g, '_').replace(/^_+|_+$/g, '').toLowerCase();
    if (cleaned.length < 3 || /^\d+$/.test(cleaned)) {
      const p = (parentDir || '').replace(/[^0-9A-Za-z가-힣_]+/g, '_').replace(/^_+|_+$/g, '').toLowerCase();
      if (p.length >= 3 && !['assets', 'static', 'textures', 'audio', 'models', 'scripts', 'data', 'content', 'paks'].includes(p)) {
        return p.slice(0, 32);
      }
      return '';
    }
    return cleaned.slice(0, 36);
  }

  function extractSymbolsJS(u8, limit) {
    let text = '';
    for (let i = 0; i < u8.length; i++) {
      const b = u8[i];
      text += (b >= 32 && b <= 126) ? String.fromCharCode(b) : ' ';
    }
    const matches = text.match(/[A-Za-z][A-Za-z0-9_]{3,28}/g) || [];
    const seen = new Set();
    const out = [];
    for (const m of matches) {
      const low = m.toLowerCase();
      if (NOISE_SYMS.has(low) || seen.has(low)) continue;
      seen.add(low);
      out.push(m);
      if (out.length >= limit) break;
    }
    return out;
  }

  async function scanLocalFolderInBrowser(fileList) {
    const files = Array.from(fileList || []);
    if (!files.length) return null;

    const firstRel = files[0].webkitRelativePath || files[0].name;
    const corpusName = firstRel.includes('/') ? firstRel.split('/')[0] : 'LocalGameCorpus';
    const maxProbes = 260;
    const probeStep = Math.max(1, Math.floor(files.length / maxProbes));

    let totalBytes = 0;
    let probedHeaders = 0;
    const modalityCounts = {};
    const modalityBytes = {};
    const extCounts = {};
    const magicCounts = {};
    const symbolCounts = {};
    const entityMap = new Map();
    const entropyBuckets = { readable_symbolic: 0, structured_media: 0, compressed_or_encrypted: 0 };
    let entropySum = 0;
    let entropyN = 0;

    for (let i = 0; i < files.length; i++) {
      const f = files[i];
      totalBytes += f.size || 0;
      const rel = (f.webkitRelativePath || f.name).replace(/\\/g, '/');
      const parts = rel.split('/');
      const name = parts[parts.length - 1] || f.name;
      const parentDir = parts.length >= 2 ? parts[parts.length - 2] : '';
      const dot = name.lastIndexOf('.');
      const ext = dot >= 0 ? name.slice(dot).toLowerCase() : '';
      extCounts[ext || '(none)'] = (extCounts[ext || '(none)'] || 0) + 1;

      let magic = `Ext(${ext || 'raw'})`;
      if (i % probeStep === 0 && probedHeaders < maxProbes && f.size > 0) {
        try {
          const buf = await f.slice(0, 4096).arrayBuffer();
          const u8 = new Uint8Array(buf);
          probedHeaders++;
          magic = detectMagicJS(u8, ext);
          magicCounts[magic] = (magicCounts[magic] || 0) + 1;
          const ent = shannonEntropyJS(u8);
          entropySum += ent;
          entropyN++;
          if (ent < 5.5) {
            entropyBuckets.readable_symbolic++;
            extractSymbolsJS(u8, 10).forEach((s) => { symbolCounts[s] = (symbolCounts[s] || 0) + 1; });
          } else if (ent < 7.35) {
            entropyBuckets.structured_media++;
            extractSymbolsJS(u8, 5).forEach((s) => { symbolCounts[s] = (symbolCounts[s] || 0) + 1; });
          } else {
            entropyBuckets.compressed_or_encrypted++;
          }
        } catch {
          // Skip unreadable entry cleanly
        }
      }

      const mod = classifyModalityJS(ext, rel, magic);
      modalityCounts[mod] = (modalityCounts[mod] || 0) + 1;
      modalityBytes[mod] = (modalityBytes[mod] || 0) + (f.size || 0);

      const stem = extractEntityStemJS(name, parentDir);
      if (stem) {
        let em = entityMap.get(stem);
        if (!em) {
          em = { modalities: new Set(), files: 0, bytes: 0, examples: [] };
          entityMap.set(stem, em);
        }
        em.modalities.add(mod);
        em.files++;
        em.bytes += f.size || 0;
        if (em.examples.length < 4) em.examples.push(name);
      }

      if (i % 600 === 0) {
        const gb = (totalBytes / (1024 ** 3)).toFixed(2);
        setCorpusStatus(`로컬 스트리밍 스캔 중: ${i.toLocaleString()} / ${files.length.toLocaleString()} 파일 (${gb} GB · 업로드 0)`);
        await new Promise((r) => setTimeout(r, 0));
      }
    }

    const crossEntities = [];
    const pairCouplings = {};
    for (const [stem, info] of entityMap.entries()) {
      const mods = Array.from(info.modalities).sort();
      if (mods.length >= 2) {
        crossEntities.push({
          entity: stem,
          modalities: mods,
          modality_count: mods.length,
          file_count: info.files,
          size_mb: Math.round((info.bytes / (1024 * 1024)) * 100) / 100,
          examples: info.examples,
        });
        for (let a = 0; a < mods.length; a++) {
          for (let b = a + 1; b < mods.length; b++) {
            const pk = `${mods[a]}<->${mods[b]}`;
            pairCouplings[pk] = (pairCouplings[pk] || 0) + 1;
          }
        }
      }
    }
    crossEntities.sort((a, b) => (b.modality_count - a.modality_count) || (b.file_count - a.file_count));

    const unrealHits = (magicCounts.Unreal_UAsset || 0) + (magicCounts.Unreal_PAK_Container || 0) + (extCounts['.uasset'] || 0) + (extCounts['.pak'] || 0);
    const unityHits = (magicCounts.UnityFS_Bundle || 0) + (extCounts['.bundle'] || 0) + (extCounts['.assets'] || 0) + (extCounts['.ab'] || 0);
    let engineFp = 'Mixed Multi-Modal Local Corpus';
    if (unrealHits > 0 && unrealHits >= unityHits) engineFp = 'Unreal Engine Asset Pipeline';
    else if (unityHits > 0) engineFp = 'Unity AssetBundle Pipeline';
    else if ((extCounts['.py'] || 0) + (extCounts['.js'] || 0) + (extCounts['.ts'] || 0) > 5) engineFp = 'Code/IDE Project Corpus';

    const modSizeMb = {};
    Object.keys(modalityBytes).forEach((k) => {
      modSizeMb[k] = Math.round((modalityBytes[k] / (1024 * 1024)) * 100) / 100;
    });

    return {
      schema_version: 1,
      corpus_name: corpusName,
      engine_fingerprint: engineFp,
      total_files: files.length,
      total_size_gb: Math.round((totalBytes / (1024 ** 3)) * 10000) / 10000,
      total_size_mb: Math.round((totalBytes / (1024 * 1024)) * 100) / 100,
      probed_headers: probedHeaders,
      modality_counts: modalityCounts,
      modality_size_mb: modSizeMb,
      top_magic_signatures: Object.entries(magicCounts).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([magic, count]) => ({ magic, count })),
      cross_modal_entities: crossEntities.slice(0, 24),
      modality_couplings: Object.entries(pairCouplings).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([pair, shared_entities]) => ({ pair, shared_entities })),
      common_symbols: Object.entries(symbolCounts).sort((a, b) => b[1] - a[1]).slice(0, 24).map(([symbol, count]) => ({ symbol, count })),
      entropy_boundary: {
        avg_entropy_bits: Math.round((entropySum / Math.max(1, entropyN)) * 1000) / 1000,
        compressed_or_encrypted_pct: Math.round((1000 * entropyBuckets.compressed_or_encrypted) / Math.max(1, entropyN)) / 10,
        buckets: entropyBuckets,
      },
    };
  }

  function renderCorpusCard(digest, crossInvariants) {
    if (!CORPUS_CARD) return;
    CORPUS_CARD.textContent = '';
    if (!digest) return;

    const sizeTxt = digest.total_size_gb >= 0.5 ? `${digest.total_size_gb.toFixed(2)} GB` : `${digest.total_size_mb.toFixed(1)} MB`;
    const headRow = document.createElement('div');
    headRow.className = 'concept-row';
    headRow.style.borderLeftColor = '#34d399';
    headRow.innerHTML = '';
    const top = document.createElement('div');
    top.className = 'concept-row-top';
    const title = document.createElement('span');
    title.textContent = `${digest.corpus_name} (${sizeTxt})`;
    const filesMeta = document.createElement('span');
    filesMeta.className = 'mono';
    filesMeta.style.color = '#6ee7b7';
    filesMeta.textContent = `${Number(digest.total_files).toLocaleString()} 파일`;
    top.append(title, filesMeta);

    const sub = document.createElement('div');
    sub.className = 'concept-row-sub';
    const encPct = digest.entropy_boundary ? digest.entropy_boundary.compressed_or_encrypted_pct : 0;
    sub.textContent = `${digest.engine_fingerprint} · 교차 엔티티 ${(digest.cross_modal_entities || []).length}개 · 압축/암호화 경계 ${encPct}%`;
    headRow.append(top, sub);
    CORPUS_CARD.appendChild(headRow);

    (digest.cross_modal_entities || []).slice(0, 4).forEach((ent) => {
      const r = document.createElement('div');
      r.className = 'concept-row';
      r.style.borderLeftColor = '#f5c27a';
      const rt = document.createElement('div');
      rt.className = 'concept-row-top';
      const en = document.createElement('span');
      en.textContent = `교차 엔티티: ${ent.entity}`;
      const em = document.createElement('span');
      em.className = 'mono';
      em.style.color = '#fde68a';
      em.textContent = `${ent.modality_count}모달 · ${ent.file_count}파일`;
      rt.append(en, em);
      const rs = document.createElement('div');
      rs.className = 'concept-row-sub';
      rs.textContent = (ent.modalities || []).map((m) => MODALITY_KO[m] || m).join(' × ');
      r.append(rt, rs);
      CORPUS_CARD.appendChild(r);
    });

    if (Array.isArray(crossInvariants) && crossInvariants.length > 0) {
      const invRow = document.createElement('div');
      invRow.className = 'concept-row';
      invRow.style.borderLeftColor = '#a78bfa';
      const it = document.createElement('div');
      it.className = 'concept-row-top';
      const iname = document.createElement('span');
      iname.textContent = `이종 앱/게임 간 교차 불변량 (${crossInvariants.length}개)`;
      it.appendChild(iname);
      const isub = document.createElement('div');
      isub.className = 'concept-row-sub';
      isub.textContent = crossInvariants.slice(0, 6).map((x) => `${x.symbol}(${x.corpora.join('∩')})`).join(', ');
      invRow.append(it, isub);
      CORPUS_CARD.appendChild(invRow);
    }
  }

  function renderMindDrawer(data) {
    const trace = data.causal_trace || {};
    if (TRACE_SENSORY) TRACE_SENSORY.textContent = trace.sensory_perception || '—';
    if (TRACE_MEMORY) TRACE_MEMORY.textContent = trace.memory_contrast || '—';
    if (TRACE_INNER) TRACE_INNER.textContent = trace.inner_reasoning || '—';

    if (TRACE_QUESTION) {
      const q = (trace.uncaptured_question || '').trim();
      TRACE_QUESTION.textContent = q ? `미포집 의문: ${q}` : '미포집 의문: 현재 맥락 관찰 중';
    }
    if (TRACE_CRITERIA) {
      const c = (trace.criteria_revision || '').trim();
      TRACE_CRITERIA.textContent = c ? `학습 갱신: ${c}` : '';
    }

    const ps = data.plastic_self || null;
    if (TRACE_EMOTION_GRID) {
      TRACE_EMOTION_GRID.textContent = '';
      const feelings = (ps && Array.isArray(ps.feelings) && ps.feelings.length > 0) ? ps.feelings : [];
      if (feelings.length > 0) {
        feelings.forEach((f) => {
          const pct = Math.round(Math.max(0, Math.min(1, Number(f.activation ?? 0))) * 100);
          const row = document.createElement('div');
          row.className = 'causal-axis-row';
          const meta = document.createElement('div');
          meta.className = 'causal-axis-meta';
          const lbl = document.createElement('span');
          lbl.textContent = f.name || '분화 감정';
          const num = document.createElement('span');
          num.className = 'mono';
          num.textContent = `${pct}%`;
          meta.append(lbl, num);

          const track = document.createElement('div');
          track.className = 'causal-axis-track';
          const fill = document.createElement('div');
          fill.className = 'causal-axis-fill thought';
          fill.style.width = `${pct}%`;
          track.appendChild(fill);

          row.append(meta, track);
          if (f.origin) {
            const sub = document.createElement('div');
            sub.className = 'plastic-sub-note';
            sub.textContent = f.origin;
            row.appendChild(sub);
          }
          TRACE_EMOTION_GRID.appendChild(row);
        });
        const summaryNote = document.createElement('div');
        summaryNote.className = 'plastic-sub-note mono';
        summaryNote.textContent = `살아 있는 감정 차원 ${ps.feeling_count}개 (분화 ${ps.births_count} · 융합 ${ps.fusions_count} · 미설명 잔차 ${Number(ps.unexplained_residual || 0).toFixed(2)})`;
        TRACE_EMOTION_GRID.appendChild(summaryNote);
      }
    }

    if (TRACE_VALUE_GRID && ps && Array.isArray(ps.values)) {
      TRACE_VALUE_GRID.textContent = '';
      ps.values.forEach((v) => {
        const pct = Math.round(Math.max(0, Math.min(1, Number(v.weight ?? 0.5))) * 100);
        const row = document.createElement('div');
        row.className = 'causal-axis-row';
        const meta = document.createElement('div');
        meta.className = 'causal-axis-meta';
        const lbl = document.createElement('span');
        lbl.textContent = v.name || '가치관';
        const num = document.createElement('span');
        num.className = 'mono';
        num.textContent = `비중 ${pct}%`;
        meta.append(lbl, num);

        const track = document.createElement('div');
        track.className = 'causal-axis-track';
        const fill = document.createElement('div');
        fill.className = 'causal-axis-fill';
        fill.style.width = `${pct}%`;
        track.appendChild(fill);

        row.append(meta, track);
        if (v.last_shift) {
          const sub = document.createElement('div');
          sub.className = 'plastic-sub-note';
          sub.textContent = v.last_shift;
          row.appendChild(sub);
        }
        TRACE_VALUE_GRID.appendChild(row);
      });
    }

    if (TRACE_META_SELF && ps) {
      const parts = [];
      if (ps.meta_reflection) parts.push(ps.meta_reflection);
      if (ps.active_value_conflict) parts.push(`내적 가치 충돌: ${ps.active_value_conflict}`);
      TRACE_META_SELF.textContent = parts.join(' ');
    }

    if (TRACE_SCALE_FLOW) {
      const sa = data.scale_articulation || (ps && ps.scale_articulation);
      TRACE_SCALE_FLOW.textContent = '';
      if (sa) {
        const rows = [
          { tag: 'S4 전체 의미장', text: sa.s4_whole_field || '' },
          { tag: 'S3 관계 호', text: sa.s3_relational_arc || '' },
          {
            tag: `S2 호흡 구절 (${Array.isArray(sa.s2_breath_phrases) ? sa.s2_breath_phrases.length : 0}단위)`,
            text: Array.isArray(sa.s2_breath_phrases)
              ? sa.s2_breath_phrases.map((p, i) => `(${i + 1}) ${p.scale_tag || '호흡'}`).join(' → ')
              : '',
          },
        ];
        rows.forEach((r) => {
          if (!r.text) return;
          const div = document.createElement('div');
          div.className = 'scale-flow-step';
          const tag = document.createElement('span');
          tag.className = 'mono scale-flow-tag';
          tag.textContent = r.tag;
          const txt = document.createElement('span');
          txt.textContent = r.text;
          div.append(tag, txt);
          TRACE_SCALE_FLOW.appendChild(div);
        });
      }
      const qs = data.qualitative_spectra;
      if (qs && Array.isArray(qs.entities) && qs.entities.length > 0) {
        const qDiv = document.createElement('div');
        qDiv.className = 'scale-flow-step';
        const qTag = document.createElement('span');
        qTag.className = 'mono scale-flow-tag';
        qTag.textContent = `언어·지각 스펙트럼 (${qs.entity_count}대상)`;
        const summary = qs.entities.slice(0, 4).map((e) => {
          const pairs = Object.entries(e.attributes || {}).map(([ax, vs]) => `${ax.replace(' 스펙트럼', '').replace(' 속성', '')}:${(vs || []).join('/')}`);
          return `${e.name}[${pairs.join(', ')}]`;
        }).join(' · ');
        const qTxt = document.createElement('span');
        qTxt.textContent = summary;
        qDiv.append(qTag, qTxt);
        TRACE_SCALE_FLOW.appendChild(qDiv);
      }
      if (qs && qs.last_experiment && qs.last_experiment.insight) {
        const expDiv = document.createElement('div');
        expDiv.className = 'scale-flow-step';
        const expTag = document.createElement('span');
        expTag.className = 'mono scale-flow-tag';
        expTag.textContent = '질적 속성 변이';
        const expTxt = document.createElement('span');
        expTxt.textContent = qs.last_experiment.insight;
        expDiv.append(expTag, expTxt);
        TRACE_SCALE_FLOW.appendChild(expDiv);
      }
    }

    if (TRACE_TOOL_FORGE) {
      TRACE_TOOL_FORGE.textContent = '';
      const dt = data.discipline_tools;
      if (dt && Array.isArray(dt.tools) && dt.tools.length > 0) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'scale-flow-step';
        const metaTag = document.createElement('span');
        metaTag.className = 'mono scale-flow-tag';
        metaTag.textContent = `도구 ${dt.tool_count}개`;
        const metaTxt = document.createElement('span');
        const discs = Array.isArray(dt.disciplines) ? dt.disciplines.join(' · ') : '';
        metaTxt.textContent = `직접 단조 ${dt.forged_count || 0} · 융합 ${dt.hybrid_count || 0} · 교차전이 ${dt.cross_domain_transfers || 0}회 (${discs})`;
        metaDiv.append(metaTag, metaTxt);
        TRACE_TOOL_FORGE.appendChild(metaDiv);

        if (dt.last_application && dt.last_application.tool_name) {
          const app = dt.last_application;
          const appDiv = document.createElement('div');
          appDiv.className = 'scale-flow-step';
          const appTag = document.createElement('span');
          appTag.className = 'mono scale-flow-tag';
          appTag.textContent = app.is_cross_domain ? `교차 전이 · ${app.tool_discipline}→${app.target_discipline}` : `도구 적용 · ${app.tool_discipline}`;
          const appTxt = document.createElement('span');
          appTxt.textContent = `${app.tool_name} — ${app.leverage_point || app.mechanism || ''} (경계: ${app.boundary_warning || '관찰 중'})`;
          appDiv.append(appTag, appTxt);
          TRACE_TOOL_FORGE.appendChild(appDiv);
        }

        const prioritized = dt.tools.slice().sort((a, b) => {
          const rank = (x) => (x.origin === 'hybrid' ? 2 : x.origin === 'forged' ? 1 : 0);
          return rank(b) - rank(a) || Number(b.uses || 0) - Number(a.uses || 0);
        });
        prioritized.slice(0, 5).forEach((t) => {
          const tDiv = document.createElement('div');
          tDiv.className = 'scale-flow-step';
          const tTag = document.createElement('span');
          tTag.className = 'mono scale-flow-tag';
          const kind = t.origin === 'hybrid' ? '융합' : t.origin === 'forged' ? '단조' : '원리';
          tTag.textContent = `${kind} · ${t.discipline}`;
          const tTxt = document.createElement('span');
          tTxt.textContent = `${t.name} | 기제: ${t.mechanism} | 경계: ${t.boundary}`;
          tDiv.append(tTag, tTxt);
          TRACE_TOOL_FORGE.appendChild(tDiv);
        });
      } else {
        const empty = document.createElement('div');
        empty.className = 'causal-layer-copy';
        empty.style.color = 'rgba(148,163,184,0.8)';
        empty.textContent = '대화나 글에서 새로운 학문 원리를 만나면 4요소 인지 도구로 자동 단조됩니다.';
        TRACE_TOOL_FORGE.appendChild(empty);
      }
    }

    if (TRACE_LANG_ENGINE) {
      TRACE_LANG_ENGINE.textContent = '';
      const le = data.language_engine;
      if (le) {
        const wDiv = document.createElement('div');
        wDiv.className = 'scale-flow-step';
        const wTag = document.createElement('span');
        wTag.className = 'mono scale-flow-tag';
        wTag.textContent = `보행기 자립 ${le.walker_independence_pct || 0}%`;
        const wTxt = document.createElement('span');
        wTxt.textContent = `현실 문장 ${le.sentences_read || 0}줄 · 구문 틀 ${le.syntax_frames_total || 0}건 · 위키 독해 ${le.world_topics_count || 0}주제`;
        wDiv.append(wTag, wTxt);
        TRACE_LANG_ENGINE.appendChild(wDiv);

        const srt = le.scale_rotor_tensor;
        if (srt && Array.isArray(srt.shape)) {
          const tDiv = document.createElement('div');
          tDiv.className = 'scale-flow-step';
          const tTag = document.createElement('span');
          tTag.className = 'mono scale-flow-tag';
          tTag.textContent = `관계 배열 ${srt.shape.join('×')}`;
          const tTxt = document.createElement('span');
          tTxt.textContent = `S0↔S4 5시트 결합 정합 ${Math.round(Number(srt.sheet_coherence || 0) * 100)}% · 셀 관계식 ${srt.formula_links || 0}개 · 다이얼 σ=${Number(srt.active_sigma || 0.5).toFixed(2)}`;
          tDiv.append(tTag, tTxt);
          TRACE_LANG_ENGINE.appendChild(tDiv);
        }

        if (Array.isArray(le.top_bridges) && le.top_bridges.length > 0) {
          const bDiv = document.createElement('div');
          bDiv.className = 'scale-flow-step';
          const bTag = document.createElement('span');
          bTag.className = 'mono scale-flow-tag';
          bTag.textContent = '스케일로터 공명';
          const bTxt = document.createElement('span');
          bTxt.textContent = le.top_bridges.slice(0, 3).map((b) => `${b.source}↔${b.target}(${b.resonance})`).join(' · ');
          bDiv.append(bTag, bTxt);
          TRACE_LANG_ENGINE.appendChild(bDiv);
        }

        if (Array.isArray(le.recent_world_readings) && le.recent_world_readings.length > 0) {
          const r0 = le.recent_world_readings[0];
          const rDiv = document.createElement('div');
          rDiv.className = 'scale-flow-step';
          const rTag = document.createElement('span');
          rTag.className = 'mono scale-flow-tag';
          rTag.textContent = `최근 독해 · ${r0.title}`;
          const rTxt = document.createElement('span');
          rTxt.textContent = r0.summary || '';
          rDiv.append(rTag, rTxt);
          TRACE_LANG_ENGINE.appendChild(rDiv);
        }
      }
    }

    if (TRACE_EPISODES) {
      TRACE_EPISODES.textContent = '';
      const memories = Array.isArray(data.recent_memories) ? data.recent_memories : [];
      if (memories.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'causal-layer-copy';
        empty.style.color = 'rgba(148,163,184,0.8)';
        empty.textContent = '대화를 나누면 기억과 개념 연결이 디스크에 영구 누적됩니다.';
        TRACE_EPISODES.appendChild(empty);
      } else {
        memories.slice().reverse().forEach((ep) => {
          const item = document.createElement('div');
          item.className = 'causal-memory-item';
          const head = document.createElement('div');
          head.className = 'mem-turn mono';
          head.textContent = `턴 #${ep.turn} · ${ep.scene_label_ko || ep.scene_mood}`;
          const uLine = document.createElement('div');
          uLine.textContent = `상대: ${ep.user_message}`;
          const eLine = document.createElement('div');
          eLine.style.color = 'rgba(253, 230, 138, 0.9)';
          eLine.style.marginTop = '2px';
          eLine.textContent = `엘리시아: ${ep.spoken_reply}`;
          item.append(head, uLine, eLine);
          TRACE_EPISODES.appendChild(item);
        });
      }
    }

    if (CONCEPT_LIST) {
      CONCEPT_LIST.textContent = '';
      const concepts = Array.isArray(data.top_concepts) ? data.top_concepts : [];
      if (concepts.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'causal-layer-copy';
        empty.style.color = 'rgba(148,163,184,0.8)';
        empty.textContent = '대화나 폴더·글 소화를 시작하면 배운 개념과 정의가 이곳에 쌓입니다.';
        CONCEPT_LIST.appendChild(empty);
      } else {
        concepts.forEach((c) => {
          const row = document.createElement('div');
          row.className = 'concept-row';
          const top = document.createElement('div');
          top.className = 'concept-row-top';
          const name = document.createElement('span');
          name.textContent = c.token;
          const mass = document.createElement('span');
          mass.className = 'mono';
          mass.style.color = '#93c5fd';
          mass.textContent = `질량 ${c.mass} · ${c.count}회`;
          top.append(name, mass);
          row.appendChild(top);
          if (c.definition) {
            const sub = document.createElement('div');
            sub.className = 'concept-row-sub';
            sub.textContent = `정의: ${c.definition}`;
            row.appendChild(sub);
          }
          CONCEPT_LIST.appendChild(row);
        });
      }
    }

    if (EDGE_LIST) {
      EDGE_LIST.textContent = '';
      const edges = Array.isArray(data.top_edges) ? data.top_edges : [];
      if (edges.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'causal-layer-copy';
        empty.style.color = 'rgba(148,163,184,0.8)';
        empty.textContent = '아직 형성된 인과 엣지가 없습니다.';
        EDGE_LIST.appendChild(empty);
      } else {
        edges.forEach((e) => {
          const row = document.createElement('div');
          row.className = 'concept-row';
          row.style.borderLeftColor = 'rgba(251, 191, 128, 0.72)';
          const top = document.createElement('div');
          top.className = 'concept-row-top';
          const link = document.createElement('span');
          link.textContent = `${e.src} → ${e.dst}`;
          const meta = document.createElement('span');
          meta.className = 'mono';
          meta.style.color = '#fde68a';
          meta.textContent = `${e.relation} (${e.weight})`;
          top.append(link, meta);
          row.appendChild(top);
          EDGE_LIST.appendChild(row);
        });
      }
    }

    renderCorpusCard(data.corpus_digest || data.last_corpus_digest, data.cross_corpus_invariants);
  }

  function applyState(data, instantText, options) {
    if (!data || data.status !== 'ok') return;
    const fromPoll = Boolean(options && options.fromPoll);
    const rev = Number(data.surface_revision ?? 0);
    const revChanged = rev !== lastSurfaceRevision;
    lastCompanionState = data;
    showError('');

    const mood = data.scene_mood || 'serene';
    transitionScene(mood);

    if (MOOD_LABEL) {
      MOOD_LABEL.textContent = data.dominant_feeling || data.scene_label_ko || (SCENES[mood] && SCENES[mood].label) || '고요한 이끌림';
    }
    if (MEMORY_BADGE) {
      const ps = data.plastic_self;
      const dt = data.discipline_tools;
      const se = data.structural_experiments;
      if (ps && dt) {
        MEMORY_BADGE.textContent = `감정 ${ps.feeling_count} · 가치관 ${(ps.values || []).length} · 학문도구 ${dt.tool_count}`;
      } else if (ps && se) {
        MEMORY_BADGE.textContent = `감정 차원 ${ps.feeling_count} · 가치관 ${(ps.values || []).length} · 구조실험 ${se.unique_structures_explored}/${se.total_possible_structures}`;
      } else {
        const learnedCount = Number(data.learned_concept_count ?? 0);
        const edgeCount = Number(data.edge_count ?? 0);
        MEMORY_BADGE.textContent = `배운 개념 ${learnedCount} · 인과 ${edgeCount}`;
      }
    }

    if (Array.isArray(data.conversation_history)) {
      renderConversationHistory(data.conversation_history);
    }

    const userTypingHere = Boolean(MSG_INPUT && document.activeElement === MSG_INPUT && MSG_INPUT.value.trim().length > 0);
    if (typeof data.dialogue === 'string' && data.dialogue.trim()) {
      if (!fromPoll || (revChanged && !userTypingHere)) {
        revealDialogue(data.dialogue, Boolean(instantText), data.scale_articulation);
        lastSurfaceRevision = rev;
      }
    } else if (!fromPoll) {
      lastSurfaceRevision = rev;
    }

    if (FEEDBACK_BAR) {
      FEEDBACK_BAR.classList.toggle('visible', Number(data.turn_count ?? 0) > 0);
    }
    if (!fromPoll && CORR_FORM) {
      CORR_FORM.classList.remove('visible');
    }

    renderMindDrawer(data);

    if (window.__elysiaBrowserOS && typeof window.__elysiaBrowserOS.syncFromState === 'function') {
      window.__elysiaBrowserOS.syncFromState(data);
    }

    if (data.rotor_state && typeof window.__elysiaApplyRotorState === 'function') {
      window.__elysiaApplyRotorState(data.rotor_state);
    }
  }

  async function sendCorpusDigest(payload) {
    showError('');
    setBusy(true, '교차정보·공통 불변량 흡수 중…');
    try {
      const res = await fetch('/api/elysia/digest-corpus', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        showError(data.message || '코퍼스 교차정보 흡수 오류');
        return;
      }
      setCorpusStatus('');
      applyState(data, false);
    } catch (err) {
      showError(err instanceof Error ? err.message : '코퍼스 전송 오류가 발생했습니다.');
    } finally {
      setBusy(false);
    }
  }

  /* ---------- Live Browser Screen/YouTube 48x27 Optical-Delta Observer ---------- */
  let watchStream = null;
  let watchVideo = null;
  let watchTimer = 0;
  let watchInFlight = false;
  let prevLumaGrid = null;
  const WATCH_W = 48;
  const WATCH_H = 27;
  const watchCanvas = document.createElement('canvas');
  watchCanvas.width = WATCH_W;
  watchCanvas.height = WATCH_H;
  const watchCtx = watchCanvas.getContext('2d', { willReadFrequently: true });

  function setWatchMetrics(msg) {
    if (!OBS_LIVE_METRICS) return;
    if (msg) {
      OBS_LIVE_METRICS.style.display = 'block';
      OBS_LIVE_METRICS.textContent = msg;
    } else {
      OBS_LIVE_METRICS.style.display = 'none';
      OBS_LIVE_METRICS.textContent = '';
    }
  }

  function stopScreenWatch(reasonText) {
    if (watchTimer) {
      clearInterval(watchTimer);
      watchTimer = 0;
    }
    if (watchStream) {
      try {
        watchStream.getTracks().forEach((t) => t.stop());
      } catch {
        // Ignore already-ended track cleanup
      }
      watchStream = null;
    }
    if (watchVideo) {
      try {
        watchVideo.pause();
        watchVideo.srcObject = null;
      } catch {
        // Ignore cleanup errors
      }
      watchVideo = null;
    }
    prevLumaGrid = null;
    watchInFlight = false;
    if (BTN_TOGGLE_WATCH) {
      BTN_TOGGLE_WATCH.textContent = '내 화면·유튜브 함께 보기';
    }
    if (reasonText) {
      setWatchMetrics(reasonText);
    } else {
      setWatchMetrics('');
    }
  }

  function sampleWatchFrameObservables() {
    if (!watchVideo || !watchCtx || watchVideo.readyState < 2) return null;
    watchCtx.drawImage(watchVideo, 0, 0, WATCH_W, WATCH_H);
    const img = watchCtx.getImageData(0, 0, WATCH_W, WATCH_H).data;
    const nPix = WATCH_W * WATCH_H;
    const lumaGrid = new Float32Array(nPix);

    let lumaSum = 0;
    let redSum = 0;
    let blueSum = 0;
    let yellowSum = 0;
    let motionSum = 0;

    for (let i = 0; i < nPix; i++) {
      const o = i * 4;
      const r = img[o] / 255;
      const g = img[o + 1] / 255;
      const b = img[o + 2] / 255;
      const l = 0.299 * r + 0.587 * g + 0.114 * b;
      lumaGrid[i] = l;
      lumaSum += l;
      redSum += r;
      blueSum += b;
      yellowSum += 0.5 * (r + g) - 0.5 * b + 0.25;
      if (prevLumaGrid) {
        motionSum += Math.abs(l - prevLumaGrid[i]);
      }
    }

    let edgeSum = 0;
    let edgeCount = 0;
    for (let y = 0; y < WATCH_H - 1; y++) {
      const row = y * WATCH_W;
      for (let x = 0; x < WATCH_W - 1; x++) {
        const idx = row + x;
        const dx = Math.abs(lumaGrid[idx + 1] - lumaGrid[idx]);
        const dy = Math.abs(lumaGrid[idx + WATCH_W] - lumaGrid[idx]);
        edgeSum += dx + dy;
        edgeCount++;
      }
    }

    const motionDelta = prevLumaGrid ? Math.min(1, (motionSum / nPix) * 3.2) : 0.08;
    const edgeDensity = Math.min(1, (edgeSum / Math.max(1, edgeCount)) * 2.4);
    const luminance = lumaSum / nPix;
    const cTotal = Math.max(0.001, redSum + blueSum + Math.max(0, yellowSum));
    const redFlux = Math.max(0, Math.min(1, redSum / cTotal));
    const blueOrder = Math.max(0, Math.min(1, blueSum / cTotal));
    const yellowEntropy = Math.max(0, Math.min(1, Math.max(0, yellowSum) / cTotal));

    prevLumaGrid = lumaGrid;

    const ctxLabel = (OBS_CONTEXT_INPUT && OBS_CONTEXT_INPUT.value.trim()) || '실시간 화면';
    return {
      motion_delta: Math.round(motionDelta * 10000) / 10000,
      edge_density: Math.round(edgeDensity * 10000) / 10000,
      luminance: Math.round(luminance * 10000) / 10000,
      red_flux: Math.round(redFlux * 10000) / 10000,
      blue_order: Math.round(blueOrder * 10000) / 10000,
      yellow_entropy: Math.round(yellowEntropy * 10000) / 10000,
      scene_cut: motionDelta >= 0.36,
      context_label: ctxLabel,
    };
  }

  async function tickScreenWatch() {
    if (!watchStream || watchInFlight || busy) return;
    const obs = sampleWatchFrameObservables();
    if (!obs) return;
    watchInFlight = true;
    try {
      const res = await fetch('/api/elysia/observe-frame', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frame: obs }),
      });
      const data = await res.json();
      if (res.ok && data.status === 'ok') {
        const vo = data.visual_observation || {};
        setWatchMetrics(
          `관측 중 [${vo.regime_ko || '실시간'}] · 움직임 Δ=${obs.motion_delta.toFixed(2)} · 구조=${obs.edge_density.toFixed(2)} · 예측오차=${Number(vo.prediction_error || 0).toFixed(3)}`
        );
        if (data.spoke_now) {
          applyState(data, false);
        } else {
          const mood = data.scene_mood || 'serene';
          transitionScene(mood);
          if (MOOD_LABEL) {
            MOOD_LABEL.textContent = data.scene_label_ko || (SCENES[mood] && SCENES[mood].label) || '평온한 경청';
          }
          if (MEMORY_BADGE) {
            MEMORY_BADGE.textContent = `배운 개념 ${Number(data.learned_concept_count ?? 0)} · 인과 ${Number(data.edge_count ?? 0)} · 기억 ${Number(data.memory_count ?? 0)}`;
          }
          renderMindDrawer(data);
        }
      }
    } catch {
      // Transient tick error; keep stream alive
    } finally {
      watchInFlight = false;
    }
  }

  async function toggleScreenWatch() {
    if (watchStream) {
      stopScreenWatch('실시간 화면 관측을 멈췄어. 언제든 다시 같이 볼 수 있어.');
      return;
    }
    showError('');
    if (!navigator.mediaDevices || typeof navigator.mediaDevices.getDisplayMedia !== 'function') {
      showError('이 브라우저 환경에서는 화면 공유(getDisplayMedia)가 제한되어 있습니다. 대신 "PC 체화 브리지 받기 (.py)"를 로컬 PC에서 실행해 체화 로그 JSON을 불러와 주세요.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { frameRate: { ideal: 2, max: 5 } },
        audio: false,
      });
      watchStream = stream;
      const track = stream.getVideoTracks()[0];
      if (track) {
        if (OBS_CONTEXT_INPUT && !OBS_CONTEXT_INPUT.value.trim() && track.label) {
          OBS_CONTEXT_INPUT.value = track.label.slice(0, 48);
        }
        track.addEventListener('ended', () => {
          stopScreenWatch('화면 공유가 종료되어 실시간 관측을 마무리했어.');
        });
      }
      const vid = document.createElement('video');
      vid.muted = true;
      vid.playsInline = true;
      vid.srcObject = stream;
      await vid.play();
      watchVideo = vid;
      prevLumaGrid = null;
      if (BTN_TOGGLE_WATCH) {
        BTN_TOGGLE_WATCH.textContent = '화면 함께 보기 중지';
      }
      setWatchMetrics('실시간 화면 연결됨 · 48×27 광학 변화량 로컬 측정 시작 (영상 업로드 0)');
      await tickScreenWatch();
      watchTimer = window.setInterval(tickScreenWatch, 1400);
    } catch (err) {
      stopScreenWatch('');
      const msg = err && err.name === 'NotAllowedError'
        ? '화면 공유가 취소되었거나 프리뷰 창 권한으로 제한되었습니다. 로컬 PC에서는 "PC 체화 브리지 받기 (.py)"로 바로 관찰할 수 있습니다.'
        : (err instanceof Error ? `화면 연결 오류: ${err.message}` : '화면 공유를 시작할 수 없습니다.');
      showError(msg);
    }
  }

  async function sendSensorimotorLog(logObj) {
    showError('');
    setBusy(true, 'PC 체화 행동→화면 인과 소화 중…');
    try {
      const res = await fetch('/api/elysia/digest-sensorimotor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ log: logObj }),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        showError(data.message || 'PC 체화 로그 소화 중 오류가 발생했습니다.');
        return;
      }
      setWatchMetrics('PC 체화 로그 흡수 완료 · 행동→화면 변화 인과가 그래프에 영구 반영됨');
      applyState(data, false);
    } catch (err) {
      showError(err instanceof Error ? err.message : 'PC 체화 로그 전송 오류가 발생했습니다.');
    } finally {
      setBusy(false);
    }
  }

  async function sendMessage(text) {
    const clean = (text || '').trim();
    if (!clean || busy) return;
    showError('');
    setBusy(true, '로컬 인과 그래프 탐색 중…');
    try {
      const res = await fetch('/api/elysia/interact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: clean }),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        showError(data.message || '로컬 인과 처리 중 오류가 발생했습니다.');
        return;
      }
      applyState(data, false);
    } catch (err) {
      showError(err instanceof Error ? err.message : '네트워크 오류가 발생했습니다.');
    } finally {
      setBusy(false);
      if (MSG_INPUT) MSG_INPUT.focus();
    }
  }

  async function digestLocalKnowledge(readWorkspace) {
    if (busy) return;
    const text = DIGEST_TEXT ? DIGEST_TEXT.value.trim() : '';
    const sourceName = DIGEST_SOURCE ? DIGEST_SOURCE.value.trim() : '';
    if (!readWorkspace && !text) {
      showError('소화할 글이나 원리를 먼저 입력해 주세요.');
      return;
    }
    showError('');
    setBusy(true, readWorkspace ? '워크스페이스 문서 읽는 중…' : '입력한 글 소화·학습 중…');
    try {
      const res = await fetch('/api/elysia/digest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          read_workspace: Boolean(readWorkspace),
          source_name: sourceName || '직접 먹인 글',
          text: readWorkspace ? '' : text,
        }),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        showError(data.message || '지식 소화 중 오류가 발생했습니다.');
        return;
      }
      if (!readWorkspace && DIGEST_TEXT) DIGEST_TEXT.value = '';
      applyState(data, false);
    } catch (err) {
      showError(err instanceof Error ? err.message : '지식 소화 요청 오류가 발생했습니다.');
    } finally {
      setBusy(false);
    }
  }

  async function sendFeedback(signal, correction) {
    if (busy) return;
    showError('');
    setBusy(true, '차이 학습 반영 중…');
    try {
      const res = await fetch('/api/elysia/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signal, correction: correction || '' }),
      });
      const data = await res.json();
      if (res.ok && data.status === 'ok') {
        if (CORR_INPUT) CORR_INPUT.value = '';
        applyState(data, false);
      }
    } finally {
      setBusy(false);
    }
  }

  async function applyDisciplineTool() {
    if (busy || !TOOL_APPLY_INPUT) return;
    const targetText = TOOL_APPLY_INPUT.value.trim();
    if (!targetText) {
      showError('교차 도메인 렌즈를 적용할 상황이나 문제를 한 줄 적어 주세요.');
      return;
    }
    showError('');
    setBusy(true, '학문 도구 교차 적용 중…');
    try {
      const res = await fetch('/api/elysia/apply-tool', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_text: targetText }),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        showError(data.message || '학문 도구 적용 중 오류가 발생했습니다.');
        return;
      }
      TOOL_APPLY_INPUT.value = '';
      applyState(data, false);
      switchDrawerTab('trace');
    } catch (err) {
      showError(err instanceof Error ? err.message : '학문 도구 적용 요청 오류가 발생했습니다.');
    } finally {
      setBusy(false);
    }
  }

  async function learnWorldKorean() {
    if (busy) return;
    const topic = WORLD_TOPIC_INPUT ? WORLD_TOPIC_INPUT.value.trim() : '';
    showError('');
    setBusy(true, topic ? `'${topic}' 현실 한국어 독해 중…` : '스스로 호기심 주제 독해 중…');
    try {
      const res = await fetch('/api/elysia/learn-world', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        showError(data.message || '현실 한국어 독해 중 오류가 발생했습니다.');
        return;
      }
      if (WORLD_TOPIC_INPUT) WORLD_TOPIC_INPUT.value = '';
      applyState(data, false);
      switchDrawerTab('trace');
    } catch (err) {
      showError(err instanceof Error ? err.message : '현실 독해 요청 오류가 발생했습니다.');
    } finally {
      setBusy(false);
    }
  }

  async function distillCausalWeights() {
    if (busy) return;
    showError('');
    setBusy(true, '5계층 스케일로터 관계 배열 증류 중…');
    try {
      const res = await fetch('/api/elysia/distill-weights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_name: '로컬 현실 코퍼스 5계층 증류' }),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        showError(data.message || '가중치·관계 배열 증류 오류');
        return;
      }
      applyState(data, false);
      switchDrawerTab('trace');
    } catch (err) {
      showError(err instanceof Error ? err.message : '배열 증류 요청 오류가 발생했습니다.');
    } finally {
      setBusy(false);
    }
  }

  async function loadInitialState() {
    try {
      const res = await fetch('/api/elysia/state');
      const data = await res.json();
      if (res.ok && data.status === 'ok') {
        applyState(data, true);
      }
    } catch {
      // Keep calm initial state silently
    }
  }

  function toggleDrawer(forceOpen) {
    if (!DRAWER) return;
    const next = typeof forceOpen === 'boolean' ? forceOpen : !DRAWER.classList.contains('open');
    DRAWER.classList.toggle('open', next);
    if (BTN_TOGGLE_DRAWER) BTN_TOGGLE_DRAWER.classList.toggle('active', next);
  }

  function switchDrawerTab(tabName) {
    document.querySelectorAll('.elysia-mind-tab').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    const tracePane = document.getElementById('mindPaneTrace');
    const learnPane = document.getElementById('mindPaneLearn');
    if (tracePane) tracePane.classList.toggle('active', tabName === 'trace');
    if (learnPane) learnPane.classList.toggle('active', tabName === 'learn');
  }

  function enterGameMode() {
    STAGE.classList.add('active');
    if (window.__elysia3DAtelier) window.__elysia3DAtelier.stop();
  }

  function enterEngineMode() {
    STAGE.classList.remove('active');
    if (document.getElementById('atelier3dStage')?.classList.contains('active') && window.__elysia3DAtelier) {
      window.__elysia3DAtelier.start();
    }
  }

  document.querySelectorAll('.elysia-mind-tab').forEach((btn) => {
    btn.addEventListener('click', () => switchDrawerTab(btn.dataset.tab || 'trace'));
  });

  if (MSG_FORM && MSG_INPUT) {
    MSG_FORM.addEventListener('submit', (e) => {
      e.preventDefault();
      const msg = MSG_INPUT.value.trim();
      if (!msg || busy) return;
      MSG_INPUT.value = '';
      sendMessage(msg);
    });
  }

  if (BTN_SCAN_FOLDER && INPUT_FOLDER) {
    BTN_SCAN_FOLDER.addEventListener('click', () => INPUT_FOLDER.click());
    INPUT_FOLDER.addEventListener('change', async () => {
      if (!INPUT_FOLDER.files || !INPUT_FOLDER.files.length) return;
      setBusy(true, '로컬 폴더 4KB 헤더 스캔 중…');
      try {
        const digest = await scanLocalFolderInBrowser(INPUT_FOLDER.files);
        INPUT_FOLDER.value = '';
        if (digest) {
          await sendCorpusDigest({ digest });
        }
      } catch (err) {
        showError(err instanceof Error ? err.message : '로컬 폴더 스캔 오류');
        setBusy(false);
      }
    });
  }

  if (BTN_IMPORT_JSON && INPUT_JSON) {
    BTN_IMPORT_JSON.addEventListener('click', () => INPUT_JSON.click());
    INPUT_JSON.addEventListener('change', async () => {
      const f = INPUT_JSON.files && INPUT_JSON.files[0];
      if (!f) return;
      try {
        const txt = await f.text();
        const parsed = JSON.parse(txt);
        INPUT_JSON.value = '';
        await sendCorpusDigest({ digest: parsed });
      } catch (err) {
        showError(err instanceof Error ? `JSON 파싱 오류: ${err.message}` : '유효한 스캔 JSON 파일이 아닙니다.');
      }
    });
  }

  if (BTN_SCAN_WS_CORPUS) {
    BTN_SCAN_WS_CORPUS.addEventListener('click', () => sendCorpusDigest({ scan_workspace: true }));
  }

  if (BTN_TOGGLE_WATCH) {
    BTN_TOGGLE_WATCH.addEventListener('click', () => toggleScreenWatch());
  }

  if (BTN_IMPORT_SENSORIMOTOR && INPUT_SENSORIMOTOR) {
    BTN_IMPORT_SENSORIMOTOR.addEventListener('click', () => INPUT_SENSORIMOTOR.click());
    INPUT_SENSORIMOTOR.addEventListener('change', async () => {
      const f = INPUT_SENSORIMOTOR.files && INPUT_SENSORIMOTOR.files[0];
      if (!f) return;
      try {
        const txt = await f.text();
        const parsed = JSON.parse(txt);
        INPUT_SENSORIMOTOR.value = '';
        await sendSensorimotorLog(parsed);
      } catch (err) {
        showError(err instanceof Error ? `체화 로그 JSON 파싱 오류: ${err.message}` : '유효한 체화 로그 JSON 파일이 아닙니다.');
      }
    });
  }

  window.addEventListener('beforeunload', () => stopScreenWatch(''));

  if (BTN_DIGEST_WORKSPACE) BTN_DIGEST_WORKSPACE.addEventListener('click', () => digestLocalKnowledge(true));
  if (BTN_DIGEST_TEXT) BTN_DIGEST_TEXT.addEventListener('click', () => digestLocalKnowledge(false));
  if (BTN_APPLY_TOOL) BTN_APPLY_TOOL.addEventListener('click', () => applyDisciplineTool());
  if (TOOL_APPLY_INPUT) {
    TOOL_APPLY_INPUT.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        applyDisciplineTool();
      }
    });
  }
  if (BTN_LEARN_WORLD) BTN_LEARN_WORLD.addEventListener('click', () => learnWorldKorean());
  if (WORLD_TOPIC_INPUT) {
    WORLD_TOPIC_INPUT.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        learnWorldKorean();
      }
    });
  }
  if (BTN_DISTILL_WEIGHTS) BTN_DISTILL_WEIGHTS.addEventListener('click', () => distillCausalWeights());
  if (BTN_FB_RESONATE) BTN_FB_RESONATE.addEventListener('click', () => sendFeedback('resonate', ''));
  if (BTN_FB_CORR_TOGGLE && CORR_FORM) {
    BTN_FB_CORR_TOGGLE.addEventListener('click', () => {
      CORR_FORM.classList.toggle('visible');
      if (CORR_FORM.classList.contains('visible') && CORR_INPUT) CORR_INPUT.focus();
    });
  }
  if (CORR_FORM && CORR_INPUT) {
    CORR_FORM.addEventListener('submit', (e) => {
      e.preventDefault();
      const corr = CORR_INPUT.value.trim();
      if (!corr) return;
      sendFeedback('correct', corr);
    });
  }

  if (BTN_TOGGLE_DRAWER) BTN_TOGGLE_DRAWER.addEventListener('click', () => toggleDrawer());
  if (BTN_CLOSE_DRAWER) BTN_CLOSE_DRAWER.addEventListener('click', () => toggleDrawer(false));
  if (BTN_INLINE_TRACE) BTN_INLINE_TRACE.addEventListener('click', () => toggleDrawer(true));
  if (BTN_RESET_MEM) {
    BTN_RESET_MEM.addEventListener('click', async () => {
      if (busy) return;
      setBusy(true, '기억 초기화 중…');
      try {
        const res = await fetch('/api/elysia/reset', { method: 'POST' });
        const data = await res.json();
        if (res.ok && data.status === 'ok') applyState(data, true);
      } finally {
        setBusy(false);
      }
    });
  }

  if (BTN_TO_ENGINE) BTN_TO_ENGINE.addEventListener('click', enterEngineMode);
  if (BTN_TO_GAME) BTN_TO_GAME.addEventListener('click', enterGameMode);

  window.__elysiaLiveGame = {
    enterGameMode,
    enterEngineMode,
    sendMessage,
    toggleDrawer,
    switchDrawerTab,
    applyState,
    getLastState: () => lastCompanionState,
    isBusy: () => busy,
  };

  async function pollLiveRotorState() {
    if (busy || statePollInFlight || document.hidden) return;
    statePollInFlight = true;
    try {
      const res = await fetch('/api/elysia/state');
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.status === 'ok') {
        applyState(data, false, { fromPoll: true });
      }
    } catch {
      // Silent retry on next interval
    } finally {
      statePollInFlight = false;
    }
  }

  if (BTN_TOGGLE_CHAT_LOG && CHAT_LOG) {
    BTN_TOGGLE_CHAT_LOG.addEventListener('click', () => {
      const collapsed = CHAT_LOG.classList.toggle('is-collapsed');
      if (collapsed) CHAT_LOG.dataset.userCollapsed = '1';
      else delete CHAT_LOG.dataset.userCollapsed;
    });
  }

  window.addEventListener('beforeunload', () => {
    clearPhraseTimers();
    if (statePollTimer) {
      clearInterval(statePollTimer);
      statePollTimer = 0;
    }
  });

  loadInitialState();
  statePollTimer = window.setInterval(pollLiveRotorState, 1500);
  const urlFrame = new URLSearchParams(window.location.search).get('frame');
  if (window.location.pathname === '/' && !urlFrame) {
    enterGameMode();
  } else {
    STAGE.classList.remove('active');
  }
})();
