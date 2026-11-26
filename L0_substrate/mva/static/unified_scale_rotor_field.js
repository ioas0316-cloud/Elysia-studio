import * as THREE from 'three';

/* ============================================================================
 * Elysia Unified Scale-Rotor Continuum Engine (4K UHD GPU + Single Living Field)
 * ----------------------------------------------------------------------------
 * Unifies all 6 coupled organs into ONE shared continuous causal field:
 *   1) 4K UHD WebGL2 Optical & Audio Spectrum Prism (exact ΣC1..C6 === O)
 *   2) 3D Falsification Relief & Off-Frame Relighting
 *   3) Coupled Digital Twin Autonomous Agents
 *   4) 6-Axis Ontological & Phenomenon Anatomy (Live Wikipedia + Commons)
 *   5) World Tree Growth Rings & Live Earth Atmospheric Telemetry (Open-Meteo)
 *   6) 4K Hardware Memory Hierarchy & CUDA Warp-32 SoA Compaction
 * ============================================================================ */

const OPTICAL_AXES = [
  { id: 'c1', code: 'C1', name: '거시 휘도 · 환경광', desc: '하늘·대기 전역 확산 조도 (S4 저주파)', color: '#38BDF8' },
  { id: 'c2', code: 'C2', name: '형태 · 구조 경계', desc: '객체 실루엣·중간 대역 윤곽 (S2 중주파)', color: '#10B981' },
  { id: 'c3', code: 'C3', name: '직사광 · 국소 음영', desc: '외부 광원 방향성·그림자 대비 (S1)', color: '#F59E0B' },
  { id: 'c4', code: 'C4', name: '색채 · 채도 스펙트럼', desc: '표면 반사 색소·분광 분포 (표면 변이)', color: '#F43F5E' },
  { id: 'c5', code: 'C5', name: '정반사 · 광택 하이라이트', desc: '물리 재질 거칠기·프레넬 반사 (S0)', color: '#E2E8F0' },
  { id: 'c6', code: 'C6', name: '미시 질감 · 고주파 잔차', desc: '미세 표면 결·고주파 색차 보전 (S0)', color: '#A78BFA' },
];

const BASIS_LABELS = {
  scale: '스케일 계층 (S0 미시 → S4 행성)',
  chromatic: '색채 동역학 (Red 흐름 · Blue 질서 · Yellow 발산)',
  causal6: '6축 인과 구조 (요소·구조·원리·변화·환경·조건)',
  hardware: '하드웨어 메모리 · CUDA (Warp-32 → SSD)',
};

const SCALE_STOP_NAMES = [
  'S0 미시 광학·원자',
  'S1 개체 형태·3D 기복',
  'S2 디지털 트윈·행위',
  'S3 6축 인과·공명망',
  'S4 세계수·행성·메모리',
];

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

const el = (id) => document.getElementById(id);

function clearChildren(node) {
  if (!node) return;
  while (node.firstChild) node.removeChild(node.firstChild);
}

function makeNode(tag, className, text) {
  const n = document.createElement(tag);
  if (className) n.className = className;
  if (text !== undefined && text !== null) n.textContent = String(text);
  return n;
}

/* ============================================================================
 * Unified Living Field State (Single Source of Truth Across All 6 Organs)
 * ============================================================================ */
const state = {
  conceptA: '나무',
  conceptB: '숲',
  basis: 'scale',           // 'scale' | 'chromatic' | 'causal6' | 'hardware'
  resTier: '4k',            // '2k' | '4k'
  autoAdapt: true,
  sigma: 2.1,               // Continuous Scale-Rotor dial [0..4]
  loupeEnabled: false,
  gpuView: 'split',         // 'split' | 'recon' | 'residual'
  splitPos: 0.52,

  activeOrgans: {
    optics: true,
    falsify3d: true,
    twin: true,
    ontology: true,
    worldtree: true,
    hardware: true,
  },

  // Optical C1..C6 switches & measured energies
  opticsOn: [true, true, true, true, true, true],
  opticsSolo: -1,
  opticsEnergy: [0.34, 0.19, 0.16, 0.15, 0.08, 0.08],
  residualPct: 0.0,
  activeTileRatio: 0.14,    // Sparse 4K tiles exceeding residual/motion threshold
  audioFlux: 0.0,
  audioActive: false,

  // Active Media Source (Image or Video or Webcam)
  mediaKind: 'none',        // 'image' | 'video' | 'webcam' | 'procedural'
  mediaLabel: '실물 광학 로딩 중',
  mediaNaturalW: 1920,
  mediaNaturalH: 1080,
  activeImg: null,
  activeVideo: null,
  mediaDirty: true,

  // 3D Falsification & Off-frame Light
  sunAzimuth: 38,
  sunElevation: 48,
  reliefDepth: 1.1,
  futureDt: 0.0,
  camYaw: 0.42,
  camPitch: 0.36,
  voidPct: 0.0,
  shadowErrPct: 0.0,

  // Coupled Digital Twin State
  twinCohesionParam: 1.15,
  twinFrictionParam: 0.35,
  twinCount: 84,
  twinMeasuredCohesion: 74,
  twinMeasuredTension: 26,
  twinShockDecay: 0,
  twinShockType: 'none',

  // Live Ontology / Multi-Instance Data
  ontology: null,
  photos: [],
  activePhotoIdx: 0,
  opticalInvariancePct: 0,
  opticalSurfaceVarPct: 0,
  lastConstraintVerdict: '',

  // Chromatic Triad (Red Flux / Blue Order / Yellow Entropy)
  chromatic: { r: 0.33, b: 0.34, y: 0.33 },

  // Live Earth Telemetry (Open-Meteo)
  earth: null,

  // World Tree Growth Rings
  rings: [],

  // Hardware / CUDA Live Metrics
  hwSavingsPct: 86.2,
  hwActiveWarps: 420,
  hwTotalWarps: 3072,
  lastCudaCode: '',
};

/* ============================================================================
 * 1. 4K UHD WebGL2 Shader Optical Prism (Zero-Blur Native 3840x2160)
 * ============================================================================ */
const gpu = {
  canvas: null,
  gl: null,
  program: null,
  tex: null,
  vao: null,
  uniforms: {},
  fallback2d: null,
  ready: false,
  width: 3840,
  height: 2160,
  mouseU: 0.5,
  mouseV: 0.5,
  mouseInside: false,
  loupeCanvas: null,
  loupeCtx: null,
  // Lightweight offscreen CPU measurement canvas (for exact residual/tile/relief math)
  probeCanvas: document.createElement('canvas'),
  probeCtx: null,
  prevLuma: null,
  depthGrid: new Float32Array(128 * 72),
};
gpu.probeCanvas.width = 128;
gpu.probeCanvas.height = 72;
gpu.probeCtx = gpu.probeCanvas.getContext('2d', { willReadFrequently: true });

const VS_SRC = `#version 300 es
precision highp float;
const vec2 POS[4] = vec2[4](
  vec2(-1.0, -1.0),
  vec2( 1.0, -1.0),
  vec2(-1.0,  1.0),
  vec2( 1.0,  1.0)
);
out vec2 vUv;
void main() {
  vec2 p = POS[gl_VertexID];
  vUv = vec2(p.x * 0.5 + 0.5, 1.0 - (p.y * 0.5 + 0.5));
  gl_Position = vec4(p, 0.0, 1.0);
}
`;

const FS_SRC = `#version 300 es
precision highp float;
in vec2 vUv;
out vec4 fragColor;

uniform sampler2D uTex;
uniform vec2 uTexel;
uniform float uW[6];       // C1..C6 active weights (0.0 or 1.0)
uniform float uSplit;      // split x position [0..1]
uniform int uViewMode;     // 0=split, 1=recon, 2=residual
uniform int uBasisMode;    // 0=scale, 1=chromatic, 2=causal6, 3=hardware
uniform float uSunBias;    // off-frame sun modulation
uniform float uAudioFlux;  // live acoustic flux
uniform float uTime;

vec3 sampleBlur(vec2 uv, float radius) {
  vec2 o = uTexel * radius;
  vec3 s = texture(uTex, uv).rgb * 0.25;
  s += texture(uTex, uv + vec2( o.x,  0.0)).rgb * 0.125;
  s += texture(uTex, uv + vec2(-o.x,  0.0)).rgb * 0.125;
  s += texture(uTex, uv + vec2( 0.0,  o.y)).rgb * 0.125;
  s += texture(uTex, uv + vec2( 0.0, -o.y)).rgb * 0.125;
  s += texture(uTex, uv + vec2( o.x,  o.y)).rgb * 0.0625;
  s += texture(uTex, uv + vec2(-o.x,  o.y)).rgb * 0.0625;
  s += texture(uTex, uv + vec2( o.x, -o.y)).rgb * 0.0625;
  s += texture(uTex, uv + vec2(-o.x, -o.y)).rgb * 0.0625;
  return s;
}

float lumaOf(vec3 c) {
  return dot(c, vec3(0.2126, 0.7152, 0.0722));
}

void main() {
  vec3 orig = texture(uTex, vUv).rgb;
  vec3 midBlur = sampleBlur(vUv, 2.5);
  vec3 wideBlur = sampleBlur(vUv, 14.0);

  float yOrig = lumaOf(orig);
  float yMid = lumaOf(midBlur);
  float yWide = lumaOf(wideBlur);

  // Exact additive partition: c1 + c2 + c3 + c4 + c5 + c6 === orig
  vec3 c1 = vec3(yWide);                                           // Macro ambient luminance
  vec3 c2 = vec3(yMid - yWide);                                    // Mid-scale structure & silhouettes
  float specMask = smoothstep(0.66, 0.94, yOrig);
  vec3 c5 = vec3(max(0.0, yOrig - yMid) * specMask);               // Specular highlight
  vec3 c3 = vec3((yOrig - yMid) * (1.0 - specMask));               // Direct lighting & local shadow
  vec3 c4 = midBlur - vec3(yMid);                                  // Surface color / chroma
  vec3 c6 = orig - (c1 + c2 + c3 + c4 + c5);                       // Micro texture & high-freq residual

  vec3 recon =
    c1 * uW[0] +
    c2 * uW[1] +
    c3 * uW[2] +
    c4 * uW[3] +
    c5 * uW[4] +
    c6 * uW[5];

  vec3 diff = abs(orig - recon);
  float err = clamp(length(diff) * 2.4, 0.0, 1.0);

  // Residual visualization responds to Reclassification Basis
  vec3 resVis;
  if (uBasisMode == 1) {
    // Chromatic Dynamics: Red=Flux(C6+C3), Blue=Order(C2+C1), Yellow=Entropy(C4+C5)
    float rCh = length(c3 * (1.0 - uW[2]) + c6 * (1.0 - uW[5])) * 2.8 + uAudioFlux * 0.15;
    float bCh = length(c1 * (1.0 - uW[0]) + c2 * (1.0 - uW[1])) * 2.4;
    float yCh = length(c4 * (1.0 - uW[3]) + c5 * (1.0 - uW[4])) * 2.8;
    resVis = vec3(rCh + yCh * 0.85, yCh * 0.72 + bCh * 0.35, bCh * 1.15);
    resVis = mix(vec3(0.03, 0.05, 0.09) + orig * 0.12, resVis, clamp(err * 1.6 + 0.18, 0.0, 1.0));
  } else if (uBasisMode == 3) {
    // Hardware CUDA Tile Compaction Overlay (32x32 Warp-32 active tile grid)
    vec2 tileUv = fract(vUv * vec2(48.0, 27.0));
    float gridLine = (tileUv.x < 0.04 || tileUv.y < 0.04) ? 0.22 : 0.0;
    float tileEnergy = clamp(length(c2) * 2.2 + err * 2.8 + length(c6) * 2.6, 0.0, 1.0);
    vec3 coldCol = vec3(0.03, 0.07, 0.14);
    vec3 hotCol = vec3(0.04, 0.78, 0.92);
    vec3 alertCol = vec3(0.96, 0.28, 0.42);
    resVis = mix(coldCol, hotCol, smoothstep(0.08, 0.45, tileEnergy));
    resVis = mix(resVis, alertCol, smoothstep(0.45, 0.85, tileEnergy));
    resVis += vec3(gridLine * (0.25 + tileEnergy * 0.75));
  } else {
    // Standard Unperceived Order Residual Heat Map
    vec3 baseDim = orig * 0.14 + vec3(0.02, 0.03, 0.06);
    vec3 heat = mix(vec3(0.06, 0.72, 0.84), vec3(0.96, 0.25, 0.38), smoothstep(0.15, 0.75, err));
    heat = mix(heat, vec3(0.99, 0.84, 0.32), smoothstep(0.75, 1.0, err));
    resVis = mix(baseDim, heat, smoothstep(0.015, 0.35, err));
  }

  // Subtle off-frame sun contrast cue on recon when C3 is active
  vec3 outRecon = clamp(recon * (1.0 + uSunBias * 0.08 * uW[2]), 0.0, 1.0);

  vec3 col = outRecon;
  if (uViewMode == 2) {
    col = resVis;
  } else if (uViewMode == 0) {
    col = (vUv.x < uSplit) ? outRecon : resVis;
    float divider = smoothstep(0.0022, 0.0, abs(vUv.x - uSplit));
    col = mix(col, vec3(0.05, 0.85, 0.96), divider);
  }

  fragColor = vec4(col, 1.0);
}
`;

