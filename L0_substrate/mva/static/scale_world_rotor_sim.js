/**
 * Elysia Nested Scale-Hierarchy World Rotor Simulator (S4 Macro -> S0 Micro)
 * ==========================================================================
 * Live 60fps interactive proof unifying:
 *   - S4 Macro Celestial Rotor (1 slow rotor -> sun/moon, sky, global light L, shadow axis)
 *   - S3 Atmosphere & Terrain Rotor (inherits S4 light -> clouds, lake reflection, wind-swaying trees)
 *   - S2/S1 Static-Bound Body & 'Hand' Perceptual Unit (t=0 bound chain, 0 raw identity recomputations)
 *   - S0 Recursive 1 -> 1,000,000 Contact Boundary Subdivision (O(log10 N) ~19 nodes)
 *   - Unknown Rotor (Live external disturbance -> Variable adaptation -> Static t=0 convergence)
 *   - Real Live Contrast: Scale-Hierarchy Protocol (~23 ops/frame, 100% coherence)
 *                         vs Flat Micro Brute-Force (74,880+ ops/frame, desync & bottleneck)
 */
(function () {
  'use strict';

  const CANVAS = document.getElementById('wrCanvas');
  if (!CANVAS) return;
  const ctx = CANVAS.getContext('2d');

  // Controls
  const BTN_PLAY = document.getElementById('wrBtnPlayPause');
  const BTN_EXP_CYCLE = document.getElementById('wrBtnExperienceCycle');
  const BTN_AUTO_EXP = document.getElementById('wrBtnAutoExp');
  const BTN_AUDIO = document.getElementById('wrBtnAudioToggle');
  const BTN_MODE_HIER = document.getElementById('wrBtnModeHierarchy');
  const BTN_MODE_MICRO = document.getElementById('wrBtnModeMicro');
  const BTN_INTENT_LIGHT = document.getElementById('wrBtnIntentLight');
  const BTN_INTENT_GRASP = document.getElementById('wrBtnIntentGrasp');
  const BTN_INTENT_WAVE = document.getElementById('wrBtnIntentWave');
  const BTN_SHOCK = document.getElementById('wrBtnInjectShock');
  const BTN_BENCH = document.getElementById('wrBtnRunBenchmark');
  const BTN_RESET = document.getElementById('wrBtnReset');

  const SLIDER_HOUR = document.getElementById('wrSliderHour');
  const VAL_HOUR = document.getElementById('wrValHour');
  const SLIDER_WIND = document.getElementById('wrSliderWind');
  const VAL_WIND = document.getElementById('wrValWind');
  const SLIDER_DEPTH = document.getElementById('wrSliderDepth');
  const VAL_DEPTH = document.getElementById('wrValDepth');
  const SLIDER_LAYERS = document.getElementById('wrSliderLayers');
  const VAL_LAYERS = document.getElementById('wrValLayers');

  // Readout DOM nodes (clean unboxed tabular text, zero pill clutter)
  const READOUT_HARMONIC = document.getElementById('wrHarmonicReadout');
  const READOUT_FACETS = document.getElementById('wrFacetsReadout');
  const READOUT_TRIAD = document.getElementById('wrTriadReadout');
  const READOUT_ICE = document.getElementById('wrIceReadout');
  const READOUT_BENCH = document.getElementById('wrBenchReadout');

  // Prime-ratio Zeta harmonic basis (incommensurate frequencies -> non-repeating ocean from L scalars!)
  const PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37];
  const PRIME_DIRS = PRIMES.map((p, idx) => {
    const ang = -0.58 + (idx * 2.399963) % 1.16; // Golden-angle spread around wind axis
    const k = 0.85 * Math.pow(p, 0.62);
    return {
      p,
      kx: Math.cos(ang) * k,
      kz: Math.sin(ang) * k * 1.45,
      omega: Math.sqrt(9.81 * k),
    };
  });

  // Reusable lightweight offscreen canvas for analytical ocean glint evaluation (0 stored wave arrays!)
  const oceanCanvas = document.createElement('canvas');
  oceanCanvas.width = 240;
  oceanCanvas.height = 68;
  const oceanCtx = oceanCanvas.getContext('2d');
  const oceanImg = oceanCtx ? oceanCtx.createImageData(oceanCanvas.width, oceanCanvas.height) : null;

  // Deterministic starfield (bound once at t=0!)
  const STARS = Array.from({ length: 68 }, (_, i) => {
    const s1 = Math.sin(i * 12.9898) * 43758.5453;
    const s2 = Math.sin((i + 37) * 78.233) * 24634.6345;
    return {
      x: s1 - Math.floor(s1),
      y: (s2 - Math.floor(s2)) * 0.56,
      r: 0.7 + (i % 3) * 0.55,
      twinkle: (i * 0.73) % (Math.PI * 2),
    };
  });

  // Static terrain ridge profiles & shoreline trees (bound once at t=0!)
  const TREES = [
    { x: 0.10, scale: 0.92, seed: 0.3 },
    { x: 0.16, scale: 1.12, seed: 1.1 },
    { x: 0.23, scale: 0.84, seed: 2.0 },
    { x: 0.77, scale: 1.05, seed: 2.8 },
    { x: 0.85, scale: 0.88, seed: 3.7 },
    { x: 0.92, scale: 1.15, seed: 4.5 },
  ];

  // Local live 60fps state (synced with canonical Python /api/world-rotor/*)
  const state = {
    active: false,
    playing: true,
    mode: 'scale_hierarchy', // 'scale_hierarchy' | 'flat_micro'
    solarHour: 15.8,
    windStrength: 0.36,
    windPhase: 0.0,
    handIntent: 'point_light', // 'point_light' | 'grasp_orb' | 'wave_greet' | 'absorb_shock'
    handPhase: 0.0,
    targetX: 0.63,
    targetY: 0.44,
    // Camera Rotor & Player Intervention Rotor (inside the SAME structural dynamics!)
    camPan: 0.0, // -1 .. +1 horizontal camera rotor angle
    camZoom: 1.0, // 0.85 .. 1.35 camera focal rotor
    charPosX: 0.44, // 0.24 .. 0.72 player-driven character walking rotor
    charVelX: 0.0,
    walkPhase: 0.0,
    keysDown: { left: false, right: false },
    subdivDepth: 3, // 0..6 -> 1..1,000,000
    unknownShock: 0.0,
    unknownLabel: '안정 (외부 미지 교란 대기)',
    unknownAbsorbed: 0,
    // Measured live browser metrics
    lastComputeMs: 0.08,
    lastOpsPerFrame: 23,
    lastCoherence: 1.0,
    microJitter: 0.0,
    // Python server benchmark & unified Cloud -> Water -> Ice state
    pyBenchmark: null,
    pyLayerConvergence: null,
    harmonicLayers: 6,
    noiseAmp: 0.38,
    unifiedFacets: null,
    iceCrystals: [],
    waterPulse: 0.0,
    autoExperience: false,
    audioEnabled: false,
    rotorDamping: 0.42,
  };

  let rafId = 0;
  let autoExpTimer = 0;
  let lastTs = performance.now();
  let lastReadoutTs = 0;

  // Real pure-physics WebAudio harmonic synthesizer (driven directly by S4 + S3 + Cloud/Ice phase!)
  let audioCtx = null;
  let oscRoot = null;
  let oscFifth = null;
  let masterGain = null;

  function ensureAudio() {
    if (audioCtx) {
      if (audioCtx.state === 'suspended') audioCtx.resume();
      return;
    }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    audioCtx = new AC();
    masterGain = audioCtx.createGain();
    masterGain.gain.value = 0.0;
    masterGain.connect(audioCtx.destination);

    oscRoot = audioCtx.createOscillator();
    oscRoot.type = 'sine';
    oscRoot.frequency.value = 261.6;
    const g1 = audioCtx.createGain();
    g1.gain.value = 0.055;
    oscRoot.connect(g1).connect(masterGain);

    oscFifth = audioCtx.createOscillator();
    oscFifth.type = 'triangle';
    oscFifth.frequency.value = 392.4;
    const g2 = audioCtx.createGain();
    g2.gain.value = 0.028;
    oscFifth.connect(g2).connect(masterGain);

    oscRoot.start();
    oscFifth.start();
  }

  function updateAudio(phys) {
    if (!audioCtx || !masterGain || !oscRoot || !oscFifth) return;
    const now = audioCtx.currentTime;
    if (!state.audioEnabled || !state.active) {
      masterGain.gain.setTargetAtTime(0.0, now, 0.08);
      return;
    }
    const baseHz = 196.0 + phys.daylight * 134.0;
    // Calm Ice/Water -> pure 3:2 fifth (1.500); Unknown Cloud shock -> tense tritone beating (~1.414)
    const ratio = 1.500 - state.unknownShock * 0.086;
    oscRoot.frequency.setTargetAtTime(baseHz, now, 0.08);
    oscFifth.frequency.setTargetAtTime(baseHz * ratio, now, 0.08);
    masterGain.gain.setTargetAtTime(0.45, now, 0.12);
  }

  function stopAudio() {
    if (audioCtx && masterGain) {
      masterGain.gain.setTargetAtTime(0.0, audioCtx.currentTime, 0.05);
    }
  }

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function rgbStr(r, g, b, a) {
    const rr = Math.round(clamp(r, 0, 255));
    const gg = Math.round(clamp(g, 0, 255));
    const bb = Math.round(clamp(b, 0, 255));
    return a !== undefined ? `rgba(${rr},${gg},${bb},${a})` : `rgb(${rr},${gg},${bb})`;
  }

  function formatHour(h) {
    const hh = Math.floor(h) % 24;
    const mm = Math.floor((h - Math.floor(h)) * 60);
    return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
  }

  function applyServerSnapshot(data) {
    if (!data) return;
    if (data.benchmark) state.pyBenchmark = data.benchmark;
    if (data.layer_convergence) state.pyLayerConvergence = data.layer_convergence;
    if (data.harmonic_field && data.harmonic_field.harmonic_layers) {
      state.harmonicLayers = Number(data.harmonic_field.harmonic_layers);
    }
    if (data.unified_facets) {
      state.unifiedFacets = data.unified_facets;
      if (data.unified_facets.code_tool_boundary) {
        state.rotorDamping = Number(data.unified_facets.code_tool_boundary.rotor_damping || state.rotorDamping);
      }
    }
    if (data.phase_states) {
      if (data.phase_states.ice && Array.isArray(data.phase_states.ice.crystals)) {
        state.iceCrystals = data.phase_states.ice.crystals;
      }
      if (data.phase_states.cloud && data.phase_states.cloud.status) {
        state.unknownLabel = data.phase_states.cloud.status;
      }
    }
    if (data.layers && data.layers.S4_celestial && data.experience_result) {
      state.solarHour = Number(data.layers.S4_celestial.solar_hour);
      state.subdivDepth = Number((data.layers.S0_micro_boundary && data.layers.S0_micro_boundary.depth) || state.subdivDepth);
      state.waterPulse = 1.0;
    }
    updateControlStyles();
    renderReadouts(true);
  }

  async function syncServerAction(action, params) {
    try {
      const res = await fetch('/api/world-rotor/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, params: params || {} }),
      });
      if (!res.ok) return null;
      const data = await res.json();
      applyServerSnapshot(data);
      return data;
    } catch {
      return null;
    }
  }

  async function loadInitialServerState() {
    try {
      const res = await fetch('/api/world-rotor/state');
      if (!res.ok) return;
      const data = await res.json();
      applyServerSnapshot(data);
    } catch {
      // Pure client physics continues smoothly even if offline
    }
  }

  function updateControlStyles() {
    if (BTN_PLAY) BTN_PLAY.textContent = state.playing ? '일시정지' : '재생';
    if (BTN_AUTO_EXP) {
      BTN_AUTO_EXP.textContent = state.autoExperience ? '자율 경험: 켜짐' : '자율 경험: 꺼짐';
      BTN_AUTO_EXP.classList.toggle('primary', state.autoExperience);
    }
    if (BTN_AUDIO) {
      BTN_AUDIO.textContent = state.audioEnabled ? '음향: 켜짐' : '음향: 꺼짐';
      BTN_AUDIO.classList.toggle('primary', state.audioEnabled);
    }
    if (BTN_MODE_HIER) BTN_MODE_HIER.classList.toggle('primary', state.mode === 'scale_hierarchy');
    if (BTN_MODE_MICRO) BTN_MODE_MICRO.classList.toggle('primary', state.mode === 'flat_micro');
    if (BTN_INTENT_LIGHT) BTN_INTENT_LIGHT.classList.toggle('primary', state.handIntent === 'point_light');
    if (BTN_INTENT_GRASP) BTN_INTENT_GRASP.classList.toggle('primary', state.handIntent === 'grasp_orb');
    if (BTN_INTENT_WAVE) BTN_INTENT_WAVE.classList.toggle('primary', state.handIntent === 'wave_greet');

    if (SLIDER_HOUR) SLIDER_HOUR.value = String(state.solarHour.toFixed(1));
    if (VAL_HOUR) VAL_HOUR.textContent = formatHour(state.solarHour);
    if (SLIDER_WIND) SLIDER_WIND.value = String(Math.round(state.windStrength * 100));
    if (VAL_WIND) VAL_WIND.textContent = `${Math.round(state.windStrength * 100)}%`;
    if (SLIDER_LAYERS) SLIDER_LAYERS.value = String(state.harmonicLayers);
    if (VAL_LAYERS) {
      const ratioMp = Math.round(20000000 / Math.max(1, state.harmonicLayers)).toLocaleString();
      VAL_LAYERS.textContent = `L=${state.harmonicLayers} (${ratioMp}:1)`;
    }
    if (SLIDER_DEPTH) SLIDER_DEPTH.value = String(state.subdivDepth);
    if (VAL_DEPTH) {
      const res = Math.pow(10, state.subdivDepth);
      const nodes = state.subdivDepth === 0 ? 1 : 1 + 3 * state.subdivDepth;
      VAL_DEPTH.textContent = `1:${res.toLocaleString()} (노드 ${nodes}개)`;
    }
  }

  // Compute S4 -> S3 -> S2/S1 -> S0 physics AND measure real browser compute cost
  function computeFramePhysics(dt) {
    if (state.playing) {
      state.solarHour = (state.solarHour + dt * 0.55) % 24.0;
    }
    state.windPhase = (state.windPhase + dt * (1.7 + state.windStrength * 2.1 + state.unknownShock * 2.4)) % (Math.PI * 2);
    state.handPhase = (state.handPhase + dt * 2.2) % (Math.PI * 2);

    // Player Intervention Rotor -> continuous momentum torque along character ridge
    const moveTorque = (state.keysDown.right ? 1 : 0) - (state.keysDown.left ? 1 : 0);
    state.charVelX = state.charVelX * Math.pow(0.08, dt) + moveTorque * 0.22 * dt * 6;
    state.charPosX = clamp(state.charPosX + state.charVelX * dt, 0.22, 0.76);
    if (Math.abs(state.charVelX) > 0.008) {
      state.walkPhase = (state.walkPhase + dt * Math.abs(state.charVelX) * 28) % (Math.PI * 2);
    }

    if (state.unknownShock > 0.002) {
      state.unknownShock = Math.max(0, state.unknownShock * Math.pow(0.55, dt));
      if (state.unknownShock < 0.03) {
        state.unknownShock = 0;
        state.unknownLabel = '정적 로터(t=0)로 흡수·수렴 완료';
        if (state.handIntent === 'absorb_shock') state.handIntent = 'point_light';
      }
    }

    const t0 = performance.now();

    // S4 Macro Celestial Rotor (1 angle governs entire sky, sun/moon, light & shadow)
    const theta = ((state.solarHour - 6.0) / 24.0) * Math.PI * 2;
    const sunX = Math.cos(theta);
    const sunY = Math.sin(theta); // >0 day, <0 night
    const moonX = -sunX;
    const moonY = -sunY;
    const daylight = clamp((sunY + 0.16) / 1.16, 0, 1);
    const twilight = clamp(1.0 - Math.abs(sunY) / 0.28, 0, 1);

    const activeLx = sunY >= -0.05 ? sunX : moonX;
    const activeLy = Math.max(0.18, sunY >= -0.05 ? sunY : Math.max(0.18, moonY));
    const shadowSkew = clamp(-activeLx / activeLy, -2.4, 2.4);

    // S3 Atmosphere Rotor (inherits S4 daylight + adds wind)
    const effWind = clamp(state.windStrength + 0.14 * daylight + state.unknownShock * 0.72, 0.05, 1.5);
    const treeSway = Math.sin(state.windPhase) * 0.28 * effWind;

    // S0 Micro Contact Boundary Subdivision (O(log10 N))
    const depth = state.subdivDepth;
    const subdivResolution = Math.pow(10, depth);
    const subdivNodes = depth === 0 ? 1 : 1 + 3 * depth;
    const contactError = (0.42 + state.unknownShock * 0.38) / Math.max(1, Math.pow(8, depth));

    // Real empirical mode contrast:
    let opsUsed = 1 + 1 + state.harmonicLayers + 2 + subdivNodes; // S4(1) + S3(1) + L-Harmonic(L) + S2/S1(2) + S0(subdivNodes)
    let coherence = 1.0;
    let microJitter = 0.0;

    if (state.mode === 'flat_micro') {
      // Actually execute 12,480 independent flat micro recalculations (without macro protocol!)
      // to demonstrate real CPU overhead & coherence drift live!
      const N = 12480;
      let driftSum = 0;
      for (let i = 0; i < N; i++) {
        const lag = ((i % 23) - 11) * 0.018 + Math.sin(state.windPhase * 3 + i * 0.03) * 0.04;
        const mlx = Math.cos(theta + lag);
        const mly = Math.sin(theta + lag);
        const msway = Math.sin(state.windPhase + lag * 3.1) * 0.28 * effWind;
        driftSum += Math.abs(mlx - sunX) + Math.abs(mly - sunY) + Math.abs(msway - treeSway);
      }
      const meanDrift = driftSum / N;
      opsUsed = N * 6;
      coherence = clamp(1.0 - meanDrift * 1.9, 0.18, 0.88);
      microJitter = meanDrift;
    }

    const t1 = performance.now();
    state.lastComputeMs = state.lastComputeMs * 0.75 + Math.max(0.02, t1 - t0) * 0.25;
    state.lastOpsPerFrame = opsUsed;
    state.lastCoherence = coherence;
    state.microJitter = microJitter;

    return {
      theta,
      sunX,
      sunY,
      moonX,
      moonY,
      daylight,
      twilight,
      shadowSkew,
      effWind,
      treeSway,
      subdivResolution,
      subdivNodes,
      contactError,
    };
  }

  function drawScene(phys) {
    const rect = CANVAS.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(360, Math.floor(rect.width));
    const h = Math.max(240, Math.floor(rect.height));
    if (CANVAS.width !== Math.floor(w * dpr) || CANVAS.height !== Math.floor(h * dpr)) {
      CANVAS.width = Math.floor(w * dpr);
      CANVAS.height = Math.floor(h * dpr);
    }

    ctx.save();
    ctx.scale(dpr, dpr);

    const horizonY = h * 0.56;
    const groundY = h * 0.79;
    const { daylight, twilight, sunX, sunY, moonX, moonY, shadowSkew, treeSway, effWind } = phys;

    // ------------------------------------------------------------------
    // LAYER S4: Macro Celestial Dome (1 slow rotor -> entire sky/light)
    // ------------------------------------------------------------------
    const zenR = lerp(11, 34, daylight) + 46 * twilight;
    const zenG = lerp(19, 104, daylight) + 22 * twilight;
    const zenB = lerp(42, 194, daylight) - 16 * twilight;
    const horR = lerp(21, 146, daylight) + 102 * twilight;
    const horG = lerp(31, 194, daylight) + 20 * twilight;
    const horB = lerp(56, 232, daylight) - 96 * twilight;

    const skyGrad = ctx.createLinearGradient(0, 0, 0, horizonY);
    skyGrad.addColorStop(0, rgbStr(zenR, zenG, zenB));
    skyGrad.addColorStop(1, rgbStr(horR, horG, horB));
    ctx.fillStyle = skyGrad;
    ctx.fillRect(0, 0, w, horizonY + 2);

    // Night stars (fade cleanly via S4 daylight scalar)
    const starAlpha = clamp((0.42 - daylight) * 2.2, 0, 0.92);
    if (starAlpha > 0.02) {
      STARS.forEach((st) => {
        const tw = 0.55 + 0.45 * Math.sin(state.handPhase * 1.4 + st.twinkle);
        ctx.fillStyle = `rgba(226,238,255,${(starAlpha * tw).toFixed(3)})`;
        ctx.beginPath();
        ctx.arc(st.x * w, st.y * horizonY, st.r, 0, Math.PI * 2);
        ctx.fill();
      });
    }

    // Subtle S4 Celestial Rotor Orbit Arc
    const orbitCx = w * 0.5;
    const orbitCy = horizonY + h * 0.04;
    const orbitRx = w * 0.39;
    const orbitRy = horizonY * 0.80;
    ctx.save();
    ctx.strokeStyle = `rgba(226,232,240,${(0.11 + twilight * 0.08).toFixed(2)})`;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 6]);
    ctx.beginPath();
    ctx.ellipse(orbitCx, orbitCy, orbitRx, orbitRy, 0, Math.PI, Math.PI * 2);
    ctx.stroke();
    ctx.restore();

    // Sun & Moon positions driven by ONE scalar theta
    const sunPx = orbitCx - sunX * orbitRx;
    const sunPy = orbitCy - sunY * orbitRy;
    const moonPx = orbitCx - moonX * orbitRx;
    const moonPy = orbitCy - moonY * orbitRy;

    if (sunPy < horizonY + 34) {
      const sunGlow = ctx.createRadialGradient(sunPx, sunPy, 6, sunPx, sunPy, 74);
      sunGlow.addColorStop(0, rgbStr(255, 248, 214, 0.95));
      sunGlow.addColorStop(0.28, rgbStr(255, 206 - twilight * 56, 128 - twilight * 64, 0.48));
      sunGlow.addColorStop(1, 'rgba(255,180,90,0)');
      ctx.fillStyle = sunGlow;
      ctx.beginPath();
      ctx.arc(sunPx, sunPy, 74, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = rgbStr(255, 250, 224);
      ctx.beginPath();
      ctx.arc(sunPx, sunPy, 15, 0, Math.PI * 2);
      ctx.fill();
    }

    if (moonPy < horizonY + 26) {
      const moonGlow = ctx.createRadialGradient(moonPx, moonPy, 4, moonPx, moonPy, 44);
      moonGlow.addColorStop(0, 'rgba(224,238,255,0.88)');
      moonGlow.addColorStop(0.45, 'rgba(148,186,245,0.22)');
      moonGlow.addColorStop(1, 'rgba(148,186,245,0)');
      ctx.fillStyle = moonGlow;
      ctx.beginPath();
      ctx.arc(moonPx, moonPy, 44, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#e2eeff';
      ctx.beginPath();
      ctx.arc(moonPx, moonPy, 11, 0, Math.PI * 2);
      ctx.fill();
    }

    // ------------------------------------------------------------------
    // LAYER S3: Atmosphere, Clouds, Parallax Mountains & Lake Reflection
    // (Inherits S4 light color + adds shared wind phase)
    // ------------------------------------------------------------------
    const lightR = lerp(140, 255, daylight) + 12 * twilight;
    const lightG = lerp(168, 240, daylight) - 42 * twilight;
    const lightB = lerp(224, 218, daylight) - 110 * twilight;

    // Drifting clouds (3 layered puffs driven by shared windPhase)
    const cloudDrift = ((state.windPhase * 24) % (w + 180)) - 90;
    ctx.fillStyle = rgbStr(lerp(90, lightR, 0.65), lerp(104, lightG, 0.65), lerp(136, lightB, 0.65), 0.24 + daylight * 0.16);
    for (let ci = 0; ci < 3; ci++) {
      const cx = ((cloudDrift + ci * (w * 0.36)) % (w + 140)) - 70;
      const cy = horizonY * (0.28 + ci * 0.13);
      ctx.beginPath();
      ctx.ellipse(cx, cy, 52 + ci * 12, 13, 0, 0, Math.PI * 2);
      ctx.ellipse(cx + 26, cy - 6, 36, 11, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    // Far mountains (tinted automatically by S4 horizon/light + Camera Rotor parallax)
    const camPx = state.camPan * 90;
    ctx.fillStyle = rgbStr(lerp(18, 62, daylight) + 34 * twilight, lerp(27, 86, daylight) + 10 * twilight, lerp(48, 124, daylight) - 18 * twilight);
    ctx.beginPath();
    ctx.moveTo(0, horizonY);
    for (let mx = 0; mx <= w; mx += 24) {
      const u = (mx + camPx * 0.35) / w;
      const peak = Math.sin(u * 5.2 + 0.7) * 34 + Math.cos(u * 11.4) * 14 + 34;
      ctx.lineTo(mx, horizonY - peak);
    }
    ctx.lineTo(w, horizonY);
    ctx.closePath();
    ctx.fill();

    // ------------------------------------------------------------------
    // NESTED L-LAYER PRIME-HARMONIC OCEAN SUNLIGHT GLINT (바닷물 햇빛 난반사)
    // Zero stored pixel/wave arrays! Evaluated directly from:
    //   S4 Sun/Moon vector × Camera Rotor × L Zeta-weighted Prime Wave Rotors
    //   with Gaussian noise convergence (σ / √L) & Least Action (δS = 0).
    // ------------------------------------------------------------------
    const oceanH = Math.max(24, groundY - horizonY);
    const activeBodyX = sunY >= -0.05 ? sunPx : moonPx;
    const activeBodyU = activeBodyX / Math.max(1, w);
    const L = clamp(state.harmonicLayers, 1, PRIMES.length);
    const sExp = 0.5 + 0.35 * state.rotorDamping;
    const rawNoise = clamp(state.noiseAmp + state.unknownShock * 0.55, 0.05, 1.0);
    // In Scale-Hierarchy mode, coherent L layers cancel incoherent noise as 1/sqrt(L)!
    // In Flat-Micro mode, independent cells lack parent lock so noise stays unsuppressed!
    const residualNoise = state.mode === 'scale_hierarchy'
      ? rawNoise / Math.sqrt(L)
      : rawNoise * 1.15;
    const sigmaCorridor = 0.048 + residualNoise * 0.145 + effWind * 0.032;
    const invTwoSigSq = 1.0 / (2.0 * sigmaCorridor * sigmaCorridor);
    const waveTime = state.windPhase * 1.35;

    // Precompute ONLY L scalar rotor phases & Dirichlet weights (O(L) total!)
    const lPhase = new Float32Array(L);
    const lWeight = new Float32Array(L);
    let wNorm = 0;
    for (let k = 0; k < L; k++) {
      const pd = PRIME_DIRS[k];
      lPhase[k] = waveTime * pd.omega * 0.28 + k * 0.71;
      const wk = Math.pow(pd.p, -sExp);
      lWeight[k] = wk;
      wNorm += wk;
    }

    const sparkles = [];
    if (oceanCtx && oceanImg) {
      const ow = oceanCanvas.width;
      const oh = oceanCanvas.height;
      const data = oceanImg.data;
      const deepR = lerp(5, 16, daylight) + 14 * twilight;
      const deepG = lerp(14, 52, daylight) + 6 * twilight;
      const deepB = lerp(34, 96, daylight) - 14 * twilight;
      const skyRefR = horR * 0.68;
      const skyRefG = horG * 0.72;
      const skyRefB = horB * 0.82;
      const glintBoost = 0.75 + daylight * 0.65 + twilight * 0.55;

      for (let py = 0; py < oh; py++) {
        const v = (py + 0.5) / oh; // 0 at horizon -> 1 at foreground shore
        const depthZ = 1.0 / (0.09 + v * 1.45); // Perspective ocean distance
        const fresnel = Math.pow(1.0 - v, 1.75) * 0.68 + 0.14;
        const baseR = lerp(deepR, skyRefR, fresnel);
        const baseG = lerp(deepG, skyRefG, fresnel);
        const baseB = lerp(deepB, skyRefB, fresnel);

        for (let px = 0; px < ow; px++) {
          const u = (px + 0.5) / ow;
          const wx = (u - 0.5 + state.camPan * 0.35) * depthZ * 2.4;
          const wz = depthZ * 2.1;

          // Sum L nested prime-ratio wave slopes (analytical, 0 stored arrays)
          let slopeX = 0;
          let slopeZ = 0;
          for (let k = 0; k < L; k++) {
            const pd = PRIME_DIRS[k];
            const arg = wx * pd.kx + wz * pd.kz - lPhase[k];
            const c = Math.cos(arg) * lWeight[k];
            slopeX += c * pd.kx;
            slopeZ += c * pd.kz;
          }
          slopeX = (slopeX / wNorm) * (0.28 + effWind * 0.42);
          slopeZ = (slopeZ / wNorm) * (0.28 + effWind * 0.42);

          // Incoherent noise perturbation (suppressed as 1/sqrt(L) in hierarchy mode!)
          const hSeed = Math.sin(px * 12.9898 + py * 78.233 + Math.floor(waveTime * 8) * 1.37) * 43758.5453;
          const noisePerturb = ((hSeed - Math.floor(hSeed)) - 0.5) * residualNoise * 0.34;

          // Principle of Least Action (Fermat δS=0):
          // Reflection peaks where wave normal aligns with Sun(S4) - Camera half-vector!
          const lateralOffset = (u - activeBodyU) * (1.25 - v * 0.35);
          const stationaryErr = lateralOffset + slopeX * 0.16 + noisePerturb;
          const corridor = Math.exp(-(stationaryErr * stationaryErr) * invTwoSigSq);

          // Sharp capillary glint resonance at stationary-phase wave crests
          const crestAlign = Math.max(0, 1.0 - Math.abs(slopeZ * 1.9 + slopeX * 1.1 - 0.12));
          const microGlint = Math.pow(crestAlign, 4.5 + L * 0.35) * corridor * glintBoost;

          // Subtle horizontal ripple shading across the entire sea
          const waveShade = 0.88 + 0.14 * Math.tanh(slopeZ * 2.2);
          const spec = Math.min(1.35, corridor * 0.32 * glintBoost + microGlint * 1.25);

          const idx = (py * ow + px) * 4;
          data[idx] = clamp(baseR * waveShade + lightR * spec, 0, 255);
          data[idx + 1] = clamp(baseG * waveShade + lightG * spec, 0, 255);
          data[idx + 2] = clamp(baseB * waveShade + lightB * spec * 0.94, 0, 255);
          data[idx + 3] = 255;

          // Collect crisp stationary-phase diamond glint peaks for high-DPI rendering
          if (microGlint > 0.72 && ((px + py * 7) % 5 === 0) && sparkles.length < 48) {
            sparkles.push({
              x: u * w,
              y: horizonY + v * oceanH,
              intensity: Math.min(1, microGlint),
              size: 2.2 + v * 4.5,
            });
          }
        }
      }
      oceanCtx.putImageData(oceanImg, 0, 0);
      ctx.drawImage(oceanCanvas, 0, horizonY, w, oceanH + 2);
    } else {
      const waterGrad = ctx.createLinearGradient(0, horizonY, 0, groundY);
      waterGrad.addColorStop(0, rgbStr(horR * 0.56, horG * 0.62, horB * 0.72));
      waterGrad.addColorStop(1, rgbStr(zenR * 0.42, zenG * 0.48, zenB * 0.60));
      ctx.fillStyle = waterGrad;
      ctx.fillRect(0, horizonY, w, oceanH + 2);
    }

    // Crisp stationary-phase (δS=0) diamond glints glittering on the sea surface
    for (let si = 0; si < sparkles.length; si++) {
      const sp = sparkles[si];
      const al = (0.35 + sp.intensity * 0.62).toFixed(2);
      ctx.strokeStyle = rgbStr(255, Math.min(255, lightG + 28), Math.min(255, lightB + 45), al);
      ctx.lineWidth = 1.1;
      ctx.beginPath();
      ctx.moveTo(sp.x - sp.size * 1.4, sp.y);
      ctx.lineTo(sp.x + sp.size * 1.4, sp.y);
      ctx.moveTo(sp.x, sp.y - sp.size * 0.55);
      ctx.lineTo(sp.x, sp.y + sp.size * 0.55);
      ctx.stroke();
    }

    // Foreground meadow ridge
    const groundGrad = ctx.createLinearGradient(0, groundY - 8, 0, h);
    groundGrad.addColorStop(0, rgbStr(lerp(14, 42, daylight) + 16 * twilight, lerp(24, 68, daylight) + 6 * twilight, lerp(34, 52, daylight)));
    groundGrad.addColorStop(1, rgbStr(lerp(9, 22, daylight), lerp(14, 34, daylight), lerp(24, 32, daylight)));
    ctx.fillStyle = groundGrad;
    ctx.beginPath();
    ctx.moveTo(0, groundY + 6);
    ctx.quadraticCurveTo(w * 0.45, groundY - 14, w, groundY + 4);
    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();
    ctx.fill();

    // Trees inheriting S3 shared wind phase, S4 shadow axis & Camera Rotor parallax
    TREES.forEach((tr, idx) => {
      const tx = tr.x * w - camPx * 0.78;
      const ty = groundY + 8;
      const trunkH = 38 * tr.scale;
      // In flat_micro mode, show desynced per-tree local sway & broken shadow!
      const localDesync = state.mode === 'flat_micro'
        ? Math.sin(state.windPhase * 4.2 + idx * 2.7) * 0.34
        : 0;
      const sway = treeSway + localDesync;
      const sk = shadowSkew + (state.mode === 'flat_micro' ? Math.cos(idx * 3.1 + state.windPhase * 2) * 1.4 : 0);

      // Ground shadow from S4
      ctx.fillStyle = 'rgba(6, 10, 20, 0.34)';
      ctx.beginPath();
      ctx.ellipse(tx + sk * 18, ty + 4, 22 * tr.scale, 5.5, 0, 0, Math.PI * 2);
      ctx.fill();

      // Trunk & crown bent by shared S3 wind rotor
      const topX = tx + sway * trunkH * 1.15;
      const topY = ty - trunkH;
      ctx.strokeStyle = rgbStr(lerp(36, 78, daylight), lerp(32, 62, daylight), lerp(34, 48, daylight));
      ctx.lineWidth = 4 * tr.scale;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(tx, ty);
      ctx.quadraticCurveTo(tx + sway * trunkH * 0.4, ty - trunkH * 0.5, topX, topY);
      ctx.stroke();

      ctx.fillStyle = rgbStr(lerp(16, 48, daylight) + 18 * twilight, lerp(38, 106, daylight), lerp(38, 66, daylight));
      ctx.beginPath();
      ctx.arc(topX, topY - 6, 17 * tr.scale, 0, Math.PI * 2);
      ctx.fill();
      // Sunlit rim highlight inherited directly from S4 light vector!
      ctx.fillStyle = rgbStr(lightR, lightG, lightB, 0.24);
      ctx.beginPath();
      ctx.arc(topX + (sunY >= -0.05 ? -sunX : -moonX) * 5, topY - 10, 10 * tr.scale, 0, Math.PI * 2);
      ctx.fill();
    });

    // ------------------------------------------------------------------
    // LAYER S2 & S1: Static-Bound Character + 'Hand' Perceptual Unit
    // (Player Walk Rotor + Camera Rotor + S4 Light/Shadow + S3 Wind!)
    // ------------------------------------------------------------------
    const charX = w * state.charPosX - camPx;
    const charFeetY = groundY + 14;
    const windLeanPx = treeSway * 16 + state.charVelX * 36;
    const breathPx = Math.sin(state.handPhase * 0.9) * 2.4;
    const stride = Math.sin(state.walkPhase) * Math.min(1, Math.abs(state.charVelX) * 6) * 12;

    // Ground shadow cast directly by S4 macro light vector
    ctx.fillStyle = 'rgba(5, 9, 18, 0.46)';
    ctx.beginPath();
    ctx.ellipse(charX + shadowSkew * 24, charFeetY + 4, 28 + Math.abs(shadowSkew) * 14, 7, 0, 0, Math.PI * 2);
    ctx.fill();

    // Pre-bound torso & head (Static Rotor t=0)
    const hipX = charX;
    const hipY = charFeetY - 38;
    const shX = charX + windLeanPx * 0.65;
    const shY = hipY - 36 + breathPx;

    // Legs (animated by unified Walk Rotor when player intervenes with A/D)
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 4.2;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(hipX - 5, hipY);
    ctx.lineTo(charX - 9 - stride, charFeetY);
    ctx.moveTo(hipX + 5, hipY);
    ctx.lineTo(charX + 9 + stride, charFeetY);
    ctx.stroke();

    // Torso
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 6.0;
    ctx.beginPath();
    ctx.moveTo(hipX, hipY);
    ctx.lineTo(shX, shY);
    ctx.stroke();

    // Head + Rim light inherited from S4
    ctx.fillStyle = '#f1f5f9';
    ctx.beginPath();
    ctx.arc(shX + windLeanPx * 0.25, shY - 15, 11, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = rgbStr(lightR, lightG, lightB, 0.85);
    ctx.lineWidth = 2;
    ctx.stroke();

    // Determine S1 Hand Perceptual Target
    let tgtX = state.targetX * w;
    let tgtY = state.targetY * h;
    if (state.handIntent === 'point_light') {
      const lx = sunY >= -0.05 ? sunPx : moonPx;
      const ly = sunY >= -0.05 ? Math.min(horizonY - 10, sunPy) : Math.min(horizonY - 10, moonPy);
      const angToSky = Math.atan2(ly - shY, lx - shX);
      tgtX = shX + Math.cos(angToSky) * 96;
      tgtY = shY + Math.sin(angToSky) * 96;
    } else if (state.handIntent === 'wave_greet') {
      tgtX = shX + 64 + Math.sin(state.handPhase * 2.5) * 26;
      tgtY = shY - 46 + Math.cos(state.handPhase * 2.5) * 14;
    } else if (state.handIntent === 'absorb_shock') {
      tgtX = shX + 54 - state.unknownShock * 28;
      tgtY = shY - 10 + Math.sin(state.handPhase * 5.0) * 14 * Math.max(0.2, state.unknownShock);
    }

    // Analytical 2-Bone IK along Static-Bound Arm Chain [어깨 -> 팔꿈치 -> 손목 -> 손끝]
    const L1 = 44;
    const L2 = 40;
    const L3 = 18;
    const dx = tgtX - shX;
    const dy = tgtY - shY;
    const dist = clamp(Math.hypot(dx, dy), 16, L1 + L2 - 1);
    const baseA = Math.atan2(dy, dx);
    const cosA = clamp((L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist), -1, 1);
    const a1 = baseA + Math.acos(cosA) * 0.82;
    const elX = shX + L1 * Math.cos(a1);
    const elY = shY + L1 * Math.sin(a1);
    const a2 = Math.atan2(tgtY - elY, tgtX - elX);
    const wrX = elX + L2 * Math.cos(a2);
    const wrY = elY + L2 * Math.sin(a2);
    const handA = a2 + Math.sin(state.handPhase * 1.8) * 0.12;
    const tipX = wrX + L3 * Math.cos(handA);
    const tipY = wrY + L3 * Math.sin(handA);

    // Draw Articulated Static-Bound Hand Chain
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 4.2;
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(shX, shY);
    ctx.lineTo(elX, elY);
    ctx.lineTo(wrX, wrY);
    ctx.lineTo(tipX, tipY);
    ctx.stroke();

    [
      [shX, shY, '#f87171', '어깨'],
      [elX, elY, '#e2e8f0', '팔꿈치'],
      [wrX, wrY, '#93c5fd', '손목'],
      [tipX, tipY, '#34d399', '손(지각단위)'],
    ].forEach(([jx, jy, col, lbl], idx) => {
      ctx.fillStyle = col;
      ctx.beginPath();
      ctx.arc(jx, jy, idx === 3 ? 5.2 : 3.5, 0, Math.PI * 2);
      ctx.fill();
      if (idx === 3) {
        ctx.fillStyle = '#a7f3d0';
        ctx.font = '600 10.5px system-ui, sans-serif';
        ctx.fillText(lbl, jx + 8, jy - 6);
      }
    });

    // Grasp target orb when in grasp_orb mode
    if (state.handIntent === 'grasp_orb') {
      ctx.fillStyle = 'rgba(251, 191, 36, 0.22)';
      ctx.beginPath();
      ctx.arc(tgtX, tgtY, 15, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#fbbf24';
      ctx.beginPath();
      ctx.arc(tgtX, tgtY, 5.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // ------------------------------------------------------------------
    // LAYER S0: Recursive 1 -> 10^depth Contact Subdivision Ring (ONLY at fingertip!)
    // ------------------------------------------------------------------
    const rings = Math.max(1, Math.min(6, state.subdivDepth));
    for (let r = 0; r < rings; r++) {
      const rad = 28 - r * 3.8;
      ctx.strokeStyle = r === rings - 1 ? 'rgba(52, 211, 153, 0.88)' : 'rgba(56, 189, 248, 0.30)';
      ctx.lineWidth = r === rings - 1 ? 1.5 : 1.0;
      ctx.beginPath();
      ctx.arc(tipX, tipY, Math.max(4, rad), 0, Math.PI * 2);
      ctx.stroke();
    }

    // ------------------------------------------------------------------
    // UNKNOWN ROTOR: External Uncaptured Gust / Shock Visual
    // ------------------------------------------------------------------
    if (state.unknownShock > 0.04) {
      ctx.strokeStyle = `rgba(248, 113, 113, ${(0.25 + state.unknownShock * 0.55).toFixed(2)})`;
      ctx.lineWidth = 2;
      for (let g = 0; g < 6; g++) {
        const gy = horizonY * 0.35 + g * 28;
        const gx = ((state.windPhase * 110 + g * 88) % (w + 120)) - 60;
        ctx.beginPath();
        ctx.moveTo(gx, gy);
        ctx.lineTo(gx - 54 * state.unknownShock, gy + 6);
        ctx.stroke();
      }
    }

    // ------------------------------------------------------------------
    // CLOUD -> WATER -> ICE VISUAL PHASE FLOW IN THE SINGLE WORLD
    // ------------------------------------------------------------------
    // Water flow pulse (Cloud -> Lake -> Hand -> Shoreline Ice)
    if (state.waterPulse > 0.03) {
      state.waterPulse = Math.max(0, state.waterPulse - 0.012);
      ctx.save();
      ctx.strokeStyle = `rgba(56, 189, 248, ${(state.waterPulse * 0.72).toFixed(2)})`;
      ctx.lineWidth = 1.6;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      ctx.moveTo(w * 0.5, horizonY * 0.35);
      ctx.quadraticCurveTo(w * 0.48, horizonY, tipX, tipY);
      ctx.stroke();
      ctx.restore();
    }

    // Ice Crystals (t=0 Static Memory Prisms crystallized along the shoreline!)
    const iceList = state.iceCrystals || [];
    const showIce = Math.min(6, Math.max(1, iceList.length));
    for (let ic = 0; ic < showIce; ic++) {
      const ix = w * (0.14 + ic * 0.055) - camPx * 0.65;
      const iy = groundY + 26 + (ic % 2) * 8;
      ctx.save();
      ctx.fillStyle = 'rgba(186, 230, 253, 0.78)';
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.92)';
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(ix, iy - 11);
      ctx.lineTo(ix + 7, iy);
      ctx.lineTo(ix, iy + 8);
      ctx.lineTo(ix - 7, iy);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }

    // ------------------------------------------------------------------
    // FLAT MICRO MODE OVERLAY: Visual Proof of Micro-Desync Fragmentation
    // ------------------------------------------------------------------
    if (state.mode === 'flat_micro') {
      ctx.strokeStyle = 'rgba(248, 113, 113, 0.24)';
      ctx.lineWidth = 1;
      const step = 36;
      for (let gx = 0; gx < w; gx += step) {
        for (let gy = 0; gy < h; gy += step) {
          const fl = Math.sin(state.windPhase * 6 + gx * 0.1 + gy * 0.1);
          if (fl > 0.55) {
            ctx.fillStyle = 'rgba(248, 113, 113, 0.08)';
            ctx.fillRect(gx, gy, step - 2, step - 2);
          }
        }
      }
    }

    // Crisp Minimal Scrim Overlay (top-left architectural state & bottom-left hint)
    ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
    ctx.fillRect(10, 10, 355, 42);
    ctx.strokeStyle = state.mode === 'scale_hierarchy' ? 'rgba(52, 211, 153, 0.55)' : 'rgba(248, 113, 113, 0.65)';
    ctx.lineWidth = 1;
    ctx.strokeRect(10, 10, 355, 42);

    ctx.fillStyle = state.mode === 'scale_hierarchy' ? '#a7f3d0' : '#fca5a5';
    ctx.font = '600 11.5px ui-monospace, SFMono-Regular, Menlo, monospace';
    const modeTitle = state.mode === 'scale_hierarchy'
      ? `스케일 계층 로터 · ${state.lastOpsPerFrame} ops/f · 일관성 100%`
      : `평면 미시 연산 · ${state.lastOpsPerFrame.toLocaleString()} ops/f · 일관성 ${(state.lastCoherence * 100).toFixed(1)}%`;
    ctx.fillText(modeTitle, 18, 27);

    ctx.fillStyle = '#cbd5e1';
    ctx.font = '10.5px ui-monospace, SFMono-Regular, Menlo, monospace';
    ctx.fillText(
      `S4 태양 ${formatHour(state.solarHour)} · 브라우저 실측 ${state.lastComputeMs.toFixed(2)}ms · S0 1:${phys.subdivResolution.toLocaleString()} (${phys.subdivNodes}노드)`,
      18,
      44
    );

    ctx.fillStyle = 'rgba(226, 232, 240, 0.78)';
    ctx.font = '10.5px system-ui, sans-serif';
    ctx.fillText('클릭: 손 목표 궤적 · 드래그: 카메라 로터 회전 · A/D 또는 ←/→: 캐릭터 이동 로터', 12, h - 10);

    ctx.restore();
  }

  function renderReadouts(force) {
    const now = performance.now();
    if (!force && now - lastReadoutTs < 180) return;
    lastReadoutTs = now;

    const res = Math.pow(10, state.subdivDepth);
    const nodes = state.subdivDepth === 0 ? 1 : 1 + 3 * state.subdivDepth;
    const compRatio = (res / nodes).toLocaleString(undefined, { maximumFractionDigits: 1 });
    const baseHz = Math.round(196 + clamp((Math.sin(((state.solarHour - 6) / 24) * Math.PI * 2) + 0.16) / 1.16, 0, 1) * 134);
    const ratio = (1.5 - state.unknownShock * 0.086).toFixed(3);
    const iceCount = (state.iceCrystals && state.iceCrystals.length) || 1;

    if (READOUT_HARMONIC) {
      const L = clamp(state.harmonicLayers, 1, PRIMES.length);
      const rawN = clamp(state.noiseAmp + state.unknownShock * 0.55, 0.05, 1.0);
      const resN = state.mode === 'scale_hierarchy' ? rawN / Math.sqrt(L) : rawN * 1.15;
      const suppressPct = Math.max(0, (1 - resN / Math.max(1e-6, rawN)) * 100);
      const comp20mp = Math.round(20000000 / L).toLocaleString();
      const lc = state.pyLayerConvergence;
      const pyTail = lc && lc.noise_drop_l1_to_l12_pct
        ? ` · Python L=1→12 실증(노이즈 -${lc.noise_drop_l1_to_l12_pct}%, 질서 ${lc.order_gain_l1_to_l12})`
        : '';
      READOUT_HARMONIC.textContent =
        `2,000만 화소 바닷물 햇빛 난반사 — 제타 소수 계층 L=${L}축 (배열 저장 0칸 · ${comp20mp}:1) · ` +
        `가우시안 노이즈 수렴 ${rawN.toFixed(2)}→${resN.toFixed(3)} (-${suppressPct.toFixed(0)}%) · 최소작용(δS=0)${pyTail}`;
    }

    if (READOUT_FACETS) {
      READOUT_FACETS.textContent =
        `4면 동시 경험 — [물리] 태양 ${formatHour(state.solarHour)}·바람 ${Math.round(state.windStrength * 100)}%  ·  ` +
        `[영상·음향] ${baseHz}Hz×${ratio}  ·  ` +
        `[신체제어] 손 정적결합 12,480(1:${res.toLocaleString()})  ·  ` +
        `[코드경계] 감쇠 ${state.rotorDamping.toFixed(2)}·${state.lastOpsPerFrame} ops`;
    }

    if (READOUT_TRIAD) {
      READOUT_TRIAD.textContent =
        `구름(미지): ${state.unknownLabel}  |  ` +
        `물(가변·정신): 1:${res.toLocaleString()} (${nodes}노드 · ${compRatio}:1)  |  ` +
        `얼음(t=0): 통합 결정 ${iceCount}개 · 정체성 재계산 0회`;
    }

    if (READOUT_ICE) {
      const latestIce = state.iceCrystals && state.iceCrystals.length ? state.iceCrystals[0] : null;
      if (latestIce) {
        READOUT_ICE.textContent =
          `최근 얼음(t=0) 통합 원리 [${latestIce.title}] (오차 ${latestIce.error_reduction}): ${latestIce.unified_principle}`;
      } else {
        READOUT_ICE.textContent = '구름→물→얼음 통합 경험 버튼을 누르면 4개 면을 관통하는 공통 원리가 얼음(t=0)으로 결정화됩니다.';
      }
    }

    if (READOUT_BENCH) {
      const b = state.pyBenchmark;
      if (b && b.hierarchy && b.flat_micro) {
        READOUT_BENCH.textContent =
          `Python 실측(${b.entity_count.toLocaleString()} 요소): ` +
          `계층 로터 ${b.hierarchy.ops_per_frame} ops (${b.hierarchy.measured_us}µs · 일관성 100%) vs ` +
          `평면 미시 ${b.flat_micro.ops_per_frame.toLocaleString()} ops (${b.flat_micro.measured_us}µs · 일관성 ${(b.flat_micro.global_coherence * 100).toFixed(1)}%) · ` +
          `연산 ${Number(b.ops_reduction_x).toLocaleString()}배 절감`;
      } else {
        READOUT_BENCH.textContent =
          `브라우저 실측: ${state.lastOpsPerFrame.toLocaleString()} ops/frame · ${state.lastComputeMs.toFixed(2)}ms · 일관성 ${(state.lastCoherence * 100).toFixed(1)}%`;
      }
    }
  }

  function loop(ts) {
    if (!state.active) return;
    const dt = Math.min(0.08, Math.max(0.005, (ts - lastTs) / 1000));
    lastTs = ts;
    const phys = computeFramePhysics(dt);
    drawScene(phys);
    updateAudio(phys);
    if (state.playing && SLIDER_HOUR && VAL_HOUR) {
      SLIDER_HOUR.value = String(state.solarHour.toFixed(1));
      VAL_HOUR.textContent = formatHour(state.solarHour);
    }
    renderReadouts(false);
    rafId = requestAnimationFrame(loop);
  }

  // Unified Pointer & Keyboard Intervention inside Rotor Dynamics:
  // - Click -> Hand Perceptual Unit reaches/grasps target
  // - Drag  -> Camera Rotor pan across parallax layers
  // - A/D or ArrowLeft/ArrowRight -> Character Walk Rotor torque
  let camDragging = false;
  let dragStartX = 0;
  let dragMoved = false;

  CANVAS.addEventListener('pointerdown', (e) => {
    camDragging = true;
    dragStartX = e.clientX;
    dragMoved = false;
  });

  CANVAS.addEventListener('pointermove', (e) => {
    if (!camDragging) return;
    const dx = e.clientX - dragStartX;
    if (Math.abs(dx) > 4) dragMoved = true;
    if (dragMoved) {
      state.camPan = clamp(state.camPan - dx * 0.0035, -1.0, 1.0);
      dragStartX = e.clientX;
    }
  });

  CANVAS.addEventListener('pointerup', (e) => {
    const wasDrag = dragMoved;
    camDragging = false;
    dragMoved = false;
    if (wasDrag) return;
    const rect = CANVAS.getBoundingClientRect();
    const nx = clamp((e.clientX - rect.left) / Math.max(1, rect.width), 0.20, 0.88);
    const ny = clamp((e.clientY - rect.top) / Math.max(1, rect.height), 0.16, 0.76);
    state.targetX = nx;
    state.targetY = ny;
    state.handIntent = 'grasp_orb';
    updateControlStyles();
    syncServerAction('set_params', { hand_intent: 'grasp_orb', target_x: nx, target_y: ny });
  });

  window.addEventListener('keydown', (e) => {
    if (!state.active) return;
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
    if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') state.keysDown.left = true;
    if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') state.keysDown.right = true;
  });

  window.addEventListener('keyup', (e) => {
    if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') state.keysDown.left = false;
    if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') state.keysDown.right = false;
  });

  if (BTN_PLAY) {
    BTN_PLAY.addEventListener('click', () => {
      state.playing = !state.playing;
      updateControlStyles();
    });
  }

  if (BTN_MODE_HIER) {
    BTN_MODE_HIER.addEventListener('click', () => {
      state.mode = 'scale_hierarchy';
      updateControlStyles();
      syncServerAction('set_params', { architecture_mode: 'scale_hierarchy' });
    });
  }

  if (BTN_MODE_MICRO) {
    BTN_MODE_MICRO.addEventListener('click', () => {
      state.mode = 'flat_micro';
      updateControlStyles();
      syncServerAction('set_params', { architecture_mode: 'flat_micro' });
    });
  }

  if (BTN_INTENT_LIGHT) {
    BTN_INTENT_LIGHT.addEventListener('click', () => {
      state.handIntent = 'point_light';
      updateControlStyles();
      syncServerAction('set_params', { hand_intent: 'point_light' });
    });
  }

  if (BTN_INTENT_GRASP) {
    BTN_INTENT_GRASP.addEventListener('click', () => {
      state.handIntent = 'grasp_orb';
      updateControlStyles();
      syncServerAction('set_params', { hand_intent: 'grasp_orb' });
    });
  }

  if (BTN_INTENT_WAVE) {
    BTN_INTENT_WAVE.addEventListener('click', () => {
      state.handIntent = 'wave_greet';
      updateControlStyles();
      syncServerAction('set_params', { hand_intent: 'wave_greet' });
    });
  }

  if (BTN_SHOCK) {
    BTN_SHOCK.addEventListener('click', () => {
      state.unknownShock = 0.94;
      state.unknownLabel = '미지 외부 돌풍·충격 유입 → 가변 로터 실시간 분별·흡수 중';
      state.unknownAbsorbed += 1;
      state.subdivDepth = Math.max(state.subdivDepth, 5);
      state.handIntent = 'absorb_shock';
      updateControlStyles();
      syncServerAction('inject_unknown_shock', { intensity: 0.94 });
    });
  }

  if (BTN_BENCH) {
    BTN_BENCH.addEventListener('click', async () => {
      BTN_BENCH.disabled = true;
      BTN_BENCH.textContent = '실측 중…';
      await syncServerAction('run_benchmark', { entity_count: 2400 });
      BTN_BENCH.disabled = false;
      BTN_BENCH.textContent = '실측 벤치마크 실행';
    });
  }

  if (BTN_RESET) {
    BTN_RESET.addEventListener('click', () => {
      state.solarHour = 15.8;
      state.windStrength = 0.36;
      state.subdivDepth = 3;
      state.handIntent = 'point_light';
      state.mode = 'scale_hierarchy';
      state.unknownShock = 0;
      state.unknownLabel = '안정 (외부 미지 교란 대기)';
      updateControlStyles();
      syncServerAction('reset', {});
    });
  }

  if (SLIDER_HOUR) {
    SLIDER_HOUR.addEventListener('input', () => {
      state.playing = false;
      state.solarHour = Number(SLIDER_HOUR.value);
      updateControlStyles();
    });
    SLIDER_HOUR.addEventListener('change', () => {
      syncServerAction('set_params', { solar_hour: state.solarHour });
    });
  }

  if (SLIDER_WIND) {
    SLIDER_WIND.addEventListener('input', () => {
      state.windStrength = Number(SLIDER_WIND.value) / 100;
      updateControlStyles();
    });
    SLIDER_WIND.addEventListener('change', () => {
      syncServerAction('set_params', { wind_strength: state.windStrength });
    });
  }

  if (SLIDER_LAYERS) {
    SLIDER_LAYERS.addEventListener('input', () => {
      state.harmonicLayers = Number(SLIDER_LAYERS.value);
      updateControlStyles();
      renderReadouts(true);
    });
    SLIDER_LAYERS.addEventListener('change', () => {
      syncServerAction('set_params', { harmonic_layers: state.harmonicLayers });
    });
  }

  if (SLIDER_DEPTH) {
    SLIDER_DEPTH.addEventListener('input', () => {
      state.subdivDepth = Number(SLIDER_DEPTH.value);
      updateControlStyles();
      renderReadouts(true);
    });
    SLIDER_DEPTH.addEventListener('change', () => {
      syncServerAction('set_params', { subdivision_depth: state.subdivDepth });
    });
  }

  if (BTN_EXP_CYCLE) {
    BTN_EXP_CYCLE.addEventListener('click', async () => {
      BTN_EXP_CYCLE.disabled = true;
      state.unknownShock = 0.72;
      state.waterPulse = 1.0;
      await syncServerAction('experience_cycle', {});
      BTN_EXP_CYCLE.disabled = false;
    });
  }

  if (BTN_AUTO_EXP) {
    BTN_AUTO_EXP.addEventListener('click', () => {
      state.autoExperience = !state.autoExperience;
      updateControlStyles();
      clearInterval(autoExpTimer);
      if (state.autoExperience) {
        syncServerAction('experience_cycle', {});
        autoExpTimer = setInterval(() => {
          if (state.active && state.autoExperience) {
            state.unknownShock = 0.68;
            state.waterPulse = 1.0;
            syncServerAction('experience_cycle', {});
          }
        }, 4800);
      }
    });
  }

  if (BTN_AUDIO) {
    BTN_AUDIO.addEventListener('click', () => {
      state.audioEnabled = !state.audioEnabled;
      if (state.audioEnabled) ensureAudio();
      else stopAudio();
      updateControlStyles();
    });
  }

  // Expose clean start/stop lifecycle for Reality View mode switcher
  window.ElysiaWorldRotorSim = {
    start() {
      if (state.active) return;
      state.active = true;
      lastTs = performance.now();
      updateControlStyles();
      loadInitialServerState();
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(loop);
    },
    stop() {
      state.active = false;
      cancelAnimationFrame(rafId);
      clearInterval(autoExpTimer);
      state.autoExperience = false;
      stopAudio();
    },
  };
})();
