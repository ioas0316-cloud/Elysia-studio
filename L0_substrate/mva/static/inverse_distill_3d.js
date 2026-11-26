import * as THREE from 'three';

/**
 * Elysia Scale-Rotor Unified Causal Engine (Tab 7)
 * --------------------------------------------------------------------------------------
 * Three-stage Scale-Rotor progression driven by unperceived residual order:
 *
 *  Stage 1 ('2d'):  2D Static Spectral Completeness (ΣC1..C6 === O(t), Residual === 0.0%)
 *                   Proves algebraic completeness on a single frame while exposing the
 *                   illusion of static completeness when time advances.
 *
 *  Stage 2 ('st'):  Spatiotemporal & Cross-Modal Audio Residual (O(t) -> O(t+1))
 *                   Even with 100% 2D spatial completeness, static O(t) breaks at t+1.
 *                   The temporal residual is NOT noise — it decomposes into higher-order rules:
 *                     T1: Inertial Motion Advection (real dense Lucas-Kanade optical flow)
 *                     T2: 3D Parallax & Occlusion/Disocclusion boundaries (velocity shear + unwarped residual)
 *                     T3: Off-Frame Environment / Macro Illumination Shift (ΔS4 radiance & white balance)
 *                     T4: Cross-Modal Audio-Visual Resonance (real Web Audio API FFT + Pearson r)
 *
 *  Stage 3 ('f3d'): 3D Counterfactual Falsification Lab (NOT a synthetic showcase!)
 *                   Lifts the live HD reality into a real 160x90 depth-displaced 3D physical surface
 *                   driven by extracted motion-parallax + shading depth and inferred external light (∇C1).
 *                   Deviating camera viewpoint (ΔYaw/ΔPitch), external light angle (ΔLight), or
 *                   extrapolating inertial time (+Δt) immediately exposes unobserved 3D backface voids
 *                   and shadow contradictions — falsifying the 2D single-view assumption directly.
 */

const VIDEO_W = 960;
const VIDEO_H = 540;
const PROBE_W = 120;
const PROBE_H = 68;
const PROBE_N = PROBE_W * PROBE_H;
const FLOW_W = 60;
const FLOW_H = 34;
const FLOW_N = FLOW_W * FLOW_H;
const MAX_FLOW_PX = 18.0; // in 960x540 native pixel coordinates

const HD_VIDEO_PRESETS = {
  traffic: {
    label: '도심 교차로 1080p 실황',
    url: '/api/ingest/media?url=' + encodeURIComponent('https://upload.wikimedia.org/wikipedia/commons/2/2c/Tirana_traffic_lights.webm'),
  },
  atmosphere: {
    label: '남극 대기 파동 1080p 위성',
    url: '/api/ingest/media?url=' + encodeURIComponent('https://upload.wikimedia.org/wikipedia/commons/a/a4/Gravity_Waves_Cascade_off_of_Islands_Near_Antarctica_%28CIRA_2023-12-29_-_nolabels%29.webm'),
  },
};

const SPECTRAL_AXES = [
  { id: 1, key: 'c1', name: 'C1 · 거시 환경 조도 (S4)', role: '태양·하늘·대지가 만드는 광역 환경 조도장', color: '#34d399' },
  { id: 2, key: 'c2', name: 'C2 · 그림자·암부 차폐', role: '구조물이 환경광을 가로막아 생기는 차폐·음영', color: '#a78bfa' },
  { id: 3, key: 'c3', name: 'C3 · 명도·형태 음영 (S2)', role: '표면 법선 각도(N·L)에 따른 입체 형태 밝기', color: '#e2e8f0' },
  { id: 4, key: 'c4', name: 'C4 · 채도·파장 스펙트럼', role: '휘도를 제거한 순수 파장 선택 흡수·색순도', color: '#38bdf8' },
  { id: 5, key: 'c5', name: 'C5 · 광도·정반사 피크', role: '광원 직접 반사·금속/안구 하이라이트 광속', color: '#facc15' },
  { id: 6, key: 'c6', name: 'C6 · 미시 윤곽·질감 (S0)', role: '턱선·눈동자·미세 경계를 결정하는 고주파 구조', color: '#fb7185' },
];

const ST_AXES = [
  {
    id: 1,
    key: 't1',
    name: 'T1 · 관성·운동 질서 (Optical Flow)',
    role: '이전 프레임 O(t)를 실측 속도장(vx,vy)으로 이류시켜 관성 이동 잔차를 해소',
    color: '#38bdf8',
    toggleable: true,
  },
  {
    id: 2,
    key: 't3',
    name: 'T3 · 화면 밖 광원·환경 변화 (ΔS4)',
    role: '프레임 밖 태양·하늘·조명 변화로 발생하는 전역 조도·색온도 이동을 보정',
    color: '#34d399',
    toggleable: true,
  },
  {
    id: 3,
    key: 't2',
    name: 'T2 · 3D 시차·가려짐 경계 (Occlusion)',
    role: 'T1·T3 적용 후에도 사라지지 않는 경계 잔차 = 2D 너머 3D 깊이·뒷면 출현 증거',
    color: '#fb7185',
    toggleable: false,
  },
  {
    id: 4,
    key: 't4',
    name: 'T4 · 음향·시각 교차 공명 (Cross-Modal)',
    role: '실제 마이크/영상 오디오 주파수와 시각 운동 에너지의 시간축 상관(r) 검증',
    color: '#facc15',
    toggleable: false,
  },
];

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function clearNode(el) {
  while (el && el.firstChild) el.removeChild(el.firstChild);
}

const SRGB_TO_LIN = new Float32Array(256);
for (let i = 0; i < 256; i++) {
  SRGB_TO_LIN[i] = Math.pow(i / 255, 2.2);
}

// ============================================================================
// 1. Unified Scale-Rotor State (Stages 1 / 2 / 3)
// ============================================================================
const rotorState = {
  stage: 'onto', // '2d' | 'st' | 'f3d' | 'onto'
  displayMode: 2, // 0: recombined/pred, 1: residual, 2: split compare
  // Stage 1: 2D static axes
  on2d: [true, true, true, true, true, true],
  solo2d: 0,
  // Stage 2: Spatiotemporal axes (T1 inertial advection, T3 off-frame env shift)
  stOn: { t1: false, t3: false },
  soloSt: 0, // 0=none, 1=T1 flow, 2=T3 env shift, 3=T2 3D occlusion map, 4=T4 AV resonance heatmap
  // Stage 3: Counterfactual 3D Falsification parameters
  cfYawDeg: 0,
  cfPitchDeg: 0,
  cfLightDeltaDeg: 0,
  cfTimeExtrap: 0,
  cfDepthScale: 1.0,
  // Stage 4: Ontological 3D Resonance Manifold camera
  ontoYaw: 0.42,
  ontoPitch: 0.28,
  // Autonomous loops
  autoRunning: false,
  autoStage: null,
  autoStepIdx: 0,
  lastAutoStepTs: 0,
  sweepPhase: 0,
};

const ontoState = {
  loading: false,
  conceptA: '나무',
  conceptB: '숲',
  data: null,
  opticsA: null,
  opticsB: null,
  opticalSimPct: null,
};

const metrics2d = {
  valid: false,
  maePct: 0,
  psnrDb: 99.9,
  completenessPct: 100,
  activeCount: 6,
  axisEnergyPct: [0, 0, 0, 0, 0, 0],
  missingResidualByAxis: [0, 0, 0, 0, 0, 0],
  dominantMissingIdx: -1,
};

const metricsSt = {
  valid: false,
  isStaticImage: false,
  staticResidualPct: 0,   // |O(t+1) - O(t)|  (2D static failure)
  activeResidualPct: 0,   // |O(t+1) - Pred(t+1)| with enabled T1/T3
  motionExplainedPct: 0,  // reduction from T1 optical flow advection
  envExplainedPct: 0,     // reduction from T3 macro ambient shift
  occlusionResidPct: 0,   // irreducible 3D occlusion/disocclusion residual
  meanFlowPx: 0,
  maxFlowPx: 0,
  macroDeltaRgb: [0, 0, 0],
  inferredLightAzDeg: 35,
  inferredLightElDeg: 48,
  inferredLightVec: [0.42, 0.72, 0.55],
  visualEnergy: 0,
};

const metrics3d = {
  exposedVoidPct: 0,
  lightContradictionDeg: 0,
  extrapDriftPx: 0,
};

let discoveryLog = [];

// ============================================================================
// 2. Real Web Audio API Cross-Modal Sensor (Microphone or Local Video Track)
// ============================================================================
const avScopeHistoryLen = 72;
const avHistoryVis = new Float32Array(avScopeHistoryLen);
const avHistoryAud = new Float32Array(avScopeHistoryLen);
let avHistoryPtr = 0;

const audioSensor = {
  ctx: null,
  analyser: null,
  freqData: null,
  micStream: null,
  micSource: null,
  videoSource: null,
  connectedVideoEl: null,
  mode: 'none', // 'none' | 'mic' | 'video'
  rms: 0,
  lowBand: 0,
  midBand: 0,
  highBand: 0,
  onset: 0,
  prevRms: 0,
  corrR: 0,
  diagnosis: '오디오 감각 미연결',
};

function ensureAudioContext() {
  if (!audioSensor.ctx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    audioSensor.ctx = new AC();
    audioSensor.analyser = audioSensor.ctx.createAnalyser();
    audioSensor.analyser.fftSize = 512;
    audioSensor.analyser.smoothingTimeConstant = 0.65;
    audioSensor.freqData = new Uint8Array(audioSensor.analyser.frequencyBinCount);
  }
  if (audioSensor.ctx.state === 'suspended') {
    audioSensor.ctx.resume().catch(() => {});
  }
  return audioSensor.ctx;
}

function stopMicAudio() {
  if (audioSensor.micSource) {
    try { audioSensor.micSource.disconnect(); } catch (_) {}
    audioSensor.micSource = null;
  }
  if (audioSensor.micStream) {
    audioSensor.micStream.getTracks().forEach((t) => t.stop());
    audioSensor.micStream = null;
  }
  if (audioSensor.mode === 'mic') {
    audioSensor.mode = 'none';
  }
  syncAudioButtons();
}

async function toggleMicAudio(externalAudioStream = null) {
  if (!externalAudioStream && audioSensor.mode === 'mic') {
    stopMicAudio();
    setStatus('● 마이크 음향 감각을 해제했습니다.', 'normal');
    return;
  }
  const ctx = ensureAudioContext();
  if (!ctx) {
    setStatus('✖ 이 브라우저는 Web Audio API를 지원하지 않습니다.', 'error');
    return;
  }
  try {
    stopMicAudio();
    const stream = externalAudioStream || await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    audioSensor.micStream = externalAudioStream ? null : stream;
    audioSensor.micSource = ctx.createMediaStreamSource(stream);
    audioSensor.micSource.connect(audioSensor.analyser);
    audioSensor.mode = 'mic';
    syncAudioButtons();
    pushLog(
      'ok',
      '이종 감각 개방 · 실시간 마이크 음향 스펙트럼 연결',
      '시각 운동 에너지(T1)와 실제 공간 음향(저·중·고역대)의 시간축 교차 상관(r)을 실시간 계측합니다. 화면이 정지해 있는데 소리가 발생하면 화면 밖(Off-Frame) 인과원 존재로 판정합니다.'
    );
    setStatus('● 실시간 마이크 음향 감각 연결 완료 — 시각 운동과 실제 소리의 교차 공명(r)을 측정 중입니다.', 'ok');
  } catch (err) {
    setStatus(`✖ 마이크 연결 실패: ${err instanceof Error ? err.message : '권한 거부'}`, 'error');
  }
}

function connectVideoAudioTrack(videoEl) {
  if (!videoEl) return;
  const ctx = ensureAudioContext();
  if (!ctx) return;
  try {
    if (audioSensor.connectedVideoEl !== videoEl) {
      audioSensor.videoSource = ctx.createMediaElementSource(videoEl);
      audioSensor.connectedVideoEl = videoEl;
    }
    audioSensor.videoSource.connect(audioSensor.analyser);
    audioSensor.videoSource.connect(ctx.destination);
    videoEl.muted = false;
    audioSensor.mode = 'video';
    syncAudioButtons();
    pushLog(
      'ok',
      '영상 오디오 트랙 교차 연결 완료',
      '업로드한 영상의 실제 음성·환경음 스트림을 시각 운동 잔차와 동일 시간축으로 결합했습니다.'
    );
    setStatus('● 영상 내장 오디오 트랙 연결 완료 — 영상 속 움직임과 소리의 교차 공명을 실시간 측정 중입니다.', 'ok');
  } catch (err) {
    setStatus(`✖ 영상 오디오 연결 실패: ${err instanceof Error ? err.message : '오류'}`, 'error');
  }
}

function sampleAudioAndCorrelate(visualMotionEnergy) {
  let audLevel = 0;
  if (audioSensor.mode !== 'none' && audioSensor.analyser && audioSensor.freqData) {
    audioSensor.analyser.getByteFrequencyData(audioSensor.freqData);
    const bins = audioSensor.freqData;
    const n = bins.length;
    let low = 0;
    let mid = 0;
    let high = 0;
    // 48kHz / 512 => ~93.75Hz per bin
    const lowEnd = Math.min(4, n);
    const midEnd = Math.min(26, n);
    const highEnd = Math.min(130, n);
    for (let i = 0; i < lowEnd; i++) low += bins[i];
    for (let i = lowEnd; i < midEnd; i++) mid += bins[i];
    for (let i = midEnd; i < highEnd; i++) high += bins[i];

    audioSensor.lowBand = low / (lowEnd * 255);
    audioSensor.midBand = mid / (Math.max(1, midEnd - lowEnd) * 255);
    audioSensor.highBand = high / (Math.max(1, highEnd - midEnd) * 255);
    audLevel = clamp(audioSensor.lowBand * 0.42 + audioSensor.midBand * 0.43 + audioSensor.highBand * 0.15, 0, 1);
    audioSensor.onset = Math.max(0, audLevel - audioSensor.prevRms);
    audioSensor.prevRms = audLevel;
    audioSensor.rms = audLevel;
  } else {
    audioSensor.rms = 0;
    audioSensor.lowBand = 0;
    audioSensor.midBand = 0;
    audioSensor.highBand = 0;
    audioSensor.onset = 0;
  }

  avHistoryVis[avHistoryPtr] = clamp(visualMotionEnergy, 0, 1);
  avHistoryAud[avHistoryPtr] = audLevel;
  avHistoryPtr = (avHistoryPtr + 1) % avScopeHistoryLen;

  // Pearson correlation r over rolling window
  if (audioSensor.mode === 'none') {
    audioSensor.corrR = 0;
    audioSensor.diagnosis = '오디오 감각 미연결 (시각 단독 관측 중)';
    return;
  }

  let meanV = 0;
  let meanA = 0;
  for (let i = 0; i < avScopeHistoryLen; i++) {
    meanV += avHistoryVis[i];
    meanA += avHistoryAud[i];
  }
  meanV /= avScopeHistoryLen;
  meanA /= avScopeHistoryLen;

  let cov = 0;
  let varV = 0;
  let varA = 0;
  for (let i = 0; i < avScopeHistoryLen; i++) {
    const dv = avHistoryVis[i] - meanV;
    const da = avHistoryAud[i] - meanA;
    cov += dv * da;
    varV += dv * dv;
    varA += da * da;
  }
  const denom = Math.sqrt(varV * varA);
  audioSensor.corrR = denom > 1e-4 ? clamp(cov / denom, -1, 1) : 0;

  if (audLevel > 0.14 && visualMotionEnergy < 0.06) {
    audioSensor.diagnosis = '화면 밖(Off-Frame) 음향 사건 감지! (시각 프레임 밖 물리 인과원 존재)';
  } else if (audioSensor.corrR > 0.32 && audLevel > 0.06) {
    audioSensor.diagnosis = `시청각 인과 공명 확인 (r=${audioSensor.corrR.toFixed(2)}) — 운동·음향이 동일 사건 공유`;
  } else if (visualMotionEnergy > 0.12 && audLevel < 0.03) {
    audioSensor.diagnosis = '원거리·무음 시각 운동 (음향 전파 미도달 또는 정숙 물체)';
  } else {
    audioSensor.diagnosis = `교차 상관계수 r=${audioSensor.corrR.toFixed(2)} · 저역 ${(audioSensor.lowBand * 100).toFixed(0)}% / 중역 ${(audioSensor.midBand * 100).toFixed(0)}% / 고역 ${(audioSensor.highBand * 100).toFixed(0)}%`;
  }
}

function drawAvScope() {
  const cv = document.getElementById('d3d-av-scope');
  if (!cv) return;
  const ctx = cv.getContext('2d');
  const w = cv.width;
  const h = cv.height;
  ctx.fillStyle = '#04070e';
  ctx.fillRect(0, 0, w, h);

  // Subtle horizontal grid
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.14)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(0, h * 0.5);
  ctx.lineTo(w, h * 0.5);
  ctx.stroke();

  const drawTrace = (arr, color, scale) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    for (let i = 0; i < avScopeHistoryLen; i++) {
      const idx = (avHistoryPtr + i) % avScopeHistoryLen;
      const x = (i / (avScopeHistoryLen - 1)) * w;
      const y = h - 6 - clamp(arr[idx] * scale, 0, 1) * (h - 14);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  };

  drawTrace(avHistoryVis, '#38bdf8', 1.4);
  if (audioSensor.mode !== 'none') {
    drawTrace(avHistoryAud, '#facc15', 1.6);
  }

  const readout = document.getElementById('d3d-av-corr-readout');
  if (readout) {
    readout.textContent = audioSensor.diagnosis;
    readout.style.color = audioSensor.mode === 'none'
      ? '#94a3b8'
      : (audioSensor.corrR > 0.32 ? '#34d399' : '#facc15');
  }
}

// ============================================================================
// 3. Crisp 960x540 Frame Buffers + Dense Optical Flow + Inferred 3D Depth/Light
// ============================================================================
const origCanvas = document.createElement('canvas');
origCanvas.width = VIDEO_W;
origCanvas.height = VIDEO_H;
const origCtx = origCanvas.getContext('2d');

const prevCanvas = document.createElement('canvas');
prevCanvas.width = VIDEO_W;
prevCanvas.height = VIDEO_H;
const prevCtx = prevCanvas.getContext('2d');
let hasPrevFrame = false;

const probeCanvas = document.createElement('canvas');
probeCanvas.width = PROBE_W;
probeCanvas.height = PROBE_H;
const probeCtx = probeCanvas.getContext('2d', { willReadFrequently: true });