function compileShader(gl, type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    console.warn('WebGL2 shader error:', gl.getShaderInfoLog(s));
    gl.deleteShader(s);
    return null;
  }
  return s;
}

function initGpuPrism() {
  gpu.canvas = el('u-gpu-canvas');
  gpu.loupeCanvas = el('u-loupe-canvas');
  if (gpu.loupeCanvas) gpu.loupeCtx = gpu.loupeCanvas.getContext('2d');
  if (!gpu.canvas) return;

  gpu.canvas.addEventListener('webglcontextlost', (e) => {
    e.preventDefault();
    gpu.ready = false;
  });
  gpu.canvas.addEventListener('webglcontextrestored', () => {
    setupWebGL2();
    state.mediaDirty = true;
  });

  setupWebGL2();
  applyResolutionTier(state.resTier);
}

function setupWebGL2() {
  const gl = gpu.canvas.getContext('webgl2', {
    antialias: false,
    alpha: false,
    preserveDrawingBuffer: true, // Needed for 1:1 4K Loupe sampling
    powerPreference: 'high-performance',
  });
  if (!gl) {
    gpu.fallback2d = gpu.canvas.getContext('2d');
    gpu.ready = false;
    return;
  }
  const vs = compileShader(gl, gl.VERTEX_SHADER, VS_SRC);
  const fs = compileShader(gl, gl.FRAGMENT_SHADER, FS_SRC);
  if (!vs || !fs) return;

  const prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    console.warn('WebGL2 link error:', gl.getProgramInfoLog(prog));
    return;
  }

  const vao = gl.createVertexArray();
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  // Seed initial 2x2 dark texture so shader never reads unbound texture
  gl.texImage2D(
    gl.TEXTURE_2D, 0, gl.RGBA, 2, 2, 0, gl.RGBA, gl.UNSIGNED_BYTE,
    new Uint8Array([14, 22, 34, 255, 22, 38, 52, 255, 18, 30, 44, 255, 10, 18, 28, 255])
  );

  gpu.gl = gl;
  gpu.program = prog;
  gpu.vao = vao;
  gpu.tex = tex;
  gpu.uniforms = {
    uTex: gl.getUniformLocation(prog, 'uTex'),
    uTexel: gl.getUniformLocation(prog, 'uTexel'),
    uW: gl.getUniformLocation(prog, 'uW'),
    uSplit: gl.getUniformLocation(prog, 'uSplit'),
    uViewMode: gl.getUniformLocation(prog, 'uViewMode'),
    uBasisMode: gl.getUniformLocation(prog, 'uBasisMode'),
    uSunBias: gl.getUniformLocation(prog, 'uSunBias'),
    uAudioFlux: gl.getUniformLocation(prog, 'uAudioFlux'),
    uTime: gl.getUniformLocation(prog, 'uTime'),
  };
  gpu.ready = true;
}

function applyResolutionTier(tier) {
  state.resTier = tier === '2k' ? '2k' : '4k';
  const w = state.resTier === '4k' ? 3840 : 2560;
  const h = state.resTier === '4k' ? 2160 : 1440;
  gpu.width = w;
  gpu.height = h;
  if (gpu.canvas) {
    gpu.canvas.width = w;
    gpu.canvas.height = h;
  }
  if (gpu.gl) {
    gpu.gl.viewport(0, 0, w, h);
  }
  if (threeState.renderer && threeState.host) {
    const dprCap = state.resTier === '4k' ? 2.5 : 1.75;
    threeState.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, dprCap));
    resizeThree();
  }
  const statRes = el('u-stat-res');
  if (statRes) statRes.textContent = `${w}×${h}`;
  const gpuMeta = el('u-gpu-meta');
  if (gpuMeta) {
    gpuMeta.textContent = `${w}×${h} WebGL2 · 원본 ${state.mediaNaturalW}×${state.mediaNaturalH}`;
  }
  updateHardwareMetrics();
}

function getEffectiveWeights() {
  if (state.opticsSolo >= 0) {
    return [0, 1, 2, 3, 4, 5].map((i) => (i === state.opticsSolo ? 1.0 : 0.0));
  }
  return state.opticsOn.map((on) => (on ? 1.0 : 0.0));
}

function uploadActiveMediaToGpuAnd3D() {
  const src =
    state.mediaKind === 'image' ? state.activeImg :
    (state.mediaKind === 'video' || state.mediaKind === 'webcam') ? state.activeVideo :
    null;
  if (!src) return;

  if (state.mediaKind === 'video' || state.mediaKind === 'webcam') {
    if (!src.videoWidth || src.readyState < 2) return;
    state.mediaNaturalW = src.videoWidth;
    state.mediaNaturalH = src.videoHeight;
  } else if (state.mediaKind === 'image') {
    if (!src.naturalWidth) return;
    state.mediaNaturalW = src.naturalWidth;
    state.mediaNaturalH = src.naturalHeight;
  }

  if (gpu.ready && gpu.gl) {
    const gl = gpu.gl;
    gl.bindTexture(gl.TEXTURE_2D, gpu.tex);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    try {
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
    } catch {
      // Ignore transient frame upload errors
    }
  } else if (gpu.fallback2d) {
    gpu.fallback2d.drawImage(src, 0, 0, gpu.width, gpu.height);
  }

  // Update Three.js 3D Relief Texture from the EXACT SAME live media!
  if (threeState.reliefMat) {
    if (state.mediaKind === 'video' || state.mediaKind === 'webcam') {
      if (!threeState.videoTex || threeState.videoTex.image !== src) {
        if (threeState.videoTex) threeState.videoTex.dispose();
        threeState.videoTex = new THREE.VideoTexture(src);
        threeState.videoTex.colorSpace = THREE.SRGBColorSpace;
        threeState.videoTex.minFilter = THREE.LinearFilter;
        threeState.videoTex.magFilter = THREE.LinearFilter;
      }
      threeState.reliefMat.map = threeState.videoTex;
      threeState.reliefMat.needsUpdate = true;
    } else if (state.mediaKind === 'image') {
      if (!threeState.imgTex || threeState.imgTex.image !== src) {
        if (threeState.imgTex) threeState.imgTex.dispose();
        threeState.imgTex = new THREE.Texture(src);
        threeState.imgTex.colorSpace = THREE.SRGBColorSpace;
        threeState.imgTex.anisotropy = 8;
        threeState.imgTex.needsUpdate = true;
      }
      threeState.reliefMat.map = threeState.imgTex;
      threeState.reliefMat.needsUpdate = true;
    }
  }

  // Run lightweight 128x72 CPU measurement for exact C1..C6 energy, depth grid, & sparse CUDA tile ratio
  measureMediaSpectrumAndDepth(src);

  const gpuMeta = el('u-gpu-meta');
  if (gpuMeta) {
    gpuMeta.textContent = `${gpu.width}×${gpu.height} WebGL2 · 실물 ${state.mediaNaturalW}×${state.mediaNaturalH}`;
  }
  state.mediaDirty = false;
}

function measureMediaSpectrumAndDepth(src) {
  const W = 128;
  const H = 72;
  const ctx = gpu.probeCtx;
  if (!ctx) return;
  try {
    ctx.drawImage(src, 0, 0, W, H);
  } catch {
    return;
  }
  const imgData = ctx.getImageData(0, 0, W, H).data;
  const N = W * H;
  const luma = new Float32Array(N);
  const chroma = new Float32Array(N);
  let sumR = 0, sumG = 0, sumB = 0;

  for (let i = 0; i < N; i++) {
    const r = imgData[i * 4] / 255;
    const g = imgData[i * 4 + 1] / 255;
    const b = imgData[i * 4 + 2] / 255;
    const y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    luma[i] = y;
    chroma[i] = Math.hypot(r - y, g - y, b - y);
    sumR += r;
    sumG += g;
    sumB += b;
  }

  // Box blur for mid & wide luma
  const mid = new Float32Array(N);
  const wide = new Float32Array(N);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let acc = 0, cnt = 0;
      for (let dy = -1; dy <= 1; dy++) {
        const ny = clamp(y + dy, 0, H - 1);
        for (let dx = -1; dx <= 1; dx++) {
          const nx = clamp(x + dx, 0, W - 1);
          acc += luma[ny * W + nx];
          cnt++;
        }
      }
      mid[y * W + x] = acc / cnt;
    }
  }
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let acc = 0, cnt = 0;
      for (let dy = -4; dy <= 4; dy += 2) {
        const ny = clamp(y + dy, 0, H - 1);
        for (let dx = -4; dx <= 4; dx += 2) {
          const nx = clamp(x + dx, 0, W - 1);
          acc += mid[ny * W + nx];
          cnt++;
        }
      }
      wide[y * W + x] = acc / cnt;
    }
  }

  let e1 = 0, e2 = 0, e3 = 0, e4 = 0, e5 = 0, e6 = 0;
  let activeTiles = 0;
  const totalTiles = 16 * 9;
  const tileAcc = new Float32Array(totalTiles);

  for (let y = 0; y < H; y++) {
    const ty = Math.min(8, Math.floor((y / H) * 9));
    for (let x = 0; x < W; x++) {
      const idx = y * W + x;
      const yO = luma[idx];
      const yM = mid[idx];
      const yW = wide[idx];
      const specMask = clamp((yO - 0.66) / 0.28, 0, 1);
      const hi = Math.abs(yO - yM);

      e1 += yW;
      e2 += Math.abs(yM - yW) * 3.5;
      e3 += hi * (1 - specMask) * 4.0;
      e4 += chroma[idx] * 2.4;
      e5 += hi * specMask * 5.2;
      const temporalDelta = gpu.prevLuma ? Math.abs(yO - gpu.prevLuma[idx]) : 0;
      e6 += (hi * 2.0 + temporalDelta * 3.2);

      // Depth relief grid combining structure + luminance + center focus
      gpu.depthGrid[idx] = clamp(yM * 0.68 + Math.abs(yM - yW) * 1.45, 0, 1);

      const tx = Math.min(15, Math.floor((x / W) * 16));
      tileAcc[ty * 16 + tx] += Math.abs(yM - yW) + hi + temporalDelta * 2.2;
    }
  }
  gpu.prevLuma = luma;

  const tot = e1 + e2 + e3 + e4 + e5 + e6 + 1e-6;
  state.opticsEnergy = [e1 / tot, e2 / tot, e3 / tot, e4 / tot, e5 / tot, e6 / tot];

  // Compute exact residual based on active optical switches
  const w = getEffectiveWeights();
  let missingEnergy = 0;
  for (let i = 0; i < 6; i++) {
    if (w[i] < 0.5) missingEnergy += state.opticsEnergy[i];
  }
  state.residualPct = Number((missingEnergy * 100).toFixed(2));

  // Count tiles that genuinely require S0 Warp-32 compute
  for (let t = 0; t < totalTiles; t++) {
    const avg = tileAcc[t] / ((W / 16) * (H / 9));
    if (avg > 0.055 || missingEnergy > 0.12) activeTiles++;
  }
  state.activeTileRatio = clamp(activeTiles / totalTiles + missingEnergy * 0.5, 0.05, 1.0);

  // Feed relief grid into 3D mesh vertices
  update3DReliefGeometry();
  updateOpticalPanels();
  updateHardwareMetrics();
}

function renderGpuFrame(tSec) {
  if (!gpu.ready || !gpu.gl) return;
  if (state.mediaKind === 'video' || state.mediaKind === 'webcam') {
    uploadActiveMediaToGpuAnd3D();
  } else if (state.mediaDirty) {
    uploadActiveMediaToGpuAnd3D();
  }

  const gl = gpu.gl;
  gl.viewport(0, 0, gpu.width, gpu.height);
  gl.useProgram(gpu.program);
  gl.bindVertexArray(gpu.vao);
  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, gpu.tex);
  gl.uniform1i(gpu.uniforms.uTex, 0);
  gl.uniform2f(gpu.uniforms.uTexel, 1 / Math.max(1, state.mediaNaturalW), 1 / Math.max(1, state.mediaNaturalH));
  gl.uniform1fv(gpu.uniforms.uW, new Float32Array(getEffectiveWeights()));
  gl.uniform1f(gpu.uniforms.uSplit, state.splitPos);
  const vMode = state.gpuView === 'recon' ? 1 : state.gpuView === 'residual' ? 2 : 0;
  gl.uniform1i(gpu.uniforms.uViewMode, vMode);
  const bMode =
    state.basis === 'chromatic' ? 1 :
    state.basis === 'causal6' ? 2 :
    state.basis === 'hardware' ? 3 : 0;
  gl.uniform1i(gpu.uniforms.uBasisMode, bMode);
  gl.uniform1f(gpu.uniforms.uSunBias, Math.sin((state.sunElevation * Math.PI) / 180) - 0.5);
  gl.uniform1f(gpu.uniforms.uAudioFlux, state.audioFlux);
  gl.uniform1f(gpu.uniforms.uTime, tSec);

  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

  // Update 1:1 4K Detail Loupe if enabled and pointer hovering
  if (state.loupeEnabled && gpu.mouseInside && gpu.loupeCtx) {
    const sx = clamp(Math.floor(gpu.mouseU * gpu.width) - 84, 0, gpu.width - 168);
    const sy = clamp(Math.floor(gpu.mouseV * gpu.height) - 84, 0, gpu.height - 168);
    gpu.loupeCtx.drawImage(gpu.canvas, sx, sy, 168, 168, 0, 0, 168, 168);
    const cap = el('u-loupe-cap');
    if (cap) cap.textContent = `1:1 (${sx}, ${sy}) · ${gpu.width}×${gpu.height}`;
  }
}

