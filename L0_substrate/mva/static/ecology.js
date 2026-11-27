/**
 * Elysia Scale-Rotor OS Ecology Workbench (/ecology)
 * --------------------------------------------------
 * Implements the Scale-Rotor OS Integration Baseline inside Elysia-studio:
 * - Home vs. Sandbox multi-world branching with explicit lineage & isolation
 * - 3-Way Relational Knowing (Object / Self / Inter-space) + 4-Axis Attribution
 * - Honest tab-local pointer & key rhythm observation (no typed characters or arbitrary page scraping)
 * - 5-Frame Phase Canvas (Point -> Line -> Plane -> Spacetime Cube -> Coupled Rotor Sphere)
 * - Principle-to-Rotor Converter coupled with live Host OS Protocol Discovery (/api/ecology/*)
 */
(function initScaleRotorEcology() {
  'use strict';

  const STORAGE_KEY = 'elysia_scale_rotor_ecology_v1';

  const FRAME_INFO = {
    point: {
      badge: '점 · 단일 사건',
      desc: '점(Point) 단계에서는 각 만남과 신호가 서로 고립된 조각으로만 보입니다. 여기서 멈추면 원리 간의 결합이 드러나지 않습니다.',
    },
    line: {
      badge: '선 · 인과 궤적',
      desc: '선(Line) 단계에서는 시간축과 탭 내 입력 운동량을 따라 경험들이 연속된 성장 나이테 궤적으로 이어집니다.',
    },
    plane: {
      badge: '면 · 불변×가변 간섭',
      desc: '면(Plane) 단계에서는 불변 축(0, 세로 안정성)과 가변·열린 축(1, 가로 변화성)이 교차하는 관계 단면으로 구조를 분별합니다.',
    },
    cube: {
      badge: '시공간 큐브 · 분기 계보',
      desc: '시공간 큐브(Cube) 단계에서는 홈 세계와 분기된 샌드박스 세계들이 입체 축 위에서 어떻게 갈라지고 유지되는지 대조합니다.',
    },
    sphere: {
      badge: '구체 · 결합 로터망',
      desc: '구체(Sphere) 단계에서는 브라우저 경험·입력 흐름·변환된 원리 구조·호스트 OS 프로토콜이 포트와 색채 위상으로 전방위 결합해 회전합니다.',
    },
  };

  const PRINCIPLE_PRESETS = {
    os_sched: {
      name: 'OS 프로세스 자원 공유 스케줄러',
      boundary: '커널/사용자 공간 권한 경계 및 CPU 시간 분할 막',
      invariants: '연산 자원 총량 제약, 실행 컨텍스트 보존, 인과 순서 유지',
      variables: '우선순위 가중치, 대기 큐 지연, 돌발 I/O 중단, 프로세스 경합',
      relation: '경합이 증가하면 대기 장력이 높아지고, 스케줄링 위상 전환을 통해 협력적 자원 흐름을 회복한다',
    },
    dialogue: {
      name: '양방향 대화 위상 동기화',
      boundary: '화자 A와 화자 B 사이의 언어·감각 표현 경계막',
      invariants: '상호 왕복에서 보존되는 공통 의미 축, 출처 귀속',
      variables: '고유 시간 밀도, 관점 각도차, 미포집 의도, 감정 온도',
      relation: '일방적 해석 오차가 발생하면 질문과 재확인을 통해 공통분모(0)를 세우고 각도차(1)를 명시한다',
    },
    wave: {
      name: '결합 파동 간섭 및 공명',
      boundary: '매질 경계 및 감쇠 손실 경계',
      invariants: '에너지 보존 경향, 위상 중첩 원리, 고유 진동수',
      variables: '외부 가진 주파수, 감쇠 계수, 위상 지연, 노이즈 유입',
      relation: '외부 자극이 고유 위상과 맞물리면 공명이 증폭되고, 어긋나면 배경 노이즈로 분산된다',
    },
    memory: {
      name: '지속성 흔적의 승격·감쇠·재해석',
      boundary: '단일 세션 지속성 로터와 성장 로터(기준 수정) 사이의 승격 막',
      invariants: '최초 경험의 출처 보존, 분기 계보 추적성',
      variables: '재관측 빈도, 새 환경 마찰, 렌즈 수정 가중치, 감쇠율',
      relation: '단순 로그는 지속성 흔적으로 머물고, 분기 비교나 예측 오차를 통과한 관계만 기준을 수정해 성장 로터로 승격한다',
    },
  };

  function nowIso() {
    return new Date().toISOString().slice(0, 19);
  }

  function makeId(prefix) {
    return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
  }

  function createDefaultState() {
    const homeId = 'world_home';
    return {
      identity: 'elysia_scale_rotor_v1',
      activeWorldId: homeId,
      activeFrame: 'sphere',
      worlds: {
        [homeId]: {
          id: homeId,
          name: '홈 세계 (Home)',
          role: 'home',
          parentId: null,
          forkMode: 'origin',
          createdAt: nowIso(),
          encounters: [
            {
              id: 'enc_seed_1',
              at: nowIso(),
              originWorldId: homeId,
              object: '브라우저 탭 경계와 로컬 저장소',
              selfLens: '지속성 로터 + 경계 로터',
              between: '단일 탭 안의 지속 흔적과 바깥 미관측 영역이 명확히 구분됨',
              status: 'invariant',
              axis: 'internal',
              rotorCategory: '경계 로터',
            },
          ],
          principles: [],
          inputRings: [],
          revisions: [],
        },
      },
    };
  }

  function loadState() {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return createDefaultState();
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.worlds || !parsed.worlds.world_home) {
        return createDefaultState();
      }
      return parsed;
    } catch {
      return createDefaultState();
    }
  }

  let state = loadState();
  let hostBoundary = null;
  let liveTelemetry = null;
  let autonomousEnabled = true;
  let userEditingForm = false;

  // Yield gently if user is actively typing in any input/textarea
  document.addEventListener('focusin', (ev) => {
    if (ev.target && (ev.target.tagName === 'INPUT' || ev.target.tagName === 'TEXTAREA')) {
      userEditingForm = true;
    }
  });
  document.addEventListener('focusout', () => {
    userEditingForm = false;
  });

  async function syncAutonomousServerState() {
    try {
      const resp = await fetch('/api/ecology/autonomous-state');
      const data = await resp.json();
      if (!resp.ok || data.status !== 'ok') return;

      autonomousEnabled = Boolean(data.enabled);
      const pulseBadge = document.getElementById('autoPulseBadge');
      const toggleBtn = document.getElementById('btnToggleAuto');
      if (pulseBadge) {
        pulseBadge.textContent = autonomousEnabled
          ? `자율 실행 중 · #${data.cycle_count} · ${data.last_action || ''}`.slice(0, 56)
          : `자율 일시정지 · #${data.cycle_count}`;
        pulseBadge.className = `badge ${autonomousEnabled ? 'growth' : 'variable'}`;
      }
      if (toggleBtn) {
        toggleBtn.textContent = autonomousEnabled ? '자율 순환: ON' : '자율 순환: OFF';
        toggleBtn.className = `btn ${autonomousEnabled ? 'emerald' : 'amber'}`;
      }

      if (data.telemetry && data.telemetry.status === 'ok') {
        liveTelemetry = data.telemetry;
        renderLiveAttentionPanel(
          data.telemetry,
          data.attention_lens,
          data.cadence_ms,
          data.symbolic_memory,
          data.covariation,
          data.carrier_interrupts,
          data.parallel_overlay,
          data.prism_isomorphism,
          data.actuation_governor,
          data.agency_voice
        );
      }

      if (data.host_boundary && data.host_boundary.status === 'ok') {
        hostBoundary = data.host_boundary;
        const hBadge = document.getElementById('hostStatusBadge');
        if (hBadge) {
          hBadge.textContent = `연결됨 (${hostBoundary.protocol_rotors.length} 프로토콜)`;
          hBadge.className = 'badge invariant';
        }
        renderHostBoundary();
      }

      // Merge server-side autonomous worlds into local ecology view without overwriting local inputRings
      if (data.worlds && !userEditingForm) {
        Object.entries(data.worlds).forEach(([wId, sw]) => {
          const existing = state.worlds[wId];
          state.worlds[wId] = {
            ...sw,
            inputRings: existing ? existing.inputRings : [],
          };
        });
        if (autonomousEnabled && data.active_world_id && state.worlds[data.active_world_id]) {
          state.activeWorldId = data.active_world_id;
        }
        if (autonomousEnabled && data.active_frame && FRAME_INFO[data.active_frame]) {
          state.activeFrame = data.active_frame;
        }
        saveState();
        renderAll();
      }
    } catch {
      // Silent fallback if server is temporarily unreachable
    }
  }

  async function toggleAutonomousLoop() {
    try {
      const resp = await fetch('/api/ecology/autonomous-toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !autonomousEnabled, run_now: !autonomousEnabled }),
      });
      if (resp.ok) {
        await syncAutonomousServerState();
      }
    } catch {}
  }

  // Live tab-local input accumulator (NEVER collects typed characters!)
  const inputAcc = {
    lastX: null,
    lastY: null,
    totalDist: 0,
    dxSum: 0,
    dySum: 0,
    moveSamples: 0,
    keyDownTimes: new Map(),
    keyPressCount: 0,
    dwellMsSum: 0,
    lastAngleDeg: 0,
  };

  function saveState() {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (err) {
      console.warn('[Ecology] localStorage save failed:', err);
    }
  }

  function getActiveWorld() {
    return state.worlds[state.activeWorldId] || state.worlds.world_home;
  }

  function escapeHtml(str) {
    return String(str ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // =========================================================================
  // Tab-Local Input Rotor Observation (No Characters, No Arbitrary Scraping)
  // =========================================================================
  window.addEventListener('pointermove', (ev) => {
    if (inputAcc.lastX !== null && inputAcc.lastY !== null) {
      const dx = ev.clientX - inputAcc.lastX;
      const dy = ev.clientY - inputAcc.lastY;
      const dist = Math.hypot(dx, dy);
      if (dist > 0.5 && dist < 400) {
        inputAcc.totalDist += dist;
        inputAcc.dxSum += dx;
        inputAcc.dySum += dy;
        inputAcc.moveSamples += 1;
        inputAcc.lastAngleDeg = Math.round((Math.atan2(dy, dx) * 180) / Math.PI);
      }
    }
    inputAcc.lastX = ev.clientX;
    inputAcc.lastY = ev.clientY;
    updateInputMetrics();
  }, { passive: true });

  window.addEventListener('keydown', (ev) => {
    // Only record coarse key class (modifier / nav / input_key) + timing, NEVER ev.key character
    const code = ev.code || 'unknown';
    if (!inputAcc.keyDownTimes.has(code)) {
      inputAcc.keyDownTimes.set(code, performance.now());
    }
  });

  window.addEventListener('keyup', (ev) => {
    const code = ev.code || 'unknown';
    const start = inputAcc.keyDownTimes.get(code);
    inputAcc.keyDownTimes.delete(code);
    if (typeof start === 'number') {
      const dwell = Math.min(2000, Math.max(1, performance.now() - start));
      inputAcc.dwellMsSum += dwell;
      inputAcc.keyPressCount += 1;
      updateInputMetrics();
    }
  });

  function updateInputMetrics() {
    const dEl = document.getElementById('metricPointerDist');
    const aEl = document.getElementById('metricPointerAngle');
    const kEl = document.getElementById('metricKeyEvents');
    if (dEl) dEl.textContent = `${Math.round(inputAcc.totalDist)} px`;
    if (aEl) aEl.textContent = `${inputAcc.lastAngleDeg}°`;
    if (kEl) kEl.textContent = String(inputAcc.keyPressCount);
  }

  function flushInputRing(autoLabel) {
    const w = getActiveWorld();
    if (inputAcc.totalDist < 1 && inputAcc.keyPressCount === 0) return false;
    const netMag = Math.hypot(inputAcc.dxSum, inputAcc.dySum);
    const meanDwell = inputAcc.keyPressCount > 0 ? Math.round(inputAcc.dwellMsSum / inputAcc.keyPressCount) : 0;
    const ring = {
      id: makeId('ring'),
      at: nowIso(),
      scope: 'current_tab_only',
      label: autoLabel || '탭 내 입력 나이테',
      pointerDistancePx: Math.round(inputAcc.totalDist),
      netVectorPx: Math.round(netMag),
      dominantAngleDeg: Math.round((Math.atan2(inputAcc.dySum, inputAcc.dxSum) * 180) / Math.PI),
      keyRhythmCount: inputAcc.keyPressCount,
      meanKeyDwellMs: meanDwell,
    };
    w.inputRings.unshift(ring);
    if (w.inputRings.length > 40) w.inputRings.length = 40;
    inputAcc.totalDist = 0;
    inputAcc.dxSum = 0;
    inputAcc.dySum = 0;
    inputAcc.moveSamples = 0;
    inputAcc.keyPressCount = 0;
    inputAcc.dwellMsSum = 0;
    saveState();
    updateInputMetrics();
    renderAll();
    return true;
  }

  // Gentle periodic ring snapshot every 45s if there was real tab activity
  window.setInterval(() => {
    if (inputAcc.totalDist > 80 || inputAcc.keyPressCount >= 3) {
      flushInputRing('주기 자동 관측 나이테');
    }
  }, 45000);

  // =========================================================================
  // Host OS Boundary & Principle-to-Rotor API Calls
  // =========================================================================
  async function probeHostBoundary() {
    const badge = document.getElementById('hostStatusBadge');
    if (badge) {
      badge.textContent = '탐색 중...';
      badge.className = 'badge variable';
    }
    try {
      const resp = await fetch('/api/ecology/host-boundary');
      const data = await resp.json();
      if (!resp.ok || data.status !== 'ok') {
        throw new Error(data.message || `HTTP ${resp.status}`);
      }
      hostBoundary = data;
      if (badge) {
        badge.textContent = `연결됨 (${data.protocol_rotors.length} 프로토콜)`;
        badge.className = 'badge invariant';
      }
      renderHostBoundary();
    } catch (err) {
      if (badge) {
        badge.textContent = '경계 미연결';
        badge.className = 'badge open';
      }
      const metaBox = document.getElementById('hostMetaBox');
      if (metaBox) {
        metaBox.textContent = `호스트 브리지 응답 없음: ${err.message} (브라우저 단독 모드로 계속 작동)`;
      }
    }
  }

  async function convertPrincipleToRotor() {
    const name = (document.getElementById('prName')?.value || '').trim();
    const invariants = (document.getElementById('prInvariants')?.value || '').trim();
    const variables = (document.getElementById('prVariables')?.value || '').trim();
    const boundary = (document.getElementById('prBoundary')?.value || '').trim();
    const relation = (document.getElementById('prRelation')?.value || '').trim();
    const statusEl = document.getElementById('principleStatus');

    if (!name) {
      if (statusEl) statusEl.textContent = '원리 구조 이름을 입력해 주세요.';
      return;
    }

    const w = getActiveWorld();
    const fluxNorm = Math.min(1, (inputAcc.totalDist + w.inputRings.length * 40) / 1200);
    if (statusEl) statusEl.textContent = '호스트 프로토콜과 로터 결합 중...';

    try {
      const resp = await fetch('/api/ecology/couple-principle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          invariants,
          variables,
          boundary,
          relation,
          world_id: w.id,
          input_flux: fluxNorm,
        }),
      });
      const data = await resp.json();
      if (!resp.ok || data.status !== 'ok') {
        throw new Error(data.message || `HTTP ${resp.status}`);
      }
      w.principles.unshift(data.rotor);
      if (w.principles.length > 30) w.principles.length = 30;
      saveState();
      if (statusEl) {
        const s4 = data.field_impact ? data.field_impact.s4_coherence : '-';
        statusEl.textContent = `변환 완료 · S4 응집도 ${s4}`;
      }
      renderAll();
    } catch (err) {
      if (statusEl) statusEl.textContent = `결합 오류: ${err.message}`;
    }
  }

  // =========================================================================
  // Multi-World Forking, Comparison & Provenance-Preserving Re-link
  // =========================================================================
  function forkWorld(mode) {
    const parent = getActiveWorld();
    const rawName = (document.getElementById('sandboxName')?.value || '').trim();
    const count = Object.keys(state.worlds).length;
    const id = makeId('world_sbx');
    const name = rawName || `샌드박스 #${count} (${mode === 'inherit' ? '승계' : '빈 공간'})`;

    state.worlds[id] = {
      id,
      name,
      role: 'sandbox',
      parentId: parent.id,
      forkMode: mode,
      createdAt: nowIso(),
      encounters: mode === 'inherit' ? JSON.parse(JSON.stringify(parent.encounters)) : [],
      principles: mode === 'inherit' ? JSON.parse(JSON.stringify(parent.principles)) : [],
      inputRings: [],
      revisions: [],
    };
    state.activeWorldId = id;
    const inputEl = document.getElementById('sandboxName');
    if (inputEl) inputEl.value = '';
    saveState();
    renderAll();
  }

  function addEncounter() {
    const obj = (document.getElementById('encObject')?.value || '').trim();
    const selfLens = (document.getElementById('encSelf')?.value || '').trim();
    const between = (document.getElementById('encBetween')?.value || '').trim();
    const status = document.getElementById('encStatus')?.value || 'variable';
    const axis = document.getElementById('encAxis')?.value || 'external';
    const rotorCategory = document.getElementById('encRotorCat')?.value || '세계 접촉 로터';

    if (!obj || !between) return;

    const w = getActiveWorld();
    w.encounters.unshift({
      id: makeId('enc'),
      at: nowIso(),
      originWorldId: w.id,
      object: obj,
      selfLens: selfLens || '기본 관찰 렌즈',
      between,
      status,
      axis,
      rotorCategory,
    });
    if (axis === 'revision') {
      w.revisions.unshift({
        id: makeId('rev'),
        at: nowIso(),
        summary: `${obj} → ${between}`,
      });
    }
    ['encObject', 'encSelf', 'encBetween'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
    saveState();
    renderAll();
  }

  function relinkUniqueInsights() {
    const selA = document.getElementById('compareWorldA');
    const selB = document.getElementById('compareWorldB');
    if (!selA || !selB) return;
    const wA = state.worlds[selA.value];
    const wB = state.worlds[selB.value];
    if (!wA || !wB || wA.id === wB.id) return;

    const existingIds = new Set(wA.encounters.map((e) => e.id));
    const uniqueFromB = wB.encounters.filter((e) => !existingIds.has(e.id));
    if (uniqueFromB.length === 0) return;

    const latest = uniqueFromB[0];
    wA.encounters.unshift({
      ...latest,
      id: makeId('relink'),
      at: nowIso(),
      relinkedFrom: wB.id,
      relinkedFromName: wB.name,
      axis: 'revision',
      between: `[${wB.name} 재연결] ${latest.between}`,
    });
    wA.revisions.unshift({
      id: makeId('rev'),
      at: nowIso(),
      summary: `${wB.name}에서 '${latest.object}' 관계 흔적을 출처 보존 재연결`,
    });
    saveState();
    renderAll();
  }

  // =========================================================================
  // Rendering UI Panels
  // =========================================================================
  function renderWorlds() {
    const list = document.getElementById('worldList');
    const badge = document.getElementById('activeWorldBadge');
    const active = getActiveWorld();
    if (badge) {
      badge.textContent = `WORLD: ${active.name}`;
      badge.className = `badge ${active.role === 'home' ? 'invariant' : 'variable'}`;
    }
    if (!list) return;
    list.innerHTML = '';

    Object.values(state.worlds).forEach((w) => {
      const div = document.createElement('div');
      div.className = `world-card ${w.id === state.activeWorldId ? 'active' : ''}`;
      const parentName = w.parentId && state.worlds[w.parentId] ? state.worlds[w.parentId].name : '기원';
      div.innerHTML = `
        <div class="world-card-top">
          <strong>${escapeHtml(w.name)}</strong>
          <span class="badge ${w.role === 'home' ? 'invariant' : 'variable'}">${w.role === 'home' ? 'HOME' : w.forkMode}</span>
        </div>
        <div class="world-meta mono">
          부모: ${escapeHtml(parentName)} · 경험 ${w.encounters.length} · 원리 ${w.principles.length} · 나이테 ${w.inputRings.length}
        </div>
      `;
      div.addEventListener('click', () => {
        state.activeWorldId = w.id;
        saveState();
        renderAll();
      });
      list.appendChild(div);
    });
  }

  function renderInputRings() {
    const list = document.getElementById('inputRingList');
    if (!list) return;
    const w = getActiveWorld();
    if (w.inputRings.length === 0) {
      list.innerHTML = '<div class="kv">아직 고정된 입력 나이테가 없습니다. 탭 안에서 움직인 뒤 기록해 보세요.</div>';
      return;
    }
    list.innerHTML = w.inputRings
      .map(
        (r) => `
      <div class="trace-item">
        <div class="trace-top">
          <strong>${escapeHtml(r.label)}</strong>
          <span class="mono" style="font-size:10px;color:var(--text-muted)">${escapeHtml(r.at.slice(11))}</span>
        </div>
        <div class="kv mono">변위 ${r.pointerDistancePx}px · 순벡터 ${r.netVectorPx}px (${r.dominantAngleDeg}°) · 키 ${r.keyRhythmCount}회 (평균 ${r.meanKeyDwellMs}ms)</div>
      </div>`
      )
      .join('');
  }

  function renderConvertedPrinciples() {
    const box = document.getElementById('convertedRotorBox');
    if (!box) return;
    const w = getActiveWorld();
    if (w.principles.length === 0) {
      box.innerHTML = '<div class="kv">프리셋을 누르거나 임의의 원리 구조를 입력해 5-프레임 스케일로터로 변환해 보세요.</div>';
      return;
    }
    box.innerHTML = w.principles
      .map((p) => {
        const pf = p.phase_frames || {};
        const c = p.chromatic_lens || { flux_red: 0.33, order_blue: 0.34, entropy_yellow: 0.33 };
        const couplings = (p.host_couplings || [])
          .map((hc) => `${hc.protocol_id}(${hc.resonance})`)
          .join(', ');
        return `
        <div class="trace-item">
          <div class="trace-top">
            <strong>${escapeHtml(p.name)}</strong>
            <span class="badge growth mono">R:${c.flux_red} B:${c.order_blue} Y:${c.entropy_yellow}</span>
          </div>
          <div class="kv"><strong>불변(0):</strong> ${escapeHtml((p.invariants || []).join(', '))}</div>
          <div class="kv"><strong>가변(1):</strong> ${escapeHtml((p.variables || []).join(', '))}</div>
          <div class="kv"><strong>면(Plane):</strong> ${escapeHtml(pf.plane?.summary || '')}</div>
          <div class="kv"><strong>구체 결합:</strong> ${escapeHtml(couplings || '호스트 결합 대기')}</div>
        </div>`;
      })
      .join('');
  }

  function renderEncounters() {
    const list = document.getElementById('encounterList');
    if (!list) return;
    const w = getActiveWorld();
    const axisLabels = {
      internal: '내적 기원',
      external: '외적 영향',
      ignorance: '무지 경계',
      revision: '기준 수정',
    };
    const statusLabels = {
      invariant: '지속적(불변)',
      variable: '가변적',
      open: '열림(미해결)',
    };
    if (w.encounters.length === 0) {
      list.innerHTML = '<div class="kv">이 세계에는 아직 기록된 관계 경험이 없습니다.</div>';
      return;
    }
    list.innerHTML = w.encounters
      .map(
        (e) => `
      <div class="trace-item">
        <div class="trace-top">
          <strong>${escapeHtml(e.object)}</strong>
          <div>
            <span class="badge ${escapeHtml(e.status)}">${statusLabels[e.status] || e.status}</span>
            <span class="badge">${axisLabels[e.axis] || e.axis}</span>
          </div>
        </div>
        <div class="kv"><strong>자기:</strong> ${escapeHtml(e.selfLens)} · <strong>로터:</strong> ${escapeHtml(e.rotorCategory)}</div>
        <div class="kv"><strong>사이:</strong> ${escapeHtml(e.between)}</div>
        <div class="kv mono" style="font-size:10px;color:var(--text-muted)">출처: ${escapeHtml(e.originWorldId)}${e.relinkedFromName ? ` ← 재연결(${escapeHtml(e.relinkedFromName)})` : ''} · ${escapeHtml(e.at)}</div>
      </div>`
      )
      .join('');
  }

  function renderComparePanel() {
    const selA = document.getElementById('compareWorldA');
    const selB = document.getElementById('compareWorldB');
    const out = document.getElementById('compareResult');
    if (!selA || !selB || !out) return;

    const worlds = Object.values(state.worlds);
    const prevA = selA.value || 'world_home';
    const prevB = selB.value || state.activeWorldId;

    const opts = worlds.map((w) => `<option value="${escapeHtml(w.id)}">${escapeHtml(w.name)}</option>`).join('');
    selA.innerHTML = opts;
    selB.innerHTML = opts;
    selA.value = state.worlds[prevA] ? prevA : worlds[0].id;
    selB.value = state.worlds[prevB] ? prevB : worlds[worlds.length - 1].id;

    const wA = state.worlds[selA.value];
    const wB = state.worlds[selB.value];
    const idsA = new Set(wA.encounters.map((e) => e.id));
    const idsB = new Set(wB.encounters.map((e) => e.id));

    const shared = wA.encounters.filter((e) => idsB.has(e.id));
    const onlyA = wA.encounters.filter((e) => !idsB.has(e.id));
    const onlyB = wB.encounters.filter((e) => !idsA.has(e.id));

    out.innerHTML = `
      <div class="kv"><strong>공통 계보 흔적:</strong> ${shared.length}건</div>
      <div class="kv"><strong>${escapeHtml(wA.name)} 고유:</strong> ${onlyA.length}건 · 원리 ${wA.principles.length}개 · 기준수정 ${wA.revisions.length}회</div>
      <div class="kv"><strong>${escapeHtml(wB.name)} 고유:</strong> ${onlyB.length}건 · 원리 ${wB.principles.length}개 · 기준수정 ${wB.revisions.length}회</div>
      <div class="kv" style="margin-top:4px;">${
        onlyB.length > 0
          ? `재연결 후보: <strong>${escapeHtml(onlyB[0].object)}</strong> (${escapeHtml(onlyB[0].between)})`
          : '비교 대상 세계에 아직 고유 분기 경험이 없습니다. 샌드박스를 분기해 새 경험을 기록해 보세요.'
      }</div>
    `;
  }

  function renderLiveAttentionPanel(tel, lens, cadenceMs, symMem, cov, interrupts, overlay, prism, gov, voice) {
    const meta = tel.stage3_meta_reobservation || {};
    const delta = tel.stage2_delta || {};
    const sys = tel.system || {};

    const pBadge = document.getElementById('perspectiveBadge');
    if (pBadge) pBadge.textContent = meta.subjective_perspective || '관측 중';

    const hEl = document.getElementById('metricScaleHorizon');
    if (hEl) hEl.textContent = typeof meta.scale_horizon === 'number' ? meta.scale_horizon.toFixed(2) : '-';

    const cEl = document.getElementById('metricCadence');
    if (cEl) cEl.textContent = `${Math.round((cadenceMs || meta.recommended_cadence_ms || 6000) / 1000 * 10) / 10}s`;

    const dEl = document.getElementById('metricDeltaRatio');
    if (dEl) dEl.textContent = `${delta.changed_count ?? 0} / ${delta.invariant_count ?? 0}`;

    const lBox = document.getElementById('attentionLensBox');
    if (lBox && lens) {
      const ram = sys.memory ? `RAM ${sys.memory.used_gb}/${sys.memory.total_gb}GB (${sys.memory.percent}%) · CPU ${sys.cpu_percent}%` : '';
      lBox.innerHTML = `<strong>자기수정 주의 렌즈:</strong> 최근변화 ${lens.w_change} · 상주메모리 ${lens.w_rss} · 미지발산 ${lens.w_novelty}<br><span class="mono" style="font-size:10.5px;color:var(--text-muted)">${escapeHtml(ram)} · 오류로터 ${delta.error_rotor_count ?? 0}개 · 스캔 파일 ${sys.total_files_scanned ?? 0}개</span>`;
    }

    const sBox = document.getElementById('symbolicMemoryBox');
    if (sBox && symMem) {
      const syms = Object.values(symMem.iceSymbols || {});
      const comps = Object.values(symMem.compounds || {});
      const lc = symMem.languageConventions || { sensoryToWord: {}, pendingWords: [], unnamedClusters: {} };
      const boundCnt = Object.keys(lc.sensoryToWord || {}).length;
      const unnamedCnt = Object.keys(lc.unnamedClusters || {}).length;
      const pendingCnt = (lc.pendingWords || []).length;
      const topSyms = syms
        .sort((a, b) => b.count - a.count)
        .slice(0, 2)
        .map((s) => `${s.rotorCategory}[${s.symbolUnit} ×${s.count}${s.melted ? '·재용해' : ''}]`)
        .join(' / ');
      const covTxt = cov ? `공변 일치 ${cov.sameDir} vs 외부독립 ${cov.externalDrift}` : '';
      const intCnt = Array.isArray(interrupts) ? interrupts.length : 0;
      sBox.innerHTML = `<strong>영속 옥타브·분자 결합 기억:</strong> 원시 ${symMem.totalRawAbsorbed}건 → 얼음 ${syms.length}개 · 분자결합 ${comps.length}개 (결합거부 ${symMem.bondRejections || 0} · 재용해 ${symMem.meltedCount})<br><strong>감각⇄언어 약속망:</strong> 연결 완료 ${boundCnt} · 미명명 시각객체 ${unnamedCnt} · 대기 단어 ${pendingCnt}<br><span class="mono" style="font-size:10.5px;color:var(--text-muted)">${escapeHtml(topSyms || '응축 중')} · ${escapeHtml(covTxt)} · 0000→1 인터럽트 ${intCnt}건</span>`;
    }

    const pBox = document.getElementById('parallelPrismBox');
    if (pBox && (overlay || prism || gov)) {
      const ovTxt = overlay
        ? `<strong>평행우주 포개기(World_E ⊕ World_R):</strong> 수렴도 ${Math.round((overlay.convergence || 0) * 100)}% (${escapeHtml(overlay.divergenceDetail || '')})`
        : '';
      const prTxt = prism
        ? `<br><strong>프리즘 장파장 원리:</strong> ${escapeHtml(prism.longWavelengthPrinciple)} ⇄ ${escapeHtml((prism.isomorphicDomains || []).join(' | '))}`
        : '';
      const gvTxt = gov
        ? `<br><strong>자율 작용 게이트:</strong> ${escapeHtml(gov.lastAction || '')}`
        : '';
      pBox.innerHTML = `${ovTxt}${prTxt}${gvTxt}`;
    }

    if (voice) {
      const phBadge = document.getElementById('agencyPhaseBadge');
      const phaseMap = {
        silent_absorb: '무의식 흡수 (정상)',
        ask_once: '저울 초과 → 질문 중',
        reask_reframed: '무응답 → 관점 바꿔 재질문',
        pivot_alternative: '무응답 → 대체 경로 자율 전환',
      };
      if (phBadge) {
        phBadge.textContent = `${phaseMap[voice.phase] || voice.phase} · 불일치 ${Math.round((voice.dissonance || 0) * 100)}%`;
        phBadge.className = `badge ${voice.phase === 'silent_absorb' ? 'invariant' : voice.phase === 'pivot_alternative' ? 'growth' : 'variable'}`;
      }
      const mList = document.getElementById('agencyMsgList');
      if (mList) {
        const msgs = Array.isArray(voice.messages) ? voice.messages : [];
        mList.innerHTML = msgs.length === 0
          ? '<div class="kv">인지 불일치가 허용 범위 안이라 조용히 스스로 관측 중입니다.</div>'
          : msgs
              .slice(0, 6)
              .map(
                (m) =>
                  `<div class="kv"><strong>${m.speaker === 'user' ? '사용자' : '엘리시아'}:</strong> ${escapeHtml(m.text)} <span class="mono" style="font-size:10px;color:var(--text-muted)">(${escapeHtml(m.at.slice(11))})</span></div>`
              )
              .join('');
      }
    }

    const rList = document.getElementById('attentionRankingList');
    if (!rList) return;
    const ranking = Array.isArray(meta.attention_ranking) ? meta.attention_ranking : [];
    if (ranking.length === 0) {
      rList.innerHTML = '<div class="kv">실시간 프로세스·파일 관측 대기 중...</div>';
      return;
    }
    rList.innerHTML = ranking
      .map((item, idx) => {
        const isProc = item.kind === 'os_process';
        const isErr = item.circuit_role === 'error_rotor_leak';
        const pct = Math.min(100, Math.round((item.attention_score || 0) * 100));
        const detail = isProc
          ? `상주 ${item.rss_mb}MB (Δ${item.delta_rss_mb}MB) · ${item.circuit_label_ko || ''}`
          : `최근 ${item.age_sec}s 전 · ${item.size_kb}KB · ${item.circuit_label_ko || ''}`;
        const badgeCls = isErr ? 'open' : (item.state_class === 'changed' ? 'variable' : 'invariant');
        const badgeTxt = isErr ? '오류 로터' : (item.state_class === 'changed' ? '변화(1)' : '질서(0)');
        const barCol = isErr ? '#F43F5E' : (item.state_class === 'changed' ? '#F59E0B' : '#06B6D4');
        return `
        <div class="trace-item">
          <div class="trace-top">
            <strong class="mono">#${idx + 1} ${escapeHtml(item.name)}</strong>
            <span class="badge ${badgeCls}">${badgeTxt} · ${pct}%</span>
          </div>
          <div class="kv mono" style="font-size:10.5px;">${escapeHtml(detail)}</div>
          <div style="height:4px;background:#1B2435;width:100%;margin-top:2px;">
            <div style="height:100%;width:${pct}%;background:${barCol};"></div>
          </div>
        </div>`;
      })
      .join('');
  }

  function renderHostBoundary() {
    const metaBox = document.getElementById('hostMetaBox');
    const honestyBox = document.getElementById('hostHonestyBox');
    const list = document.getElementById('hostProtocolList');
    if (!hostBoundary || !list) return;

    if (metaBox) {
      metaBox.innerHTML = `<strong>호스트:</strong> ${escapeHtml(hostBoundary.host.os_release)} · Python ${escapeHtml(hostBoundary.host.python_version)} · 결합 빔 ${hostBoundary.coupling_beams.length}개`;
    }
    if (honestyBox) {
      const unobs = (hostBoundary.boundary_honesty?.unobserved_or_gated || []).join(' / ');
      honestyBox.innerHTML = `<strong>열린·미관측 경계:</strong> ${escapeHtml(unobs)}`;
    }
    list.innerHTML = hostBoundary.protocol_rotors
      .map((p) => {
        const ports = (p.ports || []).map((pt) => `${pt.direction}:${pt.signal_type}`).join(' → ');
        return `
        <div class="trace-item">
          <div class="trace-top">
            <strong class="mono">${escapeHtml(p.id)}</strong>
            <span class="badge ${escapeHtml(p.relation_status)}">${escapeHtml(p.rotor_category)}</span>
          </div>
          <div class="kv">${escapeHtml(p.description_ko)}</div>
          <div class="kv mono" style="font-size:10.5px;">포트: ${escapeHtml(ports)} · 스케일 ${escapeHtml(p.scale_band)}</div>
          <div class="kv"><strong>불변:</strong> ${escapeHtml(p.invariants.join(', '))} | <strong>가변:</strong> ${escapeHtml(p.variables.join(', '))}</div>
        </div>`;
      })
      .join('');
  }

  function renderFrameButtons() {
    const bar = document.getElementById('frameBar');
    const badge = document.getElementById('frameLabelBadge');
    const expl = document.getElementById('frameExplanation');
    const info = FRAME_INFO[state.activeFrame] || FRAME_INFO.sphere;
    if (badge) badge.textContent = info.badge;
    if (expl) expl.textContent = info.desc;
    if (bar) {
      bar.querySelectorAll('button[data-frame]').forEach((btn) => {
        btn.classList.toggle('active', btn.dataset.frame === state.activeFrame);
      });
    }
  }

  function renderAll() {
    renderWorlds();
    renderInputRings();
    renderConvertedPrinciples();
    renderEncounters();
    renderComparePanel();
    renderFrameButtons();
  }

  // =========================================================================
  // 5-Frame Phase Rotor Canvas (Point -> Line -> Plane -> Cube -> Sphere)
  // =========================================================================
  const canvas = document.getElementById('rotorCanvas');
  const ctx = canvas ? canvas.getContext('2d') : null;
  let animTime = 0;

  function resizeCanvas() {
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.max(300, Math.floor(rect.width * dpr));
    canvas.height = Math.max(240, Math.floor(rect.height * dpr));
    if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  function gatherActiveNodes() {
    const w = getActiveWorld();
    const nodes = [];
    w.encounters.forEach((e, i) => {
      nodes.push({
        kind: 'encounter',
        label: e.object.slice(0, 14),
        status: e.status,
        color: e.status === 'invariant' ? '#06B6D4' : e.status === 'open' ? '#A78BFA' : '#F59E0B',
        idx: i,
        r: 5,
      });
    });
    w.principles.forEach((p, i) => {
      nodes.push({
        kind: 'principle',
        label: p.name.slice(0, 14),
        status: 'growth',
        color: '#10B981',
        idx: i,
        r: 7,
      });
    });
    if (liveTelemetry && liveTelemetry.stage3_meta_reobservation && Array.isArray(liveTelemetry.stage3_meta_reobservation.attention_ranking)) {
      liveTelemetry.stage3_meta_reobservation.attention_ranking.slice(0, 6).forEach((item, i) => {
        nodes.push({
          kind: 'principle',
          label: `${item.name.slice(0, 12)} (${Math.round((item.attention_score || 0) * 100)}%)`,
          status: item.state_class === 'changed' ? 'variable' : 'invariant',
          color: item.state_class === 'changed' ? '#F59E0B' : '#10B981',
          idx: i,
          r: Math.max(4, Math.min(10, 4 + (item.attention_score || 0) * 6)),
        });
      });
    }
    if (hostBoundary && Array.isArray(hostBoundary.protocol_rotors)) {
      hostBoundary.protocol_rotors.forEach((pr, i) => {
        nodes.push({
          kind: 'host',
          label: pr.rotor_category,
          status: pr.relation_status,
          color: pr.immutable_external ? '#38BDF8' : '#F43F5E',
          idx: i,
          r: 6,
        });
      });
    }
    return nodes;
  }

  function drawFrame() {
    animTime += 0.014;
    if (!ctx || !canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    const W = rect.width;
    const H = rect.height;
    const cx = W / 2;
    const cy = H / 2;

    ctx.clearRect(0, 0, W, H);

    // Subtle background grid
    ctx.strokeStyle = 'rgba(27, 36, 53, 0.55)';
    ctx.lineWidth = 1;
    for (let x = 40; x < W; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, H);
      ctx.stroke();
    }
    for (let y = 40; y < H; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }

    const nodes = gatherActiveNodes();
    const frame = state.activeFrame;
    const w = getActiveWorld();
    const worlds = Object.values(state.worlds);

    if (frame === 'point') {
      // Isolated points — deliberately showing disconnected point cognition
      nodes.forEach((n, i) => {
        const px = 60 + ((i * 97) % Math.max(120, W - 120));
        const py = 55 + ((i * 61) % Math.max(100, H - 110));
        ctx.fillStyle = n.color;
        ctx.beginPath();
        ctx.arc(px, py, n.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = 'rgba(241,245,249,0.75)';
        ctx.font = '10px "IBM Plex Mono", monospace';
        ctx.fillText(n.label, px + 8, py + 3);
      });
    } else if (frame === 'line') {
      // Continuous causal trajectory + input momentum vector
      const pts = nodes.map((n, i) => {
        const t = nodes.length <= 1 ? 0.5 : i / (nodes.length - 1);
        const x = 50 + t * (W - 100);
        const y = cy + Math.sin(t * Math.PI * 2.5 + animTime) * 70 + (n.kind === 'host' ? -35 : 25);
        return { x, y, n };
      });
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.7)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      pts.forEach((p, idx) => (idx === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
      ctx.stroke();
      pts.forEach((p) => {
        ctx.fillStyle = p.n.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.n.r, 0, Math.PI * 2);
        ctx.fill();
      });
    } else if (frame === 'plane') {
      // 2D Interference Plane: Invariant (Y) x Variable/Open (X)
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.4)';
      ctx.beginPath();
      ctx.moveTo(40, cy);
      ctx.lineTo(W - 40, cy);
      ctx.moveTo(cx, 28);
      ctx.lineTo(cx, H - 36);
      ctx.stroke();

      ctx.fillStyle = 'rgba(148, 163, 184, 0.75)';
      ctx.font = '11px "IBM Plex Mono", monospace';
      ctx.fillText('불변 축 (0 · Invariant)', cx + 8, 40);
      ctx.fillText('가변 · 열린 축 (1 · Variable)', W - 185, cy - 8);

      nodes.forEach((n, i) => {
        const xOff = n.status === 'invariant' ? -0.55 : n.status === 'open' ? 0.65 : 0.25;
        const yOff = n.kind === 'principle' ? -0.55 : n.kind === 'host' ? -0.2 : 0.45;
        const px = cx + xOff * (W * 0.34) + Math.cos(animTime + i) * 26;
        const py = cy + yOff * (H * 0.34) + Math.sin(animTime + i * 1.3) * 22;

        ctx.strokeStyle = 'rgba(6, 182, 212, 0.2)';
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(px, py);
        ctx.stroke();

        ctx.fillStyle = n.color;
        ctx.beginPath();
        ctx.arc(px, py, n.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = 'rgba(241,245,249,0.75)';
        ctx.font = '10px "IBM Plex Mono", monospace';
        ctx.fillText(n.label, px + 8, py + 3);
      });
    } else if (frame === 'cube') {
      // 3D Projected Spacetime Cube showing Multi-World Branching Lineage
      const size = Math.min(W, H) * 0.27;
      const rotY = animTime * 0.65;
      const rotX = 0.42;
      const project = (x, y, z) => {
        const x1 = x * Math.cos(rotY) - z * Math.sin(rotY);
        const z1 = x * Math.sin(rotY) + z * Math.cos(rotY);
        const y2 = y * Math.cos(rotX) - z1 * Math.sin(rotX);
        const z2 = y * Math.sin(rotX) + z1 * Math.cos(rotX);
        const scale = 320 / (320 + z2);
        return { x: cx + x1 * scale, y: cy + y2 * scale };
      };
      const corners = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
      ].map(([x, y, z]) => project(x * size, y * size, z * size));
      const edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],
        [4, 5], [5, 6], [6, 7], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7],
      ];
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.35)';
      ctx.lineWidth = 1.2;
      edges.forEach(([a, b]) => {
        ctx.beginPath();
        ctx.moveTo(corners[a].x, corners[a].y);
        ctx.lineTo(corners[b].x, corners[b].y);
        ctx.stroke();
      });

      // Plot each world as a lineage branch inside the cube
      worlds.forEach((world, wi) => {
        const angle = (wi * Math.PI * 2) / Math.max(1, worlds.length);
        const r = world.role === 'home' ? 0 : size * 0.62;
        const pOrigin = project(0, -size * 0.55, 0);
        const pWorld = project(Math.cos(angle) * r, size * 0.45, Math.sin(angle) * r);
        ctx.strokeStyle = world.id === w.id ? '#10B981' : 'rgba(245, 158, 11, 0.65)';
        ctx.lineWidth = world.id === w.id ? 2.5 : 1.5;
        ctx.beginPath();
        ctx.moveTo(pOrigin.x, pOrigin.y);
        ctx.lineTo(pWorld.x, pWorld.y);
        ctx.stroke();

        ctx.fillStyle = world.role === 'home' ? '#06B6D4' : '#F59E0B';
        ctx.beginPath();
        ctx.arc(pWorld.x, pWorld.y, world.id === w.id ? 8 : 5.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#F1F5F9';
        ctx.font = '10.5px "IBM Plex Mono", monospace';
        ctx.fillText(world.name.slice(0, 14), pWorld.x + 10, pWorld.y + 3);
      });
    } else {
      // Sphere / Omnidirectional Coupled Rotor Web
      const outerR = Math.min(W, H) * 0.37;
      const midR = outerR * 0.64;
      const innerR = outerR * 0.32;

      [outerR, midR, innerR].forEach((r, idx) => {
        ctx.strokeStyle = idx === 0 ? 'rgba(6, 182, 212, 0.35)' : idx === 1 ? 'rgba(16, 185, 129, 0.35)' : 'rgba(245, 158, 11, 0.35)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();
      });

      const placed = nodes.map((n, i) => {
        const ringR = n.kind === 'host' ? outerR : n.kind === 'principle' ? midR : innerR;
        const dir = n.kind === 'principle' ? -1 : 1;
        const speed = n.kind === 'host' ? 0.35 : n.kind === 'principle' ? 0.65 : 0.9;
        const ang = (i * Math.PI * 2) / Math.max(1, nodes.length) + animTime * speed * dir;
        return {
          x: cx + Math.cos(ang) * ringR,
          y: cy + Math.sin(ang) * ringR * 0.82,
          n,
        };
      });

      // Draw coupling beams between principles, encounters, and host protocols
      for (let i = 0; i < placed.length; i++) {
        for (let j = i + 1; j < placed.length; j++) {
          if (placed[i].n.kind !== placed[j].n.kind) {
            const dist = Math.hypot(placed[i].x - placed[j].x, placed[i].y - placed[j].y);
            if (dist < outerR * 1.15) {
              ctx.strokeStyle = 'rgba(6, 182, 212, 0.16)';
              ctx.lineWidth = 1;
              ctx.beginPath();
              ctx.moveTo(placed[i].x, placed[i].y);
              ctx.lineTo(placed[j].x, placed[j].y);
              ctx.stroke();
            }
          }
        }
      }

      placed.forEach(({ x, y, n }) => {
        ctx.fillStyle = n.color;
        ctx.beginPath();
        ctx.arc(x, y, n.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = 'rgba(241,245,249,0.82)';
        ctx.font = '10px "IBM Plex Mono", monospace';
        ctx.fillText(n.label, x + 8, y + 3);
      });
    }

    // Update HUD telemetry
    const hudLeft = document.getElementById('hudLeft');
    const hudRight = document.getElementById('hudRight');
    const beamCount = hostBoundary ? hostBoundary.coupling_beams.length : 0;
    if (hudLeft) {
      hudLeft.textContent = `Active Rotors: ${nodes.length} · Host Beams: ${beamCount} · Worlds: ${worlds.length}`;
    }
    if (hudRight) {
      const invCount = w.encounters.filter((e) => e.status === 'invariant').length + 1;
      const varCount = w.encounters.filter((e) => e.status === 'variable').length + 1;
      const openCount = w.encounters.filter((e) => e.status === 'open').length + 1;
      const tot = invCount + varCount + openCount;
      hudRight.textContent = `R(흐름) ${(varCount / tot).toFixed(2)} · B(질서) ${(invCount / tot).toFixed(2)} · Y(열림) ${(openCount / tot).toFixed(2)}`;
    }

    window.requestAnimationFrame(drawFrame);
  }

  // =========================================================================
  // Event Wiring
  // =========================================================================
  document.getElementById('btnForkInherit')?.addEventListener('click', () => forkWorld('inherit'));
  document.getElementById('btnForkBlank')?.addEventListener('click', () => forkWorld('blank'));
  document.getElementById('btnAddEncounter')?.addEventListener('click', addEncounter);
  document.getElementById('btnConvertPrinciple')?.addEventListener('click', convertPrincipleToRotor);
  document.getElementById('btnAgencyReply')?.addEventListener('click', async () => {
    const inp = document.getElementById('agencyReplyInput');
    const text = (inp?.value || '').trim();
    if (!text) return;
    try {
      const resp = await fetch('/api/ecology/dialogue-reply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (resp.ok) {
        if (inp) inp.value = '';
        await syncAutonomousServerState();
      }
    } catch {}
  });
  document.getElementById('btnToggleAuto')?.addEventListener('click', toggleAutonomousLoop);
  document.getElementById('btnProbeHost')?.addEventListener('click', probeHostBoundary);
  document.getElementById('btnRelinkInsight')?.addEventListener('click', relinkUniqueInsights);
  document.getElementById('btnFlushRing')?.addEventListener('click', () => flushInputRing('수동 고정 입력 나이테'));
  document.getElementById('btnClearInputRings')?.addEventListener('click', () => {
    const w = getActiveWorld();
    w.inputRings = [];
    saveState();
    renderAll();
  });

  document.getElementById('compareWorldA')?.addEventListener('change', renderComparePanel);
  document.getElementById('compareWorldB')?.addEventListener('change', renderComparePanel);

  document.getElementById('frameBar')?.addEventListener('click', (ev) => {
    const btn = ev.target.closest('button[data-frame]');
    if (!btn) return;
    state.activeFrame = btn.dataset.frame;
    saveState();
    renderFrameButtons();
  });

  document.getElementById('principlePresets')?.addEventListener('click', (ev) => {
    const btn = ev.target.closest('button[data-preset]');
    if (!btn) return;
    const p = PRINCIPLE_PRESETS[btn.dataset.preset];
    if (!p) return;
    document.getElementById('prName').value = p.name;
    document.getElementById('prBoundary').value = p.boundary;
    document.getElementById('prInvariants').value = p.invariants;
    document.getElementById('prVariables').value = p.variables;
    document.getElementById('prRelation').value = p.relation;
  });

  renderAll();
  syncAutonomousServerState();
  window.setInterval(syncAutonomousServerState, 4000);
  window.requestAnimationFrame(drawFrame);
})();