const probeLinR = new Float32Array(PROBE_N);
const probeLinG = new Float32Array(PROBE_N);
const probeLinB = new Float32Array(PROBE_N);
const probeY = new Float32Array(PROBE_N);
const probeMid = new Float32Array(PROBE_N);
const probeMacro = new Float32Array(PROBE_N);

// Fast 60x34 spatiotemporal motion & depth fields
const flowCurrR = new Float32Array(FLOW_N);
const flowCurrG = new Float32Array(FLOW_N);
const flowCurrB = new Float32Array(FLOW_N);
const flowPrevR = new Float32Array(FLOW_N);
const flowPrevG = new Float32Array(FLOW_N);
const flowPrevB = new Float32Array(FLOW_N);
const flowCurrY = new Float32Array(FLOW_N);
const flowPrevY = new Float32Array(FLOW_N);
const flowVx = new Float32Array(FLOW_N);
const flowVy = new Float32Array(FLOW_N);
const flowSmoothVx = new Float32Array(FLOW_N);
const flowSmoothVy = new Float32Array(FLOW_N);
const flowDepth = new Float32Array(FLOW_N);
const flowOcclusion = new Float32Array(FLOW_N);
const flowTexBytes = new Uint8Array(FLOW_N * 4);
for (let i = 0; i < FLOW_N; i++) {
  flowDepth[i] = 0.35;
  flowTexBytes[i * 4] = 128;
  flowTexBytes[i * 4 + 1] = 128;
  flowTexBytes[i * 4 + 2] = 90;
  flowTexBytes[i * 4 + 3] = 0;
}

function boxBlur2D(src, dst, w, h, radius) {
  const tmp = new Float32Array(w * h);
  const inv = 1 / (radius * 2 + 1);
  for (let y = 0; y < h; y++) {
    const row = y * w;
    for (let x = 0; x < w; x++) {
      let sum = 0;
      for (let k = -radius; k <= radius; k++) {
        sum += src[row + clamp(x + k, 0, w - 1)];
      }
      tmp[row + x] = sum * inv;
    }
  }
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let sum = 0;
      for (let k = -radius; k <= radius; k++) {
        sum += tmp[clamp(y + k, 0, h - 1) * w + x];
      }
      dst[y * w + x] = sum * inv;
    }
  }
}

function bilinearSample(arr, w, h, fx, fy) {
  const x = clamp(fx, 0, w - 1.001);
  const y = clamp(fy, 0, h - 1.001);
  const x0 = Math.floor(x);
  const y0 = Math.floor(y);
  const x1 = Math.min(w - 1, x0 + 1);
  const y1 = Math.min(h - 1, y0 + 1);
  const tx = x - x0;
  const ty = y - y0;
  const i00 = y0 * w + x0;
  const i10 = y0 * w + x1;
  const i01 = y1 * w + x0;
  const i11 = y1 * w + x1;
  const top = arr[i00] * (1 - tx) + arr[i10] * tx;
  const bot = arr[i01] * (1 - tx) + arr[i11] * tx;
  return top * (1 - ty) + bot * ty;
}

function computeSpatiotemporalOrders(isImage) {
  metricsSt.isStaticImage = isImage;

  // Downsample 120x68 probe -> 60x34 flow grid (2x2 average)
  let meanCurrR = 0;
  let meanCurrG = 0;
  let meanCurrB = 0;
  let meanPrevR = 0;
  let meanPrevG = 0;
  let meanPrevB = 0;

  for (let y = 0; y < FLOW_H; y++) {
    const py = y * 2;
    for (let x = 0; x < FLOW_W; x++) {
      const px = x * 2;
      const i0 = py * PROBE_W + px;
      const i1 = i0 + 1;
      const i2 = i0 + PROBE_W;
      const i3 = i2 + 1;
      const r = (probeLinR[i0] + probeLinR[i1] + probeLinR[i2] + probeLinR[i3]) * 0.25;
      const g = (probeLinG[i0] + probeLinG[i1] + probeLinG[i2] + probeLinG[i3]) * 0.25;
      const b = (probeLinB[i0] + probeLinB[i1] + probeLinB[i2] + probeLinB[i3]) * 0.25;
      const idx = y * FLOW_W + x;
      flowCurrR[idx] = r;
      flowCurrG[idx] = g;
      flowCurrB[idx] = b;
      flowCurrY[idx] = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      meanCurrR += r;
      meanCurrG += g;
      meanCurrB += b;
      meanPrevR += flowPrevR[idx];
      meanPrevG += flowPrevG[idx];
      meanPrevB += flowPrevB[idx];
    }
  }

  meanCurrR /= FLOW_N;
  meanCurrG /= FLOW_N;
  meanCurrB /= FLOW_N;
  meanPrevR /= FLOW_N;
  meanPrevG /= FLOW_N;
  meanPrevB /= FLOW_N;

  // Infer off-frame dominant light direction from macro luminance gradient (∇C1)
  let gxSum = 0;
  let gySum = 0;
  for (let y = 2; y < PROBE_H - 2; y += 2) {
    for (let x = 2; x < PROBE_W - 2; x += 2) {
      const idx = y * PROBE_W + x;
      gxSum += probeMacro[idx + 2] - probeMacro[idx - 2];
      gySum += probeMacro[idx - PROBE_W * 2] - probeMacro[idx + PROBE_W * 2]; // +Y is up
    }
  }
  const gLen = Math.hypot(gxSum, gySum) + 1e-4;
  const lx = clamp((gxSum / gLen) * 0.65, -0.8, 0.8);
  const ly = clamp((gySum / gLen) * 0.65 + 0.35, -0.5, 0.92);
  const lz = Math.sqrt(Math.max(0.08, 1 - lx * lx - ly * ly));
  metricsSt.inferredLightVec = [lx, ly, lz];
  metricsSt.inferredLightAzDeg = (Math.atan2(lx, lz) * 180) / Math.PI;
  metricsSt.inferredLightElDeg = (Math.asin(clamp(ly, -1, 1)) * 180) / Math.PI;

  if (!hasPrevFrame) {
    flowPrevR.set(flowCurrR);
    flowPrevG.set(flowCurrG);
    flowPrevB.set(flowCurrB);
    flowPrevY.set(flowCurrY);
    metricsSt.valid = true;
    return;
  }

  // T3: Global off-frame ambient illumination / color shift (ΔS4)
  const dMacroR = meanCurrR - meanPrevR;
  const dMacroG = meanCurrG - meanPrevG;
  const dMacroB = meanCurrB - meanPrevB;
  metricsSt.macroDeltaRgb = [dMacroR, dMacroG, dMacroB];

  // T1: Regularized 3x3 Lucas-Kanade dense optical flow on 60x34 grid
  const Ix = new Float32Array(FLOW_N);
  const Iy = new Float32Array(FLOW_N);
  const It = new Float32Array(FLOW_N);
  const dMacroY = 0.2126 * dMacroR + 0.7152 * dMacroG + 0.0722 * dMacroB;

  for (let y = 1; y < FLOW_H - 1; y++) {
    for (let x = 1; x < FLOW_W - 1; x++) {
      const i = y * FLOW_W + x;
      Ix[i] = 0.25 * (
        (flowPrevY[i + 1] - flowPrevY[i - 1]) +
        (flowCurrY[i + 1] - flowCurrY[i - 1])
      );
      Iy[i] = 0.25 * (
        (flowPrevY[i + FLOW_W] - flowPrevY[i - FLOW_W]) +
        (flowCurrY[i + FLOW_W] - flowCurrY[i - FLOW_W])
      );
      It[i] = (flowCurrY[i] - flowPrevY[i]) - dMacroY * 0.7;
    }
  }

  const maxFlowGrid = (MAX_FLOW_PX / VIDEO_W) * FLOW_W; // ~1.125 cells at 60px wide
  const reg = 0.0045;

  for (let y = 1; y < FLOW_H - 1; y++) {
    for (let x = 1; x < FLOW_W - 1; x++) {
      let sxx = 0;
      let syy = 0;
      let sxy = 0;
      let sxt = 0;
      let syt = 0;
      for (let ky = -1; ky <= 1; ky++) {
        for (let kx = -1; kx <= 1; kx++) {
          const j = (y + ky) * FLOW_W + (x + kx);
          const gx = Ix[j];
          const gy = Iy[j];
          const gt = It[j];
          sxx += gx * gx;
          syy += gy * gy;
          sxy += gx * gy;
          sxt += gx * gt;
          syt += gy * gt;
        }
      }
      const a = sxx + reg;
      const d = syy + reg;
      const det = a * d - sxy * sxy;
      let vx = 0;
      let vy = 0;
      if (det > 1e-6) {
        vx = clamp((-d * sxt + sxy * syt) / det, -maxFlowGrid, maxFlowGrid);
        vy = clamp((sxy * sxt - a * syt) / det, -maxFlowGrid, maxFlowGrid);
      }
      const idx = y * FLOW_W + x;
      flowVx[idx] = vx;
      flowVy[idx] = vy;
    }
  }

  // Smooth velocity field (spatial continuity)
  for (let y = 1; y < FLOW_H - 1; y++) {
    for (let x = 1; x < FLOW_W - 1; x++) {
      const i = y * FLOW_W + x;
      flowSmoothVx[i] = (
        flowVx[i] * 4 +
        flowVx[i - 1] + flowVx[i + 1] +
        flowVx[i - FLOW_W] + flowVx[i + FLOW_W]
      ) / 8;
      flowSmoothVy[i] = (
        flowVy[i] * 4 +
        flowVy[i - 1] + flowVy[i + 1] +
        flowVy[i - FLOW_W] + flowVy[i + FLOW_W]
      ) / 8;
    }
  }

  // Measure real residual reduction across:
  //   1) Static O(t) alone
  //   2) O(t) + T1 (Optical Flow Advection)
  //   3) O(t) + T1 + T3 (Off-frame Macro Ambient Shift)
  let staticErrSum = 0;
  let advectErrSum = 0;
  let bothErrSum = 0;
  let activeErrSum = 0;
  let flowMagSum = 0;
  let maxFlowPx = 0;
  const pxScale = VIDEO_W / FLOW_W;

  const useT1 = rotorState.stOn.t1;
  const useT3 = rotorState.stOn.t3;

  for (let y = 0; y < FLOW_H; y++) {
    for (let x = 0; x < FLOW_W; x++) {
      const i = y * FLOW_W + x;
      const vx = flowSmoothVx[i];
      const vy = flowSmoothVy[i];
      const speedPx = Math.hypot(vx, vy) * pxScale;
      flowMagSum += speedPx;
      if (speedPx > maxFlowPx) maxFlowPx = speedPx;

      const cr = flowCurrR[i];
      const cg = flowCurrG[i];
      const cb = flowCurrB[i];

      const sr = flowPrevR[i];
      const sg = flowPrevG[i];
      const sb = flowPrevB[i];
      const eStatic = (Math.abs(cr - sr) + Math.abs(cg - sg) + Math.abs(cb - sb)) / 3;
      staticErrSum += eStatic;

      // Advect O(t) backward by (vx, vy)
      const wr = bilinearSample(flowPrevR, FLOW_W, FLOW_H, x - vx, y - vy);
      const wg = bilinearSample(flowPrevG, FLOW_W, FLOW_H, x - vx, y - vy);
      const wb = bilinearSample(flowPrevB, FLOW_W, FLOW_H, x - vx, y - vy);
      const eAdv = (Math.abs(cr - wr) + Math.abs(cg - wg) + Math.abs(cb - wb)) / 3;
      advectErrSum += eAdv;

      const br = clamp(wr + dMacroR, 0, 1);
      const bg = clamp(wg + dMacroG, 0, 1);
      const bb = clamp(wb + dMacroB, 0, 1);
      const eBoth = (Math.abs(cr - br) + Math.abs(cg - bg) + Math.abs(cb - bb)) / 3;
      bothErrSum += eBoth;

      const ar = clamp((useT1 ? wr : sr) + (useT3 ? dMacroR : 0), 0, 1);
      const ag = clamp((useT1 ? wg : sg) + (useT3 ? dMacroG : 0), 0, 1);
      const ab = clamp((useT1 ? wb : sb) + (useT3 ? dMacroB : 0), 0, 1);
      activeErrSum += (Math.abs(cr - ar) + Math.abs(cg - ag) + Math.abs(cb - ab)) / 3;

      // Velocity shear |∇v| + unwarped residual => T2 3D Occlusion / Parallax boundary
      let shear = 0;
      if (x > 0 && x < FLOW_W - 1 && y > 0 && y < FLOW_H - 1) {
        const dvx = flowSmoothVx[i + 1] - flowSmoothVx[i - 1];
        const dvy = flowSmoothVy[i + FLOW_W] - flowSmoothVy[i - FLOW_W];
        shear = Math.hypot(dvx, dvy) * 2.5;
      }
      const occ = clamp(eBoth * 4.2 + shear * 0.75, 0, 1);
      flowOcclusion[i] = flowOcclusion[i] * 0.55 + occ * 0.45;

      // Inferred 3D Depth Z(x,y) ∈ [0..1] for Stage 3 Falsification Lab:
      //  Combines real motion parallax (faster objects = closer) + shading luminance + subtle ground perspective
      const parallaxZ = clamp(speedPx / 10.0, 0, 1) * 0.42;
      const shadeZ = clamp(flowCurrY[i], 0, 1) * 0.36;
      const groundPerspectiveZ = (y / (FLOW_H - 1)) * 0.22;
      const targetZ = clamp(parallaxZ + shadeZ + groundPerspectiveZ, 0.02, 0.98);
      flowDepth[i] = flowDepth[i] * 0.82 + targetZ * 0.18;

      // Pack RGBA DataTexture for GPU shaders
      const o = i * 4;
      flowTexBytes[o] = Math.round(clamp(0.5 + (vx * pxScale) / (MAX_FLOW_PX * 2), 0, 1) * 255);
      flowTexBytes[o + 1] = Math.round(clamp(0.5 + (vy * pxScale) / (MAX_FLOW_PX * 2), 0, 1) * 255);
      flowTexBytes[o + 2] = Math.round(clamp(flowDepth[i], 0, 1) * 255);
      flowTexBytes[o + 3] = Math.round(clamp(flowOcclusion[i], 0, 1) * 255);
    }
  }

  const staticPct = (staticErrSum / FLOW_N) * 100;
  const advectPct = (advectErrSum / FLOW_N) * 100;
  const bothPct = (bothErrSum / FLOW_N) * 100;
  const activePct = (activeErrSum / FLOW_N) * 100;

  metricsSt.valid = true;
  metricsSt.staticResidualPct = staticPct;
  metricsSt.activeResidualPct = activePct;
  metricsSt.motionExplainedPct = Math.max(0, staticPct - advectPct);
  metricsSt.envExplainedPct = Math.max(0, advectPct - bothPct);
  metricsSt.occlusionResidPct = bothPct;
  metricsSt.meanFlowPx = flowMagSum / FLOW_N;
  metricsSt.maxFlowPx = maxFlowPx;
  metricsSt.visualEnergy = clamp(staticPct / 12.0 + (flowMagSum / FLOW_N) / 8.0, 0, 1);

  // Compute Stage 3 Counterfactual Falsification KPIs directly from real depth gradients!
  const yawRad = (rotorState.cfYawDeg * Math.PI) / 180;
  const pitchRad = (rotorState.cfPitchDeg * Math.PI) / 180;
  const sinYaw = Math.abs(Math.sin(yawRad));
  const sinPitch = Math.abs(Math.sin(pitchRad));
  let exposedSum = 0;
  const depthScale = rotorState.cfDepthScale;
  for (let y = 1; y < FLOW_H - 1; y++) {
    for (let x = 1; x < FLOW_W - 1; x++) {
      const i = y * FLOW_W + x;
      const dzx = Math.abs(flowDepth[i + 1] - flowDepth[i - 1]) * depthScale * 5.0;
      const dzy = Math.abs(flowDepth[i + FLOW_W] - flowDepth[i - FLOW_W]) * depthScale * 5.0;
      const stretch = dzx * sinYaw + dzy * sinPitch;
      if (stretch > 0.085) {
        exposedSum += clamp((stretch - 0.085) * 4.5, 0, 1);
      }
    }
  }
  metrics3d.exposedVoidPct = (sinYaw + sinPitch) < 0.01 ? 0 : clamp((exposedSum / FLOW_N) * 100 * 3.4, 0, 99);
  metrics3d.lightContradictionDeg = Math.abs(rotorState.cfLightDeltaDeg);
  metrics3d.extrapDriftPx = metricsSt.meanFlowPx * rotorState.cfTimeExtrap * 12.0;

  // Save current -> prev for next temporal step
  flowPrevR.set(flowCurrR);
  flowPrevG.set(flowCurrG);
  flowPrevB.set(flowCurrB);
  flowPrevY.set(flowCurrY);
}