/* ============================================================================
 * 2. Unified 3D Scale-Rotor Continuum (Three.js Single Scene Integrating ALL)
 * ============================================================================ */
const threeState = {
  host: null,
  renderer: null,
  scene: null,
  camera: null,
  sunLight: null,
  fillLight: null,
  rimLight: null,
  ambientLight: null,
  // Organ Layer Groups (toggled/reweighted smoothly in ONE 3D scene!)
  reliefMesh: null,
  reliefGeo: null,
  reliefMat: null,
  imgTex: null,
  videoTex: null,
  ringGroup: null,
  ringMeshes: [],
  twinMesh: null,
  twinAgents: [],
  twinLines: null,
  ontoGroup: null,
  ontoNodes: [],
  ontoLines: null,
  treeGroup: null,
  treeRings: [],
  dragging: false,
  lastX: 0,
  lastY: 0,
};

function initThreeContinuum() {
  threeState.host = el('u-3d-host');
  if (!threeState.host) return;

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: 'high-performance',
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2.5));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;
  renderer.domElement.style.width = '100%';
  renderer.domElement.style.height = '100%';
  renderer.domElement.style.display = 'block';
  threeState.host.insertBefore(renderer.domElement, threeState.host.firstChild);

  renderer.domElement.addEventListener('webglcontextlost', (e) => e.preventDefault());

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#050811');
  scene.fog = new THREE.FogExp2('#050811', 0.022);

  const camera = new THREE.PerspectiveCamera(44, 16 / 9, 0.1, 140);
  camera.position.set(0, 5.5, 13.5);

  // Three-Point Studio Lighting + Off-Frame Directional Sun
  const ambient = new THREE.AmbientLight('#8AA4C8', 0.48);
  const sun = new THREE.DirectionalLight('#FFF3DC', 1.9);
  sun.position.set(8, 10, 8);
  const fill = new THREE.DirectionalLight('#38BDF8', 0.55);
  fill.position.set(-9, 4, -6);
  const rim = new THREE.DirectionalLight('#10B981', 0.45);
  rim.position.set(0, 7, -11);
  scene.add(ambient, sun, fill, rim);

  threeState.renderer = renderer;
  threeState.scene = scene;
  threeState.camera = camera;
  threeState.ambientLight = ambient;
  threeState.sunLight = sun;
  threeState.fillLight = fill;
  threeState.rimLight = rim;

  buildUnified3DLayers();
  attach3DPointerControls();
  resizeThree();
  window.addEventListener('resize', resizeThree);
}

function resizeThree() {
  if (!threeState.host || !threeState.renderer || !threeState.camera) return;
  const rect = threeState.host.getBoundingClientRect();
  const w = Math.max(320, Math.floor(rect.width));
  const h = Math.max(240, Math.floor(rect.height));
  threeState.renderer.setSize(w, h, false);
  threeState.camera.aspect = w / h;
  threeState.camera.updateProjectionMatrix();
}

function buildUnified3DLayers() {
  const scene = threeState.scene;

  // A. Center 3D Depth-Displaced Real-Media Relief Mesh (128x72 segments)
  const reliefGeo = new THREE.PlaneGeometry(6.8, 3.82, 127, 71);
  const reliefMat = new THREE.MeshStandardMaterial({
    color: '#FFFFFF',
    roughness: 0.55,
    metalness: 0.12,
    side: THREE.DoubleSide,
  });
  const reliefMesh = new THREE.Mesh(reliefGeo, reliefMat);
  reliefMesh.position.set(0, 0.25, 0);
  scene.add(reliefMesh);
  threeState.reliefGeo = reliefGeo;
  threeState.reliefMat = reliefMat;
  threeState.reliefMesh = reliefMesh;

  // B. 5 Concentric Scale-Rotor Rings (S0..S4)
  const ringGroup = new THREE.Group();
  const ringColors = ['#F59E0B', '#38BDF8', '#10B981', '#A78BFA', '#F43F5E'];
  const ringRadii = [2.4, 4.1, 5.9, 7.8, 9.8];
  for (let i = 0; i < 5; i++) {
    const geo = new THREE.TorusGeometry(ringRadii[i], 0.025, 10, 96);
    const mat = new THREE.MeshBasicMaterial({
      color: ringColors[i],
      transparent: true,
      opacity: 0.34,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.x = Math.PI / 2;
    mesh.position.y = -2.2 + i * 0.22;
    ringGroup.add(mesh);
    threeState.ringMeshes.push(mesh);
  }
  scene.add(ringGroup);
  threeState.ringGroup = ringGroup;

  // C. Coupled Digital Twin Autonomous Agents (InstancedMesh up to 160 agents)
  const maxAgents = 160;
  const agentGeo = new THREE.OctahedronGeometry(0.14, 0);
  const agentMat = new THREE.MeshStandardMaterial({
    color: '#FFFFFF',
    roughness: 0.3,
    metalness: 0.35,
    emissive: '#0B2330',
    emissiveIntensity: 0.45,
  });
  const twinMesh = new THREE.InstancedMesh(agentGeo, agentMat, maxAgents);
  twinMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  scene.add(twinMesh);
  threeState.twinMesh = twinMesh;

  threeState.twinAgents = [];
  for (let i = 0; i < maxAgents; i++) {
    const ang = (i / maxAgents) * Math.PI * 2;
    const rad = 3.2 + (i % 5) * 1.15;
    threeState.twinAgents.push({
      pos: new THREE.Vector3(Math.cos(ang) * rad, (Math.random() - 0.5) * 2.6, Math.sin(ang) * rad),
      vel: new THREE.Vector3(-Math.sin(ang) * 0.02, 0, Math.cos(ang) * 0.02),
      phase: Math.random() * Math.PI * 2,
      role: i % 3, // 0=Flux(Red), 1=Order(Blue), 2=Entropy(Yellow)
      tier: i % 5,
    });
  }

  // Dynamic coupling lines between nearby Digital Twin agents
  const maxSegs = 240;
  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(maxSegs * 6), 3));
  const lineMat = new THREE.LineBasicMaterial({
    color: '#06B6D4',
    transparent: true,
    opacity: 0.28,
  });
  const twinLines = new THREE.LineSegments(lineGeo, lineMat);
  scene.add(twinLines);
  threeState.twinLines = twinLines;

  // D. Ontological 6-Axis Constellation Group (rebuilt on concept sync, smoothly lerped on basis switch!)
  const ontoGroup = new THREE.Group();
  scene.add(ontoGroup);
  threeState.ontoGroup = ontoGroup;

  // E. Living World Tree Trunk & Stacked Growth Rings
  const treeGroup = new THREE.Group();
  const trunkGeo = new THREE.CylinderGeometry(0.05, 0.14, 7.6, 12);
  const trunkMat = new THREE.MeshStandardMaterial({
    color: '#10B981',
    emissive: '#064E3B',
    emissiveIntensity: 0.55,
    roughness: 0.5,
  });
  const trunk = new THREE.Mesh(trunkGeo, trunkMat);
  trunk.position.set(0, 0.2, -2.1);
  treeGroup.add(trunk);
  scene.add(treeGroup);
  threeState.treeGroup = treeGroup;
}

function update3DReliefGeometry() {
  if (!threeState.reliefGeo) return;
  const pos = threeState.reliefGeo.attributes.position;
  const W = 128;
  const H = 72;
  const depthScale = state.reliefDepth * (state.activeOrgans.falsify3d ? 1.0 : 0.2);
  const dt = state.futureDt;

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const idx = y * W + x;
      const d = gpu.depthGrid[idx] || 0;
      const wave = dt > 0.01 ? Math.sin(x * 0.16 + dt * 3.1) * Math.cos(y * 0.18 - dt * 2.2) * dt * 0.14 : 0;
      pos.setZ(idx, (d - 0.35) * depthScale * 1.35 + wave);
    }
  }
  pos.needsUpdate = true;
  threeState.reliefGeo.computeVertexNormals();
  update3DFalsificationKPIs();
}

function update3DFalsificationKPIs() {
  // Backface disocclusion void scales nonlinearly with camera yaw/pitch away from 2D frontal camera + relief depth
  const offAxisAngle = Math.hypot(state.camYaw, state.camPitch - 0.18);
  state.voidPct = Number(clamp(offAxisAngle * state.reliefDepth * 24.5, 0, 92).toFixed(1));

  // Shadow contradiction error scales with off-frame sun shift from frontal camera + C3 cut
  const sunShift = Math.hypot((state.sunAzimuth - 38) / 90, (state.sunElevation - 48) / 60);
  const c3OffPenalty = state.opticsOn[2] ? 0 : 34.0;
  state.shadowErrPct = Number(clamp(sunShift * 26.0 + state.futureDt * 11.5 + c3OffPenalty, 0, 98).toFixed(1));

  const kpiVoid = el('u-kpi-void');
  if (kpiVoid) kpiVoid.textContent = `${state.voidPct}%`;
  const kpiShadow = el('u-kpi-shadow');
  if (kpiShadow) kpiShadow.textContent = `${state.shadowErrPct}%`;
  const inlineVoid = el('u-3d-void');
  if (inlineVoid) inlineVoid.textContent = `${state.voidPct}%`;
}

function makeSpriteLabel(text, colorHex) {
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 56;
  const ctx = c.getContext('2d');
  ctx.fillStyle = 'rgba(6, 9, 16, 0.82)';
  ctx.fillRect(4, 6, 248, 44);
  ctx.strokeStyle = colorHex;
  ctx.lineWidth = 2;
  ctx.strokeRect(4, 6, 248, 44);
  ctx.fillStyle = '#F8FAFC';
  ctx.font = '600 21px "Plus Jakarta Sans", sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(String(text || '').slice(0, 14), 128, 28);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
  const sp = new THREE.Sprite(mat);
  sp.scale.set(2.15, 0.47, 1);
  return sp;
}

function rebuildOnto3DConstellation() {
  if (!threeState.ontoGroup) return;
  while (threeState.ontoGroup.children.length > 0) {
    const ch = threeState.ontoGroup.children[0];
    threeState.ontoGroup.remove(ch);
    if (ch.geometry) ch.geometry.dispose();
    if (ch.material) {
      if (ch.material.map) ch.material.map.dispose();
      ch.material.dispose();
    }
  }
  threeState.ontoNodes = [];
  if (!state.ontology) return;

  const cmp = state.ontology.comparison || {};
  const { conceptA, conceptB } = state.ontology;
  const sharedLinks = cmp.sharedLinks || [];
  const onlyALinks = cmp.onlyALinks || [];
  const onlyBLinks = cmp.onlyBLinks || [];
  const items = [];
  items.push({ label: conceptA.title, kind: 'coreA', scale: conceptA.scaleCenter || 1.5, axisIdx: 0 });
  items.push({ label: conceptB.title, kind: 'coreB', scale: conceptB.scaleCenter || 3.2, axisIdx: 5 });

  sharedLinks.slice(0, 12).forEach((l, i) => {
    items.push({ label: l, kind: 'shared', scale: ((conceptA.scaleCenter + conceptB.scaleCenter) * 0.5), axisIdx: i % 6 });
  });
  onlyALinks.slice(0, 10).forEach((l, i) => {
    items.push({ label: l, kind: 'onlyA', scale: conceptA.scaleCenter || 1.4, axisIdx: i % 6 });
  });
  onlyBLinks.slice(0, 10).forEach((l, i) => {
    items.push({ label: l, kind: 'onlyB', scale: conceptB.scaleCenter || 3.4, axisIdx: (i + 3) % 6 });
  });

  const colorMap = {
    coreA: '#38BDF8',
    coreB: '#10B981',
    shared: '#34D399',
    onlyA: '#06B6D4',
    onlyB: '#F43F5E',
  };

  items.forEach((it, idx) => {
    const isCore = it.kind === 'coreA' || it.kind === 'coreB';
    const geo = new THREE.SphereGeometry(isCore ? 0.34 : 0.16, 18, 18);
    const col = colorMap[it.kind] || '#38BDF8';
    const mat = new THREE.MeshStandardMaterial({
      color: col,
      emissive: col,
      emissiveIntensity: isCore ? 0.55 : 0.25,
      roughness: 0.3,
      metalness: 0.2,
    });
    const mesh = new THREE.Mesh(geo, mat);
    threeState.ontoGroup.add(mesh);

    let sprite = null;
    if (isCore || idx < 12) {
      sprite = makeSpriteLabel(it.label, col);
      threeState.ontoGroup.add(sprite);
    }

    threeState.ontoNodes.push({
      mesh,
      sprite,
      item: it,
      idx,
      pos: new THREE.Vector3((Math.random() - 0.5) * 8, (Math.random() - 0.5) * 3, (Math.random() - 0.5) * 8),
      target: new THREE.Vector3(),
    });
  });

  // Causal bridge line geometry connecting cores to shared/only nodes
  const linePositions = new Float32Array(threeState.ontoNodes.length * 6);
  const lGeo = new THREE.BufferGeometry();
  lGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
  const lMat = new THREE.LineBasicMaterial({ color: '#34D399', transparent: true, opacity: 0.32 });
  threeState.ontoLines = new THREE.LineSegments(lGeo, lMat);
  threeState.ontoGroup.add(threeState.ontoLines);

  recomputeOntoNodeTargets();
}

