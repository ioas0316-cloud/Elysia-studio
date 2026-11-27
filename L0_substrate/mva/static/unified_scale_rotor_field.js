/**
 * Elysia Unified Scale-Rotor Observation Plane (Event-Driven Client Runtime)
 * --------------------------------------------------------------------------
 * Connects directly to the single canonical L1 Python ScaleRotorState via
 * Node.js /api/scale-rotor/* bridge and renders ONLY the active Phase Frame
 * (Point | Line | Plane | Spacetime Cube | Hypersphere) strictly on state
 * deltas or pointer interaction — zero idle animation loops, zero RAM hoarding.
 */
(function () {
  'use strict';

  const PRISM_LABELS = {
    components: '구성요소',
    environment: '환경조건',
    transformation: '변화원리',
    causality: '인과구조',
  };

  const DOMAIN_LABELS = {
    vision: '시각',
    audio: '음향',
    language: '언어·수식',
    behavior: '행위·제약',
  };

  const FRAME_META = {
    atelier3d: {
      title: '통합 인과 데이터플로우 — 코드 회로 · 다중스케일 연산 절감 · 3D 공간장 · 실시간 음향 압축 결합',
      sub: '파이썬 if/else를 분기 없는 연속 수문 회로로 컴파일해 3D 빛 파동장·다중스케일 연산 최적화·실시간 배음 음향을 하나의 텐서로 동시 구동합니다',
    },
    point: {
      title: '점 (Point) — 응축 원리 씨앗 · 동형/이형 결속 · 1성~7성 위상',
      sub: '방대한 궤적을 단일 원리 씨앗으로 압축 · 씨앗 클릭 시 온디맨드 원형 복원',
    },
    line: {
      title: '선 (Line) — t1~t4 연속 인과 궤적 · 선명함·채도·명암 & 구름 예측',
      sub: '과거(얼음)·현재(물) 연속성이 만드는 종속 제약과 다음 단면 예측 구간 조망',
    },
    plane: {
      title: '면 (Plane) — 4대 프리즘 간섭 팔레트 & P ∩ O 중심와 포개기',
      sub: '경계 흐림·불일치 셀만 t2 가변 위상 분화 · 충돌 축만 국소 해빙 (클릭 프로브)',
    },
    cube: {
      title: '시공간 큐브 (Spacetime Cube) — 시간 세계 × 공간 세계 다층 볼륨',
      sub: '얼음(과거 층) → 물(현재 층) → 구름(미래 예측 층) 입체 궤적 · 드래그로 각도 회전',
    },
    sphere: {
      title: '구체 (Hypersphere) — S0..S4 쿼터니언 로터 · 0/1 이중나선 · 미포집 지평',
      sub: '0(전체·불변 극) ↔ 1(객체·변화 극) 이중나선과 전방위 관점 회전 · 드래그로 회전',
    },
  };

  const ROUTE_DEFAULT_FRAME = {
    '/': 'atelier3d',
    '/topology': 'sphere',
    '/dashboard': 'line',
    '/manifestation': 'cube',
    '/roadmap': 'point',
  };

  const PRESETS = {
    apple: {
      concept: '사과',
      vision: { structure: 0.86, motion: 0.22, contrast: 0.74 },
      audio: { freq: 0.42, harm: 0.78, noise: 0.08 },
      language: '사과의 세포벽과 껍질 경계가 내부 수분과 당도를 유지한다 (표면장력·경계균형)',
      behavior: { fatigue: 0.20, threat: 0.18, cohesion: 0.84, terrain: 0.24 },
    },
    forest: {
      concept: '숲',
      vision: { structure: 0.76, motion: 0.58, contrast: 0.68 },
      audio: { freq: 0.56, harm: 0.76, noise: 0.15 },
      language: '나무와 토양, 수분, 바람이 에너지 구배를 따라 순환하며 숲이라는 생태계를 이룬다',
      behavior: { fatigue: 0.30, threat: 0.32, cohesion: 0.78, terrain: 0.48 },
    },
    wave: {
      concept: '파동',
      vision: { structure: 0.64, motion: 0.82, contrast: 0.70 },
      audio: { freq: 0.74, harm: 0.88, noise: 0.25 },
      language: '파동과 음파와 빛은 매질이 달라도 주기 공명과 위상 동기화 원리로 동형이다 y=A*sin(wt-kx)',
      behavior: { fatigue: 0.26, threat: 0.42, cohesion: 0.72, terrain: 0.28 },
    },
    hetero: {
      concept: '태풍',
      vision: { structure: 0.92, motion: 0.08, contrast: 0.90 },
      audio: { freq: 0.88, harm: 0.26, noise: 0.55 },
      language: '정적 결정 격자의 보존 질서와 극한 난류의 발산 압력은 환경조건이 달라 이형 축으로 분화한다',
      behavior: { fatigue: 0.84, threat: 0.90, cohesion: 0.18, terrain: 0.82 },
    },
  };

  let state = null;
  let activeFrame = 'atelier3d';
  let autoTimer = null;
  let busy = false;
  let viewYaw = 0.62;
  let viewPitch = 0.46;
  let dragging = false;
  let dragLast = { x: 0, y: 0 };
  let interactiveHitTargets = [];
  let hoveredInfo = null;

  const canvas = document.getElementById('rotorCanvas');
  const ctx = canvas.getContext('2d');

  // Helper: Safe element text update
  function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = String(val);
  }

  function resolveInitialFrame() {
    const params = new URLSearchParams(window.location.search);
    const qFrame = params.get('frame');
    if (qFrame && FRAME_META[qFrame]) return qFrame;
    const p = window.location.pathname;
    return ROUTE_DEFAULT_FRAME[p] || 'atelier3d';
  }

  async function apiJson(url, options) {
    const res = await fetch(url, options);
    const ct = res.headers.get('content-type') || '';
    if (!ct.includes('application/json')) {
      throw new Error(`예상치 못한 응답 형식 (HTTP ${res.status})`);
    }
    const data = await res.json();
    if (!res.ok || data.status === 'error') {
      throw new Error(data.message || `요청 실패 (HTTP ${res.status})`);
    }
    return data;
  }

  function readControlsPayload(extra) {
    const visStructure = Number(document.getElementById('visStructure').value);
    const visMotion = Number(document.getElementById('visMotion').value);
    const visContrast = Number(document.getElementById('visContrast').value);
    const audFreq = Number(document.getElementById('audFreq').value);
    const audHarm = Number(document.getElementById('audHarm').value);
    const noiseRatio = Number(document.getElementById('noiseRatio').value);
    const langText = document.getElementById('langInput').value.trim();
    const behFatigue = Number(document.getElementById('behFatigue').value);
    const behThreat = Number(document.getElementById('behThreat').value);
    const behCohesion = Number(document.getElementById('behCohesion').value);
    const behTerrain = Number(document.getElementById('behTerrain').value);

    return Object.assign(
      {
        frame: activeFrame === 'atelier3d' ? 'plane' : activeFrame,
        noise_ratio: noiseRatio,
        vision: {
          label: document.getElementById('conceptInput').value.trim() || '시각 단면',
          structure: visStructure,
          motion: visMotion,
          contrast: visContrast,
          coherence: Math.min(0.98, Math.max(0.08, 0.55 * visStructure + 0.45 * (1 - Math.abs(visMotion - 0.5)))),
        },
        audio: {
          label: `파동 ${(audFreq * 1000).toFixed(0)}Hz`,
          frequency_norm: audFreq,
          amplitude: Math.min(0.98, 0.35 + 0.6 * audHarm),
          harmonicity: audHarm,
          noise_ratio: noiseRatio,
        },
        language: {
          label: langText.slice(0, 22) || '언어·원리',
          text: langText || '연속 인과장 공명',
        },
        behavior: {
          label: '제약 수렴 개체',
          fatigue: behFatigue,
          threat: behThreat,
          proximity: 0.52,
          cohesion: behCohesion,
          terrain_friction: behTerrain,
        },
      },
      extra || {}
    );
  }

  function syncSliderReadouts() {
    const pairs = [
      ['visStructure', 'valVisStructure', (v) => Number(v).toFixed(2)],
      ['visMotion', 'valVisMotion', (v) => Number(v).toFixed(2)],
      ['visContrast', 'valVisContrast', (v) => Number(v).toFixed(2)],
      ['audFreq', 'valAudFreq', (v) => Number(v).toFixed(2)],
      ['audHarm', 'valAudHarm', (v) => Number(v).toFixed(2)],
      ['noiseRatio', 'valNoiseRatio', (v) => `${Math.round(Number(v) * 100)}%`],
      ['behFatigue', 'valBehFatigue', (v) => Number(v).toFixed(2)],
      ['behThreat', 'valBehThreat', (v) => Number(v).toFixed(2)],
      ['behCohesion', 'valBehCohesion', (v) => Number(v).toFixed(2)],
      ['behTerrain', 'valBehTerrain', (v) => Number(v).toFixed(2)],
    ];
    for (const [inId, outId, fmt] of pairs) {
      const inp = document.getElementById(inId);
      if (inp) setText(outId, fmt(inp.value));
    }
  }

  function setFrameUI(frameKey) {
    if (!FRAME_META[frameKey]) return;
    activeFrame = frameKey;
    document.querySelectorAll('.frame-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.frame === frameKey);
    });
    setText('stageFrameTitle', FRAME_META[frameKey].title);
    setText('stageFrameSub', FRAME_META[frameKey].sub);
    hoveredInfo = null;

    const isAtelier = frameKey === 'atelier3d';
    const atelierStage = document.getElementById('atelier3dStage');
    const canvasHud = document.getElementById('canvasHud');
    if (atelierStage) atelierStage.classList.toggle('active', isAtelier);
    if (canvas) canvas.style.display = isAtelier ? 'none' : 'block';
    if (canvasHud) canvasHud.style.display = isAtelier ? 'none' : 'block';

    if (isAtelier) {
      if (window.__elysia3DAtelier) window.__elysia3DAtelier.start();
      return;
    }
    if (window.__elysia3DAtelier) window.__elysia3DAtelier.stop();
    renderCanvas();
  }

  function applyState(nextState) {
    state = nextState;
    if (!state) return;

    // Top telemetry ribbon
    setText('hudCycle', state.cycle ?? 0);
    setText('hudDim', `L${state.helix?.ascended_level ?? 1}`);
    const disc = state.discrimination || {};
    setText('hudUnits', `${disc.active_unit_count ?? 4}/${disc.equivalent_full_fine_units ?? 16}`);
    setText('hudComp', `${Number(disc.compression_ratio ?? 4).toFixed(1)}x`);

    const syncEl = document.getElementById('hudSync');
    if (syncEl) {
      const thawing = Number(disc.local_thaw_ratio || 0) > 0.16;
      syncEl.className = thawing ? 'status-thaw' : 'status-nominal';
      syncEl.textContent = thawing
        ? `▲ 국소 해빙 ${Math.round(disc.local_thaw_ratio * 100)}%`
        : (state.ledger_synced ? '● L1·원장 동기화' : '● L1 메모리 활성');
    }

    // Helix summary
    const h = state.helix || {};
    setText(
      'stageHelixSummary',
      `0/1 공명 ${Number(h.coherence_01 ?? 0).toFixed(3)} · 0000 ${Number(h.homophase_zero_energy ?? 0).toFixed(2)} · 1111 ${Number(h.homophase_one_energy ?? 0).toFixed(2)}`
    );

    // 4-State Bottom Strip
    const phases = state.phases || {};
    const iceList = Array.isArray(phases.ice) ? phases.ice : [];
    const uncapList = Array.isArray(phases.uncaptured) ? phases.uncaptured : [];
    const activePigments = phases.water?.active_pigments || {};
    const domCount = Object.keys(activePigments).length;

    setText('slotIceCount', `${iceList.length} 씨앗`);
    setText('slotIceThaw', `해빙 ${Math.round(Number(disc.local_thaw_ratio || 0) * 100)}%`);
    setText('slotIceDesc', iceList[0] ? `핵심: ${iceList[0].label}` : '영속 얼음 원장 대기');

    setText('slotWaterDomains', `${domCount} 도메인`);
    setText('slotWaterMismatch', `Δ ${Number(disc.p_o_mismatch || 0).toFixed(2)}`);
    setText('slotWaterDesc', Object.keys(activePigments).map((k) => DOMAIN_LABELS[k] || k).join(' · ') || '연속 흐름');

    setText('slotCloudConf', `${Math.round(Number(phases.cloud?.confidence || 0) * 100)}%`);
    setText('slotCloudVar', `σ ${Number(phases.cloud?.variance || 0).toFixed(2)}`);
    setText('slotCloudDesc', `예측 [${(phases.cloud?.predicted_spectrum || []).map((x) => Number(x).toFixed(2)).join(', ')}]`);

    setText('slotUncapCount', `${uncapList.length} 슬롯`);
    setText('slotUncapDesc', uncapList[0] ? uncapList[0].reason : '미지각 잔여 없음 · 경계 명료');

    // Right Inspector: t3 Discrimination
    setText('metClarity', Number(disc.clarity ?? 0).toFixed(2));
    setText('metSat', Number(disc.saturation ?? 0).toFixed(2));
    setText('metLum', Number(disc.luminance ?? 0).toFixed(2));
    setText('tagNoiseRej', `노이즈 분리 ${Math.round(Number(disc.noise_rejection ?? 0) * 100)}%`);

    // Behavior & 1★-7★
    const beh = state.behavior || {};
    setText('behWorldTier', `${beh.world_tier_label || '1성'} · ${beh.world_scope || '동네 단위'}`);
    setText('behStanceLabel', beh.stance_label || '수호·경계유지 수렴');
    setText('behEnergy', Number(beh.convergence_energy ?? 0).toFixed(3));
    setText('behInfluence', `인과 영향력 ${Number(beh.causal_influence_score ?? 0).toFixed(3)}`);

    // Cross-domain bindings (safe DOM construction)
    const bindContainer = document.getElementById('bindingsList');
    if (bindContainer) {
      bindContainer.replaceChildren();
      const bindings = Array.isArray(state.principle_bindings) ? state.principle_bindings : [];
      if (bindings.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'item-row';
        empty.textContent = '2개 이상 도메인이 동시 투입되면 동형/이형 결속이 표시됩니다.';
        bindContainer.appendChild(empty);
      } else {
        for (const b of bindings.slice(0, 6)) {
          const row = document.createElement('div');
          row.className = 'item-row';

          const top = document.createElement('div');
          top.className = 'item-top';
          const title = document.createElement('span');
          title.className = 'item-title';
          title.textContent = b.pair;
          const tag = document.createElement('span');
          tag.className = b.isomorphic ? 'iso-tag' : 'hetero-tag';
          tag.textContent = `${b.isomorphic ? '동형 통합' : '이형 분화'} ${Number(b.resonance).toFixed(2)}`;
          top.append(title, tag);

          const meta = document.createElement('div');
          meta.className = 'item-meta';
          const sp = document.createElement('span');
          sp.textContent = b.shared_principle;
          const ax = document.createElement('span');
          ax.className = 'mono';
          ax.textContent = PRISM_LABELS[b.divergence_axis] || b.divergence_axis;
          meta.append(sp, ax);

          row.append(top, meta);
          bindContainer.appendChild(row);
        }
      }
    }

    // Persistent Ice Seeds List (with On-Demand Archetype Restoration button)
    const iceContainer = document.getElementById('iceSeedsList');
    if (iceContainer) {
      iceContainer.replaceChildren();
      for (const seed of iceList.slice(0, 6)) {
        const row = document.createElement('div');
        row.className = 'item-row';

        const top = document.createElement('div');
        top.className = 'item-top';
        const title = document.createElement('span');
        title.className = 'item-title';
        title.textContent = seed.label;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'seed-btn';
        btn.textContent = '원형 복원';
        btn.addEventListener('click', () => recallSeed(seed.seed_id));
        top.append(title, btn);

        const maxThaw = Math.max(...(seed.thaw_mask || [0]));
        const meta = document.createElement('div');
        meta.className = 'item-meta mono';
        const left = document.createElement('span');
        left.textContent = `${seed.world_tier}성 · 안정 ${Math.round(seed.stability * 100)}% · ${(seed.domains || []).map((d) => DOMAIN_LABELS[d] || d).join('·')}`;
        const right = document.createElement('span');
        right.style.color = maxThaw > 0.16 ? 'var(--crimson)' : 'var(--text-muted)';
        right.textContent = maxThaw > 0.16 ? `해빙 ${Math.round(maxThaw * 100)}%` : `생존 ${seed.cycles_survived}c`;
        meta.append(left, right);

        row.append(top, meta);
        iceContainer.appendChild(row);
      }
    }

    // 4-Axis Self-Boundary
    const sb = state.self_boundary || {};
    const setBar = (valId, barId, v) => {
      const clamped = Math.max(0, Math.min(1, Number(v || 0)));
      setText(valId, clamped.toFixed(2));
      const b = document.getElementById(barId);
      if (b) b.style.width = `${Math.round(clamped * 100)}%`;
    };
    setBar('sbIntVal', 'sbIntBar', sb.internal_origin);
    setBar('sbExtVal', 'sbExtBar', sb.external_influence);
    setBar('sbIgnVal', 'sbIgnBar', sb.ignorance_boundary);
    setBar('sbRevVal', 'sbRevBar', sb.criteria_revision_delta);
    setText('sbNote', sb.revision_note || '4축 자아경계 정상');

    // External ingested banner if present
    const extBanner = document.getElementById('externalBanner');
    if (state.ingested_external && extBanner) {
      extBanner.classList.add('visible');
      setText('extTitle', state.ingested_external.title || '');
      setText('extSummary', state.ingested_external.summary || '');
      setText('lblVisTitle', state.ingested_external.title || '외부 관측');
    }

    renderCanvas();
  }

  // ==========================================================================
  // Single High-DPI Event-Driven Canvas Renderer for All 5 Phase Frames
  // ==========================================================================
  function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = Math.max(320, Math.floor(rect.width));
    const h = Math.max(300, Math.floor(rect.height));
    if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { w, h };
  }

  function renderCanvas() {
    if (activeFrame === 'atelier3d') return;
    if (!state) return;
    const { w, h } = resizeCanvas();
    interactiveHitTargets = [];

    // Deep obsidian ground + hairline calibration grid
    ctx.fillStyle = '#07090E';
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = 'rgba(27, 36, 53, 0.55)';
    ctx.lineWidth = 1;
    const step = 40;
    ctx.beginPath();
    for (let x = step; x < w; x += step) {
      ctx.moveTo(x + 0.5, 0);
      ctx.lineTo(x + 0.5, h);
    }
    for (let y = step; y < h; y += step) {
      ctx.moveTo(0, y + 0.5);
      ctx.lineTo(w, y + 0.5);
    }
    ctx.stroke();

    if (activeFrame === 'plane') {
      drawPlaneFrame(w, h);
    } else if (activeFrame === 'point') {
      drawPointFrame(w, h);
    } else if (activeFrame === 'line') {
      drawLineFrame(w, h);
    } else if (activeFrame === 'cube') {
      drawCubeFrame(w, h);
    } else if (activeFrame === 'sphere') {
      drawSphereFrame(w, h);
    }

    if (hoveredInfo) {
      setText('canvasHud', hoveredInfo);
    } else {
      const hint =
        activeFrame === 'cube' || activeFrame === 'sphere'
          ? `드래그로 관점 회전 · 현재 각도 yaw=${viewYaw.toFixed(2)} pitch=${viewPitch.toFixed(2)}`
          : activeFrame === 'point'
          ? '얼음 원리 씨앗을 클릭하면 해당 씨앗을 t1~t4로 온디맨드 원형 복원합니다'
          : '셀 위에 마우스를 올리거나 클릭하면 P ∩ O 포개기 및 국소 해빙 수치를 정밀 조회합니다';
      setText('canvasHud', hint);
    }
  }

  // 1. PLANE FRAME: 4x4 Prism Spectrum Interference + Variable Split + Local Ice Thaw
  function drawPlaneFrame(w, h) {
    const plane = state.frames?.plane;
    if (!plane) return;
    const grid = plane.grid || [];
    const padX = 86;
    const padTop = 76;
    const padBot = 48;
    const gw = Math.max(160, w - padX - 28);
    const gh = Math.max(160, h - padTop - padBot);
    const cellW = gw / 4;
    const cellH = gh / 4;

    // Top 0/1 Double-Helix phase comparison ribbon
    const zArr = plane.zero_anchor || [0.5, 0.5, 0.5, 0.5];
    const oArr = plane.one_flux || [0.5, 0.5, 0.5, 0.5];
    ctx.font = '11px "IBM Plex Mono", monospace';
    ctx.fillStyle = '#94A3B8';
    ctx.fillText('0(불변 질서) vs 1(변화 흐름) → 01 통합 위상', padX, 24);

    for (let i = 0; i < 4; i++) {
      const bx = padX + i * cellW;
      const bw = cellW - 10;
      ctx.fillStyle = '#0D121C';
      ctx.fillRect(bx, 32, bw, 18);
      ctx.strokeStyle = '#1B2435';
      ctx.strokeRect(bx + 0.5, 32.5, bw, 18);

      ctx.fillStyle = 'rgba(6, 182, 212, 0.45)';
      ctx.fillRect(bx + 1, 33, (bw - 2) * zArr[i], 7);
      ctx.fillStyle = 'rgba(244, 63, 94, 0.65)';
      ctx.fillRect(bx + 1, 41, (bw - 2) * oArr[i], 7);
    }

    // Column & Row headers
    const axes = state.prism_axes || ['components', 'environment', 'transformation', 'causality'];
    const doms = ['vision', 'audio', 'language', 'behavior'];
    ctx.font = '600 11px "IBM Plex Sans", sans-serif';
    ctx.fillStyle = '#94A3B8';
    for (let c = 0; c < 4; c++) {
      ctx.fillText(PRISM_LABELS[axes[c]] || axes[c], padX + c * cellW + 4, padTop - 10);
    }
    for (let r = 0; r < 4; r++) {
      ctx.fillText(DOMAIN_LABELS[doms[r]] || doms[r], 16, padTop + r * cellH + cellH * 0.5 + 4);
    }

    // Render 4x4 P ∩ O Superposition Cells
    for (const cell of grid) {
      const x = padX + cell.col * cellW;
      const y = padTop + cell.row * cellH;
      const cw = cellW - 10;
      const ch = cellH - 10;

      let fill = 'rgba(13, 18, 28, 0.92)';
      let stroke = '#1B2435';
      if (cell.state === 'thaw') {
        fill = 'rgba(244, 63, 94, 0.16)';
        stroke = '#F43F5E';
      } else if (cell.state === 'split') {
        fill = 'rgba(245, 158, 11, 0.14)';
        stroke = '#F59E0B';
      } else if (cell.state === 'uncaptured') {
        fill = 'rgba(148, 163, 184, 0.12)';
        stroke = '#94A3B8';
      } else {
        fill = 'rgba(6, 182, 212, 0.08)';
        stroke = 'rgba(6, 182, 212, 0.45)';
      }

      ctx.fillStyle = fill;
      ctx.fillRect(x, y, cw, ch);
      ctx.strokeStyle = stroke;
      ctx.lineWidth = cell.state === 'thaw' || cell.state === 'split' ? 1.5 : 1;
      ctx.strokeRect(x + 0.5, y + 0.5, cw, ch);

      // Dynamic t2 Variable Phase Sub-Grid ONLY when split_depth > 0 (never static!)
      if (cell.split_depth > 0) {
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.45)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x + cw * 0.5, y);
        ctx.lineTo(x + cw * 0.5, y + ch);
        ctx.moveTo(x, y + ch * 0.5);
        ctx.lineTo(x + cw, y + ch * 0.5);
        ctx.stroke();
      }

      // Local Ice thaw diagonal hatch
      if (cell.thaw > 0.18) {
        ctx.strokeStyle = 'rgba(244, 63, 94, 0.45)';
        ctx.beginPath();
        ctx.moveTo(x, y + ch);
        ctx.lineTo(x + cw, y);
        ctx.stroke();
      }

      // Predicted (Cloud) vs Observed (Water) superposition bars
      const barY = y + ch - 20;
      const barW = Math.max(20, cw - 16);
      ctx.fillStyle = 'rgba(245, 158, 11, 0.65)';
      ctx.fillRect(x + 8, barY, barW * cell.predicted, 4);
      ctx.fillStyle = '#06B6D4';
      ctx.fillRect(x + 8, barY + 6, barW * cell.observed, 4);

      ctx.font = '600 11px "IBM Plex Mono", monospace';
      ctx.fillStyle = '#F1F5F9';
      ctx.fillText(`Δ${cell.delta.toFixed(2)}`, x + 8, y + 18);

      ctx.font = '10px "IBM Plex Mono", monospace';
      ctx.fillStyle = cell.state === 'thaw' ? '#F43F5E' : cell.state === 'split' ? '#F59E0B' : '#94A3B8';
      const tag =
        cell.state === 'thaw'
          ? `해빙 ${Math.round(cell.thaw * 100)}%`
          : cell.state === 'split'
          ? 't2 세밀분화'
          : cell.state === 'uncaptured'
          ? '미포집'
          : '공명 응축';
      ctx.fillText(tag, x + 8, y + 32);

      interactiveHitTargets.push({
        type: 'plane_cell',
        x,
        y,
        w: cw,
        h: ch,
        info: `[${DOMAIN_LABELS[cell.domain]} × ${PRISM_LABELS[cell.axis]}] 예측(구름)=${cell.predicted.toFixed(3)} · 관측(물)=${cell.observed.toFixed(3)} · Δ=${cell.delta.toFixed(3)} · 해빙=${Math.round(cell.thaw * 100)}% · 상태=${tag}`,
      });
    }
  }

  // 2. POINT FRAME: Principle Seed Singularity & Cross-Domain Transfer Constellation
  function drawPointFrame(w, h) {
    const pt = state.frames?.point;
    if (!pt) return;
    const cx = w * 0.5;
    const cy = h * 0.48;
    const scaleR = Math.min(w, h) * 0.34;
    const seeds = pt.seeds || [];

    // Ascended scale rings (1★ .. 7★)
    for (let ring = 1; ring <= 4; ring++) {
      ctx.strokeStyle = ring === 4 ? 'rgba(245, 158, 11, 0.25)' : 'rgba(27, 36, 53, 0.8)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, (scaleR * ring) / 4, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Center Singularity (Current Ascended Rotor Core)
    ctx.fillStyle = 'rgba(6, 182, 212, 0.14)';
    ctx.beginPath();
    ctx.arc(cx, cy, 24, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#06B6D4';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.font = '700 11px "IBM Plex Mono", monospace';
    ctx.fillStyle = '#F1F5F9';
    ctx.textAlign = 'center';
    ctx.fillText(`L${state.helix?.ascended_level ?? 1} · ${pt.world_tier}성`, cx, cy + 4);

    // Connect seeds sharing domains (isomorphic bridges)
    const coords = seeds.map((s) => ({
      seed: s,
      x: cx + s.x * scaleR,
      y: cy + s.y * scaleR,
    }));

    for (let i = 0; i < coords.length; i++) {
      for (let j = i + 1; j < coords.length; j++) {
        const shared = coords[i].seed.domains.some((d) => coords[j].seed.domains.includes(d));
        ctx.strokeStyle = shared ? 'rgba(6, 182, 212, 0.35)' : 'rgba(245, 158, 11, 0.18)';
        ctx.setLineDash(shared ? [] : [4, 4]);
        ctx.beginPath();
        ctx.moveTo(coords[i].x, coords[i].y);
        ctx.lineTo(coords[j].x, coords[j].y);
        ctx.stroke();
      }
    }
    ctx.setLineDash([]);

    // Draw each Ice Principle Seed node
    for (const item of coords) {
      const s = item.seed;
      const r = 11 + s.world_tier * 2.2;
      const isThawing = s.thaw_max > 0.16;

      ctx.strokeStyle = 'rgba(6, 182, 212, 0.28)';
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(item.x, item.y);
      ctx.stroke();

      ctx.fillStyle = isThawing ? 'rgba(244, 63, 94, 0.22)' : 'rgba(13, 18, 28, 0.96)';
      ctx.beginPath();
      ctx.arc(item.x, item.y, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = isThawing ? '#F43F5E' : '#06B6D4';
      ctx.lineWidth = 1.6;
      ctx.stroke();

      ctx.font = '600 10px "IBM Plex Mono", monospace';
      ctx.fillStyle = '#F1F5F9';
      ctx.fillText(`${s.world_tier}★`, item.x, item.y + 3);

      ctx.font = '11px "IBM Plex Sans", sans-serif';
      ctx.fillStyle = '#CBD5E1';
      ctx.fillText(s.label.slice(0, 18), item.x, item.y + r + 14);

      interactiveHitTargets.push({
        type: 'seed',
        seedId: s.seed_id,
        x: item.x - r - 4,
        y: item.y - r - 4,
        w: (r + 4) * 2,
        h: (r + 4) * 2,
        info: `[원리 씨앗 클릭→원형 복원] ${s.label} · ${s.world_tier}성 · 안정도 ${Math.round(s.stability * 100)}% · 도메인: ${s.domains.join(', ')}`,
      });
    }
    ctx.textAlign = 'left';
  }

  // 3. LINE FRAME: Continuous t1~t4 Trajectory + Cloud Next Forecast Cone
  function drawLineFrame(w, h) {
    const line = state.frames?.line;
    if (!line) return;
    const traj = line.trajectory || [];
    const padL = 54;
    const padR = 72;
    const padT = 44;
    const padB = 56;
    const pw = Math.max(180, w - padL - padR);
    const ph = Math.max(160, h - padT - padB);

    // Axes & Y ticks
    ctx.strokeStyle = '#2C3B55';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padL, padT);
    ctx.lineTo(padL, padT + ph);
    ctx.lineTo(padL + pw, padT + ph);
    ctx.stroke();

    ctx.font = '10px "IBM Plex Mono", monospace';
    ctx.fillStyle = '#64748B';
    for (let k = 0; k <= 4; k++) {
      const val = k * 0.25;
      const y = padT + ph - val * ph;
      ctx.fillText(val.toFixed(2), 14, y + 3);
      ctx.strokeStyle = 'rgba(27, 36, 53, 0.6)';
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(padL + pw, y);
      ctx.stroke();
    }

    if (traj.length === 0) return;

    const plotSeries = (key, color, dashed) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.8;
      ctx.setLineDash(dashed ? [5, 4] : []);
      ctx.beginPath();
      traj.forEach((pt, idx) => {
        const x = padL + (idx / Math.max(1, traj.length)) * pw;
        const y = padT + ph - Math.max(0, Math.min(1, Number(pt[key] || 0))) * ph;
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.setLineDash([]);
    };

    plotSeries('clarity', '#06B6D4', false);
    plotSeries('saturation', '#F59E0B', false);
    plotSeries('luminance', '#10B981', true);
    plotSeries('local_thaw_ratio', '#F43F5E', false);

    // Future Cloud forecast cone at right edge
    const last = traj[traj.length - 1];
    const lastX = padL + ((traj.length - 1) / Math.max(1, traj.length)) * pw;
    const nextX = padL + pw;
    const lastY = padT + ph - Number(last.clarity || 0.7) * ph;
    const cloudY = padT + ph - Number(line.cloud_confidence || 0.7) * ph;
    const spreadPx = Math.max(10, Number(line.cloud_variance || 0.15) * ph * 0.45);

    ctx.fillStyle = 'rgba(245, 158, 11, 0.16)';
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(nextX, Math.max(padT, cloudY - spreadPx));
    ctx.lineTo(nextX, Math.min(padT + ph, cloudY + spreadPx));
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = '#F59E0B';
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(nextX, cloudY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#F59E0B';
    ctx.fillText('구름 예측', nextX - 48, Math.max(padT + 12, cloudY - spreadPx - 6));

    // Legend
    const legend = [
      ['선명함 Clarity', '#06B6D4'],
      ['채도 Saturation', '#F59E0B'],
      ['명암 Luminance', '#10B981'],
      ['국소 해빙 Thaw', '#F43F5E'],
    ];
    let lx = padL;
    for (const [label, col] of legend) {
      ctx.fillStyle = col;
      ctx.fillRect(lx, 18, 12, 3);
      ctx.fillStyle = '#CBD5E1';
      ctx.fillText(label, lx + 16, 23);
      lx += 116;
    }

    // Hover markers along cycles
    traj.forEach((pt, idx) => {
      const x = padL + (idx / Math.max(1, traj.length)) * pw;
      const y = padT + ph - Number(pt.clarity || 0) * ph;
      if (pt.shock > 0.2) {
        ctx.fillStyle = '#F43F5E';
        ctx.beginPath();
        ctx.arc(x, padT + ph - pt.local_thaw_ratio * ph, 4, 0, Math.PI * 2);
        ctx.fill();
      }
      interactiveHitTargets.push({
        type: 'line_pt',
        x: x - 8,
        y: padT,
        w: 16,
        h: ph,
        info: `Cycle #${pt.cycle} · 선명함=${pt.clarity.toFixed(2)} · 채도=${pt.saturation.toFixed(2)} · 명암=${pt.luminance.toFixed(2)} · 압축=${pt.compression_ratio}x · 해빙=${Math.round(pt.local_thaw_ratio * 100)}%`,
      });
    });
  }

  // Pure 3D projection helper (zero WebGL overhead)
  function project3D(x, y, z, cx, cy, scale) {
    const cyaw = Math.cos(viewYaw);
    const syaw = Math.sin(viewYaw);
    const cp = Math.cos(viewPitch);
    const sp = Math.sin(viewPitch);
    const x1 = x * cyaw - z * syaw;
    const z1 = x * syaw + z * cyaw;
    const y2 = y * cp - z1 * sp;
    const z2 = y * sp + z1 * cp;
    const persp = 3.2 / (3.2 - z2 * 0.45);
    return { sx: cx + x1 * scale * persp, sy: cy - y2 * scale * persp, depth: z2 };
  }

  // 4. SPACETIME CUBE FRAME: Stacked Time-World × Space-World Slices
  function drawCubeFrame(w, h) {
    const cube = state.frames?.cube;
    if (!cube) return;
    const slices = cube.slices || [];
    const cx = w * 0.5;
    const cy = h * 0.52;
    const scale = Math.min(w, h) * 0.27;

    // Outer spacetime cube wireframe
    const corners = [
      [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
      [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
    ].map(([x, y, z]) => project3D(x, y, z, cx, cy, scale));

    const edges = [
      [0, 1], [1, 2], [2, 3], [3, 0],
      [4, 5], [5, 6], [6, 7], [7, 4],
      [0, 4], [1, 5], [2, 6], [3, 7],
    ];
    ctx.strokeStyle = 'rgba(44, 59, 85, 0.75)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (const [a, b] of edges) {
      ctx.moveTo(corners[a].sx, corners[a].sy);
      ctx.lineTo(corners[b].sx, corners[b].sy);
    }
    ctx.stroke();

    // Stacked slices from Past (Ice, bottom) -> Present (Water) -> Future (Cloud, top)
    const centers = [];
    slices.forEach((sl, idx) => {
      const yNorm = -0.85 + (idx / Math.max(1, slices.length - 1)) * 1.7;
      const spec = sl.spectrum || [0.5, 0.5, 0.5, 0.5];
      const quad = [
        project3D(-0.85 * spec[0], yNorm, -0.85 * spec[1], cx, cy, scale),
        project3D(0.85 * spec[2], yNorm, -0.85 * spec[1], cx, cy, scale),
        project3D(0.85 * spec[2], yNorm, 0.85 * spec[3], cx, cy, scale),
        project3D(-0.85 * spec[0], yNorm, 0.85 * spec[3], cx, cy, scale),
      ];

      let fill = 'rgba(6, 182, 212, 0.12)';
      let stroke = 'rgba(6, 182, 212, 0.55)';
      if (sl.kind === 'water_present') {
        fill = 'rgba(6, 182, 212, 0.28)';
        stroke = '#06B6D4';
      } else if (sl.kind === 'cloud_future') {
        fill = 'rgba(245, 158, 11, 0.22)';
        stroke = '#F59E0B';
      } else if (sl.thaw > 0.16) {
        fill = 'rgba(244, 63, 94, 0.22)';
        stroke = '#F43F5E';
      }

      ctx.fillStyle = fill;
      ctx.strokeStyle = stroke;
      ctx.lineWidth = sl.kind === 'water_present' ? 1.8 : 1.1;
      ctx.beginPath();
      ctx.moveTo(quad[0].sx, quad[0].sy);
      for (let k = 1; k < 4; k++) ctx.lineTo(quad[k].sx, quad[k].sy);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      const mid = project3D((spec[2] - spec[0]) * 0.5, yNorm, (spec[3] - spec[1]) * 0.5, cx, cy, scale);
      centers.push(mid);

      ctx.font = '10px "IBM Plex Mono", monospace';
      ctx.fillStyle = sl.kind === 'cloud_future' ? '#F59E0B' : sl.kind === 'water_present' ? '#06B6D4' : '#94A3B8';
      const label =
        sl.kind === 'cloud_future'
          ? `구름 C+${sl.cycle}`
          : sl.kind === 'water_present'
          ? `물 C${sl.cycle}`
          : `얼음 C${sl.cycle}`;
      ctx.fillText(label, quad[1].sx + 8, quad[1].sy + 3);
    });

    // Vertical causal filament connecting slices
    if (centers.length > 1) {
      ctx.strokeStyle = '#F1F5F9';
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      centers.forEach((p, idx) => {
        if (idx === 0) ctx.moveTo(p.sx, p.sy);
        else ctx.lineTo(p.sx, p.sy);
      });
      ctx.stroke();
    }
  }

  // 5. SPHERE / HYPERSPHERE FRAME: S0..S4 Rotors + 0/1 Double-Helix + Uncaptured Horizon
  function drawSphereFrame(w, h) {
    const sph = state.frames?.sphere;
    if (!sph) return;
    const cx = w * 0.5;
    const cy = h * 0.5;
    const radius = Math.min(w, h) * 0.34;

    // Outer omnidirectional hypersphere meridian
    ctx.strokeStyle = 'rgba(44, 59, 85, 0.85)';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.stroke();

    // 5 Nested S0..S4 Quaternion Rotor Great Circles
    const rotors = sph.rotors || [];
    const ringColors = ['#F43F5E', '#F59E0B', '#10B981', '#38BDF8', '#06B6D4'];
    rotors.forEach((r, idx) => {
      const q = r.quaternion || [0, 0, 0, 1];
      const tiltA = (q[0] * 2.4) + idx * 0.35;
      const tiltB = (q[1] * 2.4) + idx * 0.25;
      const rr = (0.34 + idx * 0.16) * 1.0;

      ctx.strokeStyle = ringColors[idx % ringColors.length];
      ctx.globalAlpha = 0.35 + 0.45 * (r.coherence || 0.7);
      ctx.lineWidth = idx === 4 ? 1.8 : 1.1;
      ctx.beginPath();
      for (let s = 0; s <= 48; s++) {
        const a = (s / 48) * Math.PI * 2;
        const px = rr * Math.cos(a);
        const py = rr * Math.sin(a) * Math.cos(tiltA);
        const pz = rr * Math.sin(a) * Math.sin(tiltA) + 0.12 * Math.cos(a + tiltB);
        const p = project3D(px, py, pz, cx, cy, radius);
        if (s === 0) ctx.moveTo(p.sx, p.sy);
        else ctx.lineTo(p.sx, p.sy);
      }
      ctx.stroke();
      ctx.globalAlpha = 1.0;
    });

    // 0 (Whole/Invariant Pole) <-> 1 (Object/Flux Pole) Double-Helix
    const pZero = project3D(0, 1.05, 0, cx, cy, radius);
    const pOne = project3D(0, -1.05, 0, cx, cy, radius);

    ctx.lineWidth = 1.8;
    for (let strand = 0; strand < 2; strand++) {
      ctx.strokeStyle = strand === 0 ? '#06B6D4' : '#F43F5E';
      ctx.beginPath();
      for (let i = 0; i <= 40; i++) {
        const t = i / 40;
        const y = 1.0 - 2.0 * t;
        const ang = t * Math.PI * 4 + strand * Math.PI;
        const rad = 0.26 * Math.sin(t * Math.PI);
        const p = project3D(rad * Math.cos(ang), y, rad * Math.sin(ang), cx, cy, radius);
        if (i === 0) ctx.moveTo(p.sx, p.sy);
        else ctx.lineTo(p.sx, p.sy);
      }
      ctx.stroke();
    }

    // Pole markers
    ctx.fillStyle = '#06B6D4';
    ctx.beginPath();
    ctx.arc(pZero.sx, pZero.sy, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.font = '600 11px "IBM Plex Mono", monospace';
    ctx.fillText('0 · 전체 불변 축', pZero.sx + 9, pZero.sy + 4);

    ctx.fillStyle = '#F43F5E';
    ctx.beginPath();
    ctx.arc(pOne.sx, pOne.sy, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillText('1 · 객체 변화 극', pOne.sx + 9, pOne.sy + 4);

    // Uncaptured Horizon Slots hovering outside sphere
    const uncap = sph.uncaptured_horizon || [];
    uncap.forEach((slot, idx) => {
      const ang = (idx / Math.max(1, uncap.length)) * Math.PI * 2 + 0.5;
      const p = project3D(1.18 * Math.cos(ang), 0.25 * Math.sin(ang * 2), 1.18 * Math.sin(ang), cx, cy, radius);
      ctx.strokeStyle = '#F59E0B';
      ctx.fillStyle = 'rgba(245, 158, 11, 0.22)';
      ctx.beginPath();
      ctx.arc(p.sx, p.sy, 7, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = '#F59E0B';
      ctx.font = '10px "IBM Plex Mono", monospace';
      ctx.fillText(`미포집:${slot.domain}`, p.sx + 10, p.sy + 3);
    });
  }

  // ==========================================================================
  // Actions (L1 Python Bridge Calls)
  // ==========================================================================
  async function loadInitialState() {
    try {
      const data = await apiJson('/api/scale-rotor/state');
      applyState(data);
    } catch (err) {
      setText('canvasHud', `초기화 오류: ${err.message}`);
    }
  }

  async function runStep(extraPayload) {
    if (busy) return;
    busy = true;
    try {
      const data = await apiJson('/api/scale-rotor/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(readControlsPayload(extraPayload)),
      });
      applyState(data);
    } catch (err) {
      setText('canvasHud', `사이클 오류: ${err.message}`);
    } finally {
      busy = false;
    }
  }

  async function ingestConcept(queryText) {
    if (busy) return;
    const q = (queryText || document.getElementById('conceptInput').value || '').trim();
    if (!q) return;
    busy = true;
    setText('canvasHud', `실세계 개념 '${q}' 외부 수집 및 L1 t1~t4 투영 중...`);
    try {
      const base = readControlsPayload();
      const data = await apiJson('/api/scale-rotor/ingest-concept', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q,
          audio: base.audio,
          behavior: base.behavior,
          noise_ratio: base.noise_ratio,
          frame: activeFrame,
        }),
      });
      applyState(data);
    } catch (err) {
      setText('canvasHud', `개념 투입 오류: ${err.message}`);
    } finally {
      busy = false;
    }
  }

  async function recallSeed(seedId) {
    if (busy) return;
    busy = true;
    try {
      const data = await apiJson('/api/scale-rotor/recall-seed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed_id: seedId }),
      });
      applyState(data);
      setText('canvasHud', `얼음 씨앗 '${seedId}' 온디맨드 원형 복원 완료`);
    } catch (err) {
      setText('canvasHud', `원형 복원 오류: ${err.message}`);
    } finally {
      busy = false;
    }
  }

  async function runBenchmark() {
    if (busy) return;
    busy = true;
    setText('canvasHud', '7.4절 정량 검증 실행 중 (압축률 · 30~70% 노이즈 · 돌발 충격 복원)...');
    try {
      const report = await apiJson('/api/scale-rotor/benchmark', { method: 'POST' });
      const panel = document.getElementById('benchPanel');
      if (panel) panel.classList.add('visible');

      const vEl = document.getElementById('benchVerdict');
      if (vEl) {
        vEl.textContent = report.verdict === 'PASS' ? '● PASS' : '▲ TUNE';
        vEl.style.color = report.verdict === 'PASS' ? 'var(--emerald)' : 'var(--amber)';
      }

      const s = report.summary || {};
      setText(
        'benchSummary',
        `압축 ${s.mean_compression_ratio}x · 편향 ${s.max_drift} · 충격복원 ${s.shock_recovery_frames}프레임(얼음안정 ${Math.round((s.mean_ice_stability || 0) * 100)}%) · 동형 ${s.isomorphic_unified_pairs} / 이형 ${s.heteromorphic_separated_pairs}`
      );

      const tbody = document.getElementById('benchRows');
      if (tbody) {
        tbody.replaceChildren();
        for (const t of report.noise_trials || []) {
          const tr = document.createElement('tr');
          const cells = [
            `${Math.round(t.noise_ratio * 100)}%`,
            Number(t.clarity).toFixed(2),
            `${Math.round(t.noise_rejection * 100)}%`,
            `${t.auto_splits}분화`,
          ];
          for (const txt of cells) {
            const td = document.createElement('td');
            td.textContent = txt;
            tr.appendChild(td);
          }
          tbody.appendChild(tr);
        }
      }
      setText('canvasHud', `7.4절 정량 검증 완료: ${report.verdict}`);
    } catch (err) {
      setText('canvasHud', `벤치마크 오류: ${err.message}`);
    } finally {
      busy = false;
    }
  }

  function formatValCompact(v) {
    if (v === null || v === undefined) return 'null';
    if (typeof v === 'object') {
      const s = JSON.stringify(v);
      return s.length > 52 ? s.slice(0, 49) + '...' : s;
    }
    return String(v);
  }

  function renderContrastReport(report) {
    const panel = document.getElementById('contrastReport');
    if (!panel) return;
    panel.classList.add('visible');

    const sum = report.summary || {};
    const lens = report.observer_lens || {};
    setText(
      'contrastSummaryMeta',
      `${lens.label || ''} · 실측 ${sum.live_observed_count}건 · 미포집 ${sum.external_uncaptured_count}건 · 원형재현 ${sum.all_reproduction_verified ? 'PASS' : 'FAIL'}`
    );
    setText('contrastInsight', sum.principle_note || '');

    const titleEl = document.getElementById('contrastReportTitle');
    if (titleEl) {
      titleEl.style.color = 'var(--cyan)';
      titleEl.textContent = '실제 실행 과정 비교대조 관측 (원본 ↔ 과정 ↔ 결과 · 원형 재현 검증)';
    }
    const vbar = document.getElementById('vesselToolbar');
    if (vbar) vbar.classList.remove('visible');
    const pbar = document.getElementById('phaseSyncToolbar');
    if (pbar) pbar.classList.remove('visible');
    const dbar = document.getElementById('digestToolbar');
    if (dbar) dbar.classList.remove('visible');
    const cardsEl = document.getElementById('contrastCards');
    if (cardsEl) {
      cardsEl.replaceChildren();
      for (const obs of report.observed_processes || []) {
        const card = document.createElement('div');
        card.className = 'artifact-card';

        const head = document.createElement('div');
        head.className = 'artifact-head';
        const title = document.createElement('span');
        title.style.color = 'var(--cyan)';
        title.textContent = obs.title;
        const repro = document.createElement('span');
        repro.className = 'mono';
        repro.style.fontSize = '10px';
        repro.style.color = obs.reproduction?.verified ? 'var(--emerald)' : 'var(--crimson)';
        repro.textContent = obs.reproduction?.verified
          ? `● 재현 검증 PASS (오차 ${obs.reproduction.residual_error})`
          : '✖ 재현 불일치';
        head.append(title, repro);

        const summaryLine = document.createElement('div');
        summaryLine.className = 'artifact-line mono';
        summaryLine.style.color = 'var(--text-primary)';
        summaryLine.textContent = obs.process_summary || '';

        const invList = (obs.invariants_0 || [])
          .slice(0, 4)
          .map((x) => `${x.entity}=${formatValCompact(x.value)}`)
          .join(' | ');
        const invLine = document.createElement('div');
        invLine.className = 'artifact-line';
        invLine.style.color = 'var(--cyan)';
        invLine.textContent = `0(실제 불변 · ${(obs.invariants_0 || []).length}건): ${invList || '없음'}`;

        const mutList = (obs.mutations_1 || [])
          .slice(0, 4)
          .map((m) => `${m.entity}: ${formatValCompact(m.before)}→${formatValCompact(m.after)}`)
          .join(' | ');
        const mutLine = document.createElement('div');
        mutLine.className = 'artifact-line';
        mutLine.style.color = 'var(--crimson)';
        const totalMut = obs.delta_patch_total != null ? obs.delta_patch_total : (obs.mutations_1 || []).length;
        mutLine.textContent = `1(실제 변화 · ${totalMut}건): ${mutList || '없음'}`;

        const stepSummary = (obs.process_steps || [])
          .slice(0, 3)
          .map((st) => (st.stage ? `${st.stage}: ${st.detail}` : `L${st.line} ${st.code}`))
          .join('  /  ');
        const stepLine = document.createElement('div');
        stepLine.className = 'artifact-line mono';
        stepLine.textContent = `과정: ${stepSummary}`;

        const uncapLine = document.createElement('div');
        uncapLine.className = 'artifact-line';
        uncapLine.style.color = 'var(--amber)';
        uncapLine.textContent = `관측 한계(미포집): ${(obs.uncaptured || [])[0] || '없음'}`;

        card.append(head, summaryLine, invLine, mutLine, stepLine, uncapLine);
        cardsEl.appendChild(card);
      }
    }

    const uncapEl = document.getElementById('contrastUncaptured');
    if (uncapEl) {
      uncapEl.replaceChildren();
      for (const ext of report.external_uncaptured || []) {
        const box = document.createElement('div');
        box.className = 'item-row';
        const top = document.createElement('div');
        top.className = 'item-top';
        const sysName = document.createElement('span');
        sysName.className = 'item-title';
        sysName.textContent = ext.system;
        const badge = document.createElement('span');
        badge.className = 'hetero-tag';
        badge.textContent = '미포집 (가짜 모방 금지)';
        top.append(sysName, badge);

        const reason = document.createElement('div');
        reason.className = 'item-meta';
        reason.textContent = ext.reason;

        const hook = document.createElement('div');
        hook.className = 'item-meta mono';
        hook.style.color = 'var(--cyan)';
        hook.textContent = `연결 규격: ${ext.required_hook}`;

        box.append(top, reason, hook);
        uncapEl.appendChild(box);
      }
    }
  }

  async function runContrastObservation() {
    if (busy) return;
    busy = true;
    const lensMode = document.getElementById('contrastLensMode')?.value || 'strict';
    const geomOp = document.getElementById('contrastGeomOp')?.value || 'rigid_rotate';
    const codeSource = (document.getElementById('contrastCodeInput')?.value || '').trim();
    setText('canvasHud', `실제 실행 과정 비교대조 관측 중 (렌즈=${lensMode}, 3D연산=${geomOp})...`);
    try {
      const report = await apiJson('/api/scale-rotor/observe-contrast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lens_mode: lensMode,
          geom_op: geomOp,
          code_source: codeSource || undefined,
        }),
      });
      if (report.rotor_state) {
        applyState(report.rotor_state);
      }
      renderContrastReport(report);
      setText(
        'canvasHud',
        `실측 비교대조 완료 (${report.observer_lens?.label}) — 불변(0) ${report.summary?.total_invariants_0}건 · 변화(1) ${report.summary?.total_mutations_1}건 · 원형재현 ${report.summary?.all_reproduction_verified ? 'PASS' : 'FAIL'}`
      );
    } catch (err) {
      setText('canvasHud', `실행 과정 관측 오류: ${err.message}`);
    } finally {
      busy = false;
    }
  }

  function renderVesselTrajectoryReport(report) {
    const panel = document.getElementById('contrastReport');
    if (!panel || !report) return;
    panel.classList.add('visible');

    const titleEl = document.getElementById('contrastReportTitle');
    if (titleEl) {
      titleEl.style.color = 'var(--emerald)';
      titleEl.textContent = '그릇 간 위상 대조 · 연속 스냅샷 궤적 스케일 로터 (Node.js ↔ L1 Python ↔ 디스크 원장)';
    }
    const vbar = document.getElementById('vesselToolbar');
    if (vbar) vbar.classList.add('visible');
    const pbar = document.getElementById('phaseSyncToolbar');
    if (pbar) pbar.classList.remove('visible');
    const dbar = document.getElementById('digestToolbar');
    if (dbar) dbar.classList.remove('visible');

    const sum = report.summary || {};
    const s3 = report.scale_3_cross_vessel_plane || {};
    const s2 = report.scale_2_trajectory_rotor || {};

    setText(
      'contrastSummaryMeta',
      `스냅샷 ${sum.snapshots_captured ?? 0}틱 · 2차 승화법칙(0) ${sum.elevated_laws_count ?? 0}건 · 이탈(1) ${sum.regime_shifts_count ?? 0}건 · 그릇어긋남 ${sum.diverged_vessel_pairs ?? 0}쌍 · 재현 ${sum.all_reproduction_verified ? 'PASS' : 'FAIL'}`
    );
    setText('contrastInsight', sum.principle_note || '');

    const cardsEl = document.getElementById('contrastCards');
    if (cardsEl) {
      cardsEl.replaceChildren();

      // Card 1: Scale 3 — Cross-Vessel Structural Plane Contrast (Node <-> Python <-> Disk)
      const c3 = document.createElement('div');
      c3.className = 'artifact-card';
      const h3 = document.createElement('div');
      h3.className = 'artifact-head';
      const t3 = document.createElement('span');
      t3.style.color = 'var(--emerald)';
      t3.textContent = 'Scale 3 · 그릇 간 면 대조 (Node.js ↔ Python 메모리 ↔ 디스크 원장)';
      const st3 = document.createElement('span');
      st3.className = 'mono';
      st3.style.fontSize = '10px';
      st3.style.color = s3.all_vessels_coherent ? 'var(--emerald)' : 'var(--crimson)';
      st3.textContent = s3.all_vessels_coherent ? '● 전 그릇 정합 (0)' : `▲ 위상 어긋남 ${s3.diverged_pair_count ?? 0}쌍 (1)`;
      h3.append(t3, st3);
      c3.appendChild(h3);

      const latestV = report.latest_snapshot?.vessels || {};
      const vSnapLine = document.createElement('div');
      vSnapLine.className = 'artifact-line mono';
      vSnapLine.style.color = 'var(--text-primary)';
      vSnapLine.textContent =
        `Node(c=${latestV.node_runtime?.cycle ?? '?'}, heap=${latestV.node_runtime?.memory_heap_used_mb ?? '?'}MB, req=${latestV.node_runtime?.http_requests_served ?? '?'}) | ` +
        `PyRAM(c=${latestV.l1_python_memory?.cycle ?? '?'}, ice=${latestV.l1_python_memory?.ice_seed_count ?? '?'}) | ` +
        `Disk(c=${latestV.disk_ice_ledger?.cycle ?? '?'}, ${latestV.disk_ice_ledger?.file_size_bytes ?? 0}B)`;
      c3.appendChild(vSnapLine);

      for (const pair of s3.pairs || []) {
        const line = document.createElement('div');
        line.className = 'artifact-line';
        line.style.color = pair.status === 'COHERENT' ? 'var(--cyan)' : pair.status === 'DIVERGED' ? 'var(--crimson)' : 'var(--amber)';
        const divDetail = (pair.divergent_1 || [])
          .slice(0, 3)
          .map((d) => `${d.entity}: ${formatValCompact(d.before)}≠${formatValCompact(d.after)}`)
          .join(' | ');
        line.textContent = divDetail ? `${pair.diagnosis} → ${divDetail}` : pair.diagnosis;
        c3.appendChild(line);
      }
      cardsEl.appendChild(c3);

      // Card 2: Scale 2 — Continuous Snapshot Trajectory Rotor (Δ_{k-1} <-> Δ_k -> Δ²)
      const c2 = document.createElement('div');
      c2.className = 'artifact-card';
      const h2 = document.createElement('div');
      h2.className = 'artifact-head';
      const t2 = document.createElement('span');
      t2.style.color = 'var(--cyan)';
      t2.textContent = 'Scale 2 · 스냅샷 궤적 로터 (Δ_{k-1} ↔ Δ_k → 2차 변화법칙 승화)';
      const st2 = document.createElement('span');
      st2.className = 'mono';
      st2.style.fontSize = '10px';
      st2.style.color = s2.latest?.reproduction?.verified ? 'var(--emerald)' : 'var(--amber)';
      st2.textContent = s2.ready
        ? `● 2차 재현 ${s2.latest?.reproduction?.verified ? 'PASS' : 'FAIL'}`
        : '3틱 이상 누적 시 활성화';
      h2.append(t2, st2);
      c2.appendChild(h2);

      if (s2.ready && s2.latest) {
        const spanLine = document.createElement('div');
        spanLine.className = 'artifact-line mono';
        spanLine.style.color = 'var(--text-primary)';
        spanLine.textContent = `관측 구간: ${s2.latest.span}`;

        const lawList = (s2.latest.elevated_laws_0 || [])
          .slice(0, 5)
          .map((x) => `${x.entity}(Δ=${formatValCompact(x.value)})`)
          .join(' | ');
        const lawLine = document.createElement('div');
        lawLine.className = 'artifact-line';
        lawLine.style.color = 'var(--cyan)';
        lawLine.textContent = `1→0 승화된 불변 변화법칙 (${(s2.latest.elevated_laws_0 || []).length}건): ${lawList || '없음'}`;

        const shiftList = (s2.latest.regime_shifts_1 || [])
          .slice(0, 4)
          .map((m) => `${m.entity}: ${formatValCompact(m.before)}→${formatValCompact(m.after)}`)
          .join(' | ');
        const shiftLine = document.createElement('div');
        shiftLine.className = 'artifact-line';
        shiftLine.style.color = 'var(--crimson)';
        shiftLine.textContent = `2차 규칙 이탈·드리프트 (${(s2.latest.regime_shifts_1 || []).length}건): ${shiftList || '없음 (변화율 안정)'}`;

        const noteLine = document.createElement('div');
        noteLine.className = 'artifact-line';
        noteLine.textContent = s2.explanation || '';

        c2.append(spanLine, lawLine, shiftLine, noteLine);
      } else {
        const emptyLine = document.createElement('div');
        emptyLine.className = 'artifact-line';
        emptyLine.textContent = '연속 3틱 포집을 누르면 Δ(t0→t1)과 Δ(t1→t2)를 비교해 1차 변화가 2차 불변 법칙(0)으로 승화하는 과정을 실측합니다.';
        c2.appendChild(emptyLine);
      }
      cardsEl.appendChild(c2);

      // Card 3: Scale 1 — Recent 1st-Order Snapshot Transitions S(t_{k-1}) -> S(t_k)
      const c1 = document.createElement('div');
      c1.className = 'artifact-card';
      c1.style.gridColumn = '1 / -1';
      const h1 = document.createElement('div');
      h1.className = 'artifact-head';
      const t1 = document.createElement('span');
      t1.style.color = 'var(--amber)';
      t1.textContent = 'Scale 1 · 1차 연속 스냅샷 전이 궤적 (S(t_{k-1}) ↔ S(t_k))';
      const st1 = document.createElement('span');
      st1.className = 'mono';
      st1.style.fontSize = '10px';
      st1.style.color = 'var(--emerald)';
      st1.textContent = `전이 ${(report.scale_1_transitions || []).length}구간 · 원형재현 ${sum.all_reproduction_verified ? 'PASS' : 'FAIL'}`;
      h1.append(t1, st1);
      c1.appendChild(h1);

      for (const tr of (report.scale_1_transitions || []).slice(-4)) {
        const trLine = document.createElement('div');
        trLine.className = 'artifact-line mono';
        const muts = (tr.mutations_1 || [])
          .slice(0, 4)
          .map((m) => `${m.entity}(${formatValCompact(m.before)}→${formatValCompact(m.after)})`)
          .join(', ');
        trLine.textContent = `${tr.label} | 불변(0) ${tr.invariants_0_count}건 · 변화(1) ${tr.mutations_1_count}건 [${tr.reproduction?.verified ? '재현PASS' : 'FAIL'}] :: ${muts}`;
        c1.appendChild(trLine);
      }
      cardsEl.appendChild(c1);
    }

    const uncapEl = document.getElementById('contrastUncaptured');
    if (uncapEl) {
      uncapEl.replaceChildren();
      for (const u of report.uncaptured || []) {
        const box = document.createElement('div');
        box.className = 'item-row';
        const line = document.createElement('div');
        line.className = 'item-meta';
        line.style.color = 'var(--amber)';
        line.textContent = `[미포집 경계] ${u}`;
        box.appendChild(line);
        uncapEl.appendChild(box);
      }
    }
  }

  async function runVesselTrajectory(mode = 'capture_sequence') {
    if (busy) return;
    busy = true;
    const lensMode = document.getElementById('contrastLensMode')?.value || 'strict';
    setText('canvasHud', `그릇 간 위상 대조 · 스냅샷 궤적 로터 실행 중 (${mode}, 렌즈=${lensMode})...`);
    try {
      const report = await apiJson('/api/scale-rotor/observe-vessel-trajectory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, lens_mode: lensMode }),
      });
      if (report.rotor_state) {
        applyState(report.rotor_state);
      }
      renderVesselTrajectoryReport(report);
      const sum = report.summary || {};
      setText(
        'canvasHud',
        `그릇·궤적 로터 완료 (${mode}) — 스냅샷 ${sum.snapshots_captured}틱 · 2차 승화법칙(0) ${sum.elevated_laws_count}건 · 그릇어긋남 ${sum.diverged_vessel_pairs}쌍`
      );
    } catch (err) {
      setText('canvasHud', `그릇·궤적 로터 오류: ${err.message}`);
    } finally {
      busy = false;
    }
  }

  function renderPhaseSyncReport(report) {
    const panel = document.getElementById('contrastReport');
    if (!panel || !report) return;
    panel.classList.add('visible');

    const titleEl = document.getElementById('contrastReportTitle');
    if (titleEl) {
      titleEl.style.color = '#c4b5fd';
      titleEl.textContent = '양방향 공통분모 위상 동기화 실증 (일방통행 각도·시간차 오차 ↔ A⇄B 공통분모 정합)';
    }
    const vbar = document.getElementById('vesselToolbar');
    if (vbar) vbar.classList.remove('visible');
    const pbar = document.getElementById('phaseSyncToolbar');
    if (pbar) pbar.classList.add('visible');
    const dbar = document.getElementById('digestToolbar');
    if (dbar) dbar.classList.remove('visible');

    const sum = report.summary || {};
    const dual = report.dual_observer_sync || {};
    const ow = dual.one_way_observation || {};
    const bi = dual.bidirectional_sync || {};
    const lv = report.live_vessel_sync || null;

    setText(
      'contrastSummaryMeta',
      `일방통행 RMSE ${sum.one_way_rmse ?? '?'} → 동기화 RMSE ${sum.synced_rmse ?? '?'} (${sum.error_reduction_pct ?? 0}% 상쇄) · 왕복 ${sum.roundtrip_verified ? 'PASS' : 'FAIL'}`
    );
    setText('contrastInsight', sum.principle_note || '');

    const cardsEl = document.getElementById('contrastCards');
    if (cardsEl) {
      cardsEl.replaceChildren();

      // Card 1: One-Way Observation Error (Angle + Proper Clock Mismatch + Asymmetry)
      const c1 = document.createElement('div');
      c1.className = 'artifact-card';
      const h1 = document.createElement('div');
      h1.className = 'artifact-head';
      const t1 = document.createElement('span');
      t1.style.color = 'var(--crimson)';
      t1.textContent = '1. 일방통행 관측 (A→B / B→A 단방향 강제 비교)';
      const st1 = document.createElement('span');
      st1.className = 'mono';
      st1.style.fontSize = '10px';
      st1.style.color = 'var(--crimson)';
      st1.textContent = `RMSE ${ow.rmse_error ?? '?'} · 비대칭 ${ow.directional_asymmetry ? '발생' : '없음'}`;
      h1.append(t1, st1);

      const owDiag = document.createElement('div');
      owDiag.className = 'artifact-line';
      owDiag.style.color = 'var(--text-primary)';
      owDiag.textContent = ow.diagnosis || '';

      const owMeta = document.createElement('div');
      owMeta.className = 'artifact-line mono';
      owMeta.style.color = 'var(--crimson)';
      owMeta.textContent = `A→B(${dual.inputs?.lens_a}): 불변(0) ${ow.a_to_b_invariants_0_count}건 · 변화(1) ${ow.a_to_b_mutations_1_count}건 | B→A(${dual.inputs?.lens_b}): 불변(0) ${ow.b_to_a_invariants_0_count}건 · 변화(1) ${ow.b_to_a_mutations_1_count}건`;

      c1.append(h1, owDiag, owMeta);
      cardsEl.appendChild(c1);

      // Card 2: Bidirectional Common-Denominator Phase Sync (A ⇄ C ⇄ B)
      const c2 = document.createElement('div');
      c2.className = 'artifact-card';
      const h2 = document.createElement('div');
      h2.className = 'artifact-head';
      const t2 = document.createElement('span');
      t2.style.color = 'var(--emerald)';
      t2.textContent = '2. 양방향 공통분모 위상 동기화 (A ⇄ 대칭축 C ⇄ B)';
      const st2 = document.createElement('span');
      st2.className = 'mono';
      st2.style.fontSize = '10px';
      st2.style.color = bi.reproduction?.verified ? 'var(--emerald)' : 'var(--crimson)';
      st2.textContent = bi.reproduction?.verified
        ? `● 왕복 PASS (오차 ${bi.synced_rmse_error})`
        : '✖ 동기화 미달';
      h2.append(t2, st2);

      const recLine = document.createElement('div');
      recLine.className = 'artifact-line mono';
      recLine.style.color = 'var(--text-primary)';
      recLine.textContent =
        `역추출 고유시간비 ω_B/ω_A=${bi.recovered_clock_ratio} (오차 ${bi.clock_ratio_err}) | ` +
        `위상지연 φ=${bi.recovered_phase_lag_rad}rad (오차 ${bi.phase_lag_err}) | ` +
        `상대각 Δθ=${bi.recovered_angle_offset_deg}°`;

      const cd0 = (bi.common_denominator_0 || []).map((x) => `${x.entity}=${x.value}`).join(' | ');
      const cdLine = document.createElement('div');
      cdLine.className = 'artifact-line';
      cdLine.style.color = 'var(--cyan)';
      cdLine.textContent = `공통분모(0 · 양방향 보존): ${cd0}`;

      const rtLine = document.createElement('div');
      rtLine.className = 'artifact-line mono';
      rtLine.style.color = 'var(--emerald)';
      rtLine.textContent = `A→C→A / B→C→B 왕복 최대오차 = ${bi.max_roundtrip_error} (겹침 구간 ${bi.overlap_samples}샘플)`;

      c2.append(h2, recLine, cdLine, rtLine);
      cardsEl.appendChild(c2);

      // Card 3: Live 3-Vessel Proper Clocks (Node.js ⇄ L1 Python ⇄ Disk)
      if (lv) {
        const c3 = document.createElement('div');
        c3.className = 'artifact-card';
        c3.style.gridColumn = '1 / -1';
        const h3 = document.createElement('div');
        h3.className = 'artifact-head';
        const t3 = document.createElement('span');
        t3.style.color = '#c4b5fd';
        t3.textContent = '3. 실제 구동 중인 3그릇 고유 시간 축 & 위상 지연 실측 (Node.js ⇄ L1 Python ⇄ Disk)';
        const st3 = document.createElement('span');
        st3.className = 'mono';
        st3.style.fontSize = '10px';
        st3.style.color = lv.phase_lags?.synchronized ? 'var(--emerald)' : 'var(--crimson)';
        st3.textContent = lv.phase_lags?.synchronized ? '● 3그릇 위상 잠금(φ=0)' : `▲ 위상차 φ=${lv.phase_lags?.python_ram_minus_disk_cycles} cycle`;
        h3.append(t3, st3);

        const pc = lv.proper_clocks || {};
        const clkLine = document.createElement('div');
        clkLine.className = 'artifact-line mono';
        clkLine.style.color = 'var(--text-primary)';
        clkLine.textContent =
          `Node 시계(${pc.node_runtime?.clock_axis}: ${pc.node_runtime?.proper_tick}, cycle=${pc.node_runtime?.synced_cycle}) | ` +
          `Python 시계(${pc.l1_python_memory?.clock_axis}: ${pc.l1_python_memory?.proper_tick}) | ` +
          `Disk 시계(${pc.disk_ice_ledger?.clock_axis}: ${pc.disk_ice_ledger?.proper_tick}, ${pc.disk_ice_ledger?.file_size_bytes}B)`;

        const om = lv.one_way_vs_mutual || {};
        const mutLine = document.createElement('div');
        mutLine.className = 'artifact-line';
        mutLine.style.color = 'var(--cyan)';
        mutLine.textContent =
          `양방향 공통분모(0): [${(om.mutual_common_denominator_0 || []).join(', ') || '없음'}] | ` +
          `렌즈 각도 불일치 항목: [${(om.lens_angle_disagreement || []).join(', ') || '없음'}]`;

        c3.append(h3, clkLine, mutLine);
        cardsEl.appendChild(c3);
      }
    }

    const uncapEl = document.getElementById('contrastUncaptured');
    if (uncapEl) {
      uncapEl.replaceChildren();
      for (const u of report.uncaptured || []) {
        const box = document.createElement('div');
        box.className = 'item-row';
        const line = document.createElement('div');
        line.className = 'item-meta';
        line.style.color = 'var(--amber)';
        line.textContent = `[미포집 경계] ${u}`;
        box.appendChild(line);
        uncapEl.appendChild(box);
      }
    }
  }

  async function runPhaseSync() {
    if (busy) return;
    busy = true;
    const angle_b_deg = Number(document.getElementById('syncAngleInput')?.value ?? 42);
    const clock_rate_b = Number(document.getElementById('syncClockInput')?.value ?? 1.5);
    const phase_lag_b = Number(document.getElementById('syncLagInput')?.value ?? 0.65);
    const lens_a_mode = document.getElementById('contrastLensMode')?.value || 'strict';
    const lens_b_mode = lens_a_mode === 'strict' ? 'tolerant' : 'strict';
    setText('canvasHud', `양방향 공통분모 위상 동기화 실측 중 (Δθ=${angle_b_deg}°, ω_B=${clock_rate_b}x, φ=${phase_lag_b}rad)...`);
    try {
      const report = await apiJson('/api/scale-rotor/observe-phase-sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          angle_b_deg,
          clock_rate_b,
          phase_lag_b,
          lens_a_mode,
          lens_b_mode,
        }),
      });
      if (report.rotor_state) {
        applyState(report.rotor_state);
      }
      renderPhaseSyncReport(report);
      const sum = report.summary || {};
      setText(
        'canvasHud',
        `위상 동기화 완료 — 일방통행 RMSE ${sum.one_way_rmse} → 공통분모 RMSE ${sum.synced_rmse} (${sum.error_reduction_pct}% 상쇄 · 왕복 ${sum.roundtrip_verified ? 'PASS' : 'FAIL'})`
      );
    } catch (err) {
      setText('canvasHud', `양방향 위상 동기화 오류: ${err.message}`);
    } finally {
      busy = false;
    }
  }

  function renderDigestLabReport(report) {
    const panel = document.getElementById('contrastReport');
    if (!panel || !report) return;
    panel.classList.add('visible');

    const titleEl = document.getElementById('contrastReportTitle');
    if (titleEl) {
      titleEl.style.color = 'var(--amber)';
      titleEl.textContent = '기존 재료 소화·흡수 → 재조합 모방 → 원본·모방 차이 학습 → 차이 기반 재창조 환경';
    }
    const vbar = document.getElementById('vesselToolbar');
    if (vbar) vbar.classList.remove('visible');
    const pbar = document.getElementById('phaseSyncToolbar');
    if (pbar) pbar.classList.remove('visible');
    const dbar = document.getElementById('digestToolbar');
    if (dbar) dbar.classList.add('visible');

    const sum = report.summary || {};
    const s1 = report.stage_1_digest || {};
    const s23 = report.stage_2_3_imitate_and_learn_difference || {};
    const s4 = report.stage_4_recreate || {};

    setText(
      'contrastSummaryMeta',
      `${sum.absorption_status === 'DIGESTED_AND_VERIFIED' ? '● 원리 소화 완료' : '▲ 미포집 재료 감지'} · ${sum.rounds_taken ?? 0}라운드 · RMSE ${sum.initial_round_rmse ?? '?'} → ${sum.final_round_rmse ?? '?'}`
    );
    setText('contrastInsight', sum.principle_note || '');

    const cardsEl = document.getElementById('contrastCards');
    if (cardsEl) {
      cardsEl.replaceChildren();

      // Card 1: Stage 1 — Digesting Real Existing Workspace Knowledge & Original Trajectory
      const c1 = document.createElement('div');
      c1.className = 'artifact-card';
      const h1 = document.createElement('div');
      h1.className = 'artifact-head';
      const t1 = document.createElement('span');
      t1.style.color = 'var(--cyan)';
      t1.textContent = '1단계 · 기존 지식·재료 소화 (실제 워크스페이스 AST + 원본 관측)';
      const st1 = document.createElement('span');
      st1.className = 'mono';
      st1.style.fontSize = '10px';
      st1.style.color = 'var(--cyan)';
      st1.textContent = `파일 ${s1.workspace_knowledge?.files_scanned ?? 0} · 순수재료 ${s1.workspace_knowledge?.pure_reusable_count ?? 0}`;
      h1.append(t1, st1);

      const origTitle = document.createElement('div');
      origTitle.className = 'artifact-line';
      origTitle.style.color = 'var(--text-primary)';
      origTitle.textContent = `${s1.original?.title || ''} (${s1.original?.probes_observed ?? 0}개 입출력 프로브 실측 · 내부 계수 비공개)`;

      const wsNote = document.createElement('div');
      wsNote.className = 'artifact-line';
      wsNote.textContent = s1.workspace_knowledge?.note || '';

      const palLine = document.createElement('div');
      palLine.className = 'artifact-line mono';
      palLine.style.color = 'var(--amber)';
      palLine.textContent = `보유 기본 재료(${(s1.available_ingredients || []).length}종): ${(s1.available_ingredients || []).map((p) => p.symbol).join(', ')}`;

      c1.append(h1, origTitle, wsNote, palLine);
      cardsEl.appendChild(c1);

      // Card 2: Stage 2 & 3 — Iterative Recombination Imitation & Original <-> Imitation Difference Learning
      const c2 = document.createElement('div');
      c2.className = 'artifact-card';
      const h2 = document.createElement('div');
      h2.className = 'artifact-head';
      const t2 = document.createElement('span');
      t2.style.color = s23.absorbed_successfully ? 'var(--emerald)' : 'var(--crimson)';
      t2.textContent = '2~3단계 · 재조합 모방 & 원본↔모방 차이 학습';
      const st2 = document.createElement('span');
      st2.className = 'mono';
      st2.style.fontSize = '10px';
      st2.style.color = s23.absorbed_successfully ? 'var(--emerald)' : 'var(--crimson)';
      st2.textContent = s23.absorbed_successfully
        ? `● 소화 PASS (RMSE ${s23.final_probe_rmse})`
        : `▲ 미포집 (RMSE ${s23.final_probe_rmse})`;
      h2.append(t2, st2);
      c2.appendChild(h2);

      for (const rd of s23.rounds || []) {
        const rLine = document.createElement('div');
        rLine.className = 'artifact-line mono';
        rLine.style.color = rd.rmse_original_vs_imitation <= (report.convergence_threshold || 0.01) ? 'var(--emerald)' : 'var(--text-primary)';
        rLine.textContent = `R${rd.round} [+${rd.added_ingredient_label}, 상관 ${rd.residual_correlation}] → 모방: ${rd.imitation_formula} | 오차 RMSE=${rd.rmse_original_vs_imitation} (일치0:${rd.matched_0_probes} / 차이1:${rd.mismatched_1_probes})`;
        c2.appendChild(rLine);

        const hintLine = document.createElement('div');
        hintLine.className = 'artifact-line';
        hintLine.style.color = 'var(--text-secondary)';
        hintLine.textContent = `  ↳ 차이 학습: ${rd.learned_difference_note}`;
        c2.appendChild(hintLine);
      }
      cardsEl.appendChild(c2);

      // Card 3: Stage 4 — Re-Creation Using Learned Difference & Cross-Original Recombination (A ⊕ B)
      const c3 = document.createElement('div');
      c3.className = 'artifact-card';
      c3.style.gridColumn = '1 / -1';
      const h3 = document.createElement('div');
      h3.className = 'artifact-head';
      const t3 = document.createElement('span');
      t3.style.color = 'var(--amber)';
      t3.textContent = '4단계 · 학습된 차이를 이용한 재창조 (실제 궤적 실행 및 원형↔재창조 대조)';
      const st3 = document.createElement('span');
      st3.className = 'mono';
      st3.style.fontSize = '10px';
      st3.style.color = s4.cross_recombination?.genuinely_novel ? 'var(--emerald)' : 'var(--amber)';
      st3.textContent = s4.cross_recombination?.genuinely_novel ? '● 신규 창발 거동 확인' : '부분 변형';
      h3.append(t3, st3);

      const dm = s4.difference_modulation || {};
      const dmLine = document.createElement('div');
      dmLine.className = 'artifact-line mono';
      dmLine.style.color = 'var(--cyan)';
      dmLine.textContent =
        `${dm.title || ''} [${dm.pivoted_difference || ''}] → 재창조식: ${dm.recreated_formula || ''} | ` +
        `거동 전환: ${dm.original_trend} → ${dm.recreated_trend} (원본 대비 궤적 차이=${dm.trajectory_divergence_from_original})`;

      const cr = s4.cross_recombination || {};
      const crLine = document.createElement('div');
      crLine.className = 'artifact-line mono';
      crLine.style.color = 'var(--emerald)';
      crLine.textContent =
        `${cr.title || ''} ⇒ [${cr.emergent_name || ''}] 식: ${cr.recreated_formula || ''} | ` +
        `계승(0)=[${(cr.inherited_0_from_a || []).join(',')}] + 결합(1)=[${(cr.added_1_from_b || []).join(',')}] | ` +
        `A와 차이=${cr.divergence_from_original_a}, B와 차이=${cr.divergence_from_partner_b}, 거동=${cr.recreated_trend}`;

      c3.append(h3, dmLine, crLine);
      cardsEl.appendChild(c3);
    }

    const uncapEl = document.getElementById('contrastUncaptured');
    if (uncapEl) {
      uncapEl.replaceChildren();
      for (const u of report.uncaptured || []) {
        const box = document.createElement('div');
        box.className = 'item-row';
        const line = document.createElement('div');
        line.className = 'item-meta';
        line.style.color = 'var(--amber)';
        line.textContent = `[미포집 경계] ${u}`;
        box.appendChild(line);
        uncapEl.appendChild(box);
      }
    }
  }

  async function runDigestLab() {
    if (busy) return;
    busy = true;
    const original_id = document.getElementById('digestOriginalSelect')?.value || 'damped_harmonic';
    const partner_id = document.getElementById('digestPartnerSelect')?.value || 'wave_forcing';
    const custom_formula = (document.getElementById('digestCustomFormula')?.value || '').trim();
    const lens_mode = document.getElementById('contrastLensMode')?.value || 'strict';
    setText('canvasHud', `소화·모방·차이학습·재창조 실행 중 (원본=${original_id}, 교차재료=${partner_id})...`);
    try {
      const report = await apiJson('/api/scale-rotor/digest-imitate-recreate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_id,
          partner_id,
          custom_formula: original_id === 'custom_formula' ? custom_formula : undefined,
          lens_mode,
        }),
      });
      if (report.rotor_state) {
        applyState(report.rotor_state);
      }
      renderDigestLabReport(report);
      const sum = report.summary || {};
      setText(
        'canvasHud',
        `소화·모방·재창조 완료 (${sum.absorption_status}) — RMSE ${sum.initial_round_rmse} → ${sum.final_round_rmse} · 재창조 신규성 A차이=${sum.recreation_novelty_from_a}`
      );
    } catch (err) {
      setText('canvasHud', `소화·모방·재창조 오류: ${err.message}`);
    } finally {
      busy = false;
    }
  }

  function toggleAutoFlow() {
    const btn = document.getElementById('btnAutoFlow');
    if (autoTimer) {
      clearInterval(autoTimer);
      autoTimer = null;
      if (btn) {
        btn.classList.remove('active-flow');
        btn.textContent = '연속 흐름 시작';
      }
      return;
    }
    if (btn) {
      btn.classList.add('active-flow');
      btn.textContent = '연속 흐름 정지';
    }
    runStep();
    autoTimer = setInterval(() => {
      if (!busy) runStep();
    }, 850);
  }

  // ==========================================================================
  // Event Binding
  // ==========================================================================
  document.querySelectorAll('.frame-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const f = btn.dataset.frame;
      setFrameUI(f);
      if (f && f !== 'atelier3d') {
        apiJson('/api/scale-rotor/frame', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ frame: f }),
        }).catch(() => {});
      }
    });
  });

  document.querySelectorAll('input[type="range"]').forEach((el) => {
    el.addEventListener('input', syncSliderReadouts);
  });

  document.querySelectorAll('.preset-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const p = PRESETS[btn.dataset.preset];
      if (!p) return;
      document.getElementById('conceptInput').value = p.concept;
      document.getElementById('visStructure').value = p.vision.structure;
      document.getElementById('visMotion').value = p.vision.motion;
      document.getElementById('visContrast').value = p.vision.contrast;
      document.getElementById('audFreq').value = p.audio.freq;
      document.getElementById('audHarm').value = p.audio.harm;
      document.getElementById('noiseRatio').value = p.audio.noise;
      document.getElementById('langInput').value = p.language;
      document.getElementById('behFatigue').value = p.behavior.fatigue;
      document.getElementById('behThreat').value = p.behavior.threat;
      document.getElementById('behCohesion').value = p.behavior.cohesion;
      document.getElementById('behTerrain').value = p.behavior.terrain;
      syncSliderReadouts();
      runStep();
    });
  });

  document.getElementById('btnStep').addEventListener('click', () => runStep());
  document.getElementById('btnAutoFlow').addEventListener('click', toggleAutoFlow);
  document.getElementById('btnShock').addEventListener('click', () =>
    runStep({ shock: { strength: 0.85, spectrum: [0.14, 0.94, 0.95, 0.20] } })
  );
  document.getElementById('btnBenchmark').addEventListener('click', runBenchmark);
  document.getElementById('btnContrastObs').addEventListener('click', runContrastObservation);
  document.getElementById('btnVesselRotor').addEventListener('click', () => runVesselTrajectory('capture_sequence'));
  document.getElementById('btnPhaseSync').addEventListener('click', runPhaseSync);
  document.getElementById('btnRunPhaseSyncAgain').addEventListener('click', runPhaseSync);
  document.getElementById('btnDigestLab').addEventListener('click', runDigestLab);
  document.getElementById('btnRunDigestAgain').addEventListener('click', runDigestLab);
  document.querySelectorAll('.vessel-mode-btn').forEach((btn) => {
    if (btn.id === 'btnRunPhaseSyncAgain' || btn.id === 'btnRunDigestAgain') return;
    btn.addEventListener('click', () => runVesselTrajectory(btn.dataset.vmode || 'capture_tick'));
  });
  document.getElementById('btnCloseContrast').addEventListener('click', () => {
    const p = document.getElementById('contrastReport');
    if (p) p.classList.remove('visible');
  });
  document.getElementById('btnIngestConcept').addEventListener('click', () => ingestConcept());
  document.getElementById('conceptInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') ingestConcept();
  });
  document.getElementById('btnReset').addEventListener('click', async () => {
    if (autoTimer) toggleAutoFlow();
    try {
      const data = await apiJson('/api/scale-rotor/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ clear_ledger: false }),
      });
      applyState(data);
    } catch (err) {
      setText('canvasHud', `초기화 오류: ${err.message}`);
    }
  });

  // Canvas pointer interaction (Probe + Seed Restore + 3D Drag Rotation)
  canvas.addEventListener('pointerdown', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (activeFrame === 'cube' || activeFrame === 'sphere') {
      dragging = true;
      dragLast = { x, y };
      canvas.setPointerCapture(e.pointerId);
      return;
    }

    for (const t of interactiveHitTargets) {
      if (x >= t.x && x <= t.x + t.w && y >= t.y && y <= t.y + t.h) {
        if (t.type === 'seed' && t.seedId) {
          recallSeed(t.seedId);
          return;
        }
        hoveredInfo = t.info;
        setText('canvasHud', t.info);
        return;
      }
    }
  });

  canvas.addEventListener('pointermove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (dragging) {
      viewYaw += (x - dragLast.x) * 0.009;
      viewPitch = Math.max(-1.25, Math.min(1.25, viewPitch + (y - dragLast.y) * 0.009));
      dragLast = { x, y };
      renderCanvas();
      return;
    }

    let found = null;
    for (const t of interactiveHitTargets) {
      if (x >= t.x && x <= t.x + t.w && y >= t.y && y <= t.y + t.h) {
        found = t.info;
        break;
      }
    }
    if (found !== hoveredInfo) {
      hoveredInfo = found;
      if (found) setText('canvasHud', found);
    }
  });

  canvas.addEventListener('pointerup', () => {
    dragging = false;
  });

  window.addEventListener('resize', () => {
    if (state) renderCanvas();
  });

  // Expose safe state sync hook for Unified Causal Dataflow viewport
  window.__elysiaApplyRotorState = applyState;

  // Boot
  syncSliderReadouts();
  setFrameUI(resolveInitialFrame());
  loadInitialState();
})();