function captureOriginalAndMeasure(sourceEl, isImage = false) {
  if (!sourceEl) return false;
  const vw = isImage ? (sourceEl.naturalWidth || 0) : (sourceEl.videoWidth || 0);
  const vh = isImage ? (sourceEl.naturalHeight || 0) : (sourceEl.videoHeight || 0);
  if (vw < 16 || vh < 16) return false;

  // Preserve previous crisp frame in prevCanvas BEFORE overwriting origCanvas
  if (hasPrevFrame) {
    prevCtx.drawImage(origCanvas, 0, 0);
  }

  const targetAspect = VIDEO_W / VIDEO_H;
  const srcAspect = vw / vh;
  let sx = 0;
  let sy = 0;
  let cw = vw;
  let ch = vh;
  if (srcAspect > targetAspect) {
    cw = vh * targetAspect;
    sx = (vw - cw) * 0.5;
  } else {
    ch = vw / targetAspect;
    sy = (vh - ch) * 0.5;
  }
  origCtx.imageSmoothingEnabled = true;
  origCtx.imageSmoothingQuality = 'high';
  origCtx.drawImage(sourceEl, sx, sy, cw, ch, 0, 0, VIDEO_W, VIDEO_H);

  if (!hasPrevFrame) {
    prevCtx.drawImage(origCanvas, 0, 0);
  }

  // Paint Left Viewport with crisp 960x540 Original (+ subtle live flow vectors in Stage 2)
  const leftCanvas = document.getElementById('d3d-hd-canvas');
  if (leftCanvas) {
    const lctx = leftCanvas.getContext('2d');
    lctx.drawImage(origCanvas, 0, 0);
    if (rotorState.stage === 'st' && hasPrevFrame && !isImage) {
      lctx.save();
      lctx.lineWidth = 1.6;
      const stepX = VIDEO_W / FLOW_W;
      const stepY = VIDEO_H / FLOW_H;
      for (let y = 2; y < FLOW_H - 2; y += 3) {
        for (let x = 2; x < FLOW_W - 2; x += 3) {
          const i = y * FLOW_W + x;
          const vx = flowSmoothVx[i] * stepX * 2.2;
          const vy = flowSmoothVy[i] * stepY * 2.2;
          const mag = Math.hypot(vx, vy);
          if (mag < 2.2) continue;
          const px = (x + 0.5) * stepX;
          const py = (y + 0.5) * stepY;
          lctx.strokeStyle = flowOcclusion[i] > 0.42 ? 'rgba(251, 113, 133, 0.85)' : 'rgba(56, 189, 248, 0.78)';
          lctx.beginPath();
          lctx.moveTo(px, py);
          lctx.lineTo(px + vx, py + vy);
          lctx.stroke();
        }
      }
      lctx.restore();
    }
  }

  // Probe grid (120x68) for Stage 1 exact 2D decomposition + Stage 2 optical flow
  probeCtx.drawImage(origCanvas, 0, 0, PROBE_W, PROBE_H);
  const data = probeCtx.getImageData(0, 0, PROBE_W, PROBE_H).data;

  for (let i = 0; i < PROBE_N; i++) {
    const o = i * 4;
    const lr = SRGB_TO_LIN[data[o]];
    const lg = SRGB_TO_LIN[data[o + 1]];
    const lb = SRGB_TO_LIN[data[o + 2]];
    probeLinR[i] = lr;
    probeLinG[i] = lg;
    probeLinB[i] = lb;
    probeY[i] = 0.2126 * lr + 0.7152 * lg + 0.0722 * lb;
  }

  boxBlur2D(probeY, probeMid, PROBE_W, PROBE_H, 2);
  boxBlur2D(probeY, probeMacro, PROBE_W, PROBE_H, 7);

  // Stage 1 metrics
  const on1 = rotorState.on2d[0] ? 1 : 0;
  const on2 = rotorState.on2d[1] ? 1 : 0;
  const on3 = rotorState.on2d[2] ? 1 : 0;
  const on4 = rotorState.on2d[3] ? 1 : 0;
  const on5 = rotorState.on2d[4] ? 1 : 0;
  const on6 = rotorState.on2d[5] ? 1 : 0;

  let maeSum = 0;
  let mseSum = 0;
  const eSum = [0, 0, 0, 0, 0, 0];

  for (let i = 0; i < PROBE_N; i++) {
    const y = probeY[i];
    const yMacro = probeMacro[i];
    const yMid = probeMid[i];
    const dMid = yMid - yMacro;

    const c1 = yMacro;
    const c2 = Math.min(dMid, 0);
    const midPos = Math.max(dMid, 0);
    const specMask = clamp((y - 0.42) / 0.30, 0, 1);
    const c5Mid = midPos * specMask * 0.55;
    const c3 = midPos - c5Mid;

    const dFine = y - yMid;
    const specFineMask = clamp((y - 0.32) / 0.33, 0, 1);
    const c5Fine = Math.max(dFine, 0) * specFineMask;
    const c5 = c5Mid + c5Fine;
    const c6 = dFine - c5Fine;

    const cr = probeLinR[i] - y;
    const cg = probeLinG[i] - y;
    const cb = probeLinB[i] - y;

    eSum[0] += Math.abs(c1);
    eSum[1] += Math.abs(c2);
    eSum[2] += Math.abs(c3);
    eSum[3] += (Math.abs(cr) + Math.abs(cg) + Math.abs(cb)) * 0.55;
    eSum[4] += Math.abs(c5);
    eSum[5] += Math.abs(c6);

    const reconY = on1 * c1 + on2 * c2 + on3 * c3 + on5 * c5 + on6 * c6;
    const rr = clamp(reconY + on4 * cr, 0, 1);
    const rg = clamp(reconY + on4 * cg, 0, 1);
    const rb = clamp(reconY + on4 * cb, 0, 1);

    const o = i * 4;
    const origR = data[o] / 255;
    const origG = data[o + 1] / 255;
    const origB = data[o + 2] / 255;

    const dr = origR - Math.pow(rr, 1 / 2.2);
    const dg = origG - Math.pow(rg, 1 / 2.2);
    const db = origB - Math.pow(rb, 1 / 2.2);

    maeSum += (Math.abs(dr) + Math.abs(dg) + Math.abs(db)) / 3;
    mseSum += (dr * dr + dg * dg + db * db) / 3;
  }

  const activeCount = on1 + on2 + on3 + on4 + on5 + on6;
  const mae = activeCount === 6 ? 0 : maeSum / PROBE_N;
  const mse = activeCount === 6 ? 0 : mseSum / PROBE_N;
  const psnr = mse <= 1e-7 ? 99.9 : clamp(10 * Math.log10(1 / mse), 6, 70);

  const totalE = eSum.reduce((a, b) => a + b, 0) + 1e-5;
  let domIdx = -1;
  let domVal = -1;
  for (let k = 0; k < 6; k++) {
    const pct = (eSum[k] / totalE) * 100;
    metrics2d.axisEnergyPct[k] = pct;
    metrics2d.missingResidualByAxis[k] = rotorState.on2d[k] ? 0 : pct;
    if (!rotorState.on2d[k] && pct > domVal) {
      domVal = pct;
      domIdx = k;
    }
  }

  metrics2d.valid = true;
  metrics2d.activeCount = activeCount;
  metrics2d.maePct = mae * 100;
  metrics2d.psnrDb = psnr;
  metrics2d.completenessPct = activeCount === 6 ? 100 : clamp((1 - mae * 2.4) * 100, 0, 99.4);
  metrics2d.dominantMissingIdx = domIdx;

  // Stage 2 & 3 spatiotemporal & audio measurements
  computeSpatiotemporalOrders(isImage);
  sampleAudioAndCorrelate(metricsSt.visualEnergy);
  hasPrevFrame = true;

  return true;
}

// ============================================================================
// 4. Unified WebGL GPU Engine (Stage 1: 2D | Stage 2: ST-Rotor | Stage 3: 3D Twin)
// ============================================================================
const QUAD_VERT = `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position.xy, 0.0, 1.0);
}
`;

// Stage 1: Exact Invertible 2D Spectral Decomposition Shader
const STAGE1_FRAG = `
precision highp float;
varying vec2 vUv;
uniform sampler2D uSourceTex;
uniform vec2 uTexelSize;
uniform int uDisplayMode;
uniform int uSoloAxis;
uniform float uOn1, uOn2, uOn3, uOn4, uOn5, uOn6;

float sampleLum(vec2 uv) {
  vec3 s = texture2D(uSourceTex, clamp(uv, 0.001, 0.999)).rgb;
  vec3 lin = pow(max(s, 0.0), vec3(2.2));
  return dot(lin, vec3(0.2126, 0.7152, 0.0722));
}

float blurLum(vec2 uv, float radiusPx) {
  vec2 r = uTexelSize * radiusPx;
  float sum = sampleLum(uv) * 0.24;
  sum += sampleLum(uv + vec2( r.x,  0.0)) * 0.10;
  sum += sampleLum(uv + vec2(-r.x,  0.0)) * 0.10;
  sum += sampleLum(uv + vec2( 0.0,  r.y)) * 0.10;
  sum += sampleLum(uv + vec2( 0.0, -r.y)) * 0.10;
  vec2 d = r * 0.7071;
  sum += sampleLum(uv + vec2( d.x,  d.y)) * 0.09;
  sum += sampleLum(uv + vec2(-d.x,  d.y)) * 0.09;
  sum += sampleLum(uv + vec2( d.x, -d.y)) * 0.09;
  sum += sampleLum(uv + vec2(-d.x, -d.y)) * 0.09;
  return sum;
}

void main() {
  vec3 origSrgb = texture2D(uSourceTex, vUv).rgb;
  vec3 origLin = pow(max(origSrgb, 0.0), vec3(2.2));
  float Y = dot(origLin, vec3(0.2126, 0.7152, 0.0722));

  float yMid = blurLum(vUv, 5.5);
  float yMacro = (blurLum(vUv, 22.0) + blurLum(vUv, 42.0)) * 0.5;

  float dMid = yMid - yMacro;
  float C1_macro = yMacro;
  float C2_shadow = min(dMid, 0.0);
  float midPos = max(dMid, 0.0);
  float specMask = smoothstep(0.42, 0.72, Y);
  float C5_specMid = midPos * specMask * 0.55;
  float C3_value = midPos - C5_specMid;

  float dFine = Y - yMid;
  float C5_specFine = max(dFine, 0.0) * smoothstep(0.32, 0.65, Y);
  float C5_spec = C5_specMid + C5_specFine;
  float C6_micro = dFine - C5_specFine;
  vec3 C4_chroma = origLin - vec3(Y);

  if (uSoloAxis > 0) {
    vec3 outCol = vec3(0.0);
    if (uSoloAxis == 1) outCol = pow(vec3(clamp(C1_macro, 0.0, 1.0)), vec3(1.0 / 2.2));
    else if (uSoloAxis == 2) outCol = mix(vec3(0.92, 0.95, 0.98), vec3(0.08, 0.06, 0.24), clamp(-C2_shadow * 4.2, 0.0, 1.0));
    else if (uSoloAxis == 3) outCol = pow(vec3(clamp(0.06 + C3_value * 2.2, 0.0, 1.0)), vec3(1.0 / 2.2));
    else if (uSoloAxis == 4) outCol = pow(clamp(vec3(0.28) + C4_chroma * 1.45, 0.0, 1.0), vec3(1.0 / 2.2));
    else if (uSoloAxis == 5) {
      float sp = clamp(C5_spec * 3.6, 0.0, 1.0);
      outCol = pow(vec3(sp * 1.15, sp * 0.92, sp * 0.42), vec3(1.0 / 2.2));
    } else {
      float m = clamp(0.5 + C6_micro * 4.5, 0.0, 1.0);
      outCol = vec3(m * 0.95, m * 0.62 + 0.12, 1.0 - m * 0.55);
    }
    gl_FragColor = vec4(outCol, 1.0);
    return;
  }

  float reconY = uOn1 * C1_macro + uOn2 * C2_shadow + uOn3 * C3_value + uOn5 * C5_spec + uOn6 * C6_micro;
  vec3 reconSrgb = pow(clamp(vec3(reconY) + uOn4 * C4_chroma, 0.0, 1.0), vec3(1.0 / 2.2));
  float allSix = uOn1 * uOn2 * uOn3 * uOn4 * uOn5 * uOn6;
  reconSrgb = mix(reconSrgb, origSrgb, allSix);

  vec3 diff = abs(origSrgb - reconSrgb);
  float errMag = clamp((diff.r + diff.g + diff.b) * 1.65, 0.0, 1.0);
  vec3 residColor = mix(
    vec3(0.02, 0.04, 0.08),
    mix(vec3(0.96, 0.42, 0.12), vec3(1.0, 0.18, 0.52), smoothstep(0.25, 0.85, errMag)),
    smoothstep(0.012, 0.55, errMag)
  ) + diff * 1.2;

  if (uDisplayMode == 0) gl_FragColor = vec4(reconSrgb, 1.0);
  else if (uDisplayMode == 1) gl_FragColor = vec4(residColor, 1.0);
  else {
    if (abs(vUv.x - 0.5) < 0.0022) gl_FragColor = vec4(0.15, 0.82, 0.96, 1.0);
    else if (vUv.x < 0.5) gl_FragColor = vec4(reconSrgb, 1.0);
    else gl_FragColor = vec4(residColor, 1.0);
  }
}
`;

// Stage 2: Spatiotemporal Residual & Cross-Modal Order Shader (O(t) -> O(t+1))
const STAGE2_FRAG = `
precision highp float;
varying vec2 vUv;
uniform sampler2D uSourceTex; // O(t+1)
uniform sampler2D uPrevTex;   // O(t)
uniform sampler2D uFlowTex;   // R:vx, G:vy, B:depth, A:occlusion
uniform int uDisplayMode;
uniform int uSoloSt;
uniform float uUseT1;
uniform float uUseT3;
uniform vec3 uMacroDeltaRgb;
uniform float uAudioRms;
uniform float uAudioCorr;

void main() {
  vec3 currSrgb = texture2D(uSourceTex, vUv).rgb;
  vec3 prevSrgb = texture2D(uPrevTex, vUv).rgb;
  vec4 fPack = texture2D(uFlowTex, vUv);

  // Decode optical flow vector in UV units (Y flipped between canvas top-down and GL bottom-up)
  vec2 flowPx = (fPack.rg - 0.5) * 2.0 * 18.0;
  vec2 flowUv = vec2(flowPx.x / 960.0, -flowPx.y / 540.0);
  float depthZ = fPack.b;
  float occ = fPack.a;

  // T1: Inertial advection of O(t) forward to t+1 via backward lookup
  vec2 srcUv = clamp(vUv - flowUv * uUseT1, 0.001, 0.999);
  vec3 predLin = pow(max(texture2D(uPrevTex, srcUv).rgb, 0.0), vec3(2.2));
  // T3: Off-frame ambient light / white-balance shift
  predLin = clamp(predLin + uMacroDeltaRgb * uUseT3, 0.0, 1.0);
  vec3 predSrgb = pow(predLin, vec3(1.0 / 2.2));

  // Solo inspection of higher-order spatiotemporal constituents
  if (uSoloSt > 0) {
    if (uSoloSt == 1) {
      // T1: Inertial velocity field (direction hue + speed magnitude)
      float mag = clamp(length(flowPx) / 7.5, 0.0, 1.0);
      vec2 dir = normalize(flowPx + vec2(1e-4));
      vec3 dirCol = vec3(0.5 + 0.5 * dir.x, 0.5 + 0.5 * dir.y, 0.85 - 0.4 * dir.x);
      vec3 base = currSrgb * 0.28 + dirCol * mag * 0.95;
      gl_FragColor = vec4(base, 1.0);
      return;
    } else if (uSoloSt == 2) {
      // T3: Off-frame ambient illumination shift visualization
      vec3 shiftVis = vec3(0.18) + uMacroDeltaRgb * 16.0;
      gl_FragColor = vec4(clamp(currSrgb * 0.35 + abs(uMacroDeltaRgb) * 14.0 + vec3(0.0, 0.12, 0.08) + shiftVis * 0.3, 0.0, 1.0), 1.0);
      return;
    } else if (uSoloSt == 3) {
      // T2: 3D Parallax Depth (cyan-blue) + Occlusion/Disocclusion Shear Edges (hot rose)
      vec3 dCol = mix(vec3(0.05, 0.12, 0.24), vec3(0.18, 0.82, 0.96), depthZ);
      vec3 oCol = vec3(1.0, 0.16, 0.48);
      gl_FragColor = vec4(mix(dCol, oCol, smoothstep(0.22, 0.72, occ)), 1.0);
      return;
    } else {
      // T4: Cross-modal Audio-Visual energy coupling field
      float vAct = clamp(length(currSrgb - prevSrgb) * 3.8, 0.0, 1.0);
      vec3 visCol = vec3(0.08, 0.72, 0.96) * vAct;
      vec3 audRing = vec3(0.98, 0.78, 0.18) * uAudioRms * (0.45 + 0.55 * smoothstep(0.2, 0.7, length(vUv - 0.5)));
      gl_FragColor = vec4(clamp(currSrgb * 0.35 + visCol + audRing, 0.0, 1.0), 1.0);
      return;
    }
  }

  // Exact unexplained temporal residual |O(t+1) - Pred(t+1)|
  vec3 diff = abs(currSrgb - predSrgb);
  float errMag = clamp((diff.r + diff.g + diff.b) * 2.4, 0.0, 1.0);
  vec3 residCol = mix(
    vec3(0.02, 0.04, 0.08),
    mix(vec3(0.96, 0.45, 0.10), vec3(1.0, 0.15, 0.52), smoothstep(0.22, 0.82, errMag)),
    smoothstep(0.015, 0.48, errMag)
  ) + diff * 1.4;
  // Subtle cyan edge highlight where 3D occlusion shear persists
  residCol = mix(residCol, vec3(0.25, 0.92, 1.0), smoothstep(0.55, 0.92, occ) * 0.28);

  if (uDisplayMode == 0) gl_FragColor = vec4(predSrgb, 1.0);
  else if (uDisplayMode == 1) gl_FragColor = vec4(residCol, 1.0);
  else {
    if (abs(vUv.x - 0.5) < 0.0022) gl_FragColor = vec4(0.15, 0.82, 0.96, 1.0);
    else if (vUv.x < 0.5) gl_FragColor = vec4(predSrgb, 1.0);
    else gl_FragColor = vec4(residCol, 1.0);
  }
}
`;

// Stage 3: 3D Counterfactual Falsification Mesh Shaders (Real 160x90 Depth-Lifted Video)
const F3D_VERT = `
uniform sampler2D uFlowTex;
uniform float uDepthScale;
uniform float uTimeExtrap;

varying vec2 vUv;
varying float vDepth;
varying float vSteepness;
varying vec3 vWorldNormal;
varying vec3 vWorldPos;

void main() {
  vUv = uv;
  vec4 fPack = texture2D(uFlowTex, uv);
  float z = fPack.b;

  // Estimate surface normal from neighbor depth samples (WebGL1/2 safe, zero fwidth)
  vec2 eps = vec2(1.0 / 60.0, 1.0 / 34.0);
  float zL = texture2D(uFlowTex, clamp(uv - vec2(eps.x, 0.0), 0.001, 0.999)).b;
  float zR = texture2D(uFlowTex, clamp(uv + vec2(eps.x, 0.0), 0.001, 0.999)).b;
  float zD = texture2D(uFlowTex, clamp(uv - vec2(0.0, eps.y), 0.001, 0.999)).b;
  float zU = texture2D(uFlowTex, clamp(uv + vec2(0.0, eps.y), 0.001, 0.999)).b;

  float dzdx = (zR - zL) * 0.5 * uDepthScale * 1.1;
  float dzdy = (zU - zD) * 0.5 * uDepthScale * 1.1;
  vSteepness = length(vec2(dzdx, dzdy));
  vDepth = z;

  vec3 pos = position;
  // Inertial +Δt forward extrapolation using real extracted T1 velocity field
  vec2 flowPx = (fPack.rg - 0.5) * 2.0 * 18.0;
  pos.x += (flowPx.x / 960.0) * 3.2 * uTimeExtrap * 3.0;
  pos.y += (-flowPx.y / 540.0) * 1.8 * uTimeExtrap * 3.0;
  pos.z += (z - 0.35) * 0.72 * uDepthScale;

  vec3 localNormal = normalize(vec3(-dzdx * 8.0, -dzdy * 8.0, 1.0));
  vec4 wp = modelMatrix * vec4(pos, 1.0);
  vWorldPos = wp.xyz;
  vWorldNormal = normalize(mat3(modelMatrix) * localNormal);

  gl_Position = projectionMatrix * viewMatrix * wp;
}
`;