function recomputeOntoNodeTargets() {
  const nodes = threeState.ontoNodes;
  if (!nodes.length) return;
  const total = nodes.length;

  nodes.forEach((n, i) => {
    const it = n.item;
    if (state.basis === 'scale') {
      // Concentric S0..S4 rings
      const r = 2.4 + clamp(it.scale, 0, 4) * 1.85;
      const ang = (i / total) * Math.PI * 2;
      const y = (it.scale - 2.0) * 1.05 + (it.kind === 'coreA' || it.kind === 'coreB' ? 1.1 : 0);
      n.target.set(Math.cos(ang) * r, y, Math.sin(ang) * r);
    } else if (state.basis === 'chromatic') {
      // 3 Chromatic Attractors: Red(Flux), Blue(Order), Yellow(Entropy)
      const cluster = it.kind === 'onlyB' ? 0 : it.kind === 'shared' || it.kind === 'coreA' ? 1 : 2;
      const baseAng = (cluster / 3) * Math.PI * 2;
      const subAng = (i * 1.7) % (Math.PI * 2);
      const subR = it.kind.startsWith('core') ? 0.6 : 1.9;
      n.target.set(
        Math.cos(baseAng) * 5.2 + Math.cos(subAng) * subR,
        Math.sin(subAng) * 1.6,
        Math.sin(baseAng) * 5.2 + Math.sin(subAng) * subR
      );
    } else if (state.basis === 'causal6') {
      // 6 Hexagonal Causal Axis Columns (P1..P6)
      const axAng = (it.axisIdx / 6) * Math.PI * 2;
      const rad = it.kind.startsWith('core') ? 2.8 : 6.2;
      const h = ((i % 5) - 2) * 0.95;
      n.target.set(Math.cos(axAng) * rad, h, Math.sin(axAng) * rad);
    } else {
      // Hardware Memory Hierarchy Vertical Tiers (S0 Reg/Warp bottom -> S4 SSD top)
      const tier = Math.round(clamp(it.scale, 0, 4));
      const ang = (i / total) * Math.PI * 2;
      const r = 2.8 + tier * 1.3;
      const y = -2.6 + tier * 1.45;
      n.target.set(Math.cos(ang) * r, y, Math.sin(ang) * r);
    }
  });
}

function addWorldTreeRing(title, detail, tone = 'cyan') {
  const idx = state.rings.length + 1;
  const nowStr = new Date().toLocaleTimeString('ko-KR', { hour12: false });
  state.rings.unshift({ idx, time: nowStr, title, detail, tone });
  if (state.rings.length > 24) state.rings.pop();

  // Add physical 3D growth ring onto World Tree trunk
  if (threeState.treeGroup) {
    const colorMap = { cyan: '#06B6D4', emerald: '#10B981', amber: '#F59E0B', rose: '#F43F5E' };
    const ringIdx = threeState.treeRings.length;
    const rad = 0.45 + (ringIdx % 9) * 0.22;
    const geo = new THREE.TorusGeometry(rad, 0.028, 8, 48);
    const mat = new THREE.MeshBasicMaterial({
      color: colorMap[tone] || '#06B6D4',
      transparent: true,
      opacity: 0.72,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.x = Math.PI / 2;
    mesh.position.set(0, -2.5 + Math.min(ringIdx, 18) * 0.34, -2.1);
    threeState.treeGroup.add(mesh);
    threeState.treeRings.push(mesh);
    if (threeState.treeRings.length > 20) {
      const old = threeState.treeRings.shift();
      threeState.treeGroup.remove(old);
      old.geometry.dispose();
      old.material.dispose();
    }
  }

  renderWorldTreePanel();
  const rc = el('u-ring-count');
  if (rc) rc.textContent = String(state.rings.length);
}

function attach3DPointerControls() {
  const host = threeState.host;
  if (!host) return;
  host.addEventListener('pointerdown', (e) => {
    if (e.target.closest('input, button')) return;
    threeState.dragging = true;
    threeState.lastX = e.clientX;
    threeState.lastY = e.clientY;
    host.setPointerCapture(e.pointerId);
  });
  host.addEventListener('pointermove', (e) => {
    if (!threeState.dragging) return;
    const dx = e.clientX - threeState.lastX;
    const dy = e.clientY - threeState.lastY;
    threeState.lastX = e.clientX;
    threeState.lastY = e.clientY;
    state.camYaw += dx * 0.007;
    state.camPitch = clamp(state.camPitch + dy * 0.006, -0.45, 1.25);
    update3DFalsificationKPIs();
  });
  host.addEventListener('pointerup', () => {
    threeState.dragging = false;
  });
  host.addEventListener('wheel', (e) => {
    e.preventDefault();
    state.sigma = clamp(state.sigma + Math.sign(e.deltaY) * 0.14, 0, 4);
    syncScaleDialUI();
  }, { passive: false });
}

const dummyObj = new THREE.Object3D();
const tmpColor = new THREE.Color();

function stepAndRender3D(tSec) {
  if (!threeState.renderer || !threeState.scene || !threeState.camera) return;

  // 1) Update Off-Frame Sun Position & Light Intensity coupled to Optical C1/C3!
  const azRad = (state.sunAzimuth * Math.PI) / 180;
  const elRad = (state.sunElevation * Math.PI) / 180;
  const sunR = 14;
  threeState.sunLight.position.set(
    Math.cos(elRad) * Math.sin(azRad) * sunR,
    Math.sin(elRad) * sunR,
    Math.cos(elRad) * Math.cos(azRad) * sunR
  );
  const w = getEffectiveWeights();
  threeState.sunLight.intensity = w[2] > 0.5 ? 2.0 : 0.25;
  threeState.ambientLight.intensity = w[0] > 0.5 ? 0.52 : 0.14;
  if (threeState.reliefMat) {
    threeState.reliefMat.color.setHex(w[3] > 0.5 ? 0xFFFFFF : 0xB8C2CC);
    threeState.reliefMat.roughness = w[4] > 0.5 ? 0.42 : 0.92;
  }

  // Visibility / Prominence coupled to Active Organs
  if (threeState.reliefMesh) threeState.reliefMesh.visible = state.activeOrgans.falsify3d || state.activeOrgans.optics;
  if (threeState.twinMesh) threeState.twinMesh.visible = state.activeOrgans.twin;
  if (threeState.twinLines) threeState.twinLines.visible = state.activeOrgans.twin;
  if (threeState.ontoGroup) threeState.ontoGroup.visible = state.activeOrgans.ontology;
  if (threeState.treeGroup) threeState.treeGroup.visible = state.activeOrgans.worldtree;

  // 2) Rotate 5 Scale-Rotor Rings at golden-ratio gear speeds
  const gearSpeeds = [0.65, 0.4, 0.25, 0.15, 0.09];
  threeState.ringMeshes.forEach((rm, i) => {
    rm.rotation.z = tSec * gearSpeeds[i] * (i % 2 === 0 ? 1 : -1);
    const distFromSigma = Math.abs(state.sigma - i);
    rm.material.opacity = clamp(0.62 - distFromSigma * 0.16, 0.12, 0.68);
  });

  // 3) Step Coupled Digital Twin Autonomous Agents
  if (state.activeOrgans.twin && threeState.twinMesh) {
    const earthWind = state.earth ? (state.earth.actual.windSpeedKmh || 6) / 28 : 0.22;
    const earthDirRad = state.earth ? ((state.earth.actual.windDirectionDeg || 120) * Math.PI) / 180 : 1.1;
    const windX = Math.cos(earthDirRad) * earthWind * 0.018;
    const windZ = Math.sin(earthDirRad) * earthWind * 0.018;
    const c3LightFactor = w[2] > 0.5 ? 1.0 : 0.45; // Cutting light slows/scatters agents!
    const shockBoost = state.twinShockDecay > 0.01 ? state.twinShockDecay : 0;
    state.twinShockDecay = Math.max(0, state.twinShockDecay - 0.008);

    const speedBase = (0.025 + state.chromatic.r * 0.045 + state.audioFlux * 0.05 + shockBoost * 0.06) * c3LightFactor;
    const cohesion = state.twinCohesionParam * (0.6 + state.chromatic.b * 0.8);
    const friction = state.twinFrictionParam + (state.residualPct / 100) * 0.9 + shockBoost * 0.8;

    let avgDist = 0;
    const activeN = clamp(state.twinCount, 24, 160);
    threeState.twinMesh.count = activeN;

    for (let i = 0; i < activeN; i++) {
      const a = threeState.twinAgents[i];
      // Target attractor depends on Reclassification Basis!
      let tx = 0, ty = 0, tz = 0;
      if (state.basis === 'chromatic') {
        const ang = (a.role / 3) * Math.PI * 2 + tSec * 0.18;
        tx = Math.cos(ang) * 4.8;
        tz = Math.sin(ang) * 4.8;
        ty = Math.sin(tSec + a.phase) * 0.9;
      } else if (state.basis === 'causal6') {
        const axAng = ((i % 6) / 6) * Math.PI * 2;
        tx = Math.cos(axAng) * 5.2;
        tz = Math.sin(axAng) * 5.2;
        ty = ((i % 3) - 1) * 1.1;
      } else if (state.basis === 'hardware') {
        const tierR = 2.6 + a.tier * 1.25;
        const ang = tSec * (0.85 - a.tier * 0.14) + a.phase;
        tx = Math.cos(ang) * tierR;
        tz = Math.sin(ang) * tierR;
        ty = -2.4 + a.tier * 1.3;
      } else {
        const targetR = 2.8 + state.sigma * 1.25 + (a.tier - 2) * 0.55;
        const ang = tSec * (0.28 + state.chromatic.r * 0.35) + a.phase;
        tx = Math.cos(ang) * targetR;
        tz = Math.sin(ang) * targetR;
        ty = Math.sin(tSec * 0.9 + a.phase) * (0.65 + state.chromatic.y * 1.6);
      }

      a.vel.x += (tx - a.pos.x) * 0.004 * cohesion + windX + (Math.random() - 0.5) * friction * 0.022;
      a.vel.y += (ty - a.pos.y) * 0.005 * cohesion + (Math.random() - 0.5) * friction * 0.016;
      a.vel.z += (tz - a.pos.z) * 0.004 * cohesion + windZ + (Math.random() - 0.5) * friction * 0.022;
      a.vel.multiplyScalar(0.93);
      const vLen = a.vel.length();
      if (vLen > speedBase * 4.2) a.vel.multiplyScalar((speedBase * 4.2) / vLen);
      a.pos.add(a.vel);
      avgDist += Math.hypot(a.pos.x - tx, a.pos.y - ty, a.pos.z - tz);

      dummyObj.position.copy(a.pos);
      dummyObj.rotation.set(tSec + a.phase, tSec * 1.3, 0);
      const sc = 0.8 + state.audioFlux * 0.55;
      dummyObj.scale.setScalar(sc);
      dummyObj.updateMatrix();
      threeState.twinMesh.setMatrixAt(i, dummyObj.matrix);

      if (a.role === 0) tmpColor.set('#F43F5E');
      else if (a.role === 1) tmpColor.set('#06B6D4');
      else tmpColor.set('#F59E0B');
      threeState.twinMesh.setColorAt(i, tmpColor);
    }
    threeState.twinMesh.instanceMatrix.needsUpdate = true;
    if (threeState.twinMesh.instanceColor) threeState.twinMesh.instanceColor.needsUpdate = true;

    // Connect nearby coupled agents
    if (threeState.twinLines) {
      const lPos = threeState.twinLines.geometry.attributes.position.array;
      let seg = 0;
      const maxSeg = 220;
      const linkDistSq = 2.6 * 2.6;
      for (let i = 0; i < activeN && seg < maxSeg; i += 2) {
        const a = threeState.twinAgents[i].pos;
        for (let j = i + 1; j < Math.min(activeN, i + 10) && seg < maxSeg; j++) {
          const b = threeState.twinAgents[j].pos;
          if (a.distanceToSquared(b) < linkDistSq) {
            const off = seg * 6;
            lPos[off] = a.x; lPos[off + 1] = a.y; lPos[off + 2] = a.z;
            lPos[off + 3] = b.x; lPos[off + 4] = b.y; lPos[off + 5] = b.z;
            seg++;
          }
        }
      }
      threeState.twinLines.geometry.setDrawRange(0, seg * 2);
      threeState.twinLines.geometry.attributes.position.needsUpdate = true;
    }

    const spread = avgDist / Math.max(1, activeN);
    state.twinMeasuredCohesion = Math.round(clamp(100 - spread * 14, 12, 98));
    state.twinMeasuredTension = Math.round(clamp(friction * 34 + state.residualPct * 0.45 + shockBoost * 35, 4, 99));
  }

  // 4) Smoothly Lerp Ontological Constellation Nodes toward Active Reclassification Basis
  if (threeState.ontoNodes.length > 0 && state.activeOrgans.ontology) {
    const coreA = threeState.ontoNodes[0];
    const coreB = threeState.ontoNodes[1];
    const lineArr = threeState.ontoLines ? threeState.ontoLines.geometry.attributes.position.array : null;

    threeState.ontoNodes.forEach((n, idx) => {
      n.pos.lerp(n.target, 0.085);
      const bob = Math.sin(tSec * 1.4 + idx * 0.7) * 0.09;
      n.mesh.position.set(n.pos.x, n.pos.y + bob, n.pos.z);
      if (n.sprite) {
        n.sprite.position.set(n.pos.x, n.pos.y + bob + 0.56, n.pos.z);
      }
      if (lineArr && idx >= 2) {
        const anchor = n.item.kind === 'onlyB' ? coreB.pos : coreA.pos;
        const off = idx * 6;
        lineArr[off] = anchor.x; lineArr[off + 1] = anchor.y; lineArr[off + 2] = anchor.z;
        lineArr[off + 3] = n.pos.x; lineArr[off + 4] = n.pos.y + bob; lineArr[off + 5] = n.pos.z;
      }
    });
    if (threeState.ontoLines) {
      threeState.ontoLines.geometry.attributes.position.needsUpdate = true;
    }
  }

  // 5) Camera Choreography driven smoothly by Scale-Rotor Dial σ ∈ [0..4]
  const targetRadius = 6.2 + state.sigma * 3.1;
  const targetYOffset = -0.3 + state.sigma * 0.45;
  const cx = Math.sin(state.camYaw) * Math.cos(state.camPitch) * targetRadius;
  const cy = Math.sin(state.camPitch) * targetRadius + targetYOffset;
  const cz = Math.cos(state.camYaw) * Math.cos(state.camPitch) * targetRadius;
  threeState.camera.position.lerp(new THREE.Vector3(cx, cy, cz), 0.12);
  threeState.camera.lookAt(0, 0.15, 0);

  threeState.renderer.render(threeState.scene, threeState.camera);
}

/* ============================================================================
 * 3. Web Audio API Live Acoustic FFT Coupling
 * ============================================================================ */
const audio = {
  ctx: null,
  analyser: null,
  bins: null,
  stream: null,
  canvas: null,
  c2d: null,
};

async function toggleMicAudio() {
  const btn = el('u-btn-mic');
  if (state.audioActive && audio.stream) {
    audio.stream.getTracks().forEach((t) => t.stop());
    audio.stream = null;
    state.audioActive = false;
    state.audioFlux = 0;
    if (btn) {
      btn.textContent = '마이크 음향 연결';
      btn.classList.remove('btn-live-on');
    }
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    audio.stream = stream;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!audio.ctx) audio.ctx = new AudioCtx();
    const src = audio.ctx.createMediaStreamSource(stream);
    audio.analyser = audio.ctx.createAnalyser();
    audio.analyser.fftSize = 128;
    src.connect(audio.analyser);
    audio.bins = new Uint8Array(audio.analyser.frequencyBinCount);
    state.audioActive = true;
    if (btn) {
      btn.textContent = '마이크 음향 수신 중';
      btn.classList.add('btn-live-on');
    }
    addWorldTreeRing('음향 감각 결합', '실시간 마이크 FFT 주파수가 통합장 Red Flux와 트윈 군집 속도에 결합되었습니다.', 'emerald');
  } catch (err) {
    setVerdict(`마이크 권한을 열 수 없습니다 (${err.message || '권한 거부'}). 시각·외부 지식 통합장은 정상 가동됩니다.`, 'deficit');
  }
}

function drawAudioSpectrum(tSec) {
  if (!audio.canvas) {
    audio.canvas = el('u-audio-canvas');
    if (audio.canvas) audio.c2d = audio.canvas.getContext('2d');
  }
  if (!audio.c2d) return;
  const ctx = audio.c2d;
  const W = audio.canvas.width;
  const H = audio.canvas.height;
  ctx.fillStyle = '#050811';
  ctx.fillRect(0, 0, W, H);

  if (state.audioActive && audio.analyser && audio.bins) {
    audio.analyser.getByteFrequencyData(audio.bins);
    let sum = 0;
    const n = audio.bins.length;
    const barW = W / n;
    for (let i = 0; i < n; i++) {
      const v = audio.bins[i] / 255;
      sum += v;
      const bh = v * (H - 4);
      ctx.fillStyle = v > 0.6 ? '#F43F5E' : '#06B6D4';
      ctx.fillRect(i * barW, H - bh, Math.max(1, barW - 1), bh);
    }
    state.audioFlux = clamp(sum / n, 0, 1);
  } else {
    // Draw quiet baseline wave reflecting optical/environmental flux
    state.audioFlux = 0;
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.35)';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    for (let x = 0; x < W; x += 4) {
      const amp = 2.5 + (state.residualPct / 100) * 10;
      const y = H / 2 + Math.sin(x * 0.04 + tSec * 3.2) * amp;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  const meta = el('u-audio-meta');
  if (meta) {
    meta.textContent = state.audioActive
      ? `실측 음향 Flux ${Math.round(state.audioFlux * 100)}%`
      : '음향 대기 (마이크 미연결)';
  }
}

/* ============================================================================
 * 4. Real Multi-Instance Optical Invariance + Live Open-World Synchronization
 * ============================================================================ */
function loadImageToUnifiedField(proxyUrl, label) {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      if (state.activeVideo) {
        try { state.activeVideo.pause(); } catch {}
      }
      state.activeImg = img;
      state.mediaKind = 'image';
      state.mediaLabel = label || '외부 실물 이미지';
      state.mediaNaturalW = img.naturalWidth || 1920;
      state.mediaNaturalH = img.naturalHeight || 1080;
      state.mediaDirty = true;
      uploadActiveMediaToGpuAnd3D();
      resolve(true);
    };
    img.onerror = () => resolve(false);
    img.src = proxyUrl;
  });
}

