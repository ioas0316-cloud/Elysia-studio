/**
 * Elysia Unified Causal Dataflow Viewport (통합 인과 데이터플로우 엔진)
 * =====================================================================
 * Zero literal gear/paint-jar cartoons. Every visual, acoustic, and compute
 * element on screen is driven directly by ONE unified multi-scale causal tensor
 * computed on the L1 Python backend (/api/scale-rotor/unified-dataflow):
 *
 *   1. Code -> Branchless Transistor Circuit (Python AST if/else -> sigmoid gates)
 *   2. Multi-Scale Gear-Ratio Compute Optimization (S0 8x8 -> S1 16x16 -> S2 32x32)
 *   3. Real-Time rFFT Audio Harmonic Condensation -> Live Web Audio Synth
 *   4. Closed-Loop Perceptual Eye -> Auto-tunes steepness & gear wake threshold
 *
 * Follows Three.js studio PBR + software-WebGL pacing + zero-GC render loop.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const GRID_N = 32;
const GRID_CELLS = GRID_N * GRID_N; // 1024
const SPLAT_MULTIPLIER = 4;
const TOTAL_SPLATS = GRID_CELLS * SPLAT_MULTIPLIER; // 4096 volumetric Gaussians
const WAVE_RING_PTS = 128;

// Pre-allocated scratch math objects (zero per-frame GC)
const _tmpVecA = new THREE.Vector3();
const _tmpVecB = new THREE.Vector3();
const _tmpColor = new THREE.Color();

function detectSoftwareWebGL() {
  try {
    const probe = document.createElement('canvas');
    const gl = probe.getContext('webgl2') || probe.getContext('webgl');
    if (!gl) return true;
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    const param = ext ? ext.UNMASKED_RENDERER_WEBGL : gl.RENDERER;
    const gpu = String(gl.getParameter(param) || '');
    gl.getExtension('WEBGL_lose_context')?.loseContext();
    return /SwiftShader|llvmpipe|softpipe|Software|Basic Render/i.test(gpu);
  } catch {
    return true;
  }
}

/**
 * Procedural Polyphonic Web Audio Harmonic Synthesizer
 * Synthesizes sound strictly from the condensed rFFT harmonic seeds returned
 * by the Python Unified Dataflow Engine (zero external MP3/audio files).
 */
class HarmonicAudioBridge {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.filter = null;
    this.voices = [];
    this.enabled = false;
    this.latestSeeds = [];
  }

  toggle() {
    if (this.enabled) {
      this.stop();
      return false;
    }
    this.start();
    return true;
  }

  start() {
    if (this.enabled) return;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;

    if (!this.ctx) {
      this.ctx = new AudioCtx();
      this.filter = this.ctx.createBiquadFilter();
      this.filter.type = 'lowpass';
      this.filter.frequency.value = 1800;
      this.filter.Q.value = 1.4;

      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.value = 0.0001;

      this.filter.connect(this.masterGain);
      this.masterGain.connect(this.ctx.destination);
    }

    if (this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
    this.enabled = true;
    const now = this.ctx.currentTime;
    this.masterGain.gain.cancelScheduledValues(now);
    this.masterGain.gain.setTargetAtTime(0.14, now, 0.12);

    if (this.latestSeeds.length > 0) {
      this.applyHarmonics(this.latestSeeds, 0.5);
    }
  }

  stop() {
    this.enabled = false;
    if (!this.ctx || !this.masterGain) return;
    const now = this.ctx.currentTime;
    this.masterGain.gain.cancelScheduledValues(now);
    this.masterGain.gain.setTargetAtTime(0.0001, now, 0.08);
    window.setTimeout(() => {
      if (!this.enabled) this._clearVoices();
    }, 350);
  }

  _clearVoices() {
    for (const v of this.voices) {
      try {
        v.osc.stop();
        v.osc.disconnect();
        v.gain.disconnect();
      } catch {
        // Ignore already stopped oscillators
      }
    }
    this.voices = [];
  }

  applyHarmonics(seeds, brightnessNorm = 0.5) {
    this.latestSeeds = Array.isArray(seeds) ? seeds : [];
    if (!this.enabled || !this.ctx || !this.filter) return;

    const now = this.ctx.currentTime;
    const targetCutoff = 700 + Math.max(0, Math.min(1, brightnessNorm)) * 2400;
    this.filter.frequency.setTargetAtTime(targetCutoff, now, 0.14);

    const count = Math.min(8, this.latestSeeds.length);
    // Ensure voice pool matches harmonic seed count
    while (this.voices.length < count) {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = this.voices.length % 2 === 0 ? 'sine' : 'triangle';
      osc.frequency.value = 174;
      gain.gain.value = 0.0001;
      osc.connect(gain);
      gain.connect(this.filter);
      osc.start();
      this.voices.push({ osc, gain });
    }

    const normScale = count > 0 ? 0.55 / Math.sqrt(count) : 0.1;
    for (let i = 0; i < this.voices.length; i++) {
      const voice = this.voices[i];
      if (i < count) {
        const seed = this.latestSeeds[i];
        const freq = Math.max(55, Math.min(1800, Number(seed.freq_hz) || 174));
        const amp = Math.max(0.01, Math.min(1.0, Number(seed.amplitude) || 0.2)) * normScale;
        voice.osc.frequency.setTargetAtTime(freq, now, 0.12);
        voice.gain.gain.setTargetAtTime(amp, now, 0.12);
      } else {
        voice.gain.gain.setTargetAtTime(0.0001, now, 0.1);
      }
    }
  }
}