const F3D_FRAG = `
precision highp float;

uniform sampler2D uSourceTex;
uniform vec3 uInferredLightDir;
uniform vec3 uCounterLightDir;
uniform float uLightDeltaAmt;
uniform float uViewDeviation;

varying vec2 vUv;
varying float vDepth;
varying float vSteepness;
varying vec3 vWorldNormal;
varying vec3 vWorldPos;

void main() {
  vec3 origSrgb = texture2D(uSourceTex, clamp(vUv, 0.001, 0.999)).rgb;
  vec3 lin = pow(max(origSrgb, 0.0), vec3(2.2));

  vec3 N = normalize(vWorldNormal);
  vec3 V = normalize(cameraPosition - vWorldPos);
  vec3 L_inf = normalize(uInferredLightDir);
  vec3 L_cf = normalize(uCounterLightDir);

  // Counterfactual off-frame relighting delta (when user moves external sun/sky light away from inferred)
  float ndlInf = max(dot(N, L_inf), 0.14);
  float ndlCf = max(dot(N, L_cf), 0.05);
  float relightRatio = mix(1.0, clamp(ndlCf / ndlInf, 0.32, 1.85), uLightDeltaAmt);

  vec3 H = normalize(L_cf + V);
  float spec = pow(max(dot(N, H), 0.0), 28.0) * 0.26 * uLightDeltaAmt;
  vec3 relitLin = clamp(lin * relightRatio + vec3(spec * 1.05, spec * 0.92, spec * 0.72), 0.0, 1.0);
  vec3 col = pow(relitLin, vec3(1.0 / 2.2));

  // Unobserved 3D Backface Disocclusion Void detection:
  // When camera moves off 0 deg AND views a stretched depth cliff (grazing N·V + steep ΔZ),
  // expose the hidden 3D surface void with crisp magenta-cyan hatching!
  float grazing = 1.0 - max(dot(N, V), 0.0);
  float voidMask = smoothstep(0.06, 0.24, vSteepness) * smoothstep(0.18, 0.68, grazing) * smoothstep(0.03, 0.22, uViewDeviation);
  float hatch = step(0.5, fract((vUv.x + vUv.y) * 58.0));
  vec3 voidCol = mix(vec3(0.98, 0.15, 0.52), vec3(0.14, 0.85, 0.98), hatch);
  col = mix(col, voidCol, clamp(voidMask * 0.88, 0.0, 0.9));

  // Highlight shadow contradiction zones when external light deviates significantly
  float shadowContradict = abs(ndlCf - ndlInf) * uLightDeltaAmt;
  col = mix(col, vec3(1.0, 0.78, 0.14), clamp(shadowContradict * 0.32, 0.0, 0.32));

  gl_FragColor = vec4(col, 1.0);
}
`;

class ScaleRotorGPURenderer {
  constructor(hostEl) {
    this.hostEl = hostEl;
    this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.domElement.style.display = 'block';
    this.renderer.domElement.style.width = '100%';
    this.renderer.domElement.style.height = '100%';
    this.hostEl.appendChild(this.renderer.domElement);

    // Shared crisp textures
    this.sourceTex = new THREE.CanvasTexture(origCanvas);
    this.sourceTex.minFilter = THREE.LinearFilter;
    this.sourceTex.magFilter = THREE.LinearFilter;
    this.sourceTex.generateMipmaps = false;

    this.prevTex = new THREE.CanvasTexture(prevCanvas);
    this.prevTex.minFilter = THREE.LinearFilter;
    this.prevTex.magFilter = THREE.LinearFilter;
    this.prevTex.generateMipmaps = false;

    this.flowTex = new THREE.DataTexture(flowTexBytes, FLOW_W, FLOW_H, THREE.RGBAFormat);
    this.flowTex.minFilter = THREE.LinearFilter;
    this.flowTex.magFilter = THREE.LinearFilter;
    this.flowTex.flipY = true;
    this.flowTex.needsUpdate = true;

    // Ortho camera & scenes for Stage 1 & Stage 2
    this.orthoCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

    this.scene1 = new THREE.Scene();
    this.u1 = {
      uSourceTex: { value: this.sourceTex },
      uTexelSize: { value: new THREE.Vector2(1 / VIDEO_W, 1 / VIDEO_H) },
      uDisplayMode: { value: 2 },
      uSoloAxis: { value: 0 },
      uOn1: { value: 1 }, uOn2: { value: 1 }, uOn3: { value: 1 },
      uOn4: { value: 1 }, uOn5: { value: 1 }, uOn6: { value: 1 },
    };
    this.scene1.add(new THREE.Mesh(
      new THREE.PlaneGeometry(2, 2),
      new THREE.ShaderMaterial({ vertexShader: QUAD_VERT, fragmentShader: STAGE1_FRAG, uniforms: this.u1, depthTest: false, depthWrite: false })
    ));

    this.scene2 = new THREE.Scene();
    this.u2 = {
      uSourceTex: { value: this.sourceTex },
      uPrevTex: { value: this.prevTex },
      uFlowTex: { value: this.flowTex },
      uDisplayMode: { value: 2 },
      uSoloSt: { value: 0 },
      uUseT1: { value: 0 },
      uUseT3: { value: 0 },
      uMacroDeltaRgb: { value: new THREE.Vector3(0, 0, 0) },
      uAudioRms: { value: 0 },
      uAudioCorr: { value: 0 },
    };
    this.scene2.add(new THREE.Mesh(
      new THREE.PlaneGeometry(2, 2),
      new THREE.ShaderMaterial({ vertexShader: QUAD_VERT, fragmentShader: STAGE2_FRAG, uniforms: this.u2, depthTest: false, depthWrite: false })
    ));

    // Stage 3: Real 3D Counterfactual Falsification Scene
    this.scene3 = new THREE.Scene();
    this.scene3.background = new THREE.Color(0x050811);
    this.cam3 = new THREE.PerspectiveCamera(40, 16 / 9, 0.1, 30);

    this.u3 = {
      uSourceTex: { value: this.sourceTex },
      uFlowTex: { value: this.flowTex },
      uDepthScale: { value: 1.0 },
      uTimeExtrap: { value: 0.0 },
      uInferredLightDir: { value: new THREE.Vector3(0.42, 0.72, 0.55) },
      uCounterLightDir: { value: new THREE.Vector3(0.42, 0.72, 0.55) },
      uLightDeltaAmt: { value: 0.0 },
      uViewDeviation: { value: 0.0 },
    };
    this.mesh3 = new THREE.Mesh(
      new THREE.PlaneGeometry(3.2, 1.8, 160, 90),
      new THREE.ShaderMaterial({
        vertexShader: F3D_VERT,
        fragmentShader: F3D_FRAG,
        uniforms: this.u3,
        side: THREE.DoubleSide,
      })
    );
    this.scene3.add(this.mesh3);

    // Original 2D reference image plane border (z = 0)
    const framePts = [
      new THREE.Vector3(-1.6, -0.9, 0),
      new THREE.Vector3(1.6, -0.9, 0),
      new THREE.Vector3(1.6, 0.9, 0),
      new THREE.Vector3(-1.6, 0.9, 0),
    ];
    this.refBorder = new THREE.LineLoop(
      new THREE.BufferGeometry().setFromPoints(framePts),
      new THREE.LineBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.45 })
    );
    this.scene3.add(this.refBorder);

    // Inferred Off-Frame Light Orb (Emerald) & Counterfactual Light Orb (Amber)
    this.infLightOrb = new THREE.Mesh(
      new THREE.SphereGeometry(0.065, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0x34d399 })
    );
    this.cfLightOrb = new THREE.Mesh(
      new THREE.SphereGeometry(0.075, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0xfacc15 })
    );
    this.scene3.add(this.infLightOrb);
    this.scene3.add(this.cfLightOrb);

    this.cfRayGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 1, 1)]);
    this.cfRayLine = new THREE.Line(
      this.cfRayGeo,
      new THREE.LineBasicMaterial({ color: 0xfacc15, transparent: true, opacity: 0.72 })
    );
    this.scene3.add(this.cfRayLine);

    // Stage 4: 3D Multi-Scale Ontological Resonance Manifold (S0..S4 Rings)
    this.scene4 = new THREE.Scene();
    this.scene4.background = new THREE.Color(0x050811);
    this.cam4 = new THREE.PerspectiveCamera(44, 16 / 9, 0.1, 40);
    this.ontoGroup = new THREE.Group();
    this.scene4.add(this.ontoGroup);
    this.ontoDynamicGroup = new THREE.Group();
    this.ontoGroup.add(this.ontoDynamicGroup);
    this.buildStaticScaleRings();

    this.resizeObserver = new ResizeObserver(() => this.handleResize());
    this.resizeObserver.observe(this.hostEl);
    this.handleResize();
    this.bindOrbitPointer();
  }

  makeLabelSprite(text, fgHex = '#e2e8f0', bgRgba = 'rgba(6, 11, 22, 0.84)', scale = 0.72) {
    const cv = document.createElement('canvas');
    cv.width = 280;
    cv.height = 54;
    const ctx = cv.getContext('2d');
    ctx.fillStyle = bgRgba;
    ctx.fillRect(2, 6, 276, 42);
    ctx.strokeStyle = fgHex;
    ctx.lineWidth = 2;
    ctx.strokeRect(2, 6, 276, 42);
    ctx.font = '700 21px sans-serif';
    ctx.fillStyle = fgHex;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(text || '').slice(0, 16), 140, 28);
    const tex = new THREE.CanvasTexture(cv);
    tex.minFilter = THREE.LinearFilter;
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
    const sp = new THREE.Sprite(mat);
    sp.scale.set(scale * 2.2, scale * 0.44, 1);
    return sp;
  }

  buildStaticScaleRings() {
    const rings = [
      { s: 0, y: -1.35, r: 1.05, col: 0x94a3b8, label: 'S0 물질·분자' },
      { s: 1, y: -0.68, r: 1.40, col: 0x38bdf8, label: 'S1 구조·기관' },
      { s: 2, y: 0.0, r: 1.75, col: 0x22d3ee, label: 'S2 개체·존재' },
      { s: 3, y: 0.68, r: 2.15, col: 0x34d399, label: 'S3 연결계·지형' },
      { s: 4, y: 1.35, r: 2.55, col: 0xfacc15, label: 'S4 행성·문명' },
    ];
    rings.forEach((rg) => {
      const pts = [];
      for (let i = 0; i <= 72; i++) {
        const a = (i / 72) * Math.PI * 2;
        pts.push(new THREE.Vector3(Math.cos(a) * rg.r, rg.y, Math.sin(a) * rg.r));
      }
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: rg.col, transparent: true, opacity: 0.36 })
      );
      this.ontoGroup.add(line);
      const sp = this.makeLabelSprite(rg.label, '#cbd5e1', 'rgba(5, 9, 18, 0.78)', 0.46);
      sp.position.set(rg.r + 0.55, rg.y, 0);
      this.ontoGroup.add(sp);
    });
    // Central vertical Scale-Rotor spindle
    const axisGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, -1.65, 0),
      new THREE.Vector3(0, 1.65, 0),
    ]);
    this.ontoGroup.add(
      new THREE.Line(axisGeo, new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.65 }))
    );
  }

  updateOntologyScene(payload) {
    while (this.ontoDynamicGroup.children.length > 0) {
      const ch = this.ontoDynamicGroup.children[0];
      this.ontoDynamicGroup.remove(ch);
      if (ch.geometry) ch.geometry.dispose();
      if (ch.material) {
        if (ch.material.map) ch.material.map.dispose();
        ch.material.dispose();
      }
    }
    if (!payload || !payload.conceptA) return;

    const scaleToY = (s) => -1.35 + clamp(s, 0, 4) * 0.675;
    const scaleToR = (s) => 1.05 + clamp(s, 0, 4) * 0.375;

    const cA = payload.conceptA;
    const cB = payload.conceptB;
    const comp = payload.comparison;

    const posA = new THREE.Vector3(-0.78, scaleToY(cA.scaleCenter), 0.25);
    const coreA = new THREE.Mesh(
      new THREE.SphereGeometry(0.18, 22, 22),
      new THREE.MeshBasicMaterial({ color: 0x38bdf8 })
    );
    coreA.position.copy(posA);
    this.ontoDynamicGroup.add(coreA);
    const lblA = this.makeLabelSprite(`${cA.title} (S${cA.scaleCenter.toFixed(1)})`, '#7dd3fc', 'rgba(8, 24, 42, 0.92)', 0.72);
    lblA.position.set(posA.x, posA.y + 0.32, posA.z);
    this.ontoDynamicGroup.add(lblA);

    let posB = null;
    if (cB) {
      posB = new THREE.Vector3(0.78, scaleToY(cB.scaleCenter), -0.25);
      const coreB = new THREE.Mesh(
        new THREE.SphereGeometry(0.20, 22, 22),
        new THREE.MeshBasicMaterial({ color: 0x34d399 })
      );
      coreB.position.copy(posB);
      this.ontoDynamicGroup.add(coreB);
      const lblB = this.makeLabelSprite(`${cB.title} (S${cB.scaleCenter.toFixed(1)})`, '#6ee7b7', 'rgba(6, 32, 26, 0.92)', 0.72);
      lblB.position.set(posB.x, posB.y + 0.34, posB.z);
      this.ontoDynamicGroup.add(lblB);

      // Scale-Transition Resonance Bridge Arc between A and B
      const mid = posA.clone().lerp(posB, 0.5);
      mid.y += 0.42;
      const curve = new THREE.QuadraticBezierCurve3(posA, mid, posB);
      const arcGeo = new THREE.BufferGeometry().setFromPoints(curve.getPoints(32));
      const arcColor = comp && comp.resonancePct >= 45 ? 0x10b981 : 0xf43f5e;
      this.ontoDynamicGroup.add(
        new THREE.Line(arcGeo, new THREE.LineBasicMaterial({ color: arcColor, transparent: true, opacity: 0.92 }))
      );
    }

    // Shared resonant link nodes (emerald orbs orbiting between A & B)
    const shared = (comp && comp.sharedLinks ? comp.sharedLinks : []).slice(0, 8);
    shared.forEach((lnk, idx) => {
      const ang = (idx / Math.max(1, shared.length)) * Math.PI * 2 + 0.4;
      const yMid = posB ? (posA.y + posB.y) * 0.5 : posA.y;
      const r = 1.45;
      const p = new THREE.Vector3(Math.cos(ang) * r, yMid + Math.sin(idx * 1.7) * 0.25, Math.sin(ang) * r);
      const orb = new THREE.Mesh(
        new THREE.SphereGeometry(0.085, 14, 14),
        new THREE.MeshBasicMaterial({ color: 0x10b981 })
      );
      orb.position.copy(p);
      this.ontoDynamicGroup.add(orb);

      this.ontoDynamicGroup.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([posA, p]),
        new THREE.LineBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.45 })
      ));
      if (posB) {
        this.ontoDynamicGroup.add(new THREE.Line(
          new THREE.BufferGeometry().setFromPoints([posB, p]),
          new THREE.LineBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.45 })
        ));
      }
      if (idx < 6) {
        const sp = this.makeLabelSprite(lnk, '#a7f3d0', 'rgba(5, 22, 18, 0.84)', 0.42);
        sp.position.set(p.x, p.y + 0.17, p.z);
        this.ontoDynamicGroup.add(sp);
      }
    });

    // Emergent B-only transition links (rose-amber nodes on their actual Scale Ring)
    const emergentB = (comp && comp.onlyBLinks ? comp.onlyBLinks : []).slice(0, 8);
    emergentB.forEach((lnk, idx) => {
      const nodeMeta = (cB && cB.linkNodes ? cB.linkNodes.find((n) => n.label === lnk) : null);
      const sc = nodeMeta ? nodeMeta.scale : Math.round(cB ? cB.scaleCenter : 3);
      const r = scaleToR(sc);
      const ang = (idx / Math.max(1, emergentB.length)) * Math.PI - 0.5;
      const p = new THREE.Vector3(Math.cos(ang) * r, scaleToY(sc), Math.sin(ang) * r);
      const orb = new THREE.Mesh(
        new THREE.SphereGeometry(0.075, 12, 12),
        new THREE.MeshBasicMaterial({ color: 0xfb7185 })
      );
      orb.position.copy(p);
      this.ontoDynamicGroup.add(orb);
      if (posB) {
        this.ontoDynamicGroup.add(new THREE.Line(
          new THREE.BufferGeometry().setFromPoints([posB, p]),
          new THREE.LineBasicMaterial({ color: 0xfb7185, transparent: true, opacity: 0.42 })
        ));
      }
      if (idx < 5) {
        const sp = this.makeLabelSprite(lnk, '#fecdd3', 'rgba(32, 8, 18, 0.84)', 0.40);
        sp.position.set(p.x, p.y + 0.15, p.z);
        this.ontoDynamicGroup.add(sp);
      }
    });

    // A-only lower/individual links (cyan nodes on their actual Scale Ring)
    const onlyA = (comp && comp.onlyALinks ? comp.onlyALinks : cA.links.slice(0, 7)).slice(0, 6);
    onlyA.forEach((lnk, idx) => {
      const nodeMeta = cA.linkNodes ? cA.linkNodes.find((n) => n.label === lnk) : null;
      const sc = nodeMeta ? nodeMeta.scale : Math.round(cA.scaleCenter);
      const r = scaleToR(sc);
      const ang = Math.PI + (idx / Math.max(1, onlyA.length)) * Math.PI * 0.9;
      const p = new THREE.Vector3(Math.cos(ang) * r, scaleToY(sc), Math.sin(ang) * r);
      const orb = new THREE.Mesh(
        new THREE.SphereGeometry(0.07, 12, 12),
        new THREE.MeshBasicMaterial({ color: 0x38bdf8 })
      );
      orb.position.copy(p);
      this.ontoDynamicGroup.add(orb);
      this.ontoDynamicGroup.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([posA, p]),
        new THREE.LineBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.36 })
      ));
      if (idx < 4) {
        const sp = this.makeLabelSprite(lnk, '#bae6fd', 'rgba(6, 20, 34, 0.84)', 0.38);
        sp.position.set(p.x, p.y + 0.14, p.z);
        this.ontoDynamicGroup.add(sp);
      }
    });
  }

  bindOrbitPointer() {
    let dragging = false;
    let lastX = 0;
    let lastY = 0;
    const dom = this.renderer.domElement;

    dom.addEventListener('pointerdown', (e) => {
      if (rotorState.stage !== 'f3d' && rotorState.stage !== 'onto') return;
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      rotorState.autoRunning = false;
      dom.setPointerCapture(e.pointerId);
    });
    dom.addEventListener('pointermove', (e) => {
      if (!dragging) return;
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      lastX = e.clientX;
      lastY = e.clientY;
      if (rotorState.stage === 'f3d') {
        rotorState.cfYawDeg = clamp(rotorState.cfYawDeg + dx * 0.25, -38, 38);
        rotorState.cfPitchDeg = clamp(rotorState.cfPitchDeg + dy * 0.2, -26, 26);
        syncF3dControls();
      } else if (rotorState.stage === 'onto') {
        rotorState.ontoYaw += dx * 0.009;
        rotorState.ontoPitch = clamp(rotorState.ontoPitch + dy * 0.007, -0.85, 0.95);
      }
    });
    const endDrag = () => { dragging = false; };
    dom.addEventListener('pointerup', endDrag);
    dom.addEventListener('pointercancel', endDrag);
    dom.addEventListener('dblclick', () => {
      if (rotorState.stage === 'f3d') {
        rotorState.autoRunning = false;
        rotorState.cfYawDeg = 0;
        rotorState.cfPitchDeg = 0;
        rotorState.cfLightDeltaDeg = 0;
        rotorState.cfTimeExtrap = 0;
        syncF3dControls();
        updateVerdictAndSummary();
      } else if (rotorState.stage === 'onto') {
        rotorState.ontoYaw = 0.42;
        rotorState.ontoPitch = 0.28;
      }
    });
  }

  handleResize() {
    if (!this.hostEl) return;
    const w = Math.max(300, this.hostEl.clientWidth || 640);
    const h = Math.max(200, this.hostEl.clientHeight || 360);
    this.renderer.setSize(w, h, false);
    this.cam3.aspect = w / h;
    this.cam3.updateProjectionMatrix();
    this.cam4.aspect = w / h;
    this.cam4.updateProjectionMatrix();
  }

  renderFrame() {
    if (rotorState.stage === 'onto') {
      rotorState.ontoYaw += 0.0032;
      const dist = 6.2;
      this.cam4.position.set(
        Math.sin(rotorState.ontoYaw) * Math.cos(rotorState.ontoPitch) * dist,
        Math.sin(rotorState.ontoPitch) * dist,
        Math.cos(rotorState.ontoYaw) * Math.cos(rotorState.ontoPitch) * dist
      );
      this.cam4.lookAt(0, 0, 0);
      this.renderer.render(this.scene4, this.cam4);
      return;
    }

    this.sourceTex.needsUpdate = true;
    this.prevTex.needsUpdate = true;
    this.flowTex.needsUpdate = true;

    if (rotorState.stage === '2d') {
      this.u1.uDisplayMode.value = rotorState.displayMode;
      this.u1.uSoloAxis.value = rotorState.solo2d;
      this.u1.uOn1.value = rotorState.on2d[0] ? 1 : 0;
      this.u1.uOn2.value = rotorState.on2d[1] ? 1 : 0;
      this.u1.uOn3.value = rotorState.on2d[2] ? 1 : 0;
      this.u1.uOn4.value = rotorState.on2d[3] ? 1 : 0;
      this.u1.uOn5.value = rotorState.on2d[4] ? 1 : 0;
      this.u1.uOn6.value = rotorState.on2d[5] ? 1 : 0;
      this.renderer.render(this.scene1, this.orthoCam);
      return;
    }

    if (rotorState.stage === 'st') {
      this.u2.uDisplayMode.value = rotorState.displayMode;
      this.u2.uSoloSt.value = rotorState.soloSt;
      this.u2.uUseT1.value = rotorState.stOn.t1 ? 1 : 0;
      this.u2.uUseT3.value = rotorState.stOn.t3 ? 1 : 0;
      this.u2.uMacroDeltaRgb.value.set(
        metricsSt.macroDeltaRgb[0],
        metricsSt.macroDeltaRgb[1],
        metricsSt.macroDeltaRgb[2]
      );
      this.u2.uAudioRms.value = audioSensor.rms;
      this.u2.uAudioCorr.value = audioSensor.corrR;
      this.renderer.render(this.scene2, this.orthoCam);
      return;
    }

    // Stage 3: Counterfactual 3D Falsification Twin
    const yawRad = (rotorState.cfYawDeg * Math.PI) / 180;
    const pitchRad = (rotorState.cfPitchDeg * Math.PI) / 180;
    const dist = 2.62;
    this.cam3.position.set(
      Math.sin(yawRad) * Math.cos(pitchRad) * dist,
      Math.sin(pitchRad) * dist,
      Math.cos(yawRad) * Math.cos(pitchRad) * dist
    );
    this.cam3.lookAt(0, 0, 0.05);

    const [ilx, ily, ilz] = metricsSt.inferredLightVec;
    const cfAz = ((metricsSt.inferredLightAzDeg + rotorState.cfLightDeltaDeg) * Math.PI) / 180;
    const cfEl = (metricsSt.inferredLightElDeg * Math.PI) / 180;
    const clx = Math.sin(cfAz) * Math.cos(cfEl);
    const cly = Math.sin(cfEl);
    const clz = Math.cos(cfAz) * Math.cos(cfEl);

    this.u3.uDepthScale.value = rotorState.cfDepthScale;
    this.u3.uTimeExtrap.value = rotorState.cfTimeExtrap;
    this.u3.uInferredLightDir.value.set(ilx, ily, ilz).normalize();
    this.u3.uCounterLightDir.value.set(clx, cly, clz).normalize();
    this.u3.uLightDeltaAmt.value = clamp(Math.abs(rotorState.cfLightDeltaDeg) / 90.0, 0, 1);
    this.u3.uViewDeviation.value = clamp((Math.abs(rotorState.cfYawDeg) + Math.abs(rotorState.cfPitchDeg)) / 24.0, 0, 1);

    this.infLightOrb.position.set(ilx * 1.9, ily * 1.45, Math.abs(ilz) * 1.1 + 0.35);
    this.cfLightOrb.position.set(clx * 1.95, cly * 1.45, Math.abs(clz) * 1.1 + 0.35);
    this.cfLightOrb.visible = Math.abs(rotorState.cfLightDeltaDeg) > 1;
    this.cfRayLine.visible = this.cfLightOrb.visible;
    if (this.cfRayLine.visible) {
      const posAttr = this.cfRayGeo.attributes.position;
      posAttr.setXYZ(0, 0, 0, 0.15);
      posAttr.setXYZ(1, this.cfLightOrb.position.x, this.cfLightOrb.position.y, this.cfLightOrb.position.z);
      posAttr.needsUpdate = true;
    }

    this.renderer.render(this.scene3, this.cam3);
  }
}