function loadVideoToUnifiedField(url, label) {
  const vid = el('u-video-src');
  if (!vid) return;
  vid.crossOrigin = 'anonymous';
  vid.src = url;
  vid.loop = true;
  vid.muted = true;
  vid.playsInline = true;
  vid.onloadeddata = () => {
    state.activeVideo = vid;
    state.mediaKind = 'video';
    state.mediaLabel = label || '실물 영상 스트림';
    state.mediaDirty = true;
    vid.play().catch(() => {});
    addWorldTreeRing('실물 영상 유입', `${label} 스트림이 4K GPU 프리즘·3D 기복·CUDA 타일 로터에 동시 결합되었습니다.`, 'cyan');
  };
  vid.load();
}

let webcamStream = null;
async function toggleWebcam() {
  const btn = el('u-btn-webcam');
  const vid = el('u-video-src');
  if (webcamStream) {
    webcamStream.getTracks().forEach((t) => t.stop());
    webcamStream = null;
    if (btn) {
      btn.textContent = '웹캠·마이크 개방';
      btn.classList.remove('btn-live-on');
      btn.classList.add('btn-primary');
    }
    if (state.photos.length) {
      loadImageToUnifiedField(state.photos[0].hiResProxyUrl || state.photos[0].proxyUrl, state.photos[0].caption);
    }
    return;
  }
  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 3840 }, height: { ideal: 2160 } },
      audio: false,
    });
    if (vid) {
      vid.srcObject = webcamStream;
      vid.play().catch(() => {});
      state.activeVideo = vid;
      state.mediaKind = 'webcam';
      state.mediaLabel = '실시간 열린 웹캠 감각';
      state.mediaDirty = true;
    }
    if (btn) {
      btn.textContent = '웹캠 개방 중 (종료)';
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-live-on');
    }
    addWorldTreeRing('열린 현실 웹캠 개방', '외부 실시간 카메라 스트림이 4K 프리즘·3D 기복·트윈 환경·CUDA 워프에 직결되었습니다.', 'emerald');
  } catch (err) {
    setVerdict(`웹캠을 열 수 없습니다 (${err.message || '권한 없음'}). 4K 프리셋 또는 로컬 파일 드롭으로 실물 입력이 가능합니다.`, 'deficit');
  }
}

function measurePhotoSignature(imgEl) {
  const c = document.createElement('canvas');
  c.width = 64;
  c.height = 48;
  const ctx = c.getContext('2d');
  try {
    ctx.drawImage(imgEl, 0, 0, 64, 48);
    const d = ctx.getImageData(0, 0, 64, 48).data;
    let luma = 0, sat = 0, edge = 0;
    const N = 64 * 48;
    for (let i = 0; i < N; i++) {
      const r = d[i * 4] / 255, g = d[i * 4 + 1] / 255, b = d[i * 4 + 2] / 255;
      const y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      luma += y;
      sat += Math.max(r, g, b) - Math.min(r, g, b);
      if (i > 0) {
        const py = (d[(i - 1) * 4] * 0.2126 + d[(i - 1) * 4 + 1] * 0.7152 + d[(i - 1) * 4 + 2] * 0.0722) / 255;
        edge += Math.abs(y - py);
      }
    }
    return { luma: luma / N, sat: sat / N, edge: edge / N };
  } catch {
    return null;
  }
}

async function syncUnifiedOntologicalField(rawA, rawB) {
  const conceptA = String(rawA || el('u-input-a')?.value || '나무').trim() || '나무';
  const conceptB = String(rawB || el('u-input-b')?.value || '숲').trim() || '숲';
  if (el('u-input-a')) el('u-input-a').value = conceptA;
  if (el('u-input-b')) el('u-input-b').value = conceptB;
  state.conceptA = conceptA;
  state.conceptB = conceptB;

  setVerdict(`"${conceptA} ⇄ ${conceptB}" 외부 실재 지식·2K/4K 다중 실물 사진·6축 인과·3D 연속장을 동기화하는 중...`, 'resonant');

  try {
    const res = await fetch('/api/ontology/resonate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conceptA, conceptB }),
    });
    const data = await res.json();
    if (!res.ok || data.status !== 'ok') {
      throw new Error(data.message || '동기화 응답 오류');
    }

    state.ontology = data;

    // 1) Update Chromatic Triad from real 6-axis protocol profile (Flux=P4, Order=P2+P3, Entropy=P5+P6)
    const axA = data.conceptA.protocolAxes || [];
    const axB = data.conceptB.protocolAxes || [];
    const avgAxis = (idx) => (((axA[idx]?.strength || 0.3) + (axB[idx]?.strength || 0.3)) * 0.5);
    const rawR = 0.15 + avgAxis(3) + avgAxis(0) * 0.35;
    const rawB = 0.15 + avgAxis(1) + avgAxis(2) * 0.75;
    const rawY = 0.15 + avgAxis(4) + avgAxis(5) * 0.85;
    const sumC = rawR + rawB + rawY;
    state.chromatic = { r: rawR / sumC, b: rawB / sumC, y: rawY / sumC };

    // 2) Combine real Wikimedia Commons photos from Concept A & B into unified multi-instance swarm
    const listA = (data.conceptA.photos || []).slice(0, 3).map((p) => ({ ...p, group: 'A', label: `${data.conceptA.title} · ${p.caption}` }));
    const listB = (data.conceptB.photos || []).slice(0, 3).map((p) => ({ ...p, group: 'B', label: `${data.conceptB.title} · ${p.caption}` }));
    state.photos = [...listA, ...listB];
    state.activePhotoIdx = 0;

    renderPhotoSwarm();

    // Load first high-res photo directly into the 4K GPU Prism AND 3D Relief Mesh!
    if (state.photos.length > 0 && state.mediaKind !== 'webcam') {
      const first = state.photos[0];
      await loadImageToUnifiedField(first.hiResProxyUrl || first.proxyUrl, first.label);
    }

    // 3) Sync Scale-Rotor center σ to midpoint of A & B
    const midScale = clamp(((data.conceptA.scaleCenter || 1.5) + (data.conceptB.scaleCenter || 3.0)) * 0.5, 0.2, 3.8);
    state.sigma = Number(midScale.toFixed(2));
    syncScaleDialUI();

    // 4) Rebuild 3D Ontological Constellation & propagate to Digital Twin + World Tree + Hardware
    rebuildOnto3DConstellation();
    renderOntologyPanel();
    updateChromaticAndTwinUI();
    updateHardwareMetrics();

    const cmp = data.comparison || {};
    const sharedLinks = cmp.sharedLinks || [];
    const onlyALinks = cmp.onlyALinks || [];
    const onlyBLinks = cmp.onlyBLinks || [];

    // Also feed backend S0..S4 quaternion rotor engine
    fetch('/api/init_field', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: `${conceptA} ${conceptB} ${sharedLinks.slice(0, 4).join(' ')}` }),
    }).catch(() => {});

    // Auto-Adapt organ priorities if enabled
    if (state.autoAdapt) {
      runAutoAdaptation('concept_sync');
    }

    const resPct = Math.round(Number(cmp.resonancePct || 0));
    const scaleJump = Number(cmp.scaleJump || 0);
    const jumpStr = `${scaleJump >= 0 ? '+' : ''}${scaleJump.toFixed(2)}`;
    if (el('u-stat-resonance')) el('u-stat-resonance').textContent = `${resPct}% (ΔS ${jumpStr})`;
    if (el('u-link-count')) {
      const totalLinks = sharedLinks.length + onlyALinks.length + onlyBLinks.length;
      el('u-link-count').textContent = String(totalLinks);
    }

    const domAxis = cmp.dominantJumpAxis ? cmp.dominantJumpAxis.name : '스케일 전이';
    setVerdict(
      `${data.conceptA.title}(S${Number(data.conceptA.scaleCenter).toFixed(1)}) ⇄ ${data.conceptB.title}(S${Number(data.conceptB.scaleCenter).toFixed(1)}) 통합 동기화 완료 — 공명 ${resPct}%, 분화 주도축 [${domAxis}], 공명 교량 ${sharedLinks.length}개. 하나의 4K 장에서 광학·3D·트윈·인과·메모리가 동시 연동 중입니다.`,
      'resonant'
    );
    addWorldTreeRing(
      `${data.conceptA.title} ⇄ ${data.conceptB.title}`,
      `공명 ${resPct}% · ΔS ${jumpStr} · 주도 분화축: ${domAxis} · 교량 ${sharedLinks.slice(0, 3).join(', ') || onlyBLinks.slice(0, 3).join(', ') || '탐색 중'}`,
      'emerald'
    );
  } catch (err) {
    setVerdict(`외부 실재 동기화 실패: ${err.message || '네트워크 오류'}`, 'deficit');
  }
}

