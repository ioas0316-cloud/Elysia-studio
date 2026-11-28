/**
 * Elysia Unified Reality View — Single Canonical S0..S4 Scale-Rotor Viewport
 * ==========================================================================
 * Renders ONE continuous 3D Spacetime Scale-Rotor World Model directly from
 * the canonical Python `UnifiedNeuralSpine` (/api/spine/*):
 *   - S0: Raw tab pointer/key kinematics (privacy-preserving: direction/displacement
 *         & key class only, NEVER typed chars or page text) + L0 HW kernel ports
 *   - S1: Dependency Capability Membranes (Invariant Pure Kernel vs Variable Accelerator)
 *   - S2: Concepts + AST-Rotorized Repository Modules (1-click dependency absorption)
 *   - S3: Unified Spacetime World Model & Cl(3,0) Docking Links
 *   - S4: Multi-World Lineage (Home vs Sandbox fork), 3-Way Experience, 4-Axis Attribution
 */
(function () {
  'use strict';

  const OVERLAY = document.getElementById('elysiaRealityOverlay');
  const BTN_OPEN = document.getElementById('btnToggleRealityView');
  const BTN_OPEN_WORLD_ROTOR = document.getElementById('btnOpenWorldRotor');
  const BTN_OPEN_REAL_MEDIA = document.getElementById('btnOpenRealMedia');
  const BTN_OPEN_DYNAMIC = document.getElementById('btnOpenDynamicEngine');
  const BTN_CLOSE = document.getElementById('btnCloseRealityView');
  const CANVAS = document.getElementById('ervCanvas');
  const TAB_SPINE = document.getElementById('ervTabSpine');
  const TAB_REAL_MEDIA = document.getElementById('ervTabRealMedia');
  const TAB_WORLD_ROTOR = document.getElementById('ervTabWorldRotor');
  const TAB_DYNAMIC = document.getElementById('ervTabDynamicEngine');
  const WORLD_ROTOR_STAGE = document.getElementById('ervWorldRotorStage');
  const REAL_MEDIA_STAGE = document.getElementById('ervRealMediaStage');
  const DYNAMIC_STAGE = document.getElementById('ervDynamicEngineStage');

  const BTN_CYCLE = document.getElementById('ervBtnVerticalCycle');
  const BTN_FOLD = document.getElementById('ervBtnFoldLimit');
  const BTN_SCAN = document.getElementById('ervBtnRescanRepo');
  const BTN_FORK_INHERIT = document.getElementById('ervBtnForkInherit');
  const BTN_FORK_BLANK = document.getElementById('ervBtnForkBlank');
  const WORLD_LIST = document.getElementById('ervWorldList');
  const METRIC_STRIP = document.getElementById('ervMetricStrip');
  const VERTICAL_BOX = document.getElementById('ervVerticalBox');
  const SPECTRUM_BOX = document.getElementById('ervSpectrumBox');
  const UNIT_DIV_BOX = document.getElementById('ervUnitDivisionBox');
  const PERCEPTUAL_UNIT_BOX = document.getElementById('ervPerceptualUnitBox');
  const TRAJ_CANVAS = document.getElementById('ervTrajectoryCanvas');
  const FOUR_AXIS_BOX = document.getElementById('ervFourAxisBox');
  const EXP_LIST = document.getElementById('ervExperienceList');

  const MEMBRANE_LIST = document.getElementById('ervMembraneList');
  const HANDLE_LIST = document.getElementById('ervBoundaryHandleList');
  const HANDLE_INPUT = document.getElementById('ervHandleNameInput');
  const BTN_COUPLE_CUSTOM = document.getElementById('ervBtnCoupleCustom');
  const MOD_FILTER = document.getElementById('ervModFilter');
  const MOD_SEARCH = document.getElementById('ervModSearch');
  const MOD_LIST = document.getElementById('ervModList');
  const INSPECTOR = document.getElementById('ervNodeInspector');
  const STATUS_TOAST = document.getElementById('ervStatusToast');

  if (!OVERLAY || !BTN_OPEN || !CANVAS) return;

  function scaleColor(s) {
    const fixed = {
      0: '#f87171',
      1: '#fbbf24',
      2: '#60a5fa',
      3: '#34d399',
      4: '#c084fc',
    };
    if (Object.prototype.hasOwnProperty.call(fixed, s)) return fixed[s];
    if (s < 0) return '#fb7185'; // Sub-S0 micro split layers (S-1, S-2...)
    // Emergent macro layers (S5, S6, S7...) smooth golden-cyan-magenta spectrum
    const hue = (275 + (s - 4) * 48) % 360;
    return `hsl(${hue}, 82%, 72%)`;
  }

  function scaleLabel(s) {
    if (s === 0) return 'S0 원시·하드웨어';
    if (s === 1) return 'S1 의존성 로터 막';
    if (s === 2) return 'S2 개념·씨앗·모듈';
    if (s === 3) return 'S3 시공간 월드모델';
    if (s === 4) return 'S4 정체성·다중세계';
    if (s < 0) return `S${s} 미시 분할층`;
    return `S${s} 상위 통합 창발층`;
  }

  let spineState = null;
  let selectedNodeId = null;
  let activeFilter = 'ALL';
  let isOpen = false;
  let rafId = 0;

  // 3D Orbit camera state
  let camYaw = 0.58;
  let camPitch = 0.42;
  let camZoom = 1.0;
  let dragging = false;
  let dragLastX = 0;
  let dragLastY = 0;
  let projectedNodes = [];
  let ripplePulse = 0.0;
  let activeTrajectory = null;
  let trajAnimPhase = 0.0;

  // Privacy-preserving S0 Browser Tab Input Rotor (throttled)
  let lastPtrX = null;
  let lastPtrY = null;
  let accumDx = 0;
  let accumDy = 0;
  let lastSendTs = 0;
  let pendingKeyKind = 'none';
  let pendingKeyPhase = 'none';

  function classifyKey(e) {
    if (e.key === 'Shift' || e.key === 'Control' || e.key === 'Alt' || e.key === 'Meta') return 'modifier';
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'Tab') return 'nav';
    if (e.key === 'Enter' || e.key === 'Escape' || e.key === 'Backspace' || e.key === ' ') return 'action';
    return 'rhythm';
  }

  function flushSensoryFlow(force) {
    const now = performance.now();
    if (!force && now - lastSendTs < 1400) return;
    const dist = Math.hypot(accumDx, accumDy);
    if (dist < 18 && pendingKeyKind === 'none') return;
    const dx = accumDx;
    const dy = accumDy;
    const kk = pendingKeyKind;
    const kp = pendingKeyPhase;
    const xNorm = lastPtrX !== null ? lastPtrX / Math.max(1, window.innerWidth) : 0.5;
    const yNorm = lastPtrY !== null ? lastPtrY / Math.max(1, window.innerHeight) : 0.5;
    const dtSec = Math.max(0.1, (now - lastSendTs) / 1000);
    accumDx = 0;
    accumDy = 0;
    pendingKeyKind = 'none';
    pendingKeyPhase = 'none';
    lastSendTs = now;
    ripplePulse = Math.min(1.0, ripplePulse + 0.55);

    fetch('/api/spine/sense-flow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pointer_dx: Math.round(dx * 10) / 10,
        pointer_dy: Math.round(dy * 10) / 10,
        pointer_x_norm: Math.round(xNorm * 1000) / 1000,
        pointer_y_norm: Math.round(yNorm * 1000) / 1000,
        speed: Math.round(dist / dtSec),
        key_kind: kk,
        key_phase: kp,
      }),
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((res) => {
        if (res && isOpen && res.vertical_trace && spineState) {
          spineState.last_vertical_trace = res.vertical_trace;
          spineState.vertical_cycles = res.vertical_trace.cycle || spineState.vertical_cycles;
          spineState.prediction_gap = res.vertical_trace.gap_after ?? spineState.prediction_gap;
          renderMetricsAndVertical();
        }
      })
      .catch(() => {});
  }

  window.addEventListener('pointermove', (e) => {
    if (lastPtrX !== null && lastPtrY !== null) {
      accumDx += e.clientX - lastPtrX;
      accumDy += e.clientY - lastPtrY;
    }
    lastPtrX = e.clientX;
    lastPtrY = e.clientY;
    flushSensoryFlow(false);
  }, { passive: true });

  window.addEventListener('keydown', (e) => {
    pendingKeyKind = classifyKey(e);
    pendingKeyPhase = 'down';
    flushSensoryFlow(false);
  }, { passive: true });

  window.addEventListener('keyup', (e) => {
    pendingKeyKind = classifyKey(e);
    pendingKeyPhase = 'up';
  }, { passive: true });

  function showToast(msg, isErr) {
    if (!STATUS_TOAST) return;
    STATUS_TOAST.textContent = msg;
    STATUS_TOAST.style.color = isErr ? '#fca5a5' : '#86efac';
    STATUS_TOAST.style.opacity = '1';
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => {
      STATUS_TOAST.style.opacity = '0.72';
    }, 3200);
  }

  function clearEl(el) {
    if (!el) return;
    while (el.firstChild) el.removeChild(el.firstChild);
  }

  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  async function apiGet(url) {
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || '요청 오류');
    return data;
  }

  async function apiPost(url, body) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {}),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || '요청 오류');
    return data;
  }

  async function refreshSpineState() {
    try {
      const snap = await apiGet('/api/spine/state');
      spineState = snap;
      renderAll();
    } catch (err) {
      showToast(err.message || '척추 상태 로드 실패', true);
    }
  }

  function renderAll() {
    if (!spineState) return;
    renderMetricsAndVertical();
    renderPrincipledSpectrum();
    renderUnitDivisions();
    renderPerceptualStructures();
    renderWorlds();
    renderFourAxis();
    renderExperiences();
    renderBoundaryHandles();
    renderMembranes();
    renderModules();
    renderInspector();
  }

  function renderMetricsAndVertical() {
    if (!spineState) return;
    const g = spineState.spine_graph || {};
    const cs = spineState.codebase_summary || {};
    const aw = spineState.active_world || {};
    if (METRIC_STRIP) {
      clearEl(METRIC_STRIP);
      const sr = g.scale_range || [0, 4];
      const axesCount = (spineState.horizontal_axes || []).length;
      const items = [
        ['활성 세계', aw.name || '홈 세계'],
        ['열린 스케일 범위', `S${sr[0]} ↔ S${sr[1]} (축 ${axesCount}개)`],
        ['통합 노드 / 도킹', `${g.node_count || 0} / ${g.link_count || 0}`],
        ['수직 순환 / 오차', `${spineState.vertical_cycles || 0}회 · ${(Number(spineState.prediction_gap || 0)).toFixed(3)}`],
        ['스캔 / 흡수', `${cs.total_scanned || 0} / ${spineState.absorbed_count || 0}개`],
      ];
      items.forEach(([k, v]) => {
        const chip = el('div', 'erv-metric-chip');
        chip.appendChild(el('span', 'erv-metric-k', k));
        chip.appendChild(el('span', 'erv-metric-v mono', v));
        METRIC_STRIP.appendChild(chip);
      });
    }

    if (VERTICAL_BOX) {
      clearEl(VERTICAL_BOX);
      const vt = spineState.last_vertical_trace || {};
      const lp = spineState.limit_perception || {};
      if (!vt.cycle) {
        VERTICAL_BOX.appendChild(el('div', 'erv-muted', '수직 순환 대기 중 — 포인터를 움직이거나 순환 버튼을 누르세요.'));
      } else {
        const line1 = el('div', 'erv-kv-row');
        line1.appendChild(el('span', '', `Cycle #${vt.cycle} · ${vt.trigger || ''}`));
        line1.appendChild(
          el(
            'span',
            'mono',
            `${Number(vt.gap_before || 0).toFixed(3)} → ${Number(vt.gap_after || 0).toFixed(3)} ${vt.gap_reduced ? '▼축소' : '유지'}`
          )
        );
        VERTICAL_BOX.appendChild(line1);
        VERTICAL_BOX.appendChild(el('div', 'erv-subcopy', vt.why_ko || ''));
      }
      if (lp.viewport_projection_ratio) {
        const sbe = lp.self_boundary_envelope || {};
        VERTICAL_BOX.appendChild(
          el(
            'div',
            'erv-subcopy mono',
            `한계 지각 투영: ${lp.viewport_projection_ratio} | 스펙트럼 ${lp.spectral_dimensions || 3}채널 · 접힌 지평 ${lp.folded_horizons_count || 0}개 · 경계 결합 ${sbe.coupled_handles_count || 0}/${sbe.available_handles_count || 0} (내부 로드 0%)`
          )
        );
        VERTICAL_BOX.appendChild(el('div', 'erv-muted', lp.memory_strategy || ''));
      }
      const w = spineState.active_world || {};
      VERTICAL_BOX.appendChild(
        el(
          'div',
          'erv-subcopy mono',
          `탭 입력 나이테: 이동 ${w.total_pointer_distance || 0}px · 키 흐름 ${w.total_key_events || 0}건 (문자·페이지 비수집)`
        )
      );
    }
  }

  function renderPrincipledSpectrum() {
    if (!SPECTRUM_BOX || !spineState) return;
    clearEl(SPECTRUM_BOX);
    const ps = spineState.principled_spectrum || {};
    const continua = ps.continua || [];
    const exps = ps.recent_friction_experiments || [];
    if (!continua.length) {
      SPECTRUM_BOX.appendChild(el('div', 'erv-muted', '원리 스펙트럼 로딩 대기 중…'));
      return;
    }
    continua.forEach((ct) => {
      const card = el('div', 'erv-exp-card');
      const head = el('div', 'erv-exp-head');
      head.appendChild(el('span', 'erv-exp-obj', ct.name));
      head.appendChild(el('span', 'erv-exp-tag mono', `${(ct.members || []).length}개 분화`));
      card.appendChild(head);
      card.appendChild(el('div', 'erv-exp-line', (ct.members || []).join(' ↔ ')));
      SPECTRUM_BOX.appendChild(card);
    });
    if (exps.length) {
      const latest = exps[0];
      const fcard = el('div', 'erv-exp-card');
      fcard.style.borderColor = 'rgba(52,211,153,0.45)';
      fcard.appendChild(el('div', 'erv-exp-obj', `최근 실측 마찰 검증 (${latest.experiment_id})`));
      fcard.appendChild(el('div', 'erv-exp-line mono', latest.finding || ''));
      SPECTRUM_BOX.appendChild(fcard);
    }
  }

  function renderUnitDivisions() {
    if (!UNIT_DIV_BOX || !spineState) return;
    clearEl(UNIT_DIV_BOX);
    const ps = spineState.principled_spectrum || {};
    const divs = ps.unit_divisions || [];
    if (!divs.length) {
      UNIT_DIV_BOX.appendChild(el('div', 'erv-muted', '단위 분화 도메인 로딩 대기 중…'));
      return;
    }

    divs.forEach((d) => {
      const card = el('div', 'erv-exp-card');
      const head = el('div', 'erv-exp-head');
      head.appendChild(el('span', 'erv-exp-obj', d.name));
      const resTxt = `1 : ${Number(d.addressable_resolution || 1).toLocaleString()} (노드 ${d.stored_nodes || 1}개 · ${Number(d.compression_ratio || 1).toLocaleString()}:1)`;
      const tag = el('span', 'erv-exp-tag mono', resTxt);
      tag.style.color = (d.addressable_resolution || 1) >= 1000000 ? '#86efac' : '#93c5fd';
      head.appendChild(tag);
      card.appendChild(head);

      const iv = Array.isArray(d.active_interval) ? d.active_interval : [0, 1];
      card.appendChild(
        el(
          'div',
          'erv-exp-line mono',
          `초점 경계 [${Number(iv[0]).toFixed(6)}, ${Number(iv[1]).toFixed(6)}] · 상관결합 ${d.correlations_formed || 1}개`
        )
      );
      if (d.initial_error !== null && d.initial_error !== undefined) {
        card.appendChild(
          el(
            'div',
            'erv-exp-line mono',
            `실측 오차 변화: ${Number(d.initial_error).toFixed(5)} → ${Number(d.current_error || 0).toFixed(5)}`
          )
        );
      } else {
        card.appendChild(
          el('div', 'erv-exp-line erv-muted', `${d.input_axis} ↔ ${d.coupled_axis}`)
        );
      }

      const btnRow = el('div', 'erv-fork-row');
      btnRow.style.marginTop = '5px';
      btnRow.style.gap = '5px';

      const runRefine = async (steps, btnEl) => {
        btnEl.disabled = true;
        try {
          spineState = await apiPost('/api/spine/refine-unit-division', { domain_id: d.id, steps });
          const dr = spineState.division_result || {};
          selectedNodeId = `unitdiv::${d.id}_d${dr.depth || d.depth || 1}`;
          ripplePulse = 1.0;
          showToast(
            `${d.name}: 분별력 1:${Number(dr.addressable_resolution || 1).toLocaleString()} 도달 (저장 노드 ${dr.stored_nodes || 1}개 · 압축 ${Number(dr.compression_ratio || 1).toLocaleString()}:1)`,
            false
          );
          renderAll();
        } catch (err) {
          btnEl.disabled = false;
          showToast(err.message, true);
        }
      };

      const btnOne = el('button', 'erv-btn', '1→10× 분화 (+1단계)');
      btnOne.type = 'button';
      btnOne.style.flex = '1';
      btnOne.addEventListener('click', (ev) => {
        ev.stopPropagation();
        runRefine(1, btnOne);
      });

      const btnSix = el('button', 'erv-btn primary', '1→1,000,000 (6단계)');
      btnSix.type = 'button';
      btnSix.style.flex = '1';
      btnSix.addEventListener('click', (ev) => {
        ev.stopPropagation();
        runRefine(6, btnSix);
      });

      btnRow.appendChild(btnOne);
      btnRow.appendChild(btnSix);
      card.appendChild(btnRow);

      if (d.temporal_compass) {
        const tc = d.temporal_compass;
        const ic = tc.ideal_future_contrast || {};
        const compBox = el('div', 'erv-subcopy');
        compBox.style.marginTop = '6px';
        compBox.style.paddingTop = '5px';
        compBox.style.borderTop = '1px solid rgba(148,163,184,0.18)';
        compBox.appendChild(el('div', 'mono', `과거: ${tc.past || ''}`));
        compBox.appendChild(el('div', 'mono', `현재: ${tc.present || ''}`));
        compBox.appendChild(el('div', '', `예측 미래: ${tc.predicted_future || ''}`));
        compBox.appendChild(el('div', '', `완전한 미래 [같음]: ${ic.same || ''}`));
        compBox.appendChild(el('div', 'erv-muted', `완전한 미래 [다름]: ${ic.different || ''}`));
        card.appendChild(compBox);
      }

      UNIT_DIV_BOX.appendChild(card);
    });
  }

  function drawPerceptualTrajectory(traj) {
    if (!TRAJ_CANVAS) return;
    const ctx = TRAJ_CANVAS.getContext('2d');
    if (!ctx) return;
    const w = TRAJ_CANVAS.width;
    const h = TRAJ_CANVAS.height;
    ctx.clearRect(0, 0, w, h);

    // Subtle coordinate grid
    ctx.strokeStyle = 'rgba(148,163,184,0.10)';
    ctx.lineWidth = 1;
    for (let gx = 32; gx < w; gx += 32) {
      ctx.beginPath();
      ctx.moveTo(gx, 0);
      ctx.lineTo(gx, h);
      ctx.stroke();
    }
    for (let gy = 28; gy < h; gy += 28) {
      ctx.beginPath();
      ctx.moveTo(0, gy);
      ctx.lineTo(w, gy);
      ctx.stroke();
    }

    if (!traj || !Array.isArray(traj.frames) || !traj.frames.length) {
      ctx.fillStyle = 'rgba(148,163,184,0.80)';
      ctx.font = '11px system-ui, sans-serif';
      ctx.fillText('아래 지각 단위(손·운동·장면·코드·액터)를 누르면', 14, 52);
      ctx.fillText('정적 결합 구조의 연속 궤적이 실시간 전개됩니다.', 14, 72);
      return;
    }

    const frames = traj.frames;
    const fIdx = Math.floor(trajAnimPhase) % frames.length;
    const cur = frames[fIdx];
    const joints = cur.joints || [];

    // Compute bounding transform so chain always sits comfortably inside canvas
    let minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
    frames.forEach((f) => {
      (f.joints || []).forEach(([x, y]) => {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      });
    });
    const spanX = Math.max(0.25, maxX - minX);
    const spanY = Math.max(0.25, maxY - minY);
    const padX = 28;
    const padY = 24;
    const scale = Math.min((w - padX * 2) / spanX, (h - padY * 2 - 12) / spanY);
    const mapPt = ([x, y]) => [
      padX + (x - minX) * scale,
      padY + 10 + (y - minY) * scale,
    ];

    // Draw tip trajectory arc across all frames
    ctx.beginPath();
    frames.forEach((f, idx) => {
      const [sx, sy] = mapPt(f.tip || [0, 0]);
      if (idx === 0) ctx.moveTo(sx, sy);
      else ctx.lineTo(sx, sy);
    });
    ctx.strokeStyle = 'rgba(52, 211, 153, 0.55)';
    ctx.lineWidth = 1.6;
    ctx.setLineDash([4, 3]);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw bound articulated static-coupling chain at current frame
    if (joints.length >= 2) {
      ctx.beginPath();
      joints.forEach((pt, idx) => {
        const [sx, sy] = mapPt(pt);
        if (idx === 0) ctx.moveTo(sx, sy);
        else ctx.lineTo(sx, sy);
      });
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 3.0;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.stroke();

      const names = traj.bound_hierarchy || [];
      joints.forEach((pt, idx) => {
        const [sx, sy] = mapPt(pt);
        const isTip = idx === joints.length - 1;
        ctx.beginPath();
        ctx.arc(sx, sy, isTip ? 5.2 : 3.4, 0, Math.PI * 2);
        ctx.fillStyle = isTip ? '#34d399' : (idx === 0 ? '#f87171' : '#e2e8f0');
        ctx.fill();
        if (idx === 0 || isTip || idx === Math.floor(joints.length / 2)) {
          ctx.fillStyle = 'rgba(226,232,240,0.88)';
          ctx.font = '9.5px system-ui, sans-serif';
          ctx.fillText(String(names[idx] || '').slice(0, 8), sx + 6, sy - 4);
        }
      });
    }

    // Header badge inside canvas
    ctx.fillStyle = '#a7f3d0';
    ctx.font = '10px ui-monospace, SFMono-Regular, Menlo, monospace';
    ctx.fillText(
      `${traj.perceptual_unit} · ${traj.action_label} | 정적결합 ${Number(traj.static_raw_elements_bound || 0).toLocaleString()} · 재계산 0회`,
      8,
      14
    );
  }

  function renderPerceptualStructures() {
    if (!PERCEPTUAL_UNIT_BOX || !spineState) return;
    clearEl(PERCEPTUAL_UNIT_BOX);
    const ps = spineState.principled_spectrum || {};
    const list = ps.perceptual_structures || [];
    if (!list.length) {
      PERCEPTUAL_UNIT_BOX.appendChild(el('div', 'erv-muted', '지각 단위 구조 로딩 대기 중…'));
      drawPerceptualTrajectory(null);
      return;
    }

    if (!activeTrajectory) {
      const withTraj = list.find((p) => p.last_trajectory);
      if (withTraj) activeTrajectory = withTraj.last_trajectory;
    }
    drawPerceptualTrajectory(activeTrajectory);

    const triad = ps.rotor_triad || null;
    if (triad) {
      const tCard = el('div', 'erv-exp-card');
      tCard.style.borderColor = 'rgba(96,165,250,0.42)';
      tCard.appendChild(el('div', 'erv-exp-obj', '3중 로터 삼위일체 (정적 · 가변 · 미지)'));
      const sr = triad.static_rotor || {};
      const vr = triad.variable_rotor || {};
      const ur = triad.unknown_rotor || {};
      tCard.appendChild(
        el(
          'div',
          'erv-exp-line mono',
          `[정적 t=0] 결정 ${sr.bound_crystals || 0} · 지각구조 ${sr.bound_perceptual_units || 0} (결합 ${Number(sr.total_static_elements || 0).toLocaleString()} · 재계산 0)`
        )
      );
      tCard.appendChild(
        el(
          'div',
          'erv-exp-line mono',
          `[가변·정신] 최대 분별 1:${Number(vr.max_resolution || 1).toLocaleString()} · 궤적 전개 ${vr.active_actuations || 0}회`
        )
      );
      tCard.appendChild(
        el('div', 'erv-exp-line erv-muted', `[미지·외부] ${ur.open_boundary_state || '미포집 미래 변수 · 외부 현실 개방'}`)
      );
      PERCEPTUAL_UNIT_BOX.appendChild(tCard);
    }

    list.forEach((p) => {
      const card = el('div', 'erv-exp-card');
      const head = el('div', 'erv-exp-head');
      head.appendChild(el('span', 'erv-exp-obj', `${p.perceptual_unit} (${p.media_domain})`));
      const badge = el(
        'span',
        'erv-exp-tag mono',
        `결합 ${Number(p.static_raw_elements || 0).toLocaleString()} · 재계산 0회`
      );
      badge.style.color = p.actuation_count > 0 ? '#86efac' : '#93c5fd';
      head.appendChild(badge);
      card.appendChild(head);

      card.appendChild(
        el('div', 'erv-exp-line mono', `정적 사슬: ${(p.bound_hierarchy || []).join(' → ')}`)
      );
      card.appendChild(el('div', 'erv-exp-line erv-muted', p.causal_mechanics || ''));

      const btnRow = el('div', 'erv-fork-row');
      btnRow.style.marginTop = '5px';
      btnRow.style.gap = '4px';
      btnRow.style.flexWrap = 'wrap';

      (p.actions || []).forEach((act) => {
        const btn = el('button', 'erv-btn', act.label);
        btn.type = 'button';
        btn.style.flex = '1';
        btn.addEventListener('click', async (ev) => {
          ev.stopPropagation();
          btn.disabled = true;
          try {
            spineState = await apiPost('/api/spine/actuate-perceptual-unit', {
              unit_id: p.id,
              action: act.id,
              target: 0.82,
            });
            const tr = spineState.trajectory_result || null;
            if (tr) {
              activeTrajectory = tr;
              trajAnimPhase = 0;
              selectedNodeId = `punit::${p.id}`;
            }
            ripplePulse = 1.0;
            showToast((tr && tr.principle_summary) || `지각 단위 궤적 완료: ${p.perceptual_unit}`, false);
            renderAll();
          } catch (err) {
            btn.disabled = false;
            showToast(err.message, true);
          }
        });
        btnRow.appendChild(btn);
      });

      card.appendChild(btnRow);
      PERCEPTUAL_UNIT_BOX.appendChild(card);
    });
  }

  function renderWorlds() {
    if (!WORLD_LIST || !spineState) return;
    clearEl(WORLD_LIST);
    (spineState.worlds || []).forEach((w) => {
      const btn = el('button', 'erv-world-btn' + (w.active ? ' active' : ''));
      btn.type = 'button';
      const top = el('div', 'erv-world-top');
      top.appendChild(el('span', 'erv-world-name', w.name));
      top.appendChild(el('span', 'erv-world-role mono', w.role === 'home' ? 'HOME' : w.fork_mode.toUpperCase()));
      btn.appendChild(top);
      btn.appendChild(
        el(
          'div',
          'erv-world-meta mono',
          `경험 ${w.experience_count} · 입력링 ${w.input_ring_count} · 순환 ${w.cycles}`
        )
      );
      btn.addEventListener('click', async () => {
        if (w.active) return;
        try {
          spineState = await apiPost('/api/spine/switch-world', { world_id: w.id });
          ripplePulse = 0.85;
          showToast(`세계 전환 완료: ${w.name}`, false);
          renderAll();
        } catch (err) {
          showToast(err.message, true);
        }
      });
      WORLD_LIST.appendChild(btn);
    });
  }

  function renderFourAxis() {
    if (!FOUR_AXIS_BOX || !spineState) return;
    clearEl(FOUR_AXIS_BOX);
    const fa = spineState.four_axis || {};
    const rows = [
      ['내부 기원 (Internal)', Number(fa.internal_origin || 0), '#60a5fa'],
      ['외부 영향 (External)', Number(fa.external_influence || 0), '#fbbf24'],
      ['경계 · 미지 (Ignorance)', Number(fa.boundary_ignorance || 0), '#f87171'],
      ['기준 자기수정 (Revision)', Number(fa.criteria_revision || 0), '#34d399'],
    ];
    rows.forEach(([lbl, val, col]) => {
      const wrap = el('div', 'erv-bar-wrap');
      const head = el('div', 'erv-bar-head');
      head.appendChild(el('span', '', lbl));
      head.appendChild(el('span', 'mono', val.toFixed(2)));
      const track = el('div', 'erv-bar-track');
      const fill = el('div', 'erv-bar-fill');
      fill.style.width = `${Math.max(4, Math.min(100, Math.round(val * 100)))}%`;
      fill.style.background = col;
      track.appendChild(fill);
      wrap.appendChild(head);
      wrap.appendChild(track);
      FOUR_AXIS_BOX.appendChild(wrap);
    });
    if (fa.last_revision_note) {
      FOUR_AXIS_BOX.appendChild(el('div', 'erv-subcopy', fa.last_revision_note));
    }
  }

  function renderExperiences() {
    if (!EXP_LIST || !spineState) return;
    clearEl(EXP_LIST);
    const exps = (spineState.active_world && spineState.active_world.experiences) || [];
    if (!exps.length) {
      EXP_LIST.appendChild(el('div', 'erv-muted', '아직 기록된 3-Way 경험이 없습니다. 대화·모듈 흡수·세계 분기를 해보세요.'));
      return;
    }
    exps.slice(0, 8).forEach((ex) => {
      const card = el('div', 'erv-exp-card');
      const head = el('div', 'erv-exp-head');
      head.appendChild(el('span', 'erv-exp-obj', ex.object));
      head.appendChild(el('span', 'erv-exp-tag mono', ex.relation_state_ko || ex.relation_state));
      card.appendChild(head);
      card.appendChild(el('div', 'erv-exp-line', `자기 렌즈: ${ex.self_lens}`));
      card.appendChild(el('div', 'erv-exp-line', `사이 변화: ${ex.inter_space}`));
      EXP_LIST.appendChild(card);
    });
  }

  function renderBoundaryHandles() {
    if (!HANDLE_LIST || !spineState) return;
    clearEl(HANDLE_LIST);
    const handles = spineState.external_handles || [];
    if (!handles.length) {
      HANDLE_LIST.appendChild(el('div', 'erv-muted', '등록된 외부 경계 핸들이 없습니다.'));
      return;
    }
    handles.forEach((h) => {
      const card = el('div', 'erv-mem-card');
      const top = el('div', 'erv-mem-top');
      top.appendChild(el('span', 'erv-mem-name', h.name));
      const badge = el('span', 'erv-mem-badge mono', h.coupled ? `결합 중 · 숙련 ${Math.round((h.mastery_at_boundary || 0) * 100)}%` : '비자아 대기 (분리됨)');
      badge.style.color = h.coupled ? '#86efac' : '#94a3b8';
      top.appendChild(badge);
      card.appendChild(top);
      card.appendChild(el('div', 'erv-mem-line', `제어면: ${(h.control_handles || []).slice(0, 3).join(' · ')}`));
      card.appendChild(el('div', 'erv-mem-line', `관측면: ${(h.observable_surface || []).slice(0, 2).join(' · ')}`));
      card.appendChild(el('div', 'erv-mem-line erv-muted', `비자아(몰라도 됨): ${h.opaque_non_self || ''}`));
      if (h.last_observed) {
        card.appendChild(el('div', 'erv-mem-line mono', `최근: ${h.last_action} → ${h.last_observed}`));
      }

      const btnRow = el('div', 'erv-fork-row');
      btnRow.style.marginTop = '5px';

      if (!h.coupled) {
        const btnCouple = el('button', 'erv-btn primary', '조작면 결합');
        btnCouple.type = 'button';
        btnCouple.addEventListener('click', async (ev) => {
          ev.stopPropagation();
          btnCouple.disabled = true;
          try {
            spineState = await apiPost('/api/spine/couple-handle', { handle_id: h.id });
            selectedNodeId = h.id;
            ripplePulse = 0.95;
            showToast(`경계 결합 완료: ${h.name} (내부 설계 0% 로드 · 조작/관측면만 결합)`, false);
            renderAll();
          } catch (err) {
            btnCouple.disabled = false;
            showToast(err.message, true);
          }
        });
        btnRow.appendChild(btnCouple);
      } else {
        const btnAct = el('button', 'erv-btn primary', '조작 → 관측 시험');
        btnAct.type = 'button';
        btnAct.addEventListener('click', async (ev) => {
          ev.stopPropagation();
          btnAct.disabled = true;
          try {
            spineState = await apiPost('/api/spine/actuate-handle', { handle_id: h.id });
            selectedNodeId = h.id;
            ripplePulse = 1.0;
            const tr = (spineState.topology_result && spineState.topology_result.handle) || h;
            showToast(`경계 조작 확인: ${tr.last_action} → ${tr.last_observed}`, false);
            renderAll();
          } catch (err) {
            btnAct.disabled = false;
            showToast(err.message, true);
          }
        });
        btnRow.appendChild(btnAct);

        const btnDetach = el('button', 'erv-btn', '분리 (내려놓기)');
        btnDetach.type = 'button';
        btnDetach.addEventListener('click', async (ev) => {
          ev.stopPropagation();
          btnDetach.disabled = true;
          try {
            spineState = await apiPost('/api/spine/detach-handle', { handle_id: h.id });
            if (selectedNodeId === h.id) selectedNodeId = null;
            ripplePulse = 0.7;
            showToast(`경계 분리 완료: ${h.name} (도구 내려놓음 · 자아 오염 0%)`, false);
            renderAll();
          } catch (err) {
            btnDetach.disabled = false;
            showToast(err.message, true);
          }
        });
        btnRow.appendChild(btnDetach);
      }

      card.appendChild(btnRow);
      card.addEventListener('click', () => {
        if (h.coupled) {
          selectedNodeId = h.id;
          renderInspector();
        }
      });
      HANDLE_LIST.appendChild(card);
    });
  }

  function renderMembranes() {
    if (!MEMBRANE_LIST || !spineState) return;
    clearEl(MEMBRANE_LIST);
    const rt = spineState.runtime_capabilities || {};
    (rt.membranes || []).forEach((m) => {
      const card = el('div', 'erv-mem-card');
      const top = el('div', 'erv-mem-top');
      top.appendChild(el('span', 'erv-mem-name', m.name_ko));
      const badge = el('span', 'erv-mem-badge mono', m.mode === 'ACCELERATED' ? '가속기 결합' : '불변 순수 구동');
      badge.style.color = m.mode === 'ACCELERATED' ? '#86efac' : '#fde68a';
      top.appendChild(badge);
      card.appendChild(top);
      card.appendChild(el('div', 'erv-mem-line', `불변 로터: ${m.invariant_rotor}`));
      card.appendChild(el('div', 'erv-mem-line erv-muted', `가변 가속: ${m.variable_accelerator} (${(m.external_deps || []).join(', ')})`));
      card.addEventListener('click', () => {
        selectedNodeId = m.id;
        renderInspector();
      });
      MEMBRANE_LIST.appendChild(card);
    });
  }

  function renderModules() {
    if (!MOD_LIST || !spineState) return;
    clearEl(MOD_LIST);
    const q = (MOD_SEARCH ? MOD_SEARCH.value : '').trim().toLowerCase();
    const mods = (spineState.codebase_modules || []).filter((m) => {
      if (activeFilter !== 'ALL' && m.status !== activeFilter) return false;
      if (q && !m.path.toLowerCase().includes(q) && !m.name.toLowerCase().includes(q)) return false;
      return true;
    });

    if (!mods.length) {
      MOD_LIST.appendChild(el('div', 'erv-muted', '조건에 맞는 모듈이 없습니다.'));
      return;
    }

    mods.slice(0, 48).forEach((m) => {
      const row = el('div', 'erv-mod-row');
      const info = el('div', 'erv-mod-info');
      const titleRow = el('div', 'erv-mod-title-row');
      titleRow.appendChild(el('span', 'erv-scale-dot', `S${m.scale}`));
      titleRow.appendChild(el('span', 'erv-mod-name mono', m.name));
      titleRow.appendChild(el('span', 'erv-mod-status mono', m.status_ko));
      info.appendChild(titleRow);
      info.appendChild(el('div', 'erv-mod-path mono', `${m.path} (${m.lines}줄)`));
      info.appendChild(el('div', 'erv-mod-recipe', m.bridge_recipe));
      info.addEventListener('click', () => {
        selectedNodeId = `mod::${m.path}`;
        renderInspector(m);
      });

      const btnCol = el('div', '');
      btnCol.style.display = 'flex';
      btnCol.style.flexDirection = 'column';
      btnCol.style.gap = '4px';

      const handleBtn = el('button', 'erv-absorb-btn', '조작면 결합');
      handleBtn.type = 'button';
      handleBtn.style.borderColor = 'rgba(52,211,153,0.55)';
      handleBtn.style.color = '#a7f3d0';
      handleBtn.addEventListener('click', async (ev) => {
        ev.stopPropagation();
        handleBtn.disabled = true;
        try {
          const hid = `handle::mod_${m.name}`;
          spineState = await apiPost('/api/spine/couple-handle', {
            handle_id: hid,
            name: `${m.name} (외부 모듈 경계)`,
            domain: 'code_module',
            control_handles: (m.functions && m.functions.length) ? m.functions.slice(0, 3) : [`${m.name} 호출 경계`],
            observable_surface: [`S${m.scale} 상태 변화 관측`, m.status_ko || '경계 응답'],
            opaque_non_self: `${m.path} (${m.lines}줄) 및 외부 의존성(${(m.missing_deps || []).join(', ') || '없음'}) 전체 — 내부 비열람`,
          });
          selectedNodeId = hid;
          ripplePulse = 0.9;
          showToast(`모듈 조작면 결합 완료: ${m.name} (내부 코드 0% 흡수 · 경계만 사용)`, false);
          renderAll();
        } catch (err) {
          handleBtn.disabled = false;
          showToast(err.message, true);
        }
      });

      const act = el('button', 'erv-absorb-btn', m.absorbed ? '흡수됨' : '원리 흡수');
      act.type = 'button';
      if (m.absorbed) act.classList.add('done');
      act.addEventListener('click', async (ev) => {
        ev.stopPropagation();
        act.disabled = true;
        act.textContent = '흡수 중…';
        try {
          const res = await apiPost('/api/spine/absorb-module', { rel_path: m.path });
          spineState = res;
          selectedNodeId = `mod::${m.path}`;
          ripplePulse = 1.0;
          showToast(`AST 불변 원리 흡수·Cl(3,0) 도킹 완료: ${m.name}`, false);
          renderAll();
        } catch (err) {
          act.disabled = false;
          act.textContent = '원리 흡수';
          showToast(err.message, true);
        }
      });

      btnCol.appendChild(handleBtn);
      btnCol.appendChild(act);
      row.appendChild(info);
      row.appendChild(btnCol);
      MOD_LIST.appendChild(row);
    });
  }

  function renderInspector(fallbackMod) {
    if (!INSPECTOR || !spineState) return;
    clearEl(INSPECTOR);
    const nodes = (spineState.spine_graph && spineState.spine_graph.nodes) || [];
    const nd = nodes.find((n) => n.id === selectedNodeId);
    if (!nd && !fallbackMod) {
      INSPECTOR.appendChild(el('div', 'erv-muted', '3D 리얼리티 뷰에서 노드를 클릭하거나 우측 모듈을 선택하면 Cl(3,0) 멀티벡터와 의존성 가교 처방이 표시됩니다.'));
      return;
    }

    const title = nd ? nd.label : fallbackMod.name;
    const scale = nd ? nd.scale : fallbackMod.scale;
    const mv = (nd ? nd.multivector : fallbackMod.multivector) || [];
    const ch = (nd ? nd.chromatic : fallbackMod.chromatic) || [0.33, 0.34, 0.33];
    const meta = (nd && nd.meta) || {};
    const modPath = meta.path || (fallbackMod && fallbackMod.path) || '';

    const head = el('div', 'erv-insp-head');
    head.appendChild(el('span', 'erv-insp-title', title));
    head.appendChild(el('span', 'erv-scale-pill mono', scaleLabel(scale)));
    INSPECTOR.appendChild(head);

    const openSpec = (nd && nd.open_spectrum) || { flux: ch[0], order: ch[1], entropy: ch[2] };
    const specTxt = Object.entries(openSpec)
      .map(([k, v]) => `${k} ${(Number(v) * 100).toFixed(0)}%`)
      .join(' · ');
    INSPECTOR.appendChild(
      el(
        'div',
        'erv-subcopy mono',
        `열린 스펙트럼(${Object.keys(openSpec).length}채널): ${specTxt} | Cl(3,0): [${mv.map((x) => Number(x).toFixed(2)).join(', ')}]`
      )
    );

    if (meta.root_continuum) {
      INSPECTOR.appendChild(el('div', 'erv-subcopy', `상위 원리 스펙트럼(전체): ${meta.root_continuum}`));
      INSPECTOR.appendChild(el('div', 'erv-subcopy', `구성요소(축): ${(meta.constituents || []).join(' · ')}`));
      INSPECTOR.appendChild(el('div', 'erv-subcopy', `환경·매질 조건: ${meta.conditions || ''}`));
    }
    if (meta.opaque_non_self) {
      INSPECTOR.appendChild(el('div', 'erv-subcopy', `제어 가능면: ${(meta.control_handles || []).join(' · ')}`));
      INSPECTOR.appendChild(el('div', 'erv-subcopy', `관측 가능면: ${(meta.observable_surface || []).join(' · ')}`));
      INSPECTOR.appendChild(el('div', 'erv-subcopy erv-muted', `비자아(내부 0% 로드): ${meta.opaque_non_self}`));
    }
    if (meta.invariant_rotor) {
      INSPECTOR.appendChild(el('div', 'erv-subcopy', `불변 커널: ${meta.invariant_rotor}`));
      INSPECTOR.appendChild(el('div', 'erv-subcopy erv-muted', `가변 가속기: ${meta.variable_accelerator}`));
    }
    if (meta.bridge_recipe || (fallbackMod && fallbackMod.bridge_recipe)) {
      INSPECTOR.appendChild(el('div', 'erv-subcopy', `로터 가교: ${meta.bridge_recipe || fallbackMod.bridge_recipe}`));
    }
    if (meta.bridge_steps && meta.bridge_steps.length) {
      meta.bridge_steps.forEach((st) => {
        INSPECTOR.appendChild(el('div', 'erv-subcopy', `• ${st}`));
      });
    }

    // Universal Recursive Scale-Rotor Controls: Split (↓) / Integrate (↑) / Horizontal Expand (↔)
    const opBar = el('div', 'erv-fork-row');
    opBar.style.marginTop = '7px';
    opBar.style.flexWrap = 'wrap';

    if (nd) {
      const btnSplit = el('button', 'erv-btn', `↓ 분할 (S${scale} → S${scale - 1})`);
      btnSplit.type = 'button';
      btnSplit.addEventListener('click', async () => {
        btnSplit.disabled = true;
        try {
          spineState = await apiPost('/api/spine/differentiate', { unit_id: nd.id });
          ripplePulse = 1.0;
          showToast(`분할 완료: ${nd.label} → S${scale - 1} 하위 단위 생성`, false);
          renderAll();
        } catch (err) {
          btnSplit.disabled = false;
          showToast(err.message, true);
        }
      });
      opBar.appendChild(btnSplit);

      const btnInteg = el('button', 'erv-btn primary', `↑ 통합 (S${scale} → S${scale + 1})`);
      btnInteg.type = 'button';
      btnInteg.addEventListener('click', async () => {
        btnInteg.disabled = true;
        try {
          spineState = await apiPost('/api/spine/integrate', { unit_ids: [nd.id] });
          const created = spineState.topology_result && spineState.topology_result.merged_node;
          if (created) selectedNodeId = created.id;
          ripplePulse = 1.0;
          showToast(`상향 통합 완료 → S${scale + 1} 상위 공명체 창발`, false);
          renderAll();
        } catch (err) {
          btnInteg.disabled = false;
          showToast(err.message, true);
        }
      });
      opBar.appendChild(btnInteg);

      const btnExpand = el('button', 'erv-btn', `↔ 수평 축 확장 (S${scale})`);
      btnExpand.type = 'button';
      btnExpand.style.borderColor = 'rgba(192,132,252,0.6)';
      btnExpand.style.color = '#e9d5ff';
      btnExpand.addEventListener('click', async () => {
        btnExpand.disabled = true;
        try {
          spineState = await apiPost('/api/spine/expand-axis', { anchor_unit_id: nd.id });
          const created = spineState.topology_result && spineState.topology_result.node;
          if (created) selectedNodeId = created.id;
          ripplePulse = 1.0;
          showToast(`수평 축 확장 완료 (총 ${(spineState.horizontal_axes || []).length}개 축)`, false);
          renderAll();
        } catch (err) {
          btnExpand.disabled = false;
          showToast(err.message, true);
        }
      });
      opBar.appendChild(btnExpand);
    }

    if (modPath) {
      const btn = el('button', 'erv-absorb-btn', meta.absorbed ? '재흡수 · 도킹 갱신' : 'AST 불변 원리 흡수 · 도킹');
      btn.type = 'button';
      btn.addEventListener('click', async () => {
        btn.disabled = true;
        try {
          spineState = await apiPost('/api/spine/absorb-module', { rel_path: modPath });
          selectedNodeId = `mod::${modPath}`;
          ripplePulse = 1.0;
          showToast(`흡수 완료: ${modPath}`, false);
          renderAll();
        } catch (err) {
          btn.disabled = false;
          showToast(err.message, true);
        }
      });
      opBar.appendChild(btn);
    }

    if (opBar.childNodes.length) {
      INSPECTOR.appendChild(opBar);
    }
  }

  // ---------------------------------------------------------------------------
  // 3D Spacetime Scale-Rotor Reality View Canvas Renderer
  // ---------------------------------------------------------------------------

  function project3D(x, y, z, w, h) {
    const cy = Math.cos(camYaw);
    const sy = Math.sin(camYaw);
    const cp = Math.cos(camPitch);
    const sp = Math.sin(camPitch);

    // Rotate around Y (yaw)
    const x1 = x * cy - z * sy;
    const z1 = x * sy + z * cy;
    // Rotate around X (pitch)
    const y2 = y * cp - z1 * sp;
    const z2 = y * sp + z1 * cp;

    const fov = 520 * camZoom;
    const dist = 8.4 + z2;
    const scale = fov / Math.max(2.2, dist);
    return {
      sx: w * 0.5 + x1 * scale,
      sy: h * 0.5 - y2 * scale,
      depth: dist,
      scale,
    };
  }

  function drawRealityCanvas(now) {
    if (!isOpen) return;
    rafId = requestAnimationFrame(drawRealityCanvas);

    const rect = CANVAS.getBoundingClientRect();
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = Math.max(320, Math.floor(rect.width));
    const h = Math.max(260, Math.floor(rect.height));
    if (CANVAS.width !== w * dpr || CANVAS.height !== h * dpr) {
      CANVAS.width = w * dpr;
      CANVAS.height = h * dpr;
    }
    const ctx = CANVAS.getContext('2d');
    if (!ctx) return;

    ctx.save();
    ctx.scale(dpr, dpr);

    // Deep obsidian studio backdrop
    const bg = ctx.createRadialGradient(w * 0.5, h * 0.5, 24, w * 0.5, h * 0.5, Math.max(w, h) * 0.65);
    bg.addColorStop(0, '#0f172a');
    bg.addColorStop(1, '#04070f');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    if (!dragging) {
      camYaw += 0.0018;
    }
    ripplePulse = Math.max(0, ripplePulse * 0.965);

    // 1. Draw Unbounded Concentric Spacetime Scale Rings (S_min .. S_max)
    const graph = (spineState && spineState.spine_graph) || { nodes: [], links: [], active_scales: [0, 1, 2, 3, 4] };
    const activeScales = (graph.active_scales && graph.active_scales.length) ? graph.active_scales : [0, 1, 2, 3, 4];
    activeScales.forEach((s) => {
      const r = Math.max(0.38, 0.92 + Math.max(-2.5, s) * 0.56);
      const y = (s - 2.0) * 0.68;
      const col = scaleColor(s);
      ctx.beginPath();
      const segs = 64;
      for (let i = 0; i <= segs; i++) {
        const th = (i / segs) * Math.PI * 2;
        const p = project3D(Math.cos(th) * r, y, Math.sin(th) * r, w, h);
        if (i === 0) ctx.moveTo(p.sx, p.sy);
        else ctx.lineTo(p.sx, p.sy);
      }
      ctx.strokeStyle = col;
      ctx.globalAlpha = s === 3 || s > 4 || s < 0 ? 0.36 : 0.22;
      ctx.lineWidth = s === 3 || s > 4 ? 1.5 : 1.0;
      ctx.stroke();
      ctx.globalAlpha = 1.0;

      const lp = project3D(r, y, 0, w, h);
      ctx.fillStyle = col;
      ctx.font = '11px ui-monospace, SFMono-Regular, Menlo, monospace';
      ctx.fillText(`S${s}`, lp.sx + 4, lp.sy - 3);
    });

    // Sensory ripple wave when live input, split, integrate, or absorption happens
    if (ripplePulse > 0.03) {
      const rr = (1.0 - ripplePulse) * 3.6 + 0.5;
      ctx.beginPath();
      for (let i = 0; i <= 48; i++) {
        const th = (i / 48) * Math.PI * 2;
        const p = project3D(Math.cos(th) * rr, -1.2 + (1 - ripplePulse) * 2.4, Math.sin(th) * rr, w, h);
        if (i === 0) ctx.moveTo(p.sx, p.sy);
        else ctx.lineTo(p.sx, p.sy);
      }
      ctx.strokeStyle = `rgba(125, 211, 252, ${ripplePulse * 0.7})`;
      ctx.lineWidth = 2.0;
      ctx.stroke();
    }

    const nodePosMap = new Map();
    projectedNodes = [];

    // 2. Project all nodes
    const tSec = now * 0.001;
    graph.nodes.forEach((nd) => {
      const base = nd.pos || [0, 0, 0];
      const bob = Math.sin(tSec * 1.4 + base[0] * 1.9 + nd.scale) * 0.04;
      const p = project3D(base[0], base[1] + bob, base[2], w, h);
      const item = { nd, p };
      nodePosMap.set(nd.id, item);
      projectedNodes.push(item);
    });

    // 3. Draw Cl(3,0) Docking & Recursive Split/Integrate/Expand Links
    graph.links.forEach((lk) => {
      const a = nodePosMap.get(lk.src);
      const b = nodePosMap.get(lk.dst);
      if (!a || !b) return;
      const isSelected = selectedNodeId && (lk.src === selectedNodeId || lk.dst === selectedNodeId);
      ctx.beginPath();
      ctx.moveTo(a.p.sx, a.p.sy);
      ctx.lineTo(b.p.sx, b.p.sy);
      if (isSelected) {
        ctx.strokeStyle = 'rgba(253, 224, 71, 0.85)';
        ctx.lineWidth = 1.9;
      } else if (lk.relation === 'integrates_into' || lk.relation === 'differentiates_into') {
        ctx.strokeStyle = 'rgba(244, 114, 182, 0.56)';
        ctx.lineWidth = 1.45;
      } else if (lk.relation === 'expands_axis' || lk.relation === 'horizontal_span') {
        ctx.strokeStyle = 'rgba(192, 132, 252, 0.52)';
        ctx.lineWidth = 1.3;
      } else if (lk.relation === 'organ_integrated' || lk.relation === 'live_spine') {
        ctx.strokeStyle = 'rgba(52, 211, 153, 0.44)';
        ctx.lineWidth = 1.25;
      } else if (lk.relation === 'reconstructs' || lk.relation === 'ascends_to') {
        ctx.strokeStyle = 'rgba(192, 132, 252, 0.58)';
        ctx.lineWidth = 1.5;
      } else if (lk.relation === 'docks') {
        ctx.strokeStyle = 'rgba(96, 165, 250, 0.28)';
        ctx.lineWidth = 0.9;
      } else {
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.16)';
        ctx.lineWidth = 0.75;
      }
      ctx.stroke();
    });

    // 4. Draw depth-sorted nodes
    projectedNodes.sort((a, b) => b.p.depth - a.p.depth);
    projectedNodes.forEach(({ nd, p }) => {
      const isSel = nd.id === selectedNodeId;
      const isCore = nd.kind === 'world_model' || nd.kind === 'telos' || nd.kind === 'membrane' || nd.kind === 'emergent_merged' || nd.kind === 'emergent_axis';
      const isAbsorbed = nd.kind === 'absorbed_organ' || (nd.meta && nd.meta.absorbed);
      const baseR = isCore ? 7.2 : isAbsorbed ? 6.0 : nd.kind === 'seed_lens' ? 5.6 : nd.kind === 'sensory' ? 6.2 : 4.2;
      const r = Math.max(2.6, Math.min(13, baseR * (p.scale / 72)));
      const col = isAbsorbed ? '#34d399' : scaleColor(nd.scale);

      if (isSel || isCore || isAbsorbed) {
        ctx.beginPath();
        ctx.arc(p.sx, p.sy, r + 4.5, 0, Math.PI * 2);
        ctx.fillStyle = isSel ? 'rgba(253, 224, 71, 0.30)' : col;
        ctx.globalAlpha = isSel ? 1.0 : 0.16;
        ctx.fill();
        ctx.globalAlpha = 1.0;
      }

      ctx.beginPath();
      ctx.arc(p.sx, p.sy, r, 0, Math.PI * 2);
      ctx.fillStyle = col;
      ctx.fill();
      ctx.strokeStyle = isSel ? '#fef08a' : 'rgba(15, 23, 42, 0.9)';
      ctx.lineWidth = isSel ? 2.0 : 1.0;
      ctx.stroke();

      if (isSel || isCore || isAbsorbed || nd.kind === 'seed_lens' || nd.kind === 'emergent_split' || nd.kind === 'sensory' || nd.kind === 'dialogue') {
        ctx.fillStyle = isSel ? '#fef08a' : 'rgba(226, 232, 240, 0.88)';
        ctx.font = isSel ? '600 11.5px system-ui, sans-serif' : '10.5px system-ui, sans-serif';
        ctx.fillText(nd.label.slice(0, 26), p.sx + r + 5, p.sy + 3.5);
      }
    });

    // Bottom canvas legend
    ctx.fillStyle = 'rgba(203, 213, 225, 0.72)';
    ctx.font = '11px ui-monospace, SFMono-Regular, Menlo, monospace';
    ctx.fillText('드래그: 3D 회전 · 노드 클릭 → 하단에서 ↓분할(S-1) / ↑통합(S+1) / ↔수평축확장 실시간 실행', 14, h - 14);

    ctx.restore();

    if (activeTrajectory) {
      trajAnimPhase += 0.14;
      drawPerceptualTrajectory(activeTrajectory);
    }
  }

  // Canvas interactions
  CANVAS.addEventListener('pointerdown', (e) => {
    dragging = true;
    dragLastX = e.clientX;
    dragLastY = e.clientY;
    CANVAS.setPointerCapture(e.pointerId);
  });

  CANVAS.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    const dx = e.clientX - dragLastX;
    const dy = e.clientY - dragLastY;
    dragLastX = e.clientX;
    dragLastY = e.clientY;
    camYaw += dx * 0.008;
    camPitch = Math.max(-1.1, Math.min(1.1, camPitch + dy * 0.008));
  });

  CANVAS.addEventListener('pointerup', (e) => {
    dragging = false;
    try { CANVAS.releasePointerCapture(e.pointerId); } catch {}
  });

  CANVAS.addEventListener('wheel', (e) => {
    e.preventDefault();
    camZoom = Math.max(0.55, Math.min(2.1, camZoom * (e.deltaY > 0 ? 0.92 : 1.08)));
  }, { passive: false });

  CANVAS.addEventListener('click', (e) => {
    const rect = CANVAS.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    let best = null;
    let bestDist = 18;
    projectedNodes.forEach(({ nd, p }) => {
      const d = Math.hypot(p.sx - mx, p.sy - my);
      if (d < bestDist) {
        bestDist = d;
        best = nd;
      }
    });
    if (best) {
      selectedNodeId = best.id;
      renderInspector();
    }
  });

  // Buttons & Controls
  let centerTab = 'spine';

  function setCenterTab(mode) {
    centerTab = (mode === 'world_rotor' || mode === 'real_media' || mode === 'dynamic_engine') ? mode : 'spine';
    const isSpine = centerTab === 'spine';
    const isWR = centerTab === 'world_rotor';
    const isRM = centerTab === 'real_media';
    const isDE = centerTab === 'dynamic_engine';

    if (TAB_SPINE) {
      TAB_SPINE.classList.toggle('active', isSpine);
      TAB_SPINE.setAttribute('aria-selected', String(isSpine));
    }
    if (TAB_DYNAMIC) {
      TAB_DYNAMIC.classList.toggle('active', isDE);
      TAB_DYNAMIC.setAttribute('aria-selected', String(isDE));
    }
    if (TAB_REAL_MEDIA) {
      TAB_REAL_MEDIA.classList.toggle('active', isRM);
      TAB_REAL_MEDIA.setAttribute('aria-selected', String(isRM));
    }
    if (TAB_WORLD_ROTOR) {
      TAB_WORLD_ROTOR.classList.toggle('active', isWR);
      TAB_WORLD_ROTOR.setAttribute('aria-selected', String(isWR));
    }
    if (CANVAS) CANVAS.style.display = isSpine ? 'block' : 'none';
    if (INSPECTOR) INSPECTOR.style.display = isSpine ? 'block' : 'none';
    if (WORLD_ROTOR_STAGE) WORLD_ROTOR_STAGE.classList.toggle('active', isWR);
    if (REAL_MEDIA_STAGE) REAL_MEDIA_STAGE.classList.toggle('active', isRM);
    if (DYNAMIC_STAGE) DYNAMIC_STAGE.classList.toggle('active', isDE);

    if (isWR) {
      cancelAnimationFrame(rafId);
      if (window.ElysiaRealMediaLab) window.ElysiaRealMediaLab.stop();
      if (window.ElysiaDynamicEngine) window.ElysiaDynamicEngine.stop();
      if (window.ElysiaWorldRotorSim) window.ElysiaWorldRotorSim.start();
    } else if (isRM) {
      cancelAnimationFrame(rafId);
      if (window.ElysiaWorldRotorSim) window.ElysiaWorldRotorSim.stop();
      if (window.ElysiaDynamicEngine) window.ElysiaDynamicEngine.stop();
      if (window.ElysiaRealMediaLab) window.ElysiaRealMediaLab.start();
    } else if (isDE) {
      cancelAnimationFrame(rafId);
      if (window.ElysiaWorldRotorSim) window.ElysiaWorldRotorSim.stop();
      if (window.ElysiaRealMediaLab) window.ElysiaRealMediaLab.stop();
      if (window.ElysiaDynamicEngine) window.ElysiaDynamicEngine.start();
    } else {
      if (window.ElysiaWorldRotorSim) window.ElysiaWorldRotorSim.stop();
      if (window.ElysiaRealMediaLab) window.ElysiaRealMediaLab.stop();
      if (window.ElysiaDynamicEngine) window.ElysiaDynamicEngine.stop();
      if (isOpen) {
        cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(drawRealityCanvas);
      }
    }
  }

  function openOverlay(initialTab) {
    isOpen = true;
    OVERLAY.classList.add('open');
    refreshSpineState();
    setCenterTab(initialTab || centerTab);
  }

  function closeOverlay() {
    isOpen = false;
    OVERLAY.classList.remove('open');
    cancelAnimationFrame(rafId);
    if (window.ElysiaWorldRotorSim) window.ElysiaWorldRotorSim.stop();
    if (window.ElysiaRealMediaLab) window.ElysiaRealMediaLab.stop();
    if (window.ElysiaDynamicEngine) window.ElysiaDynamicEngine.stop();
  }

  BTN_OPEN.addEventListener('click', () => {
    if (isOpen && centerTab === 'spine') closeOverlay();
    else openOverlay('spine');
  });

  if (BTN_OPEN_WORLD_ROTOR) {
    BTN_OPEN_WORLD_ROTOR.addEventListener('click', () => {
      if (isOpen && centerTab === 'world_rotor') closeOverlay();
      else openOverlay('world_rotor');
    });
  }

  if (BTN_OPEN_REAL_MEDIA) {
    BTN_OPEN_REAL_MEDIA.addEventListener('click', () => {
      if (isOpen && centerTab === 'real_media') closeOverlay();
      else openOverlay('real_media');
    });
  }

  if (BTN_OPEN_DYNAMIC) {
    BTN_OPEN_DYNAMIC.addEventListener('click', () => {
      if (isOpen && centerTab === 'dynamic_engine') closeOverlay();
      else openOverlay('dynamic_engine');
    });
  }

  if (TAB_SPINE) TAB_SPINE.addEventListener('click', () => setCenterTab('spine'));
  if (TAB_DYNAMIC) TAB_DYNAMIC.addEventListener('click', () => setCenterTab('dynamic_engine'));
  if (TAB_REAL_MEDIA) TAB_REAL_MEDIA.addEventListener('click', () => setCenterTab('real_media'));
  if (TAB_WORLD_ROTOR) TAB_WORLD_ROTOR.addEventListener('click', () => setCenterTab('world_rotor'));

  if (BTN_CLOSE) BTN_CLOSE.addEventListener('click', closeOverlay);

  if (BTN_CYCLE) {
    BTN_CYCLE.addEventListener('click', async () => {
      try {
        spineState = await apiPost('/api/spine/vertical-cycle', { trigger: '리얼리티 뷰 수직 통합 순환' });
        ripplePulse = 0.95;
        const vt = spineState.cycle_trace || spineState.last_vertical_trace || {};
        showToast(`S0↔S4 순환 #${vt.cycle || ''} 완료 (오차 ${Number(vt.gap_before || 0).toFixed(3)} → ${Number(vt.gap_after || 0).toFixed(3)})`, false);
        renderAll();
      } catch (err) {
        showToast(err.message, true);
      }
    });
  }

  if (BTN_FOLD) {
    BTN_FOLD.addEventListener('click', async () => {
      BTN_FOLD.disabled = true;
      try {
        spineState = await apiPost('/api/spine/fold-limit', { cluster_size: 4, reason: '리얼리티 뷰 한계 지각 · 원근 압축 접기' });
        const tr = spineState.topology_result || {};
        if (tr.horizon) selectedNodeId = tr.horizon.id;
        ripplePulse = 0.95;
        showToast(
          tr.folded_count
            ? `한계 지각 접기 완료: ${tr.folded_count}개 단위 → 1개 지평으로 무손실 응축 (↓분할로 복원 가능)`
            : (tr.message || '접을 비핵심 단위가 없습니다.'),
          false
        );
        renderAll();
      } catch (err) {
        showToast(err.message, true);
      } finally {
        BTN_FOLD.disabled = false;
      }
    });
  }

  if (BTN_SCAN) {
    BTN_SCAN.addEventListener('click', async () => {
      BTN_SCAN.disabled = true;
      try {
        spineState = await apiPost('/api/spine/scan-codebase', { max_entries: 180 });
        ripplePulse = 0.9;
        showToast(`저장소 ${spineState.codebase_summary.total_scanned}개 파일 의존성 로터화 재스캔 완료`, false);
        renderAll();
      } catch (err) {
        showToast(err.message, true);
      } finally {
        BTN_SCAN.disabled = false;
      }
    });
  }

  if (BTN_FORK_INHERIT) {
    BTN_FORK_INHERIT.addEventListener('click', async () => {
      try {
        spineState = await apiPost('/api/spine/fork-world', { fork_mode: 'inherit' });
        ripplePulse = 0.85;
        showToast('부모 계보를 승계한 샌드박스 세계로 분기했습니다 (홈 보존).', false);
        renderAll();
      } catch (err) {
        showToast(err.message, true);
      }
    });
  }

  if (BTN_FORK_BLANK) {
    BTN_FORK_BLANK.addEventListener('click', async () => {
      try {
        spineState = await apiPost('/api/spine/fork-world', { fork_mode: 'blank' });
        ripplePulse = 0.85;
        showToast('빈 공간 샌드박스 세계로 분기했습니다 (홈 보존).', false);
        renderAll();
      } catch (err) {
        showToast(err.message, true);
      }
    });
  }

  if (BTN_COUPLE_CUSTOM && HANDLE_INPUT) {
    const doCoupleCustom = async () => {
      const nm = (HANDLE_INPUT.value || '').trim();
      if (!nm) return;
      BTN_COUPLE_CUSTOM.disabled = true;
      try {
        spineState = await apiPost('/api/spine/couple-handle', { name: nm, domain: 'tool' });
        const h = spineState.topology_result && spineState.topology_result.handle;
        if (h) selectedNodeId = h.id;
        HANDLE_INPUT.value = '';
        ripplePulse = 0.95;
        showToast(`외부 경계 결합 완료: ${nm} (내부 설계 0% · 조작면만 연결)`, false);
        renderAll();
      } catch (err) {
        showToast(err.message, true);
      } finally {
        BTN_COUPLE_CUSTOM.disabled = false;
      }
    };
    BTN_COUPLE_CUSTOM.addEventListener('click', doCoupleCustom);
    HANDLE_INPUT.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') doCoupleCustom();
    });
  }

  OVERLAY.querySelectorAll('.erv-friction-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const eid = btn.getAttribute('data-exp') || 'memory_hierarchy';
      btn.disabled = true;
      try {
        spineState = await apiPost('/api/spine/run-friction-experiment', { experiment_id: eid });
        const fr = spineState.friction_result || {};
        ripplePulse = 1.0;
        showToast(fr.finding || `실측 마찰 실험 완료: ${eid}`, false);
        renderAll();
      } catch (err) {
        showToast(err.message, true);
      } finally {
        btn.disabled = false;
      }
    });
  });

  if (MOD_FILTER) {
    MOD_FILTER.addEventListener('change', () => {
      activeFilter = MOD_FILTER.value || 'ALL';
      renderModules();
    });
  }

  if (MOD_SEARCH) {
    MOD_SEARCH.addEventListener('input', () => {
      renderModules();
    });
  }
})();