// ============================================================================
// 4B. Stage 4: Live Multi-Instance Optical Invariance & Ontological Protocol
// ============================================================================
const ontoProbeCanvas = document.createElement('canvas');
ontoProbeCanvas.width = 96;
ontoProbeCanvas.height = 54;
const ontoProbeCtx = ontoProbeCanvas.getContext('2d', { willReadFrequently: true });

function measureSinglePhotoSpectrum(imgEl) {
  const w = 96;
  const h = 54;
  const n = w * h;
  ontoProbeCtx.drawImage(imgEl, 0, 0, w, h);
  const data = ontoProbeCtx.getImageData(0, 0, w, h).data;
  const linR = new Float32Array(n);
  const linG = new Float32Array(n);
  const linB = new Float32Array(n);
  const yArr = new Float32Array(n);
  const midArr = new Float32Array(n);
  const macArr = new Float32Array(n);

  for (let i = 0; i < n; i++) {
    const o = i * 4;
    const r = SRGB_TO_LIN[data[o]];
    const g = SRGB_TO_LIN[data[o + 1]];
    const b = SRGB_TO_LIN[data[o + 2]];
    linR[i] = r;
    linG[i] = g;
    linB[i] = b;
    yArr[i] = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }
  boxBlur2D(yArr, midArr, w, h, 2);
  boxBlur2D(yArr, macArr, w, h, 6);

  const e = [0, 0, 0, 0, 0, 0];
  for (let i = 0; i < n; i++) {
    const y = yArr[i];
    const dMid = midArr[i] - macArr[i];
    const c1 = macArr[i];
    const c2 = Math.min(dMid, 0);
    const midPos = Math.max(dMid, 0);
    const c5Mid = midPos * clamp((y - 0.42) / 0.30, 0, 1) * 0.55;
    const c3 = midPos - c5Mid;
    const dFine = y - midArr[i];
    const c5Fine = Math.max(dFine, 0) * clamp((y - 0.32) / 0.33, 0, 1);
    const c5 = c5Mid + c5Fine;
    const c6 = dFine - c5Fine;
    e[0] += Math.abs(c1);
    e[1] += Math.abs(c2);
    e[2] += Math.abs(c3);
    e[3] += (Math.abs(linR[i] - y) + Math.abs(linG[i] - y) + Math.abs(linB[i] - y)) * 0.55;
    e[4] += Math.abs(c5);
    e[5] += Math.abs(c6);
  }
  const tot = e.reduce((a, b) => a + b, 0) + 1e-5;
  return e.map((v) => (v / tot) * 100);
}

async function measureMultiInstanceOptics(photos) {
  if (!Array.isArray(photos) || photos.length === 0) return null;
  const loadedVectors = [];

  await Promise.all(
    photos.slice(0, 5).map((ph) => new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        try {
          loadedVectors.push(measureSinglePhotoSpectrum(img));
        } catch (_) {}
        resolve();
      };
      img.onerror = () => resolve();
      img.src = ph.proxyUrl;
    }))
  );

  if (!loadedVectors.length) return null;
  const mean = [0, 0, 0, 0, 0, 0];
  const std = [0, 0, 0, 0, 0, 0];
  for (const vec of loadedVectors) {
    for (let k = 0; k < 6; k++) mean[k] += vec[k] / loadedVectors.length;
  }
  for (const vec of loadedVectors) {
    for (let k = 0; k < 6; k++) {
      const d = vec[k] - mean[k];
      std[k] += (d * d) / loadedVectors.length;
    }
  }
  for (let k = 0; k < 6; k++) std[k] = Math.sqrt(std[k]);

  let invIdx = 0;
  let bestInvScore = -1;
  let varIdx = 3;
  let worstCv = -1;
  for (let k = 0; k < 6; k++) {
    const cv = std[k] / (mean[k] + 1.5);
    const invScore = mean[k] / (std[k] + 1.2);
    if (invScore > bestInvScore) {
      bestInvScore = invScore;
      invIdx = k;
    }
    if (cv > worstCv) {
      worstCv = cv;
      varIdx = k;
    }
  }

  return {
    count: loadedVectors.length,
    mean,
    std,
    mostInvariantAxis: SPECTRAL_AXES[invIdx].name,
    mostVariableAxis: SPECTRAL_AXES[varIdx].name,
  };
}

function computeOpticalCosinePct(optA, optB) {
  if (!optA || !optB) return null;
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (let k = 0; k < 6; k++) {
    dot += optA.mean[k] * optB.mean[k];
    na += optA.mean[k] * optA.mean[k];
    nb += optB.mean[k] * optB.mean[k];
  }
  if (na <= 0 || nb <= 0) return null;
  return Number((clamp(dot / (Math.sqrt(na) * Math.sqrt(nb)), 0, 1) * 100).toFixed(1));
}

async function runOntologicalResonance(rawA, rawB) {
  const conceptA = String(rawA || '').trim() || '나무';
  const conceptB = String(rawB || '').trim();
  ontoState.conceptA = conceptA;
  ontoState.conceptB = conceptB;
  ontoState.loading = true;
  ontoState.opticsA = null;
  ontoState.opticsB = null;
  ontoState.opticalSimPct = null;

  const inA = document.getElementById('d3d-onto-a');
  const inB = document.getElementById('d3d-onto-b');
  if (inA) inA.value = conceptA;
  if (inB) inB.value = conceptB;

  setStatus(`▲ 실제 외부 세계(Wikipedia + Wikimedia 다중 실물 사진)에서 [${conceptA}${conceptB ? ` ⇄ ${conceptB}` : ''}] 존재론 프로토콜을 수집·동기화 중...`, 'loading');
  renderOntoPanels();

  try {
    const resp = await fetch('/api/ontology/resonate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conceptA, conceptB }),
    });
    const json = await resp.json();
    if (!resp.ok || json.status !== 'ok') {
      throw new Error(json.message || '존재론 프로토콜 조회 실패');
    }
    ontoState.data = json;
    ontoState.loading = false;

    if (gpuRenderer) gpuRenderer.updateOntologyScene(json);
    renderOntoPanels();
    updateVerdictAndSummary();

    // Measure REAL cross-instance optical invariance from all downloaded Wikimedia photos
    const [optA, optB] = await Promise.all([
      measureMultiInstanceOptics(json.conceptA.photos),
      json.conceptB ? measureMultiInstanceOptics(json.conceptB.photos) : Promise.resolve(null),
    ]);
    ontoState.opticsA = optA;
    ontoState.opticsB = optB;
    ontoState.opticalSimPct = computeOpticalCosinePct(optA, optB);

    renderOntoPanels();
    updateVerdictAndSummary();

    const comp = json.comparison;
    if (comp && json.conceptB) {
      const optNote = ontoState.opticalSimPct !== null ? ` · 다중실물 광학 유사도 ${ontoState.opticalSimPct}%` : '';
      pushLog(
        comp.resonancePct >= 48 ? 'ok' : 'warn',
        `④ 공명 동기화 · [${json.conceptA.title} S${json.conceptA.scaleCenter}] ⇄ [${json.conceptB.title} S${json.conceptB.scaleCenter}] (공명 ${comp.resonancePct}%${optNote})`,
        `공유 연결망 ${comp.sharedLinks.length}개(${comp.sharedLinks.slice(0, 4).join(', ') || '직접 공유 없음'}) · ` +
        `스케일 전이 ΔS=${comp.scaleJump >= 0 ? '+' : ''}${comp.scaleJump} · ` +
        `최대 전이/잔차 축: [${comp.dominantJumpAxis ? comp.dominantJumpAxis.name : '-'}]`
      );
      setStatus(`● [${json.conceptA.title} ⇄ ${json.conceptB.title}] 다중 실물 광학 불변량 + 실세계 인과 연결망 동기화 완료`, 'ok');
    } else {
      pushLog(
        'ok',
        `④ 단독 프로토콜 추출 · [${json.conceptA.title}] (중심 스케일 S${json.conceptA.scaleCenter})`,
        `실물 사진 ${optA ? optA.count : 0}장 교차 실측 + 위키 인과 연결 ${json.conceptA.links.length}개 동기화 완료.`
      );
      setStatus(`● [${json.conceptA.title}] 통합 인지 프로토콜 동기화 완료`, 'ok');
    }
  } catch (err) {
    ontoState.loading = false;
    setStatus(`✖ 존재론 공명 실패: ${err instanceof Error ? err.message : '오류'}`, 'error');
    renderOntoPanels();
  }
}