class UnifiedDataflowViewport {
  constructor(container) {
    this.container = container;
    this.isSoftwareGl = detectSoftwareWebGL();
    this.active = false;
    this.frameId = 0;
    this.clock = new THREE.Clock();
    this.elapsed = 0;

    // Unified dataflow parameters
    this.presetId = 'wave_interference';
    this.customCode = null;
    this.gateSteepness = 14.0;
    this.wakeThreshold = 0.16;
    this.audioHarmonics = 6;
    this.autoOptimize = false;
    this.showComputeFocus = false;
    this.liveFlowEnabled = true;
    this.cinematicMode = false;
    this.cinematicAngle = 0.55;

    // Backend fetch cadence (runs cleanly without flooding Python)
    this.fetchInFlight = false;
    this.fetchTimer = 0;
    this.tPhase = 0.0;
    this.lastReport = null;

    // Current vs Target field buffers for silky-smooth frame-rate-independent damping
    this.curHeight = new Float32Array(GRID_CELLS);
    this.tgtHeight = new Float32Array(GRID_CELLS);
    this.curTemp = new Float32Array(GRID_CELLS).fill(0.5);
    this.tgtTemp = new Float32Array(GRID_CELLS).fill(0.5);
    this.curMask = new Float32Array(GRID_CELLS).fill(1.0);
    this.tgtMask = new Float32Array(GRID_CELLS).fill(1.0);
    this.curWave = new Float32Array(64);
    this.tgtWave = new Float32Array(64);

    // Deterministic sub-splat jitter offsets around each 32x32 grid cell
    this.splatJitter = new Float32Array(TOTAL_SPLATS * 3);
    for (let i = 0; i < TOTAL_SPLATS; i++) {
      const s1 = Math.sin(i * 12.9898) * 43758.5453;
      const s2 = Math.sin(i * 78.233 + 1.7) * 24634.6345;
      const s3 = Math.sin(i * 39.425 + 4.1) * 19283.4123;
      this.splatJitter[i * 3 + 0] = ((s1 - Math.floor(s1)) - 0.5) * 0.24;
      this.splatJitter[i * 3 + 1] = ((s2 - Math.floor(s2)) - 0.5) * 0.26;
      this.splatJitter[i * 3 + 2] = ((s3 - Math.floor(s3)) - 0.5) * 0.24;
    }

    this.audio = new HarmonicAudioBridge();

    this._initRendererAndScene();
    this._buildEnvironmentStage();
    this._buildUnifiedFieldMesh();
    this._buildVolumetricGaussianSplats();
    this._buildHarmonicSpectrumRing();
    this._bindUI();

    window.addEventListener('resize', () => this._resize());
    this._resize();
  }