function renderPhotoSwarm() {
  const wrap = el('u-photo-swarm');
  if (!wrap) return;
  clearChildren(wrap);

  const signatures = [];
  if (!state.photos.length) {
    wrap.appendChild(makeNode('span', 'prose-note', '표본 이미지를 불러오는 중입니다.'));
    return;
  }

  state.photos.forEach((p, idx) => {
    const btn = makeNode('button', `swarm-thumb${idx === state.activePhotoIdx ? ' active' : ''}`);
    btn.type = 'button';
    btn.title = `${p.label} (${p.width || '?'}×${p.height || '?'})`;

    const img = document.createElement('img');
    img.crossOrigin = 'anonymous';
    img.referrerPolicy = 'no-referrer';
    img.alt = p.label;
    img.src = p.proxyUrl;
    img.onload = () => {
      const sig = measurePhotoSignature(img);
      if (sig) {
        signatures.push(sig);
        if (signatures.length >= 2) {
          const avgSat = signatures.reduce((a, b) => a + b.sat, 0) / signatures.length;
          const varSat = Math.sqrt(signatures.reduce((a, b) => a + (b.sat - avgSat) ** 2, 0) / signatures.length);
          const avgEdge = signatures.reduce((a, b) => a + b.edge, 0) / signatures.length;
          const varEdge = Math.sqrt(signatures.reduce((a, b) => a + (b.edge - avgEdge) ** 2, 0) / signatures.length);
          state.opticalSurfaceVarPct = Math.round(clamp(varSat * 280, 4, 96));
          state.opticalInvariancePct = Math.round(clamp(100 - varEdge * 420, 22, 98));
          const invEl = el('u-opt-invariance');
          if (invEl) {
            invEl.textContent = `표본 ${signatures.length}장 실측 · 구조 불변 ${state.opticalInvariancePct}% / 표면 채도 변이 ${state.opticalSurfaceVarPct}%`;
          }
        }
      }
    };
    const cap = makeNode('span', 'swarm-thumb-cap', `${p.group === 'A' ? 'A' : 'B'} · ${p.caption}`);
    btn.appendChild(img);
    btn.appendChild(cap);

    btn.addEventListener('click', () => {
      state.activePhotoIdx = idx;
      wrap.querySelectorAll('.swarm-thumb').forEach((b, i) => b.classList.toggle('active', i === idx));
      loadImageToUnifiedField(p.hiResProxyUrl || p.proxyUrl, p.label);
      addWorldTreeRing('실물 표본 전환', `${p.label} 고해상도 표본을 4K 프리즘과 3D 기복 메쉬에 동시 투영했습니다.`, 'cyan');
    });
    wrap.appendChild(btn);
  });
}

/* ============================================================================
 * 5. Live Earth Atmospheric Telemetry & Counterfactual Constraint Falsifier
 * ============================================================================ */