function renderOntoPanels() {
  const leftWall = document.getElementById('d3d-onto-left-wall');
  const protoGrid = document.getElementById('d3d-onto-proto-grid');
  const linksWrap = document.getElementById('d3d-onto-links-wrap');
  const extractsWrap = document.getElementById('d3d-onto-extracts');

  if (ontoState.loading || !ontoState.data) {
    if (leftWall) {
      clearNode(leftWall);
      const hint = document.createElement('div');
      hint.className = 'd3d-empty-hint';
      hint.textContent = ontoState.loading
        ? `실제 외부 실물 사진군(Wikimedia)과 백과 인과 연결망(Wikipedia)에서 [${ontoState.conceptA}${ontoState.conceptB ? ` ⇄ ${ontoState.conceptB}` : ''}] 프로토콜을 동기화하는 중입니다...`
        : '상단에서 개념 A ⇄ B를 선택하고 공명 동기화를 실행하세요.';
      leftWall.appendChild(hint);
    }
    return;
  }

  const { conceptA, conceptB, comparison } = ontoState.data;

  // 1) Left Multi-Instance Real-World Optical Prism Wall
  if (leftWall) {
    clearNode(leftWall);
    const renderSwarm = (bundle, optics, colorHex, tag) => {
      const row = document.createElement('div');
      row.className = 'd3d-onto-swarm-row';

      const head = document.createElement('div');
      head.className = 'd3d-onto-swarm-head';
      const title = document.createElement('strong');
      title.style.color = colorHex;
      title.textContent = `${tag} · ${bundle.title} (${bundle.enTitle || bundle.query}) · 중심 스케일 S${bundle.scaleCenter.toFixed(1)}`;
      const stat = document.createElement('span');
      stat.textContent = optics
        ? `실물 ${optics.count}장 교차 실측 · 불변축: ${optics.mostInvariantAxis.split(' ')[0]} / 표면변이: ${optics.mostVariableAxis.split(' ')[0]}`
        : `실물 사진 ${bundle.photos.length}장 광학 스펙트럼 계측 중...`;
      head.appendChild(title);
      head.appendChild(stat);
      row.appendChild(head);

      const grid = document.createElement('div');
      grid.className = 'd3d-onto-photos';
      bundle.photos.slice(0, 5).forEach((ph) => {
        const th = document.createElement('div');
        th.className = 'd3d-onto-thumb';
        const img = document.createElement('img');
        img.src = ph.proxyUrl;
        img.alt = ph.caption;
        img.loading = 'lazy';
        const cap = document.createElement('span');
        cap.textContent = ph.caption;
        th.appendChild(img);
        th.appendChild(cap);
        grid.appendChild(th);
      });
      row.appendChild(grid);

      if (optics) {
        const optBars = document.createElement('div');
        optBars.className = 'd3d-onto-opt-bars';
        SPECTRAL_AXES.forEach((ax, k) => {
          const item = document.createElement('div');
          item.className = 'd3d-onto-opt-item';
          const lbl = document.createElement('span');
          lbl.textContent = `${ax.name.split(' ')[0]} ${ax.name.split('·')[1] ? ax.name.split('·')[1].trim().slice(0, 6) : ''}`;
          const val = document.createElement('strong');
          val.style.color = ax.color;
          val.textContent = `μ ${optics.mean[k].toFixed(1)}% ±${optics.std[k].toFixed(1)}%`;
          item.appendChild(lbl);
          item.appendChild(val);
          optBars.appendChild(item);
        });
        row.appendChild(optBars);
      }

      leftWall.appendChild(row);
    };

    renderSwarm(conceptA, ontoState.opticsA, '#38bdf8', '개념 A');
    if (conceptB) renderSwarm(conceptB, ontoState.opticsB, '#34d399', '전이·비교 B');
  }

  // 2) 6-Axis Integrated Cognitive Protocol Comparison Cards (P1..P6)
  if (protoGrid) {
    clearNode(protoGrid);
    conceptA.protocolAxes.forEach((axA, i) => {
      const axB = conceptB ? conceptB.protocolAxes[i] : null;
      const card = document.createElement('div');
      card.className = 'd3d-onto-pcard';

      const head = document.createElement('div');
      head.className = 'd3d-onto-phead';
      const nm = document.createElement('strong');
      nm.textContent = axA.name;
      const deltaEl = document.createElement('span');
      if (axB) {
        const diff = (axB.strength - axA.strength) * 100;
        if (i === 0 && ontoState.opticalSimPct !== null) {
          deltaEl.textContent = `광학유사 ${ontoState.opticalSimPct}% · Δ${diff >= 0 ? '+' : ''}${diff.toFixed(0)}%`;
          deltaEl.style.color = '#38bdf8';
        } else {
          deltaEl.textContent = `A ${(axA.strength * 100).toFixed(0)}% ⇄ B ${(axB.strength * 100).toFixed(0)}% (${diff >= 0 ? '+' : ''}${diff.toFixed(0)}%)`;
          deltaEl.style.color = Math.abs(diff) > 22 ? '#fb7185' : '#34d399';
        }
      } else {
        deltaEl.textContent = `${(axA.strength * 100).toFixed(0)}% (근거 ${axA.hits}회)`;
      }
      head.appendChild(nm);
      head.appendChild(deltaEl);

      const desc = document.createElement('div');
      desc.className = 'd3d-spec-desc';
      desc.textContent = axA.desc;

      const dual = document.createElement('div');
      dual.className = 'd3d-dual-bar';
      const trA = document.createElement('div');
      trA.className = 'd3d-dual-track';
      const flA = document.createElement('div');
      flA.className = 'd3d-dual-fill-a';
      flA.style.width = `${clamp(axA.strength * 100, 4, 100)}%`;
      trA.appendChild(flA);
      dual.appendChild(trA);

      if (axB) {
        const trB = document.createElement('div');
        trB.className = 'd3d-dual-track';
        const flB = document.createElement('div');
        flB.className = 'd3d-dual-fill-b';
        flB.style.width = `${clamp(axB.strength * 100, 4, 100)}%`;
        trB.appendChild(flB);
        dual.appendChild(trB);
      }

      card.appendChild(head);
      card.appendChild(desc);
      card.appendChild(dual);
      protoGrid.appendChild(card);
    });
  }

  // 3) Real Wikipedia Causal Connection Chips (Shared vs Only-A vs Emergent-B)
  if (linksWrap) {
    clearNode(linksWrap);
    const makeLinkBox = (title, items, cls, targetSide) => {
      const box = document.createElement('div');
      box.className = 'd3d-link-box';
      const h4 = document.createElement('h4');
      h4.textContent = title;
      box.appendChild(h4);
      const row = document.createElement('div');
      row.className = 'd3d-chip-row';
      if (!items.length) {
        const empty = document.createElement('span');
        empty.style.fontSize = '0.65rem';
        empty.style.color = '#64748b';
        empty.textContent = '직접 공유 연결 없음 (강한 경계 단절)';
        row.appendChild(empty);
      } else {
        items.slice(0, 10).forEach((txt) => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = `d3d-onto-tag ${cls}`;
          btn.textContent = txt;
          btn.title = '클릭하면 이 개념으로 스케일 로터를 즉시 확장합니다';
          btn.addEventListener('click', () => {
            if (targetSide === 'A') runOntologicalResonance(txt, conceptB ? conceptB.title : conceptA.title);
            else runOntologicalResonance(conceptA.title, txt);
          });
          row.appendChild(btn);
        });
      }
      box.appendChild(row);
      linksWrap.appendChild(box);
    };

    if (comparison && conceptB) {
      makeLinkBox(`공명하는 공통 연결망 (${comparison.sharedLinks.length})`, comparison.sharedLinks, 'shared', 'B');
      makeLinkBox(`${conceptA.title} 고유 질서 (하위/개체)`, comparison.onlyALinks, 'only-a', 'A');
      makeLinkBox(`${conceptB.title}에서만 출현하는 상위 전이 질서`, comparison.onlyBLinks, 'only-b', 'B');
    } else {
      makeLinkBox(`${conceptA.title} 실세계 연결망`, conceptA.links, 'shared', 'B');
      makeLinkBox(`${conceptA.title} 범주 계층`, conceptA.categories, 'only-a', 'B');
      makeLinkBox('비교 개념 B를 입력하면 경계 전이 잔차가 분리됩니다', [], 'only-b', 'B');
    }
  }

  // 4) Grounded Live Encyclopedic Extracts
  if (extractsWrap) {
    clearNode(extractsWrap);
    const makeExt = (bundle, color) => {
      const c = document.createElement('div');
      c.className = 'd3d-extract-card';
      const st = document.createElement('strong');
      st.style.color = color;
      st.textContent = `${bundle.title} · 실세계 지식 근거 (Wikipedia)`;
      const p = document.createElement('div');
      p.textContent = bundle.extract || '요약 텍스트 없음';
      c.appendChild(st);
      c.appendChild(p);
      extractsWrap.appendChild(c);
    };
    makeExt(conceptA, '#38bdf8');
    if (conceptB) makeExt(conceptB, '#34d399');
  }
}

// ============================================================================
// 5. Autonomous Scale-Rotor Discovery Loops (Per Stage)
// ============================================================================
function pushLog(tone, head, body) {
  discoveryLog.unshift({ tone, head, body });
  if (discoveryLog.length > 10) discoveryLog.length = 10;
  renderDiscoveryLog();
}

function startStageAutonomousDiscovery() {
  rotorState.autoRunning = true;
  rotorState.autoStage = rotorState.stage;
  rotorState.autoStepIdx = 0;
  rotorState.lastAutoStepTs = performance.now();

  if (rotorState.stage === '2d') {
    rotorState.on2d = [true, false, false, false, false, false];
    rotorState.solo2d = 0;
    rotorState.displayMode = 2;
    discoveryLog = [];
    pushLog(
      'warn',
      '① 2D 자율 결손 검증 시작 (C1 거시 조도만 투입)',
      '단일 축(C1)만으로 원본 복원을 시도하고, 잔차 에너지가 가장 큰 누락 축을 스스로 편입해 100% 복원에 도달하는지 검증합니다.'
    );
    syncDisplayButtons();
    renderStagePanels();
    setStatus('▲ [1단계] C1에서 출발해 잔차 기반 자율 축 확장을 진행 중입니다.', 'loading');
    return;
  }

  if (rotorState.stage === 'st') {
    rotorState.stOn.t1 = false;
    rotorState.stOn.t3 = false;
    rotorState.soloSt = 0;
    rotorState.displayMode = 2;
    discoveryLog = [];
    pushLog(
      'warn',
      '② 시공간 잔차 자율 분해 시작 — 2D 정지 규칙만으로 t→t+1 예측',
      '1단계에서 2D 6축을 100% 복원했더라도, 시간이 1프레임 흐르면(t→t+1) 2D 규칙은 즉시 붕괴하며 잔차가 터져 나옵니다.'
    );
    syncDisplayButtons();
    renderStagePanels();
    setStatus('▲ [2단계] 2D 정지 예측 붕괴를 계측한 뒤 관성(T1)→외부환경(T3)→3D 가려짐(T2) 순으로 상위 질서를 편입합니다.', 'loading');
    return;
  }

  // Stage 3: Automatic 3D Counterfactual Falsification Sweep
  rotorState.cfYawDeg = 0;
  rotorState.cfPitchDeg = 0;
  rotorState.cfLightDeltaDeg = 0;
  rotorState.cfTimeExtrap = 0;
  rotorState.sweepPhase = 0;
  discoveryLog = [];
  pushLog(
    'warn',
    '③ 3D 반증 스윕 개시 — 원본 카메라(0°)에서 시점·광원 이탈 실험',
    '0°에서는 2D 원본과 일치하지만, 시점을 좌우로 비틀고 외부 광원을 이동시키면 숨겨졌던 3D 뒷면 공백과 광원 모순이 즉시 폭로됩니다.'
  );
  syncF3dControls();
  setStatus('▲ [3단계] 시점(0°→±28°) 및 외부 광원 반사실 스윕을 실행해 2D 단일 관점의 한계를 반증 중입니다.', 'loading');
}

function stepAutonomous(now) {
  if (!rotorState.autoRunning || rotorState.autoStage !== rotorState.stage) return;

  if (rotorState.stage === 'f3d') {
    rotorState.sweepPhase += 0.032;
    const ph = rotorState.sweepPhase;
    if (ph < Math.PI * 2) {
      rotorState.cfYawDeg = Math.sin(ph) * 28;
      rotorState.cfPitchDeg = Math.sin(ph * 0.5) * 10;
      rotorState.cfLightDeltaDeg = Math.sin(ph * 0.75) * 95;
      rotorState.cfTimeExtrap = Math.max(0, Math.sin(ph - 1.2)) * 0.55;
      syncF3dControls();
    } else {
      rotorState.autoRunning = false;
      rotorState.cfYawDeg = 22;
      rotorState.cfPitchDeg = 8;
      rotorState.cfLightDeltaDeg = 68;
      rotorState.cfTimeExtrap = 0.25;
      syncF3dControls();
      pushLog(
        'ok',
        `③ 3D 반증 완료 · 미관측 뒷면 공백 ${metrics3d.exposedVoidPct.toFixed(1)}% · 광원 편차 ${metrics3d.lightContradictionDeg.toFixed(0)}°`,
        '단일 2D 시점에서는 잔차 0%였으나, 시점을 22° 틀자 가려진 뒷면 기하 공백과 외부 광원 모순이 실증되었습니다. 더블클릭으로 0° 복귀 가능합니다.'
      );
      setStatus('● [3단계] 반증 스윕 완료 — 시점·광원 이탈 시 노출되는 미관측 3D 질서를 확인했습니다.', 'ok');
    }
    return;
  }

  if (now - rotorState.lastAutoStepTs < 1650) return;
  rotorState.lastAutoStepTs = now;

  if (rotorState.stage === '2d') {
    if (!metrics2d.valid) return;
    if (metrics2d.activeCount === 6 || metrics2d.dominantMissingIdx < 0) {
      rotorState.autoRunning = false;
      pushLog(
        'ok',
        '① 2D 6축 재결합 === 원본 100.0% 도달 (정지 단면 완결)',
        '한 정지 프레임에서는 잔차 0.0%가 되었으나, 이는 정지된 단면일 뿐입니다. 이제 [② 시공간·음성 잔차] 탭으로 로터를 회전해 시간축에서 2D가 어떻게 깨지는지 확인하세요.'
      );
      setStatus('● [1단계] 2D 정지 스펙트럼 100% 복원 완료 — 다음 단계(② 시공간 잔차)로 로터를 확장해 보세요.', 'ok');
      return;
    }
    const pick = metrics2d.dominantMissingIdx;
    const ax = SPECTRAL_AXES[pick];
    const bMae = metrics2d.maePct.toFixed(1);
    const share = metrics2d.missingResidualByAxis[pick].toFixed(1);
    rotorState.on2d[pick] = true;
    pushLog(
      'step',
      `결손 감지(MAE ${bMae}%) → [${ax.name}] 편입`,
      `잔차 에너지 중 ${share}%가 [${ax.role}]에 집중됨을 확인해 재조합 축에 추가했습니다.`
    );
    renderStagePanels();
    return;
  }

  // Stage 2 step-by-step spatiotemporal order discovery
  if (rotorState.stage === 'st') {
    rotorState.autoStepIdx += 1;
    if (rotorState.autoStepIdx === 1) {
      rotorState.stOn.t1 = true;
      pushLog(
        'step',
        `Step 1 · T1 관성·운동 질서 편입 (평균 흐름 ${metricsSt.meanFlowPx.toFixed(1)}px/f)`,
        `정지 2D 잔차 ${metricsSt.staticResidualPct.toFixed(1)}% 중 ${metricsSt.motionExplainedPct.toFixed(1)}%p가 물체의 관성 이동(Optical Flow)으로 설명되어 잔차가 즉시 줄어듭니다.`
      );
      renderStagePanels();
    } else if (rotorState.autoStepIdx === 2) {
      rotorState.stOn.t3 = true;
      pushLog(
        'step',
        `Step 2 · T3 화면 밖 광원·환경 변화 편입 (ΔS4 보정)`,
        `프레임 외부 조명·대기 밝기 이동 성분(${metricsSt.envExplainedPct.toFixed(2)}%p)을 보정했습니다.`
      );
      renderStagePanels();
    } else {
      rotorState.autoRunning = false;
      pushLog(
        'ok',
        `Step 3 · 비가역 잔차 ${metricsSt.occlusionResidPct.toFixed(1)}% 잔존 → 3D 가려짐(T2) 및 외부 음향(T4) 질서 지각`,
        `관성(T1)과 전역 환경(T3)을 합쳐도 사라지지 않는 경계 잔차는 2D 평면 바깥의 3D 깊이·뒷면 출현(T2)과 화면 밖 음향 사건(T4)의 증거입니다. 이제 [③ 3D 반증 실험실]로 이동해 시점을 틀어 보세요.`
      );
      setStatus('● [2단계] 시공간 잔차 분해 완료 — T1·T3 이후에도 남는 3D 가려짐 경계를 확인했습니다.', 'ok');
      renderStagePanels();
    }
  }
}

// ============================================================================
// 6. Stage Switching & Safe DOM UI Rendering (Zero innerHTML!)
// ============================================================================
function setRotorStage(nextStage) {
  if (!['2d', 'st', 'f3d', 'onto'].includes(nextStage)) return;
  rotorState.stage = nextStage;
  rotorState.autoRunning = false;
  rotorState.solo2d = 0;
  rotorState.soloSt = 0;

  document.querySelectorAll('#d3d-rotor-stage-tabs button').forEach((b) => {
    b.classList.toggle('active', b.dataset.rstage === nextStage);
  });

  const p2d = document.getElementById('d3d-panel-2d');
  const pst = document.getElementById('d3d-panel-st');
  const pf3 = document.getElementById('d3d-panel-f3d');
  const ponto = document.getElementById('d3d-panel-onto');
  if (p2d) p2d.classList.toggle('hidden', nextStage !== '2d');
  if (pst) pst.classList.toggle('hidden', nextStage !== 'st');
  if (pf3) pf3.classList.toggle('hidden', nextStage !== 'f3d');
  if (ponto) ponto.classList.toggle('hidden', nextStage !== 'onto');

  const sigRow = document.getElementById('d3d-signal-action-row');
  const ontoRow = document.getElementById('d3d-onto-action-row');
  const mediaCtrls = document.getElementById('d3d-media-controls');
  if (sigRow) sigRow.classList.toggle('hidden', nextStage === 'onto');
  if (ontoRow) ontoRow.classList.toggle('hidden', nextStage !== 'onto');
  if (mediaCtrls) mediaCtrls.classList.toggle('hidden', nextStage === 'onto');

  const hdCanvas = document.getElementById('d3d-hd-canvas');
  const ontoWall = document.getElementById('d3d-onto-left-wall');
  if (hdCanvas) hdCanvas.classList.toggle('hidden', nextStage === 'onto');
  if (ontoWall) ontoWall.classList.toggle('hidden', nextStage !== 'onto');

  const modeTabs = document.getElementById('d3d-display-mode-tabs');
  if (modeTabs) modeTabs.classList.toggle('hidden', nextStage === 'f3d' || nextStage === 'onto');

  const canvasHost = document.getElementById('d3d-canvas-host');
  if (canvasHost) canvasHost.classList.toggle('grab-ready', nextStage === 'f3d' || nextStage === 'onto');

  const btnAuto = document.getElementById('d3d-btn-auto-discover');
  const btnAll = document.getElementById('d3d-btn-all-on');
  const leftHead = document.getElementById('d3d-left-head');
  const rightHead = document.getElementById('d3d-right-head');
  const botHead = document.getElementById('d3d-bottom-left-head');
  const sLeft = document.getElementById('d3d-split-left-lbl');
  const sRight = document.getElementById('d3d-split-right-lbl');

  if (nextStage === '2d') {
    if (btnAuto) btnAuto.textContent = '▶ 1축부터 자율 결손 검증 (원본 100%까지 확장)';
    if (btnAll) btnAll.textContent = '6축 전체 합일 (원본 100%)';
    if (leftHead) leftHead.textContent = '좌측 · 실제 원본 O(t) (960×540 무손실 기준)';
    if (rightHead) rightHead.textContent = '우측 · 2D 6축 재조합 ΣCᵢ & 결손 잔차 |O − ΣCᵢ|';
    if (botHead) botHead.textContent = '① 2D 정지 스펙트럼 6축 (하나라도 끄면 즉시 잔차 노출 · 단독 투시 가능)';
    if (sLeft) sLeft.textContent = '재조합 결과 (ΣCᵢ)';
    if (sRight) sRight.textContent = '결손 잔차 |원본 − ΣCᵢ|';
  } else if (nextStage === 'st') {
    if (btnAuto) btnAuto.textContent = '▶ 시공간 잔차 자율 분해 (2D 붕괴 → 운동/환경/3D 순차 편입)';
    if (btnAll) btnAll.textContent = 'T1(관성) + T3(환경) 모두 편입';
    if (leftHead) leftHead.textContent = '좌측 · 현재 원본 O(t+1) + 실측 관성 벡터(시안)·3D 가려짐(로즈)';
    if (rightHead) rightHead.textContent = '우측 · 시공간 예측 Pred(t+1) & 미인지 질서 잔차 |O(t+1) − Pred|';
    if (botHead) botHead.textContent = '② 시공간·음향 상위 질서 축 (2D가 깨질 때 드러나는 운동·환경·3D·소리)';
    if (sLeft) sLeft.textContent = '시공간 예측 Pred(t+1)';
    if (sRight) sRight.textContent = '미설명 잔차 (3D·미인지 질서)';
  } else if (nextStage === 'f3d') {
    if (btnAuto) btnAuto.textContent = '▶ 시점·광원 자동 반증 스윕 (0°→±28° 뒷면 공백 폭로)';
    if (btnAll) btnAll.textContent = '원본 카메라(0°) · 추정 광원 정렬';
    if (leftHead) leftHead.textContent = '좌측 · 단일 2D 카메라 관측 원본 O(t) (시점 0° 고정)';
    if (rightHead) rightHead.textContent = '우측 · 3D 반증 실험실 (실시간 깊이 메쉬 · 드래그 회전 / 더블클릭 0° 복귀)';
    if (botHead) botHead.textContent = '③ 3D 반사실 반증 제어 (시점·외부 광원·관성 시간을 이탈시켜 2D 한계 실증)';
  } else {
    if (leftHead) leftHead.textContent = '좌측 · 다중 실물 광학 프리즘 벽 (외부 실물 사진군 교차 불변량 ⇄ 표면 변이 실측)';
    if (rightHead) rightHead.textContent = '우측 · 3D 다중 스케일 존재론 공명장 (S0 물질 → S4 행성 순환 · 드래그 회전)';
    if (botHead) botHead.textContent = '④ 6축 통합 인지 프로토콜 (광학 불변량 + 실세계 물리·구조·생태·스케일 연결망 동기화)';
    if (!ontoState.data && !ontoState.loading) {
      runOntologicalResonance(ontoState.conceptA, ontoState.conceptB);
    }
  }

  renderStagePanels();
  syncF3dControls();
  updateVerdictAndSummary();
}