  _initRendererAndScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x050811);
    this.scene.fog = new THREE.FogExp2(0x050811, 0.052);

    this.camera = new THREE.PerspectiveCamera(44, 16 / 9, 0.1, 90);
    this.camera.position.set(0.0, 5.2, 8.6);

    this.renderer = new THREE.WebGLRenderer({
      antialias: !this.isSoftwareGl,
      powerPreference: 'high-performance',
      alpha: false,
    });
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.12;
    this.renderer.setPixelRatio(this.isSoftwareGl ? 1 : Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.shadowMap.enabled = !this.isSoftwareGl;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Mandatory studio environment reflection map
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();

    const domEl = this.renderer.domElement;
    domEl.style.width = '100%';
    domEl.style.height = '100%';
    domEl.style.display = 'block';
    this.container.replaceChildren(domEl);

    // WebGL context loss/restore safety
    domEl.addEventListener('webglcontextlost', (e) => {
      e.preventDefault();
      this.stop();
    });
    domEl.addEventListener('webglcontextrestored', () => {
      if (document.getElementById('atelier3dStage')?.classList.contains('active')) {
        this.start();
      }
    });

    this.controls = new OrbitControls(this.camera, domEl);
    this.controls.enableDamping = !this.isSoftwareGl;
    this.controls.dampingFactor = 0.06;
    this.controls.minDistance = 4.2;
    this.controls.maxDistance = 17.5;
    this.controls.maxPolarAngle = Math.PI * 0.485;
    this.controls.target.set(0, 0.35, 0);
    this.controls.addEventListener('start', () => {
      if (this.cinematicMode) {
        this.cinematicMode = false;
        const btn = document.getElementById('btnAtelierCinema');
        if (btn) {
          btn.classList.remove('active');
          btn.textContent = '시점 자동 순회';
        }
      }
    });

    // Warm/Cool 3-point architectural lighting rig
    const hemi = new THREE.HemisphereLight(0x8ecae6, 0x0b1020, 0.72);
    this.scene.add(hemi);

    const keyLight = new THREE.DirectionalLight(0xfff1dc, 1.85);
    keyLight.position.set(6.5, 9.5, 5.5);
    if (!this.isSoftwareGl) {
      keyLight.castShadow = true;
      keyLight.shadow.mapSize.set(1024, 1024);
      keyLight.shadow.camera.left = -7;
      keyLight.shadow.camera.right = 7;
      keyLight.shadow.camera.top = 7;
      keyLight.shadow.camera.bottom = -7;
      keyLight.shadow.bias = -0.0005;
      keyLight.shadow.normalBias = 0.02;
    }
    this.scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.1);
    rimLight.position.set(-7.0, 4.5, -6.0);
    this.scene.add(rimLight);
  }

  _buildEnvironmentStage() {
    // Open architectural horizon plane (no boxed indoor walls!)
    const floorGeom = new THREE.CircleGeometry(28, 72);
    floorGeom.rotateX(-Math.PI / 2);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x070c17,
      roughness: 0.78,
      metalness: 0.22,
    });
    const floor = new THREE.Mesh(floorGeom, floorMat);
    floor.position.y = -1.65;
    floor.receiveShadow = !this.isSoftwareGl;
    this.scene.add(floor);

    // Subtle polar calibration rings flush on horizon (offset Y >= 0.02, polygonOffset)
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x1e3a5f,
      transparent: true,
      opacity: 0.34,
      polygonOffset: true,
      polygonOffsetFactor: -1,
      polygonOffsetUnits: -1,
    });
    for (const r of [3.9, 5.4, 7.2]) {
      const ringGeom = new THREE.RingGeometry(r - 0.014, r + 0.014, 96);
      ringGeom.rotateX(-Math.PI / 2);
      const ring = new THREE.Mesh(ringGeom, ringMat);
      ring.position.y = -1.62;
      this.scene.add(ring);
    }

    // Distant star/dust depth field for atmospheric parallax
    const bgCount = 360;
    const bgPos = new Float32Array(bgCount * 3);
    for (let i = 0; i < bgCount; i++) {
      const a = (i * 2.39996) % (Math.PI * 2);
      const rad = 11.0 + (i % 19) * 0.9;
      bgPos[i * 3 + 0] = Math.cos(a) * rad;
      bgPos[i * 3 + 1] = -0.8 + ((i * 17) % 100) * 0.11;
      bgPos[i * 3 + 2] = Math.sin(a) * rad;
    }
    const bgGeom = new THREE.BufferGeometry();
    bgGeom.setAttribute('position', new THREE.BufferAttribute(bgPos, 3));
    const bgPts = new THREE.Points(
      bgGeom,
      new THREE.PointsMaterial({
        color: 0x64748b,
        size: 0.08,
        transparent: true,
        opacity: 0.45,
        depthWrite: false,
      })
    );
    this.scene.add(bgPts);
  }

  _buildUnifiedFieldMesh() {
    // 32x32 continuous unified causal field substrate mesh (PBR translucent dark glass-wave)
    const geom = new THREE.PlaneGeometry(7.2, 7.2, GRID_N - 1, GRID_N - 1);
    geom.rotateX(-Math.PI / 2);
    const colors = new Float32Array(GRID_CELLS * 3);
    geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const mat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.28,
      metalness: 0.58,
      wireframe: false,
      transparent: true,
      opacity: 0.72,
      side: THREE.DoubleSide,
    });
    this.fieldMesh = new THREE.Mesh(geom, mat);
    this.fieldMesh.position.y = 0.05;
    this.scene.add(this.fieldMesh);

    // Crisp hairline topographic wireframe overlay showing the multi-scale grid directly
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      wireframe: true,
      transparent: true,
      opacity: 0.14,
      depthWrite: false,
    });
    this.fieldWire = new THREE.Mesh(geom, wireMat);
    this.fieldWire.position.y = 0.065;
    this.scene.add(this.fieldWire);
  }

  _buildVolumetricGaussianSplats() {
    // 4,096 custom GLSL anisotropic Gaussian light-splats floating on the unified field
    const posArr = new Float32Array(TOTAL_SPLATS * 3);
    const colArr = new Float32Array(TOTAL_SPLATS * 3);
    const sizeArr = new Float32Array(TOTAL_SPLATS);
    const awakeArr = new Float32Array(TOTAL_SPLATS);

    this.splatGeom = new THREE.BufferGeometry();
    this.splatGeom.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
    this.splatGeom.setAttribute('aColor', new THREE.BufferAttribute(colArr, 3));
    this.splatGeom.setAttribute('aSize', new THREE.BufferAttribute(sizeArr, 1));
    this.splatGeom.setAttribute('aAwake', new THREE.BufferAttribute(awakeArr, 1));

    this.splatMat = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uPixelRatio: { value: this.renderer.getPixelRatio() },
        uShowComputeFocus: { value: 0.0 },
      },
      vertexShader: `
        attribute vec3 aColor;
        attribute float aSize;
        attribute float aAwake;
        uniform float uTime;
        uniform float uPixelRatio;
        uniform float uShowComputeFocus;
        varying vec3 vColor;
        varying float vAlpha;

        void main() {
          vec3 p = position;
          p.y += sin(uTime * 1.9 + position.x * 1.4 + position.z * 1.2) * 0.035;

          vec4 mvPos = modelViewMatrix * vec4(p, 1.0);
          gl_Position = projectionMatrix * mvPos;

          float focusBoost = mix(1.0, mix(0.48, 1.42, aAwake), uShowComputeFocus);
          gl_PointSize = clamp((aSize * focusBoost * uPixelRatio * 290.0) / max(1.2, -mvPos.z), 3.0, 46.0);

          vec3 quietTint = vec3(0.14, 0.22, 0.38);
          vec3 activeTint = vec3(0.22, 0.96, 0.88);
          vec3 computeColor = mix(quietTint, activeTint, aAwake);
          vColor = mix(aColor, computeColor, uShowComputeFocus * 0.82);
          vAlpha = mix(0.84, mix(0.22, 0.98, aAwake), uShowComputeFocus);
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        varying float vAlpha;

        void main() {
          vec2 d = gl_PointCoord - vec2(0.5);
          float r2 = dot(d, d);
          if (r2 > 0.25) discard;
          // Soft 2D Gaussian splat falloff with luminous core
          float g = exp(-r2 * 14.5);
          float core = exp(-r2 * 38.0) * 0.45;
          gl_FragColor = vec4(vColor + vec3(core * 0.35), g * vAlpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    this.splatPoints = new THREE.Points(this.splatGeom, this.splatMat);
    this.splatPoints.position.y = 0.08;
    this.splatPoints.frustumCulled = false;
    this.scene.add(this.splatPoints);
  }

  _buildHarmonicSpectrumRing() {
    // Living 3D acoustic waveform ring orbiting the unified field
    const pos = new Float32Array((WAVE_RING_PTS + 1) * 3);
    this.waveRingGeom = new THREE.BufferGeometry();
    this.waveRingGeom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.LineBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.72,
    });
    this.waveRing = new THREE.Line(this.waveRingGeom, mat);
    this.waveRing.position.y = -0.35;
    this.scene.add(this.waveRing);
  }

  async fetchUnifiedCycle(forcePhaseAdvance = true) {
    if (this.fetchInFlight) return;
    this.fetchInFlight = true;
    if (forcePhaseAdvance) {
      this.tPhase += 0.38;
    }

    try {
      const res = await fetch('/api/scale-rotor/unified-dataflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          preset_id: this.presetId,
          code_source: this.customCode || undefined,
          gate_steepness: this.gateSteepness,
          wake_threshold: this.wakeThreshold,
          audio_harmonics: this.audioHarmonics,
          t_phase: this.tPhase,
          auto_optimize: this.autoOptimize,
        }),
      });
      const data = await res.json();
      if (!res.ok || data.status === 'error') {
        this._setCodeError(data.message || `HTTP ${res.status}`);
        return;
      }
      this._setCodeError('');
      this._ingestReport(data);
    } catch (err) {
      this._setCodeError(err instanceof Error ? err.message : '통신 오류');
    } finally {
      this.fetchInFlight = false;
    }
  }

  _ingestReport(report) {
    this.lastReport = report;
    const sf = report.spatial_field || {};
    const hArr = sf.height || [];
    const tArr = sf.temp || [];
    const mArr = sf.active_mask || [];

    for (let i = 0; i < GRID_CELLS; i++) {
      this.tgtHeight[i] = Number(hArr[i] ?? 0);
      this.tgtTemp[i] = Number(tArr[i] ?? 0.5);
      this.tgtMask[i] = Number(mArr[i] ?? 0);
    }

    const wavePrev = report.signal_audio?.reconstructed_preview || [];
    for (let i = 0; i < 64; i++) {
      this.tgtWave[i] = Number(wavePrev[i] ?? 0);
    }

    // Update live procedural Web Audio synth from exact condensed rFFT harmonics
    const avgTemp = tArr.length ? tArr.reduce((a, b) => a + b, 0) / tArr.length : 0.5;
    this.audio.applyHarmonics(report.signal_audio?.harmonics || [], avgTemp);

    // If auto-eye adjusted thresholds, reflect smoothly in sliders
    if (this.autoOptimize && report.params) {
      this.gateSteepness = Number(report.params.gate_steepness) || this.gateSteepness;
      this.wakeThreshold = Number(report.params.wake_threshold) || this.wakeThreshold;
      const kSlider = document.getElementById('atelierGateSlider');
      const kVal = document.getElementById('atelierGateVal');
      const wSlider = document.getElementById('atelierGearSlider');
      const wVal = document.getElementById('atelierGearVal');
      if (kSlider) kSlider.value = String(Math.round(this.gateSteepness));
      if (kVal) kVal.textContent = `k=${this.gateSteepness.toFixed(0)}`;
      if (wSlider) wSlider.value = String(Math.round(this.wakeThreshold * 100));
      if (wVal) wVal.textContent = `${Math.round(this.wakeThreshold * 100)}%`;
    }

    // Populate code editor if user hasn't typed custom edits
    const codeBox = document.getElementById('atelierCodeEditor');
    if (codeBox && !this.customCode && report.code_circuit?.source) {
      codeBox.value = report.code_circuit.source;
    }

    // Update unified unboxed proof readout (safe textContent only!)
    this._renderProofHUD(report);

    // Propagate canonical L1 Scale-Rotor state to outer telemetry ribbon
    if (report.rotor_state && typeof window.__elysiaApplyRotorState === 'function') {
      window.__elysiaApplyRotorState(report.rotor_state);
    }
  }

  _setCodeError(msg) {
    const el = document.getElementById('atelierCodeError');
    if (!el) return;
    el.textContent = msg;
    el.style.display = msg ? 'block' : 'none';
  }

  _renderProofHUD(report) {
    const cc = report.code_circuit || {};
    const mg = report.multiscale_gear || {};
    const sa = report.signal_audio || {};
    const cd = report.cross_domain_coupling || {};
    const eye = report.eye_feedback || {};

    const proofEl = document.getElementById('atelierProofLine');
    if (proofEl) {
      proofEl.textContent =
        `연산 절감 ${Number(mg.compute_saved_pct ?? 0).toFixed(1)}% (${mg.s2_micro_awake ?? 0}/${mg.s2_micro_total ?? 1024} 미세셀 활성 · ${mg.effective_speedup ?? 1}x)` +
        `  ·  공간 복원 ${Number(mg.spatial_fidelity_pct ?? 0).toFixed(1)}%` +
        `  ·  분기문 ${cc.original_if_branches ?? 0}→0 트랜지스터 회로 (일치 ${Number(cc.discrete_equivalence_pct ?? 0).toFixed(1)}%)` +
        `  ·  음향 압축 ${sa.compression_ratio ?? 0}x (${sa.condensed_harmonics ?? 0}배음 · ${Number(sa.waveform_fidelity_pct ?? 0).toFixed(1)}%)` +
        `  ·  3도메인 결합도 ${Number(cd.unified_coherence ?? 0).toFixed(2)}`;
    }

    const narrEl = document.getElementById('atelierNarration');
    if (narrEl) {
      const gates = Array.isArray(cc.gates) ? cc.gates : [];
      const gateStr = gates.length
        ? gates.map((g) => `${g.gate_id}: ${g.compiled_formula} (열림 ${Math.round(g.open_ratio * 100)}%)`).join('  /  ')
        : '연속 함수 직접 통과';
      narrEl.textContent = this.autoOptimize
        ? `[눈 자동 조율] ${eye.action_note}  ·  ${gateStr}`
        : `컴파일된 수문 회로: ${gateStr}`;
    }
  }

  _updateGeometryBuffers(dt) {
    const dampFactor = 1.0 - Math.exp(-7.5 * dt);

    const meshPos = this.fieldMesh.geometry.attributes.position;
    const meshCol = this.fieldMesh.geometry.attributes.color;
    const splatPos = this.splatGeom.attributes.position;
    const splatCol = this.splatGeom.attributes.aColor;
    const splatSize = this.splatGeom.attributes.aSize;
    const splatAwake = this.splatGeom.attributes.aAwake;

    const span = 7.2;
    const half = span * 0.5;
    const step = span / (GRID_N - 1);

    for (let row = 0; row < GRID_N; row++) {
      const z = -half + row * step;
      for (let col = 0; col < GRID_N; col++) {
        const idx = row * GRID_N + col;
        const x = -half + col * step;

        const h = this.curHeight[idx] + (this.tgtHeight[idx] - this.curHeight[idx]) * dampFactor;
        const t = this.curTemp[idx] + (this.tgtTemp[idx] - this.curTemp[idx]) * dampFactor;
        const m = this.curMask[idx] + (this.tgtMask[idx] - this.curMask[idx]) * dampFactor;

        this.curHeight[idx] = h;
        this.curTemp[idx] = t;
        this.curMask[idx] = m;

        const yElev = h * 1.15;
        meshPos.setY(idx, yElev);

        // Domain-authentic curated color mapping (deep obsidian -> cyan -> warm amber-gold)
        if (this.showComputeFocus) {
          _tmpColor.setRGB(
            0.07 + 0.12 * m,
            0.12 + 0.62 * m,
            0.24 + 0.58 * m
          );
        } else {
          // Cold phase (else branch, low temp) = deep sapphire/cyan; Warm phase (if branch, high temp) = luminous amber/coral
          const rC = 0.08 + 0.88 * Math.pow(t, 1.35);
          const gC = 0.36 + 0.42 * Math.sin(t * Math.PI) + 0.14 * Math.max(0, h);
          const bC = 0.92 * (1.0 - 0.72 * t) + 0.12 * Math.max(0, h);
          _tmpColor.setRGB(
            Math.min(1, rC),
            Math.min(1, gC),
            Math.min(1, bC)
          );
        }
        meshCol.setXYZ(idx, _tmpColor.r, _tmpColor.g, _tmpColor.b);

        // Update 4 volumetric Gaussian splats per cell
        const baseSplat = idx * SPLAT_MULTIPLIER;
        for (let s = 0; s < SPLAT_MULTIPLIER; s++) {
          const si = baseSplat + s;
          const jx = this.splatJitter[si * 3 + 0];
          const jy = this.splatJitter[si * 3 + 1];
          const jz = this.splatJitter[si * 3 + 2];

          splatPos.setXYZ(si, x + jx, yElev + 0.14 + jy * (0.4 + Math.abs(h) * 0.6), z + jz);
          splatCol.setXYZ(si, _tmpColor.r, _tmpColor.g, _tmpColor.b);
          splatSize.setX(si, 0.24 + Math.abs(h) * 0.22 + m * 0.12);
          splatAwake.setX(si, m);
        }
      }
    }

    meshPos.needsUpdate = true;
    meshCol.needsUpdate = true;
    this.fieldMesh.geometry.computeVertexNormals();

    splatPos.needsUpdate = true;
    splatCol.needsUpdate = true;
    splatSize.needsUpdate = true;
    splatAwake.needsUpdate = true;

    // Update 3D acoustic harmonic spectrum ring from Python rFFT reconstruction
    const ringPos = this.waveRingGeom.attributes.position;
    for (let i = 0; i < 64; i++) {
      this.curWave[i] += (this.tgtWave[i] - this.curWave[i]) * dampFactor;
    }
    const baseR = 4.65;
    for (let i = 0; i <= WAVE_RING_PTS; i++) {
      const frac = i / WAVE_RING_PTS;
      const angle = frac * Math.PI * 2.0 + this.elapsed * 0.18;
      const sampleIdx = Math.floor(frac * 64) % 64;
      const amp = this.curWave[sampleIdx];
      const rad = baseR + amp * 0.55;
      ringPos.setXYZ(i, Math.cos(angle) * rad, amp * 0.42, Math.sin(angle) * rad);
    }
    ringPos.needsUpdate = true;
  }

  _tick(dt) {
    this.elapsed += dt;

    // Periodic unified Python cycle when live flow is enabled
    if (this.liveFlowEnabled) {
      this.fetchTimer += dt;
      if (this.fetchTimer >= 0.95) {
        this.fetchTimer = 0;
        this.fetchUnifiedCycle(true);
      }
    }

    // Smoothly transition compute-focus shader uniform
    const targetFocus = this.showComputeFocus ? 1.0 : 0.0;
    this.splatMat.uniforms.uShowComputeFocus.value = THREE.MathUtils.damp(
      this.splatMat.uniforms.uShowComputeFocus.value,
      targetFocus,
      7.0,
      dt
    );
    this.splatMat.uniforms.uTime.value = this.elapsed;

    this._updateGeometryBuffers(dt);

    // Optional smooth orbit camera tour (zero GC allocations)
    if (this.cinematicMode) {
      this.cinematicAngle += dt * 0.24;
      const cx = Math.sin(this.cinematicAngle) * 8.8;
      const cz = Math.cos(this.cinematicAngle) * 8.8;
      const cy = 4.6 + Math.sin(this.cinematicAngle * 1.4) * 1.25;
      _tmpVecA.set(cx, cy, cz);
      _tmpVecB.set(0.0, 0.25, 0.0);
      const camDamp = 1.0 - Math.exp(-2.8 * dt);
      this.camera.position.lerp(_tmpVecA, camDamp);
      this.controls.target.lerp(_tmpVecB, camDamp);
    }

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  _afterDraw(cb) {
    const gl = this.renderer.getContext();
    if (typeof WebGL2RenderingContext !== 'undefined' && gl instanceof WebGL2RenderingContext) {
      const sync = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0);
      gl.flush();
      const poll = () => {
        if (!this.active) {
          if (sync) gl.deleteSync(sync);
          return;
        }
        const status = sync && gl.getSyncParameter(sync, gl.SYNC_STATUS);
        if (status === gl.UNSIGNALED) {
          this.frameId = window.setTimeout(poll, 5);
        } else {
          if (sync) gl.deleteSync(sync);
          this.frameId = window.setTimeout(cb, 80);
        }
      };
      this.frameId = window.setTimeout(poll, 5);
    } else {
      this.frameId = window.setTimeout(cb, 90);
    }
  }

  start() {
    if (this.active) return;
    this.active = true;
    this._resize();
    this.clock.getDelta();

    if (!this.lastReport) {
      this.fetchUnifiedCycle(false);
    }

    const loop = () => {
      if (!this.active) return;
      const dt = Math.min(0.05, this.clock.getDelta());
      this._tick(dt);
      if (this.isSoftwareGl) {
        this._afterDraw(loop);
      } else {
        this.frameId = requestAnimationFrame(loop);
      }
    };

    if (this.isSoftwareGl) {
      this.frameId = window.setTimeout(loop, 16);
    } else {
      this.frameId = requestAnimationFrame(loop);
    }
  }

  stop() {
    this.active = false;
    cancelAnimationFrame(this.frameId);
    window.clearTimeout(this.frameId);
    this.frameId = 0;
    this.audio.stop();
    const audioBtn = document.getElementById('btnAtelierAudio');
    if (audioBtn) {
      audioBtn.classList.remove('active');
      audioBtn.textContent = '소리 공명: 꺼짐';
    }
  }

  _resize() {
    if (!this.container || !this.renderer) return;
    const w = Math.max(300, this.container.clientWidth);
    const h = Math.max(280, this.container.clientHeight);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h, false);
    if (this.splatMat) {
      this.splatMat.uniforms.uPixelRatio.value = this.renderer.getPixelRatio();
    }
  }

  _bindUI() {
    // 1. Unified world presets
    document.querySelectorAll('.atelier-scene-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.atelier-scene-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        this.presetId = btn.dataset.scene || 'wave_interference';
        this.customCode = null;
        this.fetchUnifiedCycle(false);
      });
    });

    // 2. Gate Steepness Slider (Analog field <-> Digital transistor switch k)
    const gateSlider = document.getElementById('atelierGateSlider');
    const gateVal = document.getElementById('atelierGateVal');
    if (gateSlider) {
      gateSlider.addEventListener('input', () => {
        this.gateSteepness = Number(gateSlider.value);
        if (gateVal) gateVal.textContent = `k=${this.gateSteepness}`;
        this.autoOptimize = false;
        const autoBtn = document.getElementById('btnAtelierAutoEye');
        if (autoBtn) {
          autoBtn.classList.remove('active');
          autoBtn.textContent = '눈 자동 최적화: 꺼짐';
        }
        this.fetchUnifiedCycle(false);
      });
    }

    // 3. Multi-Scale Gear Wake Threshold Slider (100% Brute Force <-> High Compute Savings)
    const gearSlider = document.getElementById('atelierGearSlider');
    const gearVal = document.getElementById('atelierGearVal');
    if (gearSlider) {
      gearSlider.addEventListener('input', () => {
        const pct = Number(gearSlider.value);
        this.wakeThreshold = pct / 100.0;
        if (gearVal) gearVal.textContent = `${pct}%`;
        this.autoOptimize = false;
        const autoBtn = document.getElementById('btnAtelierAutoEye');
        if (autoBtn) {
          autoBtn.classList.remove('active');
          autoBtn.textContent = '눈 자동 최적화: 꺼짐';
        }
        this.fetchUnifiedCycle(false);
      });
    }

    // 4. Web Audio Harmonic Resonator Toggle
    const btnAudio = document.getElementById('btnAtelierAudio');
    if (btnAudio) {
      btnAudio.addEventListener('click', () => {
        const on = this.audio.toggle();
        btnAudio.classList.toggle('active', on);
        btnAudio.textContent = on ? '소리 공명: 켜짐' : '소리 공명: 꺼짐';
      });
    }

    // 5. Multi-Scale Compute Focus View Toggle
    const btnCompute = document.getElementById('btnAtelierComputeView');
    if (btnCompute) {
      btnCompute.addEventListener('click', () => {
        this.showComputeFocus = !this.showComputeFocus;
        btnCompute.classList.toggle('active', this.showComputeFocus);
        btnCompute.textContent = this.showComputeFocus ? '연산 집중도: 보는 중' : '연산 집중도 보기';
      });
    }

    // 6. Closed-Loop Perceptual Eye Auto-Optimization
    const btnAutoEye = document.getElementById('btnAtelierAutoEye');
    if (btnAutoEye) {
      btnAutoEye.addEventListener('click', () => {
        this.autoOptimize = !this.autoOptimize;
        btnAutoEye.classList.toggle('active', this.autoOptimize);
        btnAutoEye.textContent = this.autoOptimize ? '눈 자동 최적화: 켜짐' : '눈 자동 최적화: 꺼짐';
        this.fetchUnifiedCycle(false);
      });
    }

    // 7. Camera Tour Toggle
    const btnCinema = document.getElementById('btnAtelierCinema');
    if (btnCinema) {
      btnCinema.addEventListener('click', () => {
        this.cinematicMode = !this.cinematicMode;
        btnCinema.classList.toggle('active', this.cinematicMode);
        btnCinema.textContent = this.cinematicMode ? '시점 순회 정지' : '시점 자동 순회';
      });
    }

    // 8. Code Circuit Drawer Toggle & Live Compile
    const btnCodeToggle = document.getElementById('btnAtelierCodeToggle');
    const codeDrawer = document.getElementById('atelierCodeDrawer');
    if (btnCodeToggle && codeDrawer) {
      btnCodeToggle.addEventListener('click', () => {
        const open = codeDrawer.classList.toggle('open');
        btnCodeToggle.classList.toggle('active', open);
      });
    }

    const btnCompile = document.getElementById('btnAtelierCompileCode');
    const codeEditor = document.getElementById('atelierCodeEditor');
    if (btnCompile && codeEditor) {
      btnCompile.addEventListener('click', () => {
        this.customCode = codeEditor.value.trim();
        this.fetchUnifiedCycle(false);
      });
    }

    // 9. Collapsible Bottom Dock (Zero Viewport Occlusion!)
    const btnCollapse = document.getElementById('btnAtelierDockToggle');
    const dockWrap = document.getElementById('atelierDockWrap');
    if (btnCollapse && dockWrap) {
      btnCollapse.addEventListener('click', () => {
        const collapsed = dockWrap.classList.toggle('collapsed');
        btnCollapse.textContent = collapsed ? '▴ 컨트롤 열기' : '▾ 컨트롤 숨기기';
      });
    }
  }
}

// Mount & expose clean lifecycle bridge for unified_scale_rotor_field.js
const mountEl = document.getElementById('atelier3dCanvasHost');
if (mountEl) {
  const viewport = new UnifiedDataflowViewport(mountEl);
  window.__elysia3DAtelier = viewport;
  const gameActive = document.getElementById('elysiaGameStage')?.classList.contains('active');
  if (!gameActive && document.getElementById('atelier3dStage')?.classList.contains('active')) {
    viewport.start();
  }
}