async function probeLiveEarthAtmosphere() {
  try {
    const res = await fetch('/api/epistemic/reality-probe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    const data = await res.json();
    if (!res.ok || data.status !== 'ok') throw new Error(data.message || '실측 오류');
    state.earth = data;

    // Physically inject real Earth wind & friction into Digital Twin + 3D Sun/Fog!
    const actual = data.actual || {};
    state.twinFrictionParam = Number(clamp((data.frictionPct || 25) / 55, 0.15, 1.8).toFixed(2));
    if (el('u-sl-friction')) el('u-sl-friction').value = String(state.twinFrictionParam);
    if (el('u-val-friction')) el('u-val-friction').textContent = `${state.twinFrictionParam.toFixed(2)}×`;

    if (threeState.scene && threeState.scene.fog) {
      threeState.scene.fog.density = 0.016 + ((actual.cloudCoverPct || 10) / 100) * 0.022;
    }

    if (el('u-earth-temp')) {
      el('u-earth-temp').textContent = `${data.city} · ${actual.temperatureC}°C · ${actual.surfacePressureHpa}hPa`;
    }
    if (el('u-earth-wind')) {
      el('u-earth-wind').textContent = `풍속 ${actual.windSpeedKmh}km/h (${actual.windDirectionDeg}°) · 마찰 ${data.frictionPct}%`;
    }
    if (el('u-earth-inline')) {
      el('u-earth-inline').textContent = `${actual.temperatureC}°C · 풍속 ${actual.windSpeedKmh}km/h`;
    }

    addWorldTreeRing(
      `지구 실측 결합 (${data.city})`,
      `온도 ${actual.temperatureC}°C · 기압 ${actual.surfacePressureHpa}hPa · 풍속 ${actual.windSpeedKmh}km/h → 3D 트윈 풍향·대기 밀도·마찰 계수에 직접 반영됨`,
      'amber'
    );
    if (state.autoAdapt) runAutoAdaptation('earth_probe');
  } catch (err) {
    setVerdict(`지구 대기 실측 호출 실패: ${err.message}`, 'deficit');
  }
}

async function runConstraintFalsification(rawQuery) {
  const query = String(rawQuery || el('u-constraint-input')?.value || '').trim();
  if (!query) return;
  try {
    const res = await fetch('/api/epistemic/constraint-check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    if (!res.ok || data.status !== 'ok') throw new Error(data.message || '반증 오류');
    const verdictTxt = data.verdict || data.summary || `${query} 제약 검증 완료`;
    state.lastConstraintVerdict = verdictTxt;
    const isRejected = /배제|모순|불가능|척력|붕괴/i.test(verdictTxt);

    // Physical repulsion shockwave inside 3D Digital Twin when constraint is falsified!
    if (isRejected) {
      state.twinShockDecay = 1.0;
      state.twinShockType = 'repulsion';
    }
    const summaryEl = el('u-onto-summary');
    if (summaryEl) summaryEl.textContent = `[제약 반증: ${query}] ${verdictTxt}`;
    setVerdict(`[반사실 제약 반증] ${query} → ${verdictTxt}`, isRejected ? 'deficit' : 'resonant');
    addWorldTreeRing(`제약 반증: ${query}`, verdictTxt.slice(0, 120), isRejected ? 'rose' : 'emerald');
  } catch (err) {
    setVerdict(`제약 반증 실패: ${err.message}`, 'deficit');
  }
}

/* ============================================================================
 * 6. Dynamic Reclassification & Auto-Recombination Engine
 * ============================================================================ */
function setReclassificationBasis(basis) {
  if (!BASIS_LABELS[basis]) return;
  state.basis = basis;

  document.querySelectorAll('#u-basis-tabs button').forEach((b) => {
    b.classList.toggle('active', b.dataset.basis === basis);
  });
  const hud = el('u-3d-basis-hud');
  if (hud) hud.textContent = `분류축: ${BASIS_LABELS[basis]}`;

  // Physically reorganize 3D Ontological Constellation + Reorder Organ Matrix by relevance!
  recomputeOntoNodeTargets();
  reorderOrgansForBasis(basis);

  addWorldTreeRing(
    `재분류 기준 전환: ${basis}`,
    `동일한 4K 통합장을 [${BASIS_LABELS[basis]}] 기준으로 즉시 재분류·재배치했습니다.`,
    'cyan'
  );
}

function reorderOrgansForBasis(basis) {
  const grid = el('u-organ-grid');
  if (!grid) return;
  const orderMap = {
    scale: ['optics', 'falsify3d', 'twin', 'ontology', 'worldtree', 'hardware'],
    chromatic: ['worldtree', 'twin', 'optics', 'ontology', 'falsify3d', 'hardware'],
    causal6: ['ontology', 'worldtree', 'twin', 'optics', 'falsify3d', 'hardware'],
    hardware: ['hardware', 'optics', 'falsify3d', 'twin', 'ontology', 'worldtree'],
  };
  const seq = orderMap[basis] || orderMap.scale;
  seq.forEach((key, idx) => {
    const card = grid.querySelector(`[data-organ-card="${key}"]`);
    if (card) {
      card.style.order = String(idx);
      card.classList.toggle('priority', idx < 2);
    }
  });
}

function runAutoAdaptation(trigger) {
  const verdictAction = el('u-verdict-action');
  if (state.residualPct >= 14) {
    // High Optical Residual -> prioritize Optics + 3D Falsification + CUDA Warp-32
    if (state.basis !== 'hardware') {
      reorderOrgansForBasis('hardware');
    }
    if (verdictAction) verdictAction.textContent = `자율 재조합: 광학 잔차 ${state.residualPct}% → 광학·CUDA 우선 승격`;
  } else if (trigger === 'earth_probe' || trigger === 'shock') {
    reorderOrgansForBasis('chromatic');
    if (verdictAction) verdictAction.textContent = '자율 재조합: 환경 외란 감지 → 트윈·세계수·색채축 우선';
  } else if (state.ontology && Math.abs((state.ontology.comparison && state.ontology.comparison.scaleJump) || 0) >= 0.7) {
    reorderOrgansForBasis('causal6');
    if (verdictAction) verdictAction.textContent = `자율 재조합: 스케일 도약 ΔS=${Number(state.ontology.comparison.scaleJump).toFixed(2)} → 6축 존재·트윈 우선`;
  } else {
    reorderOrgansForBasis(state.basis);
    if (verdictAction) verdictAction.textContent = '자율 재조합: 전계층 균형 결합';
  }
}

function applyEnvironmentPreset(preset) {
  const presets = {
    all: { optics: true, falsify3d: true, twin: true, ontology: true, worldtree: true, hardware: true },
    optical_3d: { optics: true, falsify3d: true, twin: false, ontology: false, worldtree: false, hardware: true },
    eco_onto: { optics: true, falsify3d: false, twin: true, ontology: true, worldtree: true, hardware: false },
    compute: { optics: true, falsify3d: true, twin: true, ontology: false, worldtree: false, hardware: true },
  };
  const cfg = presets[preset];
  if (!cfg) return;
  Object.assign(state.activeOrgans, cfg);
  syncOrganVisibilityUI();
  if (preset === 'compute') setReclassificationBasis('hardware');
  else if (preset === 'eco_onto') setReclassificationBasis('causal6');
  else if (preset === 'optical_3d') setReclassificationBasis('scale');
  addWorldTreeRing(`환경 재조합 (${preset})`, '필요한 기관 조합만 활성화하여 통합장 연산·시각 구조를 재구성했습니다.', 'cyan');
}

function syncOrganVisibilityUI() {
  document.querySelectorAll('#u-organ-toggles button[data-organ]').forEach((btn) => {
    const key = btn.dataset.organ;
    btn.classList.toggle('btn-active', !!state.activeOrgans[key]);
  });
  document.querySelectorAll('[data-organ-card]').forEach((card) => {
    const key = card.dataset.organCard;
    card.classList.toggle('hidden-organ', !state.activeOrgans[key]);
  });
}

/* ============================================================================
 * 7. Panel Renderers (100% Safe DOM — Zero innerHTML)
 * ============================================================================ */
function setVerdict(text, tone = 'resonant') {
  const box = el('u-verdict');
  const txt = el('u-verdict-text');
  if (txt) txt.textContent = text;
  if (box) {
    box.classList.remove('resonant', 'deficit');
    box.classList.add(tone === 'deficit' ? 'deficit' : 'resonant');
  }
}

function updateOpticalPanels() {
  const list = el('u-optics-list');
  if (!list) return;
  clearChildren(list);

  const weights = getEffectiveWeights();
  OPTICAL_AXES.forEach((ax, i) => {
    const isOn = weights[i] > 0.5;
    const isSolo = state.opticsSolo === i;
    const pct = Math.round((state.opticsEnergy[i] || 0) * 100);

    const row = makeNode('div', `spec-row${isOn ? '' : ' off'}`);
    const top = makeNode('div', 'spec-top');
    top.appendChild(makeNode('span', 'spec-name', `${ax.code} ${ax.name}`));
    top.appendChild(makeNode('span', 'spec-val', `${pct}% · ${isOn ? '결합' : '차단'}`));
    row.appendChild(top);

    const track = makeNode('div', 'bar-track');
    const fill = makeNode('div', 'bar-fill');
    fill.style.width = `${clamp(pct * 2.2, 4, 100)}%`;
    fill.style.background = isOn ? ax.color : '#334155';
    track.appendChild(fill);
    row.appendChild(track);

    const btns = makeNode('div', 'spec-btns');
    const toggleBtn = makeNode('button', `btn btn-sm${isOn && !isSolo ? ' btn-active' : ''}`, isOn ? '축 차단' : '축 복원');
    toggleBtn.type = 'button';
    toggleBtn.addEventListener('click', () => {
      state.opticsSolo = -1;
      state.opticsOn[i] = !state.opticsOn[i];
      onOpticalAxesChanged(ax.name, state.opticsOn[i]);
    });
    const soloBtn = makeNode('button', `btn btn-sm${isSolo ? ' btn-primary' : ''}`, isSolo ? '단독 해제' : '단독 관측');
    soloBtn.type = 'button';
    soloBtn.addEventListener('click', () => {
      state.opticsSolo = state.opticsSolo === i ? -1 : i;
      onOpticalAxesChanged(`${ax.name} 단독`, state.opticsSolo === i);
    });
    btns.appendChild(toggleBtn);
    btns.appendChild(soloBtn);
    row.appendChild(btns);
    list.appendChild(row);
  });

  const statRes = el('u-stat-residual');
  if (statRes) statRes.textContent = `${state.residualPct.toFixed(2)}%`;

  const note = el('u-optics-note');
  if (note) {
    if (state.residualPct < 0.05) {
      note.textContent = 'ΣC1..C6 = 원본 완전 수렴 (미인지 잔차 0.00%). 어느 한 축을 차단하면 누락된 질서가 3D·트윈·CUDA에 동시 전파됩니다.';
    } else {
      note.textContent = `미인지 질서 잔차 ${state.residualPct.toFixed(2)}% 감지 — 누락된 광학 성분이 3D 조명 결손, 트윈 긴장도 상승, S0 CUDA 활성 워프 승격으로 즉시 전파되었습니다.`;
    }
  }
}

function onOpticalAxesChanged(axisLabel, turnedOn) {
  const w = getEffectiveWeights();
  let missing = 0;
  for (let i = 0; i < 6; i++) {
    if (w[i] < 0.5) missing += state.opticsEnergy[i];
  }
  state.residualPct = Number((missing * 100).toFixed(2));
  state.activeTileRatio = clamp(0.14 + missing * 0.78, 0.06, 1.0);
  updateOpticalPanels();
  update3DFalsificationKPIs();
  updateHardwareMetrics();
  if (state.autoAdapt) runAutoAdaptation('optical_cut');

  if (state.residualPct > 0.5) {
    setVerdict(
      `[${axisLabel}] 조작 → 미인지 광학 잔차 ${state.residualPct.toFixed(2)}% 발생! 3D 조명, 트윈 긴장도(${state.twinMeasuredTension}%), S0 CUDA 활성 워프(${state.hwActiveWarps})가 연쇄 반응 중입니다.`,
      'deficit'
    );
    addWorldTreeRing(`광학 결손 검증 (${axisLabel})`, `잔차 ${state.residualPct.toFixed(2)}% · CUDA S0 워프 ${state.hwActiveWarps}/${state.hwTotalWarps} 즉시 승격`, 'amber');
  } else {
    setVerdict('6축 광학 스펙트럼 완전 재결합 (ΣC1..C6 = 원본 · 잔차 0.00%).', 'resonant');
  }
}

function renderOntologyPanel() {
  const bars = el('u-proto-bars');
  const linksWrap = el('u-onto-links');
  const summary = el('u-onto-summary');
  const jumpTag = el('u-onto-jump-tag');
  if (!state.ontology || !bars || !linksWrap) return;

  const cmp = state.ontology.comparison || {};
  const { conceptA, conceptB } = state.ontology;
  const sharedLinks = cmp.sharedLinks || [];
  const onlyBLinks = cmp.onlyBLinks || [];
  const scaleJump = Number(cmp.scaleJump || 0);
  if (jumpTag) {
    jumpTag.textContent = `S${Number(conceptA.scaleCenter).toFixed(1)} → S${Number(conceptB.scaleCenter).toFixed(1)} (ΔS ${scaleJump >= 0 ? '+' : ''}${Number(scaleJump).toFixed(2)})`;
  }

  clearChildren(bars);
  const axesA = conceptA.protocolAxes || [];
  const axesB = conceptB.protocolAxes || [];
  axesA.forEach((ax, i) => {
    const bAx = axesB[i] || { strength: 0.1 };
    const pA = Math.round((ax.strength || 0) * 100);
    const pB = Math.round((bAx.strength || 0) * 100);
    const isLightDeficit = i === 4 && !state.opticsOn[2];

    const row = makeNode('div', 'spec-row');
    const top = makeNode('div', 'spec-top');
    top.appendChild(makeNode('span', 'spec-name', `${ax.id} ${ax.name}${isLightDeficit ? ' (외부 광원 결손)' : ''}`));
    top.appendChild(makeNode('span', 'spec-val', `A ${pA}% / B ${pB}%`));
    row.appendChild(top);

    const tA = makeNode('div', 'bar-track');
    const fA = makeNode('div', 'bar-fill');
    fA.style.width = `${pA}%`;
    tA.appendChild(fA);
    row.appendChild(tA);

    const tB = makeNode('div', 'bar-track');
    const fB = makeNode('div', `bar-fill ${isLightDeficit ? 'rose' : 'emerald'}`);
    fB.style.width = `${pB}%`;
    tB.appendChild(fB);
    row.appendChild(tB);

    bars.appendChild(row);
  });

  clearChildren(linksWrap);
  sharedLinks.slice(0, 8).forEach((l) => {
    const b = makeNode('button', 'link-btn shared', `교량 · ${l}`);
    b.type = 'button';
    b.addEventListener('click', () => syncUnifiedOntologicalField(state.conceptA, l));
    linksWrap.appendChild(b);
  });
  onlyBLinks.slice(0, 8).forEach((l) => {
    const b = makeNode('button', 'link-btn only-b', `창발 · ${l}`);
    b.type = 'button';
    b.addEventListener('click', () => syncUnifiedOntologicalField(state.conceptB, l));
    linksWrap.appendChild(b);
  });

  if (summary) {
    const extA = (conceptA.extract || '').slice(0, 110);
    const extB = (conceptB.extract || '').slice(0, 110);
    summary.textContent = `${conceptA.title}: ${extA}... | ${conceptB.title}: ${extB}...`;
  }
}

function updateChromaticAndTwinUI() {
  const rPct = Math.round(state.chromatic.r * 100);
  const bPct = Math.round(state.chromatic.b * 100);
  const yPct = Math.max(0, 100 - rPct - bPct);
  if (el('u-bar-red')) el('u-bar-red').style.width = `${rPct}%`;
  if (el('u-bar-blue')) el('u-bar-blue').style.width = `${bPct}%`;
  if (el('u-bar-yellow')) el('u-bar-yellow').style.width = `${yPct}%`;
  if (el('u-chroma-summary')) el('u-chroma-summary').textContent = `R ${rPct} · B ${bPct} · Y ${yPct}`;

  const modeTag = el('u-twin-mode-tag');
  if (modeTag) {
    modeTag.textContent =
      rPct >= bPct && rPct >= yPct ? 'Red 흐름 · 고속 순환' :
      bPct >= yPct ? 'Blue 질서 · 구조 응집' : 'Yellow 발산 · 경계 탐색';
  }
  const tc = el('u-twin-count');
  if (tc) tc.textContent = String(state.twinCount);
}

function renderWorldTreePanel() {
  const ledger = el('u-ring-ledger');
  if (!ledger) return;
  clearChildren(ledger);
  state.rings.slice(0, 10).forEach((r) => {
    const item = makeNode('div', 'ring-entry');
    const head = makeNode('div', 'ring-entry-head');
    head.appendChild(makeNode('span', '', `t${r.idx} · ${r.title}`));
    head.appendChild(makeNode('span', '', r.time));
    item.appendChild(head);
    item.appendChild(makeNode('div', '', r.detail));
    ledger.appendChild(item);
  });
}

function updateHardwareMetrics() {
  const totalPx = gpu.width * gpu.height; // 8,294,400 at 4K UHD!
  const tileSize = 32 * 32;
  const totalWarps = Math.ceil(totalPx / (tileSize * 2.5));
  const activeRatio = clamp(state.activeTileRatio, 0.05, 1.0);
  const activeWarps = Math.max(32, Math.round(totalWarps * activeRatio));
  const savingsPct = clamp((1 - activeRatio) * 100, 0, 95);

  state.hwTotalWarps = totalWarps;
  state.hwActiveWarps = activeWarps;
  state.hwSavingsPct = savingsPct;

  if (el('u-hw-savings')) el('u-hw-savings').textContent = `-${savingsPct.toFixed(1)}% (${(totalPx / 1e6).toFixed(2)}M px)`;
  if (el('u-stat-warp')) el('u-stat-warp').textContent = `${activeWarps}/${totalWarps}`;

  const tiersWrap = el('u-hw-tiers');
  if (tiersWrap) {
    clearChildren(tiersWrap);
    const tiers = [
      { name: 'S0 Reg · Warp-32 (고잔차 4K 타일)', pct: Math.round(activeRatio * 100), cls: 'rose' },
      { name: 'S1 L1/Shared (3D 기복·경계 정점)', pct: Math.round(clamp(22 + state.reliefDepth * 14, 10, 90)), cls: 'amber' },
      { name: 'S2 VRAM (트윈 개체·실물 텍스처)', pct: Math.round(clamp((state.twinCount / 160) * 85, 15, 92)), cls: '' },
      { name: 'S3 RAM (6축 인과망·위키 연결)', pct: Math.round(clamp((threeState.ontoNodes.length / 36) * 85, 18, 90)), cls: 'emerald' },
      { name: 'S4 SSD (세계수 불변 나이테 원장)', pct: Math.round(clamp(100 - activeRatio * 55, 20, 95)), cls: 'emerald' },
    ];
    tiers.forEach((t) => {
      const row = makeNode('div', 'spec-row');
      const top = makeNode('div', 'spec-top');
      top.appendChild(makeNode('span', 'spec-name', t.name));
      top.appendChild(makeNode('span', 'spec-val', `${t.pct}% 할당`));
      row.appendChild(top);
      const track = makeNode('div', 'bar-track');
      const fill = makeNode('div', `bar-fill ${t.cls}`);
      fill.style.width = `${t.pct}%`;
      track.appendChild(fill);
      row.appendChild(track);
      tiersWrap.appendChild(row);
    });
  }

  const code = `// Live 4K UHD (${gpu.width}x${gpu.height}) Scale-Rotor SoA Kernel
// Basis: ${state.basis} | Residual: ${state.residualPct.toFixed(2)}% | Active Warps: ${activeWarps}/${totalWarps}
__global__ void scale_rotor_4k_soa(
    const float* __restrict__ luma,   // SoA coalesced 32-lane read
    const int*   __restrict__ activeTiles, // Compacted S0 indices
    float*       __restrict__ fieldOut,
    int numActiveWarps) {
  int wId = blockIdx.x;
  if (wId >= numActiveWarps) return;  // 0% intra-warp branch divergence
  int tile = activeTiles[wId];
  int lane = threadIdx.x & 31;
  float delta = luma[tile * 32 + lane] * ${(1 - state.residualPct / 100).toFixed(3)}f;
  fieldOut[tile * 32 + lane] = __shfl_sync(0xffffffff, delta, (lane + 1) & 31);
}`;
  state.lastCudaCode = code;
  const pre = el('u-cuda-code');
  if (pre) pre.textContent = code;
}

function syncScaleDialUI() {
  const sl = el('u-scale-dial');
  if (sl) sl.value = String(state.sigma);
  const nearest = Math.round(clamp(state.sigma, 0, 4));
  const hud = el('u-3d-scale-hud');
  if (hud) hud.textContent = `초점 σ = ${state.sigma.toFixed(2)} (${SCALE_STOP_NAMES[nearest]})`;
  document.querySelectorAll('#u-scale-stops button').forEach((b) => {
    b.classList.toggle('active', Number(b.dataset.sigma) === nearest);
  });
}

/* ============================================================================
 * 8. Event Wiring & Media Preset Loader
 * ============================================================================ */
let serverPresets = [];

async function loadMediaPresetById(presetId) {
  if (!serverPresets.length) {
    try {
      const r = await fetch('/api/ingest/presets');
      const d = await r.json();
      serverPresets = d.presets || [];
    } catch {}
  }
  const p = serverPresets.find((x) => x.id === presetId);
  if (!p) return;
  const proxyUrl = `/api/ingest/media?url=${encodeURIComponent(p.url)}`;
  if (p.kind === 'video') {
    loadVideoToUnifiedField(proxyUrl, p.label);
  } else {
    await loadImageToUnifiedField(proxyUrl, p.label);
    addWorldTreeRing('4K 실물 원화 유입', `${p.label} — 4K GPU 6축 분해·3D 기복·CUDA 타일에 즉시 결합`, 'cyan');
  }
}

function handleLocalFile(file) {
  if (!file) return;
  const objUrl = URL.createObjectURL(file);
  if (file.type.startsWith('video/')) {
    loadVideoToUnifiedField(objUrl, `로컬 영상 · ${file.name}`);
  } else if (file.type.startsWith('image/')) {
    loadImageToUnifiedField(objUrl, `로컬 고해상도 이미지 · ${file.name}`);
  }
}

function wireAllControls() {
  // Top Webcam CTA
  el('u-btn-webcam')?.addEventListener('click', toggleWebcam);
  el('u-btn-mic')?.addEventListener('click', toggleMicAudio);

  // Unified Concept Sync
  el('u-btn-sync')?.addEventListener('click', () => syncUnifiedOntologicalField());
  el('u-input-a')?.addEventListener('keydown', (e) => { if (e.key === 'Enter') syncUnifiedOntologicalField(); });
  el('u-input-b')?.addEventListener('keydown', (e) => { if (e.key === 'Enter') syncUnifiedOntologicalField(); });

  // Quick Transition Pairs
  document.querySelectorAll('[data-pair]').forEach((b) => {
    b.addEventListener('click', () => {
      const [a, c] = String(b.dataset.pair || '').split('|');
      syncUnifiedOntologicalField(a, c);
    });
  });

  // 4K Media Presets
  document.querySelectorAll('[data-media-preset]').forEach((b) => {
    b.addEventListener('click', () => loadMediaPresetById(b.dataset.mediaPreset));
  });

  // Earth Live Telemetry
  el('u-btn-earth')?.addEventListener('click', probeLiveEarthAtmosphere);

  // Local 4K Upload + Drag & Drop anywhere on workspace
  el('u-btn-upload')?.addEventListener('click', () => el('u-file-input')?.click());
  el('u-file-input')?.addEventListener('change', (e) => {
    const f = e.target.files && e.target.files[0];
    if (f) handleLocalFile(f);
  });
  const dropZone = el('u-drop-zone');
  if (dropZone) {
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drop-active'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drop-active'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drop-active');
      const f = e.dataTransfer?.files?.[0];
      if (f) handleLocalFile(f);
    });
  }

  // Reclassification Basis Tabs
  document.querySelectorAll('#u-basis-tabs button').forEach((b) => {
    b.addEventListener('click', () => setReclassificationBasis(b.dataset.basis));
  });

  // Resolution Tier Switch (2K QHD / 4K UHD)
  document.querySelectorAll('#u-res-tabs button').forEach((b) => {
    b.addEventListener('click', () => {
      document.querySelectorAll('#u-res-tabs button').forEach((x) => x.classList.toggle('active', x === b));
      applyResolutionTier(b.dataset.res);
    });
  });

  // Auto-Adapt Toggle
  el('u-btn-auto-adapt')?.addEventListener('click', () => {
    state.autoAdapt = !state.autoAdapt;
    const btn = el('u-btn-auto-adapt');
    if (btn) {
      btn.textContent = `자율 재조합: ${state.autoAdapt ? '켜짐' : '꺼짐'}`;
      btn.classList.toggle('btn-active', state.autoAdapt);
    }
    if (state.autoAdapt) runAutoAdaptation('manual_on');
  });

  // 4K GPU Prism Split & View Mode & 1:1 Loupe
  el('u-split-slider')?.addEventListener('input', (e) => { state.splitPos = Number(e.target.value); });
  document.querySelectorAll('#u-gpu-view-tabs button').forEach((b) => {
    b.addEventListener('click', () => {
      state.gpuView = b.dataset.gview;
      document.querySelectorAll('#u-gpu-view-tabs button').forEach((x) => x.classList.toggle('active', x === b));
    });
  });
  el('u-btn-loupe')?.addEventListener('click', () => {
    state.loupeEnabled = !state.loupeEnabled;
    el('u-btn-loupe')?.classList.toggle('btn-active', state.loupeEnabled);
    el('u-loupe-box')?.classList.toggle('visible', state.loupeEnabled && gpu.mouseInside);
  });
  const gpuBox = el('u-gpu-box');
  if (gpuBox) {
    gpuBox.addEventListener('pointerenter', () => {
      gpu.mouseInside = true;
      if (state.loupeEnabled) el('u-loupe-box')?.classList.add('visible');
    });
    gpuBox.addEventListener('pointerleave', () => {
      gpu.mouseInside = false;
      el('u-loupe-box')?.classList.remove('visible');
    });
    gpuBox.addEventListener('pointermove', (e) => {
      const rect = gpuBox.getBoundingClientRect();
      gpu.mouseU = clamp((e.clientX - rect.left) / Math.max(1, rect.width), 0, 1);
      gpu.mouseV = clamp((e.clientY - rect.top) / Math.max(1, rect.height), 0, 1);
    });
  }

  // Scale-Rotor Continuous Dial & Quick Stops
  el('u-scale-dial')?.addEventListener('input', (e) => {
    state.sigma = Number(e.target.value);
    syncScaleDialUI();
  });
  document.querySelectorAll('#u-scale-stops button').forEach((b) => {
    b.addEventListener('click', () => {
      state.sigma = Number(b.dataset.sigma);
      syncScaleDialUI();
    });
  });

  // Organ Toggles & Environment Recombination Presets
  document.querySelectorAll('#u-organ-toggles button[data-organ]').forEach((b) => {
    b.addEventListener('click', () => {
      const key = b.dataset.organ;
      state.activeOrgans[key] = !state.activeOrgans[key];
      syncOrganVisibilityUI();
    });
  });
  document.querySelectorAll('#u-env-presets button[data-env]').forEach((b) => {
    b.addEventListener('click', () => applyEnvironmentPreset(b.dataset.env));
  });

  // Organ 1: All Optics ON
  el('u-btn-optics-all')?.addEventListener('click', () => {
    state.opticsOn = [true, true, true, true, true, true];
    state.opticsSolo = -1;
    onOpticalAxesChanged('6축 전체 복원', true);
  });

  // Organ 2: 3D Falsification Controls
  el('u-sl-sun-az')?.addEventListener('input', (e) => {
    state.sunAzimuth = Number(e.target.value);
    if (el('u-val-sun-az')) el('u-val-sun-az').textContent = `${state.sunAzimuth}°`;
    update3DFalsificationKPIs();
  });
  el('u-sl-sun-el')?.addEventListener('input', (e) => {
    state.sunElevation = Number(e.target.value);
    if (el('u-val-sun-el')) el('u-val-sun-el').textContent = `${state.sunElevation}°`;
    update3DFalsificationKPIs();
  });
  el('u-sl-relief')?.addEventListener('input', (e) => {
    state.reliefDepth = Number(e.target.value);
    if (el('u-val-relief')) el('u-val-relief').textContent = `${state.reliefDepth.toFixed(2)}×`;
    update3DReliefGeometry();
  });
  el('u-sl-dt')?.addEventListener('input', (e) => {
    state.futureDt = Number(e.target.value);
    if (el('u-val-dt')) el('u-val-dt').textContent = `+${state.futureDt.toFixed(2)} s`;
    update3DReliefGeometry();
  });
  el('u-btn-3d-reset')?.addEventListener('click', () => {
    state.sunAzimuth = 38;
    state.sunElevation = 48;
    state.reliefDepth = 1.1;
    state.futureDt = 0;
    state.camYaw = 0.42;
    state.camPitch = 0.36;
    if (el('u-sl-sun-az')) el('u-sl-sun-az').value = '38';
    if (el('u-sl-sun-el')) el('u-sl-sun-el').value = '48';
    if (el('u-sl-relief')) el('u-sl-relief').value = '1.1';
    if (el('u-sl-dt')) el('u-sl-dt').value = '0';
    if (el('u-val-sun-az')) el('u-val-sun-az').textContent = '38°';
    if (el('u-val-sun-el')) el('u-val-sun-el').textContent = '48°';
    if (el('u-val-relief')) el('u-val-relief').textContent = '1.10×';
    if (el('u-val-dt')) el('u-val-dt').textContent = '+0.00 s';
    update3DReliefGeometry();
  });

  // Organ 3: Digital Twin Sliders & Environmental Shocks
  el('u-sl-cohesion')?.addEventListener('input', (e) => {
    state.twinCohesionParam = Number(e.target.value);
    if (el('u-val-cohesion')) el('u-val-cohesion').textContent = `${state.twinCohesionParam.toFixed(2)}×`;
  });
  el('u-sl-friction')?.addEventListener('input', (e) => {
    state.twinFrictionParam = Number(e.target.value);
    if (el('u-val-friction')) el('u-val-friction').textContent = `${state.twinFrictionParam.toFixed(2)}×`;
  });
  document.querySelectorAll('[data-shock]').forEach((b) => {
    b.addEventListener('click', () => {
      const kind = b.dataset.shock;
      if (kind === 'storm') {
        state.twinShockDecay = 1.0;
        state.twinFrictionParam = 1.65;
        state.futureDt = 1.25;
        if (el('u-sl-friction')) el('u-sl-friction').value = '1.65';
        if (el('u-val-friction')) el('u-val-friction').textContent = '1.65×';
        if (el('u-sl-dt')) el('u-sl-dt').value = '1.25';
        if (el('u-val-dt')) el('u-val-dt').textContent = '+1.25 s';
        update3DReliefGeometry();
        addWorldTreeRing('폭풍·외부 마찰 주입', '3D 관성 파동·트윈 산란·CUDA S0 활성 타일이 동시 상승했습니다.', 'rose');
      } else if (kind === 'drought') {
        state.twinCohesionParam = 0.35;
        state.opticsOn[2] = false; // Cut directional moisture/light balance
        if (el('u-sl-cohesion')) el('u-sl-cohesion').value = '0.35';
        if (el('u-val-cohesion')) el('u-val-cohesion').textContent = '0.35×';
        onOpticalAxesChanged('환경 가뭄·광원 결손', false);
      } else if (kind === 'bloom') {
        state.twinCount = Math.min(160, state.twinCount * 2);
        updateChromaticAndTwinUI();
        updateHardwareMetrics();
        addWorldTreeRing('개체 밀도 ×2 증식', `디지털 트윈 군집 ${state.twinCount}개체로 확장 → S2 VRAM 할당량 자동 갱신`, 'emerald');
      } else if (kind === 'harmonize') {
        state.twinCohesionParam = 1.35;
        state.twinFrictionParam = 0.25;
        state.twinShockDecay = 0;
        state.opticsOn = [true, true, true, true, true, true];
        state.opticsSolo = -1;
        if (el('u-sl-cohesion')) el('u-sl-cohesion').value = '1.35';
        if (el('u-val-cohesion')) el('u-val-cohesion').textContent = '1.35×';
        if (el('u-sl-friction')) el('u-sl-friction').value = '0.25';
        if (el('u-val-friction')) el('u-val-friction').textContent = '0.25×';
        onOpticalAxesChanged('원점 공명 정렬', true);
      }
      if (state.autoAdapt) runAutoAdaptation('shock');
    });
  });

  // Organ 4: Counterfactual Constraint Falsification
  el('u-btn-constraint')?.addEventListener('click', () => runConstraintFalsification());
  el('u-constraint-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') runConstraintFalsification();
  });

  // Organ 6: Copy Live CUDA Kernel
  el('u-btn-copy-cuda')?.addEventListener('click', async () => {
    const btn = el('u-btn-copy-cuda');
    try {
      await navigator.clipboard.writeText(state.lastCudaCode || '');
      if (btn) {
        btn.textContent = '복사 완료';
        setTimeout(() => { btn.textContent = '.cu 복사'; }, 1400);
      }
    } catch {
      if (btn) btn.textContent = '복사 불가';
    }
  });
}