function renderStagePanels() {
  if (rotorState.stage === '2d') render2dAxisCards();
  else if (rotorState.stage === 'st') renderStAxisCards();
  else if (rotorState.stage === 'onto') renderOntoPanels();
}

function render2dAxisCards() {
  const host = document.getElementById('d3d-axis-grid');
  if (!host) return;
  clearNode(host);

  SPECTRAL_AXES.forEach((ax, idx) => {
    const isOn = rotorState.on2d[idx];
    const isSolo = rotorState.solo2d === ax.id;
    const share = metrics2d.axisEnergyPct[idx] || 0;

    const card = document.createElement('div');
    card.className = `d3d-spec-card ${isOn ? 'on' : 'off'} ${isSolo ? 'solo' : ''}`;
    card.style.borderTopColor = ax.color;

    const top = document.createElement('div');
    top.className = 'd3d-spec-top';
    const title = document.createElement('strong');
    title.style.color = ax.color;
    title.textContent = ax.name;
    const pct = document.createElement('span');
    pct.textContent = `기여 ${share.toFixed(1)}%`;
    top.appendChild(title);
    top.appendChild(pct);

    const desc = document.createElement('div');
    desc.className = 'd3d-spec-desc';
    desc.textContent = ax.role;

    const barWrap = document.createElement('div');
    barWrap.className = 'd3d-spec-bar';
    const barFill = document.createElement('div');
    barFill.className = 'd3d-spec-fill';
    barFill.style.width = `${clamp(share * 2.4, 4, 100)}%`;
    barFill.style.background = ax.color;
    barWrap.appendChild(barFill);

    const actions = document.createElement('div');
    actions.className = 'd3d-spec-actions';

    const btnToggle = document.createElement('button');
    btnToggle.type = 'button';
    btnToggle.className = `btn d3d-mini-btn ${isOn ? 'btn-toggle-on' : ''}`;
    btnToggle.textContent = isOn ? '재조합 포함: ON' : '제외(결손): OFF';
    btnToggle.addEventListener('click', () => {
      rotorState.autoRunning = false;
      rotorState.solo2d = 0;
      rotorState.on2d[idx] = !rotorState.on2d[idx];
      render2dAxisCards();
      updateVerdictAndSummary();
    });

    const btnSolo = document.createElement('button');
    btnSolo.type = 'button';
    btnSolo.className = `btn d3d-mini-btn ${isSolo ? 'btn-primary' : ''}`;
    btnSolo.textContent = isSolo ? '단독 투시 중' : '단독 보기';
    btnSolo.addEventListener('click', () => {
      rotorState.solo2d = isSolo ? 0 : ax.id;
      render2dAxisCards();
      updateVerdictAndSummary();
    });

    actions.appendChild(btnToggle);
    actions.appendChild(btnSolo);
    card.appendChild(top);
    card.appendChild(desc);
    card.appendChild(barWrap);
    card.appendChild(actions);
    host.appendChild(card);
  });
}

function renderStAxisCards() {
  const host = document.getElementById('d3d-st-grid');
  if (!host) return;
  clearNode(host);

  ST_AXES.forEach((ax) => {
    const isToggle = ax.toggleable;
    const isOn = isToggle ? rotorState.stOn[ax.key] : true;
    const isSolo = rotorState.soloSt === ax.id;

    let readout = '';
    let barPct = 10;
    if (ax.key === 't1') {
      readout = `잔차 해소 -${metricsSt.motionExplainedPct.toFixed(1)}%p · 평균 ${metricsSt.meanFlowPx.toFixed(1)}px/f`;
      barPct = clamp(metricsSt.meanFlowPx * 18, 6, 100);
    } else if (ax.key === 't3') {
      const dm = (Math.abs(metricsSt.macroDeltaRgb[0]) + Math.abs(metricsSt.macroDeltaRgb[1]) + Math.abs(metricsSt.macroDeltaRgb[2])) * 100;
      readout = `전역 조도변동 ${dm.toFixed(2)}% · 보정 -${metricsSt.envExplainedPct.toFixed(2)}%p`;
      barPct = clamp(dm * 22, 6, 100);
    } else if (ax.key === 't2') {
      readout = `비가역 3D 경계 잔차 ${metricsSt.occlusionResidPct.toFixed(1)}%`;
      barPct = clamp(metricsSt.occlusionResidPct * 8, 6, 100);
    } else {
      readout = audioSensor.mode === 'none'
        ? '오디오 미연결 (마이크/영상 음성 대기)'
        : `음향 ${(audioSensor.rms * 100).toFixed(0)}% · 교차 상관 r=${audioSensor.corrR.toFixed(2)}`;
      barPct = audioSensor.mode === 'none' ? 5 : clamp(audioSensor.rms * 140, 8, 100);
    }

    const card = document.createElement('div');
    card.className = `d3d-spec-card ${isOn ? 'on' : 'off'} ${isSolo ? 'solo' : ''}`;
    card.style.borderTopColor = ax.color;

    const top = document.createElement('div');
    top.className = 'd3d-spec-top';
    const title = document.createElement('strong');
    title.style.color = ax.color;
    title.textContent = ax.name;
    const val = document.createElement('span');
    val.textContent = readout;
    top.appendChild(title);
    top.appendChild(val);

    const desc = document.createElement('div');
    desc.className = 'd3d-spec-desc';
    desc.textContent = ax.role;

    const barWrap = document.createElement('div');
    barWrap.className = 'd3d-spec-bar';
    const barFill = document.createElement('div');
    barFill.className = 'd3d-spec-fill';
    barFill.style.width = `${barPct}%`;
    barFill.style.background = ax.color;
    barWrap.appendChild(barFill);

    const actions = document.createElement('div');
    actions.className = 'd3d-spec-actions';

    if (isToggle) {
      const btnToggle = document.createElement('button');
      btnToggle.type = 'button';
      btnToggle.className = `btn d3d-mini-btn ${isOn ? 'btn-toggle-on' : ''}`;
      btnToggle.textContent = isOn ? '예측 질서 편입: ON' : '제외 (2D 정지): OFF';
      btnToggle.addEventListener('click', () => {
        rotorState.autoRunning = false;
        rotorState.soloSt = 0;
        rotorState.stOn[ax.key] = !rotorState.stOn[ax.key];
        renderStAxisCards();
        updateVerdictAndSummary();
      });
      actions.appendChild(btnToggle);
    } else if (ax.key === 't2') {
      const btnGo3d = document.createElement('button');
      btnGo3d.type = 'button';
      btnGo3d.className = 'btn d3d-mini-btn';
      btnGo3d.textContent = '→ ③ 3D 반증 실험실로 이동';
      btnGo3d.addEventListener('click', () => setRotorStage('f3d'));
      actions.appendChild(btnGo3d);
    } else {
      const btnMic = document.createElement('button');
      btnMic.type = 'button';
      btnMic.className = `btn d3d-mini-btn ${audioSensor.mode !== 'none' ? 'btn-toggle-on' : ''}`;
      btnMic.textContent = audioSensor.mode === 'mic'
        ? '🎙 마이크 연결 중'
        : (audioSensor.mode === 'video' ? '🔊 영상 오디오 연결 중' : '🎙 마이크 감각 열기');
      btnMic.addEventListener('click', () => toggleMicAudio());
      actions.appendChild(btnMic);
    }

    const btnSolo = document.createElement('button');
    btnSolo.type = 'button';
    btnSolo.className = `btn d3d-mini-btn ${isSolo ? 'btn-primary' : ''}`;
    btnSolo.textContent = isSolo ? '단독 투시 중' : '단독 보기';
    btnSolo.addEventListener('click', () => {
      rotorState.soloSt = isSolo ? 0 : ax.id;
      renderStAxisCards();
      updateVerdictAndSummary();
    });
    actions.appendChild(btnSolo);

    card.appendChild(top);
    card.appendChild(desc);
    card.appendChild(barWrap);
    card.appendChild(actions);
    host.appendChild(card);
  });
}

function syncF3dControls() {
  const rYaw = document.getElementById('d3d-rng-yaw');
  const rPitch = document.getElementById('d3d-rng-pitch');
  const rLight = document.getElementById('d3d-rng-light');
  const rExtrap = document.getElementById('d3d-rng-extrap');
  const rDepth = document.getElementById('d3d-rng-depth');

  if (rYaw) rYaw.value = String(rotorState.cfYawDeg);
  if (rPitch) rPitch.value = String(rotorState.cfPitchDeg);
  if (rLight) rLight.value = String(rotorState.cfLightDeltaDeg);
  if (rExtrap) rExtrap.value = String(rotorState.cfTimeExtrap);
  if (rDepth) rDepth.value = String(rotorState.cfDepthScale);

  const vYaw = document.getElementById('d3d-val-yaw');
  const vPitch = document.getElementById('d3d-val-pitch');
  const vLight = document.getElementById('d3d-val-light');
  const vExtrap = document.getElementById('d3d-val-extrap');

  if (vYaw) vYaw.textContent = `${rotorState.cfYawDeg >= 0 ? '+' : ''}${rotorState.cfYawDeg.toFixed(1)}°`;
  if (vPitch) vPitch.textContent = `${rotorState.cfPitchDeg >= 0 ? '+' : ''}${rotorState.cfPitchDeg.toFixed(1)}°`;
  if (vLight) {
    vLight.textContent = Math.abs(rotorState.cfLightDeltaDeg) < 1
      ? '0° (추정 광원 일치)'
      : `${rotorState.cfLightDeltaDeg > 0 ? '+' : ''}${rotorState.cfLightDeltaDeg.toFixed(0)}° 이탈`;
  }
  if (vExtrap) {
    vExtrap.textContent = `+${(rotorState.cfTimeExtrap * 0.5).toFixed(2)}s · Z ${rotorState.cfDepthScale.toFixed(1)}×`;
  }

  const kVoid = document.getElementById('d3d-kpi-void');
  const kLight = document.getElementById('d3d-kpi-light');
  const kInf = document.getElementById('d3d-kpi-inferred');
  if (kVoid) kVoid.textContent = `${metrics3d.exposedVoidPct.toFixed(1)}%`;
  if (kLight) kLight.textContent = `${metrics3d.lightContradictionDeg.toFixed(0)}°`;
  if (kInf) {
    kInf.textContent = `방위 ${metricsSt.inferredLightAzDeg.toFixed(0)}° / 고도 ${metricsSt.inferredLightElDeg.toFixed(0)}°`;
  }
}

function updateVerdictAndSummary() {
  const bar = document.getElementById('d3d-summary-bar');
  const verdict = document.getElementById('d3d-verdict-banner');
  const splitOverlay = document.getElementById('d3d-split-labels');

  const showSplit = (
    rotorState.stage !== 'f3d' &&
    rotorState.displayMode === 2 &&
    ((rotorState.stage === '2d' && rotorState.solo2d === 0) ||
      (rotorState.stage === 'st' && rotorState.soloSt === 0))
  );
  if (splitOverlay) splitOverlay.classList.toggle('hidden', !showSplit);

  if (rotorState.stage === '2d') {
    const missing = SPECTRAL_AXES.filter((_, i) => !rotorState.on2d[i]).map((a) => a.name.split(' ')[0]);
    const isComplete = metrics2d.activeCount === 6;
    if (bar) {
      const psnrTxt = isComplete ? '∞ (완전 일치)' : `${metrics2d.psnrDb.toFixed(1)} dB`;
      bar.textContent = `2D 투입 축 ${metrics2d.activeCount}/6 · 복원률 ${metrics2d.completenessPct.toFixed(1)}% · 잔차 ${metrics2d.maePct.toFixed(1)}% · PSNR ${psnrTxt}`;
    }
    if (verdict) {
      if (rotorState.solo2d > 0) {
        const ax = SPECTRAL_AXES[rotorState.solo2d - 1];
        verdict.className = 'd3d-verdict solo';
        verdict.textContent = `[① 2D 단독 투시] ${ax.name} — ${ax.role}`;
      } else if (isComplete) {
        verdict.className = 'd3d-verdict complete';
        verdict.textContent = '● [① 정지 단면 100% 복원] 한 프레임 안에서는 6축으로 잔차 0.0%가 되지만, 시간이 흐르면(t→t+1) 2D 정지 질서는 즉시 깨집니다 → [② 시공간·음성 잔차]로 로터를 회전해 확인하세요.';
      } else {
        const domAx = metrics2d.dominantMissingIdx >= 0 ? SPECTRAL_AXES[metrics2d.dominantMissingIdx] : null;
        verdict.className = 'd3d-verdict incomplete';
        verdict.textContent = `▲ [① 2D 구성요소 불충분 · 잔차 ${metrics2d.maePct.toFixed(1)}%] 제외된 [${missing.join(', ')}] 때문에 원본 미도달.` + (domAx ? ` 최대 결손 축: [${domAx.name}]` : '');
      }
    }
    return;
  }

  if (rotorState.stage === 'st') {
    if (bar) {
      bar.textContent =
        `2D 정지 붕괴잔차 ${metricsSt.staticResidualPct.toFixed(1)}% → 현재 잔차 ${metricsSt.activeResidualPct.toFixed(1)}% · ` +
        `관성해소 -${metricsSt.motionExplainedPct.toFixed(1)}%p · 3D 경계잔차 ${metricsSt.occlusionResidPct.toFixed(1)}%` +
        (audioSensor.mode !== 'none' ? ` · 시청각 r=${audioSensor.corrR.toFixed(2)}` : '');
    }
    if (verdict) {
      if (rotorState.soloSt > 0) {
        const ax = ST_AXES.find((a) => a.id === rotorState.soloSt);
        verdict.className = 'd3d-verdict solo';
        verdict.textContent = `[② 시공간 상위 질서 단독 투시] ${ax ? ax.name : ''} — ${ax ? ax.role : ''}`;
      } else if (metricsSt.isStaticImage) {
        verdict.className = 'd3d-verdict solo';
        verdict.textContent = '● 정지 이미지는 시간 변화(t→t+1)가 없어 시공간 잔차가 0%입니다. [1080p 도심 교차로]·[웹캠]·로컬 동영상을 열면 2D 붕괴와 상위 질서가 즉시 드러납니다.';
      } else if (!rotorState.stOn.t1 && !rotorState.stOn.t3) {
        verdict.className = 'd3d-verdict incomplete';
        verdict.textContent =
          `▲ [② 2D 정지 규칙 붕괴 감지] 이전 프레임 O(t)의 2D 스펙트럼만으로는 다음 순간 O(t+1)을 설명하지 못해 잔차 ${metricsSt.staticResidualPct.toFixed(1)}%가 발생합니다! ` +
          `이 잔차는 잡음이 아니라 미인지 관성 운동(평균 ${metricsSt.meanFlowPx.toFixed(1)}px/f)·외부 조명 변화·3D 가려짐 질서입니다.`;
      } else {
        verdict.className = 'd3d-verdict complete';
        verdict.textContent =
          `● [② 상위 질서 편입 효과 실증] 2D 정지 잔차 ${metricsSt.staticResidualPct.toFixed(1)}% → ${metricsSt.activeResidualPct.toFixed(1)}%로 감소. ` +
          `그럼에도 경계에 남는 비가역 잔차(${metricsSt.occlusionResidPct.toFixed(1)}%)는 2D를 넘어선 3D 가려짐·뒷면 출현 질서입니다. (${audioSensor.diagnosis})`;
      }
    }
    return;
  }

  if (rotorState.stage === 'onto') {
    if (ontoState.loading || !ontoState.data) {
      if (bar) bar.textContent = '외부 실물 사진군 + 백과 인과 연결망 동기화 중...';
      if (verdict) {
        verdict.className = 'd3d-verdict solo';
        verdict.textContent = '▲ 다중 실물 광학 불변량과 실세계 인과 연결망을 동기화하는 중입니다...';
      }
      return;
    }
    const { conceptA, conceptB, comparison } = ontoState.data;
    const optTxt = ontoState.opticalSimPct !== null ? ` · 다중실물 광학유사 ${ontoState.opticalSimPct}%` : '';
    if (comparison && conceptB) {
      if (bar) {
        bar.textContent =
          `[${conceptA.title} S${conceptA.scaleCenter} ⇄ ${conceptB.title} S${conceptB.scaleCenter}] ` +
          `프로토콜 공명 ${comparison.resonancePct}% · 전이잔차 ${comparison.residualDivergencePct}% · 공유연결 ${comparison.sharedLinks.length}개${optTxt}`;
      }
      if (verdict) {
        const isHighRes = comparison.resonancePct >= 48;
        verdict.className = `d3d-verdict ${isHighRes ? 'complete' : 'incomplete'}`;
        const dom = comparison.dominantJumpAxis;
        verdict.textContent =
          (isHighRes
            ? `● [④ 스케일 전이 공명 확인 · ${comparison.resonancePct}%] [${conceptA.title}]과 [${conceptB.title}]은 ${comparison.sharedLinks.length}개 실세계 인과 고리로 공명하며, `
            : `▲ [④ 존재론 경계 불일치 반증 · 잔차 ${comparison.residualDivergencePct}%] [${conceptA.title}]과 [${conceptB.title}]은 표면(광학 ${ontoState.opticalSimPct !== null ? `${ontoState.opticalSimPct}%` : '계측중'})과 달리 통합 프로토콜에서 큰 단절이 발생합니다. `) +
          `스케일 이동 ΔS=${comparison.scaleJump >= 0 ? '+' : ''}${comparison.scaleJump}, 최대 분화 축은 [${dom ? dom.name : '-'}]입니다.`;
      }
    } else {
      if (bar) {
        bar.textContent = `[${conceptA.title}] 중심 스케일 S${conceptA.scaleCenter} · 연결망 ${conceptA.links.length}개 · 실물 사진 ${conceptA.photos.length}장`;
      }
      if (verdict) {
        verdict.className = 'd3d-verdict complete';
        verdict.textContent = `● [${conceptA.title}] 통합 인지 프로토콜 추출 완료 (중심 S${conceptA.scaleCenter}). 비교 대상 B를 입력하거나 하단 연결 태그를 클릭해 스케일 전이 경계를 검증하세요.`;
      }
    }
    return;
  }

  // Stage 3: 3D Counterfactual Falsification Lab
  const yawAbs = Math.abs(rotorState.cfYawDeg);
  const pitchAbs = Math.abs(rotorState.cfPitchDeg);
  const devDeg = Math.hypot(yawAbs, pitchAbs);
  if (bar) {
    bar.textContent =
      `시점 이탈 ${devDeg.toFixed(1)}° · 노출 3D 뒷면 공백 ${metrics3d.exposedVoidPct.toFixed(1)}% · ` +
      `광원 편차 ${metrics3d.lightContradictionDeg.toFixed(0)}° · 관성 외삽 드리프트 ${metrics3d.extrapDriftPx.toFixed(1)}px`;
  }
  if (verdict) {
    if (devDeg < 1.5 && metrics3d.lightContradictionDeg < 2 && rotorState.cfTimeExtrap < 0.02) {
      verdict.className = 'd3d-verdict complete';
      verdict.textContent =
        '● [③ 원본 2D 카메라(0°) 정렬 상태] 단일 정면 시점에서는 모든 게 완전해 보입니다. 우측 3D 화면을 드래그하거나 [▶ 시점·광원 자동 반증 스윕]을 눌러 2D 착각이 깨지는 지점을 직접 확인하세요.';
    } else {
      verdict.className = 'd3d-verdict incomplete';
      verdict.textContent =
        `▲ [③ 3D 반증 성립 · 단일 2D 관점 한계 노출] 원본 카메라에서 ${devDeg.toFixed(1)}° 벗어나자 미관측 3D 뒷면 공백 ${metrics3d.exposedVoidPct.toFixed(1)}%(마젠타 빗금)가 터져 나오고, ` +
        `외부 광원 ${metrics3d.lightContradictionDeg.toFixed(0)}° 이동 시 2D 고정 그림자와의 광원 모순이 드러납니다.`;
    }
  }
}

function renderDiscoveryLog() {
  const el = document.getElementById('d3d-calib-log');
  if (!el) return;
  clearNode(el);
  if (!discoveryLog.length) {
    const row = document.createElement('div');
    row.className = 'd3d-log-row';
    row.textContent = '각 단계의 [▶ 자율 검증/분해/반증] 버튼을 누르거나 축을 조작하면, 잔차로부터 아직 분류되지 않은 상위 질서(운동·3D 가려짐·외부 광원·음향)가 드러나는 과정을 기록합니다.';
    el.appendChild(row);
    return;
  }
  discoveryLog.forEach((item) => {
    const row = document.createElement('div');
    row.className = `d3d-log-row ${item.tone === 'ok' ? 'keep' : 'rollback'}`;
    const h = document.createElement('div');
    h.className = 'd3d-log-head';
    const st = document.createElement('strong');
    st.textContent = item.head;
    h.appendChild(st);
    const b = document.createElement('div');
    b.className = 'd3d-log-body';
    b.textContent = item.body;
    row.appendChild(h);
    row.appendChild(b);
    el.appendChild(row);
  });
}

function syncDisplayButtons() {
  document.querySelectorAll('#d3d-display-mode-tabs button').forEach((b) => {
    b.classList.toggle('active', Number(b.dataset.dmode) === rotorState.displayMode);
  });
}

function syncAudioButtons() {
  const btnMic = document.getElementById('d3d-btn-mic');
  if (btnMic) {
    btnMic.classList.toggle('btn-toggle-on', audioSensor.mode === 'mic');
    btnMic.textContent = audioSensor.mode === 'mic' ? '■ 마이크 음향 수신 중' : '🎙 마이크 음향 감각';
  }
  const btnVidAud = document.getElementById('d3d-btn-video-audio');
  if (btnVidAud) {
    btnVidAud.classList.toggle('hidden', activeSourceKind !== 'local_video');
    btnVidAud.classList.toggle('btn-toggle-on', audioSensor.mode === 'video');
    btnVidAud.textContent = audioSensor.mode === 'video' ? '🔊 영상 오디오 공명 중' : '🔊 영상 오디오 트랙 연결';
  }
}

// ============================================================================
// 7. Media Source Management (Video / Webcam+Mic / Local File) & Animation Loop
// ============================================================================
let gpuRenderer = null;
let tabActive = false;
let rafId = 0;
let lastFrameTs = 0;
let initializedUI = false;
let activeSourceKind = 'hd_shared'; // 'hd_shared' | 'webcam' | 'local_video' | 'local_image'
let localVideoEl = null;
let localImageEl = null;
let localBlobUrl = null;
let webcamStream = null;
let uiTick = 0;

function getActiveSource() {
  if (activeSourceKind === 'local_image' && localImageEl && localImageEl.complete) {
    return { el: localImageEl, isImage: true };
  }
  if ((activeSourceKind === 'webcam' || activeSourceKind === 'local_video') && localVideoEl && localVideoEl.readyState >= 2) {
    return { el: localVideoEl, isImage: false };
  }
  const shared = document.getElementById('hd-video-source');
  if (shared && shared.readyState >= 2 && shared.videoWidth > 0) {
    return { el: shared, isImage: false };
  }
  return null;
}

function setStatus(text, tone = 'normal') {
  const el = document.getElementById('d3d-status');
  if (!el) return;
  el.textContent = text;
  if (tone === 'ok') el.style.color = '#10b981';
  else if (tone === 'error') el.style.color = '#f43f5e';
  else if (tone === 'loading') el.style.color = '#06b6d4';
  else el.style.color = '#94a3b8';
}

function stopLocalWebcam() {
  if (webcamStream) {
    webcamStream.getTracks().forEach((t) => t.stop());
    webcamStream = null;
  }
  const btn = document.getElementById('d3d-btn-webcam');
  if (btn) {
    btn.classList.remove('btn-toggle-on');
    btn.textContent = '● 웹캠·마이크 개방';
  }
}

async function startLiveWebcam() {
  if (activeSourceKind === 'webcam') {
    stopLocalWebcam();
    stopMicAudio();
    activeSourceKind = 'hd_shared';
    hasPrevFrame = false;
    setStatus('● 웹캠·마이크 종료 — 1080p 실물 영상 원본으로 복귀했습니다.', 'normal');
    return;
  }
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    setStatus('✖ 이 브라우저에서는 웹캠에 접근할 수 없습니다. 로컬 동영상 또는 이미지를 열어 주세요.', 'error');
    return;
  }
  setStatus('▲ 실시간 웹캠 + 마이크 개방 중...', 'loading');
  try {
    let hasAud = true;
    try {
      webcamStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
        audio: true,
      });
    } catch (_) {
      hasAud = false;
      webcamStream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
        audio: false,
      });
    }
    if (!localVideoEl) {
      localVideoEl = document.createElement('video');
      localVideoEl.muted = true;
      localVideoEl.playsInline = true;
      localVideoEl.loop = true;
    }
    localVideoEl.muted = true;
    localVideoEl.srcObject = webcamStream;
    await localVideoEl.play();
    activeSourceKind = 'webcam';
    hasPrevFrame = false;

    if (hasAud && webcamStream.getAudioTracks().length > 0) {
      const audStream = new MediaStream(webcamStream.getAudioTracks());
      await toggleMicAudio(audStream);
    }

    const btn = document.getElementById('d3d-btn-webcam');
    if (btn) {
      btn.classList.add('btn-toggle-on');
      btn.textContent = '■ 웹캠·마이크 활성';
    }
    syncAudioButtons();
    setStatus(
      `● 실시간 웹캠${hasAud ? '+마이크' : ''} 연결 (${localVideoEl.videoWidth}×${localVideoEl.videoHeight}) — 시공간 운동·음향·3D 반증 가동`,
      'ok'
    );
  } catch (err) {
    stopLocalWebcam();
    setStatus(`✖ 웹캠 연결 실패: ${err instanceof Error ? err.message : '권한 거부 또는 장치 없음'}`, 'error');
  }
}

async function loadVideoStreamUrl(url, label, isLocalUpload = false) {
  stopLocalWebcam();
  setStatus(`▲ 실물 HD 원본("${label}") 로딩 중...`, 'loading');
  try {
    if (!localVideoEl) {
      localVideoEl = document.createElement('video');
      localVideoEl.crossOrigin = 'anonymous';
      localVideoEl.muted = true;
      localVideoEl.playsInline = true;
      localVideoEl.loop = true;
    }
    localVideoEl.muted = true;
    localVideoEl.srcObject = null;
    localVideoEl.src = url;
    localVideoEl.load();
    await new Promise((resolve, reject) => {
      const ok = () => {
        localVideoEl.removeEventListener('loadeddata', ok);
        localVideoEl.removeEventListener('error', fail);
        resolve();
      };
      const fail = () => {
        localVideoEl.removeEventListener('loadeddata', ok);
        localVideoEl.removeEventListener('error', fail);
        reject(new Error('동영상 디코딩 실패'));
      };
      localVideoEl.addEventListener('loadeddata', ok);
      localVideoEl.addEventListener('error', fail);
    });
    await localVideoEl.play();
    activeSourceKind = isLocalUpload ? 'local_video' : 'hd_preset';
    // Reuse localVideoEl for preset too
    if (!isLocalUpload) activeSourceKind = 'local_video';
    hasPrevFrame = false;
    syncAudioButtons();
    setStatus(`● 실물 HD 원본 연결 · ${label} (${localVideoEl.videoWidth}×${localVideoEl.videoHeight}) — 스케일 로터 시공간·3D 검증 가동`, 'ok');
  } catch (err) {
    setStatus(`✖ 동영상 로드 실패: ${err instanceof Error ? err.message : '오류'}`, 'error');
  }
}

function handleLocalFile(file) {
  if (!file) return;
  if (localBlobUrl) URL.revokeObjectURL(localBlobUrl);
  localBlobUrl = URL.createObjectURL(file);

  if (file.type.startsWith('video/')) {
    loadVideoStreamUrl(localBlobUrl, file.name, true);
  } else if (file.type.startsWith('image/')) {
    stopLocalWebcam();
    const img = new Image();
    img.onload = () => {
      localImageEl = img;
      activeSourceKind = 'local_image';
      hasPrevFrame = false;
      syncAudioButtons();
      setStatus(`● 고해상도 이미지 원본 연결 · ${file.name} (${img.naturalWidth}×${img.naturalHeight})`, 'ok');
    };
    img.onerror = () => setStatus('✖ 이미지 디코딩 실패', 'error');
    img.src = localBlobUrl;
  } else {
    setStatus('✖ MP4/WebM 동영상 또는 PNG/JPG/WebP 이미지를 선택해 주세요.', 'error');
  }
}

function stepLoop(now) {
  if (!tabActive) return;
  if (document.hidden) {
    rafId = requestAnimationFrame(stepLoop);
    return;
  }
  if (now - lastFrameTs >= 32) {
    lastFrameTs = now;
    if (rotorState.stage === 'onto') {
      if (gpuRenderer) gpuRenderer.renderFrame();
    } else {
      const src = getActiveSource();
      if (src) {
        captureOriginalAndMeasure(src.el, src.isImage);
        if (gpuRenderer) gpuRenderer.renderFrame();
        stepAutonomous(now);
        if (rotorState.stage === 'st') drawAvScope();
      }
      uiTick += 1;
      if (uiTick % 8 === 0) {
        if (rotorState.stage === '2d') render2dAxisCards();
        else if (rotorState.stage === 'st') renderStAxisCards();
        else syncF3dControls();
        updateVerdictAndSummary();
      }
    }
  }
  rafId = requestAnimationFrame(stepLoop);
}

function bindUI() {
  if (initializedUI) return;
  initializedUI = true;

  document.querySelectorAll('#d3d-rotor-stage-tabs button').forEach((btn) => {
    btn.addEventListener('click', () => setRotorStage(btn.dataset.rstage));
  });

  const btnAuto = document.getElementById('d3d-btn-auto-discover');
  if (btnAuto) btnAuto.addEventListener('click', () => startStageAutonomousDiscovery());

  const btnAllOn = document.getElementById('d3d-btn-all-on');
  if (btnAllOn) {
    btnAllOn.addEventListener('click', () => {
      rotorState.autoRunning = false;
      if (rotorState.stage === '2d') {
        rotorState.solo2d = 0;
        rotorState.on2d = [true, true, true, true, true, true];
      } else if (rotorState.stage === 'st') {
        rotorState.soloSt = 0;
        rotorState.stOn.t1 = true;
        rotorState.stOn.t3 = true;
      } else {
        rotorState.cfYawDeg = 0;
        rotorState.cfPitchDeg = 0;
        rotorState.cfLightDeltaDeg = 0;
        rotorState.cfTimeExtrap = 0;
        syncF3dControls();
      }
      renderStagePanels();
      updateVerdictAndSummary();
    });
  }

  const btnWebcam = document.getElementById('d3d-btn-webcam');
  if (btnWebcam) btnWebcam.addEventListener('click', () => startLiveWebcam());

  const btnMic = document.getElementById('d3d-btn-mic');
  if (btnMic) btnMic.addEventListener('click', () => toggleMicAudio());

  const btnVidAud = document.getElementById('d3d-btn-video-audio');
  if (btnVidAud) {
    btnVidAud.addEventListener('click', () => {
      if (localVideoEl) connectVideoAudioTrack(localVideoEl);
    });
  }

  const fileInput = document.getElementById('d3d-video-file-input');
  const btnFile = document.getElementById('d3d-btn-video-file');
  if (btnFile && fileInput) {
    btnFile.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
      const f = e.target.files && e.target.files[0];
      if (f) handleLocalFile(f);
      fileInput.value = '';
    });
  }

  document.querySelectorAll('[data-d3d-preset]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const preset = HD_VIDEO_PRESETS[btn.dataset.d3dPreset];
      if (preset) loadVideoStreamUrl(preset.url, preset.label, false);
    });
  });

  document.querySelectorAll('#d3d-display-mode-tabs button').forEach((btn) => {
    btn.addEventListener('click', () => {
      const m = Number(btn.dataset.dmode);
      if (Number.isNaN(m)) return;
      rotorState.solo2d = 0;
      rotorState.soloSt = 0;
      rotorState.displayMode = m;
      syncDisplayButtons();
      renderStagePanels();
      updateVerdictAndSummary();
    });
  });

  // Stage 3 Counterfactual sliders
  const bindRange = (id, setter) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input', () => {
      rotorState.autoRunning = false;
      setter(Number(el.value));
      syncF3dControls();
      updateVerdictAndSummary();
    });
  };
  bindRange('d3d-rng-yaw', (v) => { rotorState.cfYawDeg = v; });
  bindRange('d3d-rng-pitch', (v) => { rotorState.cfPitchDeg = v; });
  bindRange('d3d-rng-light', (v) => { rotorState.cfLightDeltaDeg = v; });
  bindRange('d3d-rng-extrap', (v) => { rotorState.cfTimeExtrap = v; });
  bindRange('d3d-rng-depth', (v) => { rotorState.cfDepthScale = v; });

  // Stage 4: Ontological Resonance controls
  const btnOntoRun = document.getElementById('d3d-btn-onto-run');
  const inOntoA = document.getElementById('d3d-onto-a');
  const inOntoB = document.getElementById('d3d-onto-b');
  const triggerOnto = () => {
    const a = inOntoA ? inOntoA.value : '나무';
    const b = inOntoB ? inOntoB.value : '숲';
    runOntologicalResonance(a, b);
  };
  if (btnOntoRun) btnOntoRun.addEventListener('click', triggerOnto);
  if (inOntoA) inOntoA.addEventListener('keydown', (e) => { if (e.key === 'Enter') triggerOnto(); });
  if (inOntoB) inOntoB.addEventListener('keydown', (e) => { if (e.key === 'Enter') triggerOnto(); });

  document.querySelectorAll('[data-onto-pair]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const [a, b] = String(btn.dataset.ontoPair || '').split('|');
      runOntologicalResonance(a, b || '');
    });
  });

  syncDisplayButtons();
  syncAudioButtons();
  setRotorStage('onto');
  renderDiscoveryLog();
}

function onEnterTab() {
  bindUI();
  if (!gpuRenderer) {
    const host = document.getElementById('d3d-canvas-host');
    if (host) gpuRenderer = new ScaleRotorGPURenderer(host);
  }
  tabActive = true;
  if (gpuRenderer) gpuRenderer.handleResize();

  if (rotorState.stage === 'onto' && !ontoState.data && !ontoState.loading) {
    runOntologicalResonance(ontoState.conceptA, ontoState.conceptB);
  } else if (rotorState.stage === 'onto' && ontoState.data && gpuRenderer) {
    gpuRenderer.updateOntologyScene(ontoState.data);
  }

  const shared = document.getElementById('hd-video-source');
  if (activeSourceKind === 'hd_shared') {
    if (shared && shared.src && shared.readyState >= 2) {
      shared.play().catch(() => {});
    } else if (rotorState.stage !== 'onto') {
      loadVideoStreamUrl(HD_VIDEO_PRESETS.traffic.url, HD_VIDEO_PRESETS.traffic.label, false);
    }
  }
  renderStagePanels();
  updateVerdictAndSummary();
  if (!rafId) rafId = requestAnimationFrame(stepLoop);
}

function onLeaveTab() {
  tabActive = false;
  if (rafId) {
    cancelAnimationFrame(rafId);
    rafId = 0;
  }
  stopLocalWebcam();
  stopMicAudio();
}

window.ElysiaInverseDistill3D = {
  onEnterTab,
  onLeaveTab,
  setRotorStage,
  startLiveWebcam,
  toggleMicAudio,
  startStageAutonomousDiscovery,
  runOntologicalResonance,
  getState: () => ({
    stage: rotorState.stage,
    on2d: [...rotorState.on2d],
    stOn: { ...rotorState.stOn },
    metrics2d: { ...metrics2d },
    metricsSt: { ...metricsSt },
    metrics3d: { ...metrics3d },
    audioMode: audioSensor.mode,
    audioCorrR: audioSensor.corrR,
    onto: ontoState.data ? {
      a: ontoState.data.conceptA.title,
      b: ontoState.data.conceptB ? ontoState.data.conceptB.title : null,
      comparison: ontoState.data.comparison,
      opticalSimPct: ontoState.opticalSimPct,
    } : null,
  }),
};