/* ============================================================================
 * 9. Main Unified 60FPS Animation Loop
 * ============================================================================ */
let lastUiTick = 0;
function animate(nowMs) {
  requestAnimationFrame(animate);
  const tSec = nowMs * 0.001;

  drawAudioSpectrum(tSec);
  renderGpuFrame(tSec);
  stepAndRender3D(tSec);

  if (nowMs - lastUiTick > 250) {
    lastUiTick = nowMs;
    const kc = el('u-kpi-cohesion');
    if (kc) kc.textContent = `${state.twinMeasuredCohesion}%`;
    const kt = el('u-kpi-tension');
    if (kt) kt.textContent = `${state.twinMeasuredTension}%`;
  }
}

/* ============================================================================
 * Bootstrap
 * ============================================================================ */
function boot() {
  initGpuPrism();
  initThreeContinuum();
  wireAllControls();
  syncScaleDialUI();
  syncOrganVisibilityUI();
  updateOpticalPanels();
  updateHardwareMetrics();
  addWorldTreeRing('통합 스케일로터 기동', '4K GPU 프리즘 · 3D 연속장 · 트윈 · 6축 인과 · 세계수 · CUDA 로터가 단일 장으로 결합되었습니다.', 'cyan');

  // Immediately synchronize default living transition ("나무 ⇄ 숲") + Live Earth Telemetry!
  syncUnifiedOntologicalField('나무', '숲');
  probeLiveEarthAtmosphere();
  requestAnimationFrame(animate);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}
