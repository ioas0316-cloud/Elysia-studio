/**
 * Elysia Cognitive CAD MVA & Scale-Rotor Hierarchy Server (Node.js)
 * -----------------------------------------------------------------
 * Serves the existing MVA web UI (/L0_substrate/mva/static/) on 0.0.0.0:3000
 * and implements continuous Scale-Rotor Hierarchy dynamics (S0..S4),
 * S^3 quaternion resonance alignment, 3D OLS symbolic regression,
 * Semantic Optimization Lock, and Mirror Cognitive Protocol natively.
 */

const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const dns = require('node:dns').promises;
const net = require('node:net');
const { URL } = require('node:url');

const PORT = Number(process.env.PORT || 3000);
const HOST = '0.0.0.0';
const STATIC_DIR = path.resolve(__dirname, 'L0_substrate', 'mva', 'static');
const ASSETS_IMG_DIR = path.resolve(__dirname, 'src', 'assets', 'images');
const THREE_VENDOR_DIR = path.resolve(__dirname, 'node_modules', 'three');
const ROADMAP_PATH = path.join(STATIC_DIR, 'roadmap.md');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
};

// ============================================================================
// Quaternion & S^3 Rotor Mathematics (Pure Continuous Dynamics)
// ============================================================================
function qNormalize(q) {
  const n = Math.hypot(q[0], q[1], q[2], q[3]);
  if (n < 1e-12) return [0, 0, 0, 1];
  return [q[0] / n, q[1] / n, q[2] / n, q[3] / n];
}

function qMul(a, b) {
  const [ax, ay, az, aw] = a;
  const [bx, by, bz, bw] = b;
  return qNormalize([
    aw * bx + ax * bw + ay * bz - az * by,
    aw * by - ax * bz + ay * bw + az * bx,
    aw * bz + ax * by - ay * bx + az * bw,
    aw * bw - ax * bx - ay * by - az * bz,
  ]);
}

function qFromAxisAngle(ux, uy, uz, angle) {
  const n = Math.hypot(ux, uy, uz);
  if (n < 1e-12) return [0, 0, 0, 1];
  const half = angle * 0.5;
  const s = Math.sin(half) / n;
  return qNormalize([ux * s, uy * s, uz * s, Math.cos(half)]);
}

function qRotateVec3(q, v) {
  const [qx, qy, qz, qw] = qNormalize(q);
  const [vx, vy, vz] = v;
  const tx = 2 * (qy * vz - qz * vy);
  const ty = 2 * (qz * vx - qx * vz);
  const tz = 2 * (qx * vy - qy * vx);
  return [
    vx + qw * tx + (qy * tz - qz * ty),
    vy + qw * ty + (qz * tx - qx * tz),
    vz + qw * tz + (qx * ty - qy * tx),
  ];
}

function qGeodesicDistance(a, b) {
  const dot = Math.abs(a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]);
  return 2 * Math.acos(Math.min(1, Math.max(0, dot)));
}

// ============================================================================
// Hangul Jamo Decomposition for S0 -> S1 -> S2 -> S3 -> S4 Scale-Rotor Ascent
// ============================================================================
function decomposeTextToScaleUnits(text) {
  const trimmed = (text || '').trim();
  if (!trimmed) return { s0: [], s1: [], s2: [], s3: trimmed };
  const s2 = trimmed.split(/[\s,]+/).filter(Boolean);
  const s1 = [];
  const s0 = [];
  for (const ch of trimmed) {
    if (/\s/.test(ch)) continue;
    s1.push(ch);
    const code = ch.charCodeAt(0);
    if (code >= 0xac00 && code <= 0xd7a3) {
      const idx = code - 0xac00;
      const cho = Math.floor(idx / 588);
      const jung = Math.floor((idx % 588) / 28);
      const jong = idx % 28;
      s0.push(`cho:${cho}`, `jung:${jung}`);
      if (jong > 0) s0.push(`jong:${jong}`);
    } else {
      s0.push(`atom:${code}`);
    }
  }
  return { s0, s1, s2, s3: trimmed };
}

function hashToPhaseVec(str) {
  let h1 = 2166136261;
  let h2 = 16777619;
  for (let i = 0; i < str.length; i++) {
    const c = str.charCodeAt(i);
    h1 = Math.imul(h1 ^ c, 16777619) >>> 0;
    h2 = Math.imul(h2 ^ (c * 31 + i), 2246822519) >>> 0;
  }
  const a1 = ((h1 % 3600) / 3600) * Math.PI * 2;
  const a2 = ((h2 % 3600) / 3600) * Math.PI * 2;
  return [
    Math.cos(a1) * Math.cos(a2),
    Math.sin(a1) * Math.cos(a2),
    Math.sin(a2),
  ];
}

// ============================================================================
// 5-Scale Fractal Rotor Hierarchy (S0..S4) + Causal Field Engine State
// ============================================================================
const SCALE_META = [
  { scale: 0, name: 'S0 Atomic Impulse', gearRatio: 1.0, damping: 0.04, radius: 1.8 },
  { scale: 1, name: 'S1 Micro-Composite', gearRatio: 0.618, damping: 0.06, radius: 2.6 },
  { scale: 2, name: 'S2 Functional Unit', gearRatio: 0.382, damping: 0.08, radius: 3.5 },
  { scale: 3, name: 'S3 Modal Configuration', gearRatio: 0.236, damping: 0.10, radius: 4.5 },
  { scale: 4, name: 'S4 Episode Attractor', gearRatio: 0.146, damping: 0.12, radius: 5.6 },
];

class ElysiaLiveEngine {
  constructor() {
    this.cycleIndex = 0;
    this.scaleDial = 0.5; // Continuous sigma in [0, 1] across S0..S4
    this.stateLocked = false;
    this.jumpEvents = [];
    this.crystalsCount = 3;
    this.points = [];
    this.resonanceLog = [];

    // 5 nested scale rotors (S0..S4) with quaternion orientation & so(3) angular velocity
    this.rotors = SCALE_META.map((m, idx) => ({
      ...m,
      quaternion: qFromAxisAngle(0.3 * (idx + 1), 1.0, 0.2 * idx, 0.25 * idx),
      omega: [0.08 / (idx + 1), 0.18 / (idx + 1), 0.05 / (idx + 1)],
      mass: 1.0 + idx * 0.85,
      chromatic: [0.35, 0.40, 0.25], // [Red: Flux, Blue: Order, Yellow: Entropy]
      unitCount: idx === 0 ? 12 : idx === 1 ? 6 : idx === 2 ? 3 : 1,
      coherence: 0.82,
      tension: 0.18,
    }));

    // Mirror Cognitive Protocol state
    this.mirror = {
      selfPhaseVector: [0.577, 0.577, 0.577],
      lastDivergence: 0.142,
      accumulatedGrowthEnergy: 1.25,
      nodes: {
        'S0_Atom': { angle: 0.42, energy: 0.88 },
        'S1_Syllable': { angle: 0.78, energy: 0.91 },
        'S2_Stem': { angle: 1.15, energy: 0.85 },
        'S3_Modal': { angle: 1.52, energy: 0.94 },
        'S4_Telos': { angle: 1.88, energy: 0.97 },
      },
    };

    // Seed initial field & log so dashboard and 3D canvas are immediately alive
    this.injectText('하늘, 바다, 로터, 공명');
    for (let i = 0; i < 12; i++) {
      this.stepCycle();
    }
  }

  injectText(text) {
    const units = decomposeTextToScaleUnits(text);
    const tokens = units.s2.length ? units.s2 : [text];
    const now = Date.now();

    tokens.forEach((tok, idx) => {
      const vec = hashToPhaseVec(tok + ':' + idx);
      const scaleRadius = 2.5 + (idx % 5) * 1.4;
      this.points.push({
        id: `pt_${now}_${idx}`,
        label: tok,
        pos: [
          vec[0] * scaleRadius,
          vec[1] * 2.2,
          vec[2] * scaleRadius,
        ],
        vel: [vec[1] * 0.1, vec[2] * 0.1, vec[0] * 0.1],
        mass: 1.0 + tok.length * 0.2,
        scale: Math.min(4, Math.max(0, tok.length > 4 ? 3 : 2)),
      });
    });

    if (this.points.length > 180) {
      this.points = this.points.slice(-180);
    }

    // Inject S0 atomic impulse and propagate upward S0 -> S4 via gear ratios
    const impulseVec = hashToPhaseVec(units.s3 || text);
    const s0 = this.rotors[0];
    s0.omega[0] += impulseVec[0] * 0.9;
    s0.omega[1] += impulseVec[1] * 0.9;
    s0.omega[2] += impulseVec[2] * 0.9;
    s0.unitCount += units.s0.length;
    this.rotors[1].unitCount += units.s1.length;
    this.rotors[2].unitCount += units.s2.length;
    this.rotors[3].unitCount += 1;

    // Observer divergence feeds Mirror Cognitive growth energy
    const dot = Math.max(-1, Math.min(1,
      this.mirror.selfPhaseVector[0] * impulseVec[0] +
      this.mirror.selfPhaseVector[1] * impulseVec[1] +
      this.mirror.selfPhaseVector[2] * impulseVec[2]
    ));
    const divergence = Math.acos(dot) / Math.PI;
    this.mirror.lastDivergence = divergence;
    this.mirror.accumulatedGrowthEnergy += divergence * 0.45;
    this.stateLocked = false;

    this.evolveScaleRotors(0.15);
    return {
      injected_tokens: tokens.length,
      s0_atoms: units.s0.length,
      s1_composites: units.s1.length,
      s2_units: units.s2.length,
    };
  }

  injectImage(imageBase64) {
    const sample = String(imageBase64 || '').slice(-128);
    const vec = hashToPhaseVec('img:' + sample);
    for (let i = 0; i < 8; i++) {
      const ang = (i / 8) * Math.PI * 2;
      this.points.push({
        id: `img_${Date.now()}_${i}`,
        label: `chroma_${i}`,
        pos: [
          Math.cos(ang) * 4.0 + vec[0],
          Math.sin(ang * 2) * 1.6,
          Math.sin(ang) * 4.0 + vec[2],
        ],
        vel: [vec[0] * 0.25, vec[1] * 0.25, vec[2] * 0.25],
        mass: 1.5,
        scale: 0,
      });
    }
    if (this.points.length > 180) {
      this.points = this.points.slice(-180);
    }
    // Cross-modal disruption excites S0 and S3 simultaneously
    this.rotors[0].omega = [vec[0] * 1.4, vec[1] * 1.4, vec[2] * 1.4];
    this.rotors[3].omega[1] += 0.6;
    this.stateLocked = false;
    this.evolveScaleRotors(0.2);
  }

  evolveScaleRotors(dt = 0.12) {
    // 1) Upward Dimensional Rotor Ascent (S0 -> S4): gear-ratio torque transfer
    for (let i = 0; i < this.rotors.length - 1; i++) {
      const child = this.rotors[i];
      const parent = this.rotors[i + 1];
      const gamma = parent.gearRatio / child.gearRatio;
      const coupling = 0.35 * (0.6 + 0.4 * (1.0 - this.scaleDial));
      for (let k = 0; k < 3; k++) {
        const torque = coupling * (child.omega[k] * gamma - parent.omega[k]);
        parent.omega[k] += (torque / parent.mass) * dt;
      }
    }

    // 2) Downward Plastic Differentiation (S4 -> S0): macro attractor phase stabilization
    const topRotor = this.rotors[4];
    for (let i = this.rotors.length - 2; i >= 0; i--) {
      const r = this.rotors[i];
      const above = this.rotors[i + 1];
      const dist = qGeodesicDistance(r.quaternion, above.quaternion);
      r.coherence = Math.max(0, Math.min(1, Math.cos(dist * 0.5)));
      r.tension = Math.min(2.0, dist / Math.PI);
      const plasticFeedback = 0.25 * (0.5 + 0.5 * this.scaleDial);
      for (let k = 0; k < 3; k++) {
        r.omega[k] = r.omega[k] * (1.0 - r.damping * dt) + plasticFeedback * (above.omega[k] - r.omega[k]) * dt;
      }
      // Chromatic flow: high coherence increases Blue (Order), high speed increases Red (Flux)
      const speed = Math.hypot(r.omega[0], r.omega[1], r.omega[2]);
      const red = Math.min(0.85, 0.2 + speed * 0.4);
      const blue = Math.min(0.85, 0.2 + r.coherence * 0.6);
      const yellow = Math.max(0.05, r.tension * 0.5);
      const s = red + blue + yellow;
      r.chromatic = [red / s, blue / s, yellow / s];
    }

    // 3) Integrate unit quaternions on S^3 (exact exponential map, norm-preserving)
    for (const r of this.rotors) {
      const wMag = Math.hypot(r.omega[0], r.omega[1], r.omega[2]);
      if (wMag > 1e-8) {
        const dq = qFromAxisAngle(r.omega[0], r.omega[1], r.omega[2], wMag * dt);
        r.quaternion = qMul(dq, r.quaternion);
      }
      // Subtle ambient vacuum precession to keep the field alive
      const ambient = qFromAxisAngle(0.2, 1.0, 0.1, 0.04 * r.gearRatio * dt);
      r.quaternion = qMul(ambient, r.quaternion);
    }

    // Compute top-scale coherence against the mean of lower scales
    const meanCoh = this.rotors.slice(0, 4).reduce((acc, r) => acc + r.coherence, 0) / 4;
    topRotor.coherence = meanCoh;
    topRotor.tension = Math.max(0.01, 1.0 - meanCoh);

    // Sync mirror cognitive nodes to the 5 scales
    const keys = Object.keys(this.mirror.nodes);
    this.rotors.forEach((r, idx) => {
      const k = keys[idx];
      if (k) {
        const angle = 2 * Math.acos(Math.min(1, Math.max(-1, r.quaternion[3])));
        this.mirror.nodes[k] = {
          angle,
          energy: Math.min(1.5, 0.4 + r.coherence * 0.8),
        };
      }
    });
    const q4 = topRotor.quaternion;
    const vNorm = Math.hypot(q4[0], q4[1], q4[2]) || 1;
    this.mirror.selfPhaseVector = [q4[0] / vNorm, q4[1] / vNorm, q4[2] / vNorm];
  }

  getActivePoints(externalPoints) {
    if (Array.isArray(externalPoints) && externalPoints.length >= 3) {
      return externalPoints.map((p) => (Array.isArray(p) ? p : p.pos || [0, 0, 0]));
    }
    if (this.points.length >= 3) {
      return this.points.map((p) => p.pos);
    }
    return [
      [1, 0.2, 0],
      [-1, -0.1, 0.8],
      [0.3, 0.15, -1.2],
      [0.6, -0.05, 0.9],
    ];
  }

  // Real 3D Ordinary Least Squares planar regression: y = a*x + b*z + c
  fitSymbolicPlane(pts, q) {
    const rotated = pts.map((p) => qRotateVec3(q, p));
    const n = rotated.length;
    if (n < 3) {
      return { variance: 0, formula: 'y = 0.000x + 0.000z + 0.000', rSquared: 1.0 };
    }

    // Solve normal equations (X^T X) beta = X^T y for [x, z, 1] -> y
    let sxx = 0, sxz = 0, sx1 = 0;
    let szz = 0, sz1 = 0;
    let sxy = 0, szy = 0, sy1 = 0;
    for (const [x, y, z] of rotated) {
      sxx += x * x; sxz += x * z; sx1 += x;
      szz += z * z; sz1 += z;
      sxy += x * y; szy += z * y; sy1 += y;
    }

    const reg = 1e-6;
    const M = [
      [sxx + reg, sxz, sx1],
      [sxz, szz + reg, sz1],
      [sx1, sz1, n + reg],
    ];
    const rhs = [sxy, szy, sy1];
    const beta = solve3x3(M, rhs);
    const [a, b, c] = beta;

    const meanY = sy1 / n;
    let ssRes = 0;
    let ssTot = 0;
    for (const [x, y, z] of rotated) {
      const pred = a * x + b * z + c;
      ssRes += (y - pred) ** 2;
      ssTot += (y - meanY) ** 2;
    }
    const variance = ssRes / n;
    const rSquared = ssTot > 1e-9 ? Math.max(0, Math.min(1, 1 - ssRes / ssTot)) : 1.0;
    const formula = `y = ${a.toFixed(3)}x ${b >= 0 ? '+' : '-'} ${Math.abs(b).toFixed(3)}z ${c >= 0 ? '+' : '-'} ${Math.abs(c).toFixed(3)} (R²=${rSquared.toFixed(3)})`;
    return { variance, formula, rSquared };
  }

  // Real S^3 Quaternion Resonance Alignment minimizing residual variance
  findResonanceAngle(externalPoints, timeT = 0) {
    const pts = this.getActivePoints(externalPoints);
    let bestQ = this.rotors[2].quaternion;
    let bestFit = this.fitSymbolicPlane(pts, bestQ);

    // Golden-spiral Fibonacci sampling on S^2 axis + coarse-to-fine angle sweep
    const axes = [
      [1, 0, 0], [0, 1, 0], [0, 0, 1],
      [1, 1, 0], [0, 1, 1], [1, 0, 1],
      [1, 1, 1], [-1, 1, 0.5],
    ];
    for (const ax of axes) {
      for (let k = 0; k < 12; k++) {
        const ang = (k / 12) * Math.PI + (timeT * 0.01) % (Math.PI / 6);
        const q = qFromAxisAngle(ax[0], ax[1], ax[2], ang);
        const fit = this.fitSymbolicPlane(pts, q);
        if (fit.variance < bestFit.variance) {
          bestFit = fit;
          bestQ = q;
        }
      }
    }

    // Local geodesic refinement
    for (let step = 0.15; step >= 0.02; step *= 0.5) {
      const deltas = [
        [step, 0, 0], [-step, 0, 0],
        [0, step, 0], [0, -step, 0],
        [0, 0, step], [0, 0, -step],
      ];
      for (const d of deltas) {
        const dq = qFromAxisAngle(d[0], d[1], d[2], Math.hypot(d[0], d[1], d[2]));
        const cand = qMul(dq, bestQ);
        const fit = this.fitSymbolicPlane(pts, cand);
        if (fit.variance < bestFit.variance) {
          bestFit = fit;
          bestQ = cand;
        }
      }
    }

    // Align S2/S3 rotors toward the resonant quaternion
    this.rotors[2].quaternion = bestQ;
    return {
      quaternion: bestQ,
      variance: bestFit.variance,
      formula: bestFit.formula,
      r_squared: bestFit.rSquared,
    };
  }

  stepCycle() {
    this.cycleIndex += 1;
    this.evolveScaleRotors(0.18);

    const avgCoherence = this.rotors.reduce((s, r) => s + r.coherence, 0) / this.rotors.length;
    const avgTension = this.rotors.reduce((s, r) => s + r.tension, 0) / this.rotors.length;
    const resonanceScore = Math.max(0.05, Math.min(0.995, avgCoherence));
    const synesthesia = Math.max(0, Math.min(1, avgCoherence * (1.0 - 0.3 * avgTension)));

    let status = 'RESONATING';
    if (resonanceScore > 0.85 && avgTension < 0.22) {
      status = 'CRYSTALLIZED';
      this.crystalsCount += 1;
      if (!this.stateLocked && resonanceScore > 0.90) {
        this.stateLocked = true;
        this.jumpEvents.push({
          cycle: this.cycleIndex,
          timestamp: new Date().toISOString(),
          distance_to_s_abs: Number(avgTension.toFixed(4)),
          coherence: Number(resonanceScore.toFixed(4)),
          scale_dial: Number(this.scaleDial.toFixed(3)),
        });
        if (this.jumpEvents.length > 50) this.jumpEvents.shift();
      }
    } else if (avgTension > 0.55) {
      status = 'FRICTION_SHIFT';
      this.stateLocked = false;
    }

    const entry = {
      cycle_index: this.cycleIndex,
      status,
      resonance_score: Number(resonanceScore.toFixed(4)),
      tension: Number(avgTension.toFixed(4)),
      synesthesia: Number(synesthesia.toFixed(4)),
      scale_dial: Number(this.scaleDial.toFixed(3)),
    };
    this.resonanceLog.push(entry);
    if (this.resonanceLog.length > 300) this.resonanceLog.shift();

    return entry;
  }

  getHealthSummary() {
    const recent = this.resonanceLog.slice(-20);
    const n = recent.length || 1;
    const avgRes = recent.reduce((s, r) => s + r.resonance_score, 0) / n;
    const avgTen = recent.reduce((s, r) => s + r.tension, 0) / n;
    let emotionalState = 'Stable';
    if (avgRes >= 0.82 && avgTen < 0.25) emotionalState = 'Thriving';
    else if (avgTen > 0.65) emotionalState = 'Crisis';
    else if (avgRes < 0.55) emotionalState = 'Struggling';

    return {
      emotional_state: emotionalState,
      resonance_rate: Number(avgRes.toFixed(4)),
      avg_tension: Number(avgTen.toFixed(4)),
      total_resonance_events: this.crystalsCount,
      crystals: this.crystalsCount,
      cycles: this.cycleIndex,
      scale_dial: Number(this.scaleDial.toFixed(3)),
    };
  }
}

function solve3x3(A, b) {
  const m = A.map((row, i) => [...row, b[i]]);
  for (let i = 0; i < 3; i++) {
    let pivot = i;
    for (let r = i + 1; r < 3; r++) {
      if (Math.abs(m[r][i]) > Math.abs(m[pivot][i])) pivot = r;
    }
    [m[i], m[pivot]] = [m[pivot], m[i]];
    const div = Math.abs(m[i][i]) > 1e-12 ? m[i][i] : 1e-12;
    for (let c = i; c < 4; c++) m[i][c] /= div;
    for (let r = 0; r < 3; r++) {
      if (r === i) continue;
      const factor = m[r][i];
      for (let c = i; c < 4; c++) m[r][c] -= factor * m[i][c];
    }
  }
  return [m[0][3], m[1][3], m[2][3]];
}

const engine = new ElysiaLiveEngine();

// ============================================================================
// HTTP Helpers
// ============================================================================
function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  });
  res.end(body);
}

function sendFileFromDir(res, baseDir, filePath) {
  const resolved = path.resolve(filePath);
  if (resolved !== baseDir && !resolved.startsWith(baseDir + path.sep)) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }
  fs.readFile(resolved, (err, content) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not Found');
      return;
    }
    const ext = path.extname(resolved).toLowerCase();
    res.writeHead(200, {
      'Content-Type': MIME_TYPES[ext] || 'application/octet-stream',
      'Cache-Control': 'public, max-age=300',
    });
    res.end(content);
  });
}

function sendFile(res, filePath) {
  const resolved = path.resolve(filePath);
  if (resolved !== STATIC_DIR && !resolved.startsWith(STATIC_DIR + path.sep)) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }
  fs.readFile(resolved, (err, content) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not Found');
      return;
    }
    const ext = path.extname(resolved).toLowerCase();
    res.writeHead(200, {
      'Content-Type': MIME_TYPES[ext] || 'application/octet-stream',
      'Cache-Control': 'no-cache',
    });
    res.end(content);
  });
}

function readJsonBody(req) {
  return new Promise((resolve) => {
    const chunks = [];
    let size = 0;
    const MAX_BYTES = 10 * 1024 * 1024;
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size <= MAX_BYTES) chunks.push(chunk);
    });
    req.on('end', () => {
      if (!chunks.length) return resolve({});
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8')));
      } catch {
        resolve({});
      }
    });
    req.on('error', () => resolve({}));
  });
}

function readRoadmapMarkdown() {
  try {
    return fs.readFileSync(ROADMAP_PATH, 'utf8');
  } catch {
    try {
      return fs.readFileSync(path.resolve(__dirname, 'README.md'), 'utf8');
    } catch {
      return '# Elysia Scale-Rotor Roadmap\nActive continuous causal engine.';
    }
  }
}

// ============================================================================
// Universal Cross-Domain Dimensional Manifold Engine (Surface -> Cube -> Sphere -> Planets)
// ============================================================================
const DOMAIN_PRESETS = [
  {
    id: 'chemistry_catalyst',
    domain: 'chemistry',
    label: '화학 · 촉매 상전이',
    text: '반응물 엔탈피 구배와 촉매 표면 결합이 활성화 에너지 장벽을 낮추어 비평형 상전이와 결정 성장을 유도한다',
    theta2: [0.35, 0.30, 0.35],
  },
  {
    id: 'physics_wave',
    domain: 'physics',
    label: '물리 · 보존장과 위상 공명',
    text: '에너지 보존 관성과 퍼텐셜 구배가 경계 조건 안에서 결합 공명을 형성하며 최소 작용 궤도로 수렴한다',
    theta2: [-0.25, -0.35, 0.15],
  },
  {
    id: 'biology_homeostasis',
    domain: 'biology',
    label: '생물 · 세포막 항상성과 분화',
    text: '세포막 경계 안팎의 삼투 구배와 대사 효소 결합이 항상성 보존과 형태발생 분화를 동시에 조율한다',
    theta2: [0.10, 0.45, 0.40],
  },
  {
    id: 'language_a4',
    domain: 'language',
    label: '언어 · A4 1,024토큰 동시 결정화',
    text: '문단 서두의 불변 명제와 말미의 결론이 가변저항 면 위에서 동시에 공명하여 단선적 토큰 생성을 넘어선다',
    theta2: [0.05, -0.20, 0.25],
  },
  {
    id: 'systems_economy',
    domain: 'systems',
    label: '복잡계 · 네트워크 신뢰와 분기',
    text: '수요 구배와 거래 마찰 장벽 사이에서 신뢰 결합이 임계점을 넘으면 단일 시장이 다중 생태계로 평행 분화한다',
    theta2: [0.45, 0.55, 0.70],
  },
];

function clampVal(v, lo, hi) {
  return Math.max(lo, Math.min(hi, Number.isFinite(v) ? v : 0));
}

function tokenStructuralSig(token) {
  let h = 2166136261;
  for (let i = 0; i < token.length; i++) {
    h = Math.imul(h ^ token.charCodeAt(i), 16777619) >>> 0;
    h = Math.imul(h ^ Math.imul(i + 1, 2654435761), 2246822519) >>> 0;
  }
  let a = (h & 0xff) / 255;
  let b = ((h >>> 8) & 0xff) / 255;
  let c = ((h >>> 16) & 0xff) / 255;
  let d = ((h >>> 24) & 0xff) / 255;
  const low = token.toLowerCase();
  if (/보존|질량|에너지|평형|불변|명제|항상성|const|mass|law|=/.test(low)) a = Math.min(1, a * 0.4 + 0.65);
  if (/열|압력|전위|구배|반응|엔탈피|삼투|수요|flux|grad|delta|->|→/.test(low)) b = Math.min(1, b * 0.4 + 0.65);
  if (/결합|촉매|공명|연결|상호|효소|신뢰|bond|sync|link|\+/.test(low)) c = Math.min(1, c * 0.4 + 0.65);
  if (/경계|장벽|한계|막|제약|임계|마찰|limit|wall|threshold/.test(low)) d = Math.min(1, d * 0.4 + 0.65);
  const norm = Math.hypot(a, b, c, d) || 1;
  return [a / norm, b / norm, c / norm, d / norm];
}

function translateCrossDomainJS(t1, t2) {
  const [cCons, cGrad, cCoup, cBnd] = t1;
  const fluxMode = t2[0] > 0.15;
  const expandMode = t2[1] > 0.15;
  const tempEnt = Math.max(0.05, 0.5 + 0.4 * t2[0]);

  return {
    physics: {
      name: '물리학 (Physics)',
      equation: `dE/dt = -${cBnd.toFixed(2)}∇·J + ${cGrad.toFixed(2)}(-∇U) + ${cCoup.toFixed(2)}κ·sin(Δφ)`,
      regime: fluxMode ? '비평형 상전이 · 파동 확산' : '보존 해밀토니안 정상 궤도',
      interpretation: `관성 보존(${cCons.toFixed(2)}) 대비 퍼텐셜 구배(${cGrad.toFixed(2)})가 ${
        expandMode ? '임계 장벽을 넘어 외부 위상으로 팽창·전파됩니다.' : '경계 구속 안에서 최소 작용 궤도로 수렴합니다.'
      }`,
    },
    chemistry: {
      name: '화학 (Chemistry)',
      equation: `ΔG = ΔH(${cGrad.toFixed(2)}) - TΔS(${tempEnt.toFixed(2)}), Ea = ${cBnd.toFixed(2)}`,
      regime: cCoup >= cBnd ? '촉매 활성화 · 연쇄 합성' : '동적 평형 · 결정 석출',
      interpretation: `결합 친화도(${cCoup.toFixed(2)})와 활성화 장벽(${cBnd.toFixed(2)})의 비대칭이 ${
        expandMode ? '신규 생성물 상으로 역확산 합성을 촉발합니다.' : '저에너지 안정 결정 격자로 침전 수렴합니다.'
      }`,
    },
    biology: {
      name: '생물학 (Biology)',
      equation: `dH/dt = ${cCons.toFixed(2)}(H₀-H) + ${cCoup.toFixed(2)}·Symbiosis - ${cGrad.toFixed(2)}·Stress`,
      regime: expandMode ? '형태발생 · 표현형 분화' : '항상성 유지 · 대사 복원',
      interpretation: `막 경계(${cBnd.toFixed(2)})를 사이에 두고 내부 보존(${cCons.toFixed(2)})과 외부 구배(${cGrad.toFixed(2)})가 ${
        expandMode ? '새로운 기능 조직으로 분화 적응합니다.' : '자가복구 피드백 루프로 수렴합니다.'
      }`,
    },
    language: {
      name: '언어 · A4 면 (Language)',
      equation: `A4[32×32]: R_anchor=${cCons.toFixed(2)}, G_fluid=${cGrad.toFixed(2)}, Beam=${cCoup.toFixed(2)}`,
      regime: expandMode ? '역발상 발산 생성 (S4→S0)' : '핵심 원리 수렴 압축 (S0→S4)',
      interpretation: `고저항 불변 문맥(${cCons.toFixed(2)})을 고정한 채 저저항 슬롯 전체를 병렬 결정화하여 ${
        expandMode ? '기존 전제를 비튼 새로운 서사 가지를 생성합니다.' : '문서 전체의 인과를 단일 핵심 원리로 압축합니다.'
      }`,
    },
    systems: {
      name: '경제 · 복잡계 (Systems)',
      equation: `Flow = (${cGrad.toFixed(2)}·Demand) / (${cBnd.toFixed(2)}·Friction), Trust = ${cCoup.toFixed(2)}`,
      regime: t2[2] > 0.2 ? '네트워크 분기 · 다중 생태계' : '균형 가격 · 신뢰 수렴',
      interpretation: `거래 마찰(${cBnd.toFixed(2)}) 대비 유인 구배(${cGrad.toFixed(2)})와 신뢰 결합(${cCoup.toFixed(2)})이 ${
        t2[2] > 0.2 ? '평행 생태계로 스케일 분화됩니다.' : '단일 안정 균형점으로 수렴합니다.'
      }`,
    },
  };
}

function runUniversalManifoldTransform(body) {
  const ROWS = 8;
  const COLS = 8;
  const TIME_LAYERS = 5;
  const PASSES = 8;
  const inputText = String(body.text || DOMAIN_PRESETS[0].text).trim();
  const domain = String(body.domain || 'unified');
  const rawT2 = Array.isArray(body.theta2) ? body.theta2 : [0.2, 0.15, 0.35];
  const t2 = [
    clampVal(Number(rawT2[0]), -1, 1),
    clampVal(Number(rawT2[1]), -1, 1),
    clampVal(Number(rawT2[2]), -1, 1),
  ];

  const tokens = inputText.replace(/[\n,]+/g, ' ').split(/\s+/).filter(Boolean);
  const safeTokens = tokens.length ? tokens : ['보존', '구배', '결합', '경계'];

  // 1) Build 2D A4 Surface Frame (8x8 macro-blocks representing 32x32=1,024 slots)
  const grid = [];
  for (let r = 0; r < ROWS; r++) {
    const row = [];
    for (let c = 0; c < COLS; c++) {
      const idx = r * COLS + c;
      const tok = safeTokens[idx % safeTokens.length];
      let state = tokenStructuralSig(tok);
      const isDirect = idx < safeTokens.length;
      const resistance = isDirect ? 0.88 : 0.24 + 0.16 * ((idx % 3) / 2);
      if (!isDirect) {
        const p = 0.35 * Math.sin(idx * 0.7);
        state = state.map((x, k) => clampVal(x + p * (k % 2 === 0 ? 0.15 : -0.15), 0.01, 1));
        const n = Math.hypot(...state) || 1;
        state = state.map((x) => x / n);
      }
      row.push({ r, c, token: tok, resistance, state, tension: 0 });
    }
    grid.push(row);
  }

  const measureTension = () => {
    let sum = 0;
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const cur = grid[r][c];
        let acc = 0;
        const nbs = [
          grid[(r + ROWS - 1) % ROWS][c],
          grid[(r + 1) % ROWS][c],
          grid[r][(c + COLS - 1) % COLS],
          grid[r][(c + 1) % COLS],
        ];
        for (const nb of nbs) {
          let d2 = 0;
          for (let k = 0; k < 4; k++) d2 += (cur.state[k] - nb.state[k]) ** 2;
          acc += Math.sqrt(d2);
        }
        cur.tension = acc / 4;
        sum += cur.tension;
      }
    }
    return sum / (ROWS * COLS);
  };

  const tensionBefore = measureTension();

  // Parallel variable-resistor surface crystallization
  for (let pass = 0; pass < PASSES; pass++) {
    const s4 = [0, 0, 0, 0];
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        for (let k = 0; k < 4; k++) s4[k] += grid[r][c].state[k];
      }
    }
    const s4n = Math.hypot(...s4) || 1;
    for (let k = 0; k < 4; k++) s4[k] /= s4n;

    const next = Array.from({ length: ROWS }, () => Array(COLS));
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const cell = grid[r][c];
        const G = 1 - cell.resistance;
        const nbs = [
          grid[(r + ROWS - 1) % ROWS][c],
          grid[(r + 1) % ROWS][c],
          grid[r][(c + COLS - 1) % COLS],
          grid[r][(c + 1) % COLS],
        ];
        const upd = [0, 0, 0, 0];
        for (let k = 0; k < 4; k++) {
          const nbAvg = 0.25 * (nbs[0].state[k] + nbs[1].state[k] + nbs[2].state[k] + nbs[3].state[k]);
          upd[k] = (1 - G * 0.65) * cell.state[k] + G * 0.5 * nbAvg + G * 0.15 * s4[k];
        }
        const un = Math.hypot(...upd) || 1;
        next[r][c] = upd.map((x) => x / un);
      }
    }
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) grid[r][c].state = next[r][c];
    }
  }
  const tensionAfter = measureTension();

  const extractLaws = (t2Vec) => {
    let wSum = 0;
    const core = [0, 0, 0, 0];
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const w = 0.35 + grid[r][c].resistance;
        wSum += w;
        for (let k = 0; k < 4; k++) core[k] += w * grid[r][c].state[k];
      }
    }
    for (let k = 0; k < 4; k++) core[k] /= wSum;
    const raw = [
      clampVal(core[0] - 0.25 * t2Vec[0] - 0.15 * t2Vec[1], 0.05, 1),
      clampVal(core[1] + 0.30 * t2Vec[0] + 0.20 * t2Vec[1], 0.05, 1),
      clampVal(core[2] - 0.20 * t2Vec[2] + 0.18 * t2Vec[0], 0.05, 1),
      clampVal(core[3] - 0.25 * t2Vec[1] - 0.15 * t2Vec[0], 0.05, 1),
    ];
    const n = Math.hypot(...raw) || 1;
    return raw.map((x) => x / n);
  };

  const theta1 = extractLaws(t2);
  const crossDomain = translateCrossDomainJS(theta1, t2);

  // 4) Parallel Planetary Worlds bifurcated along Theta_2
  const spread = 0.45 + 0.45 * Math.max(0, t2[2]);
  const planetSpecs = [
    ['planet_base', '기준 행성 (현재 관측 축)', t2, '현재 메타인과 축의 정본 세계선'],
    ['planet_order', '결정질 질서 행성', [clampVal(t2[0] - spread, -1, 1), clampVal(t2[1] - 0.35, -1, 1), -0.4], '보존·경계 법칙이 강화되어 구조가 결정화된 세계선'],
    ['planet_catalyst', '촉매 흐름 행성', [clampVal(t2[0] + spread, -1, 1), clampVal(t2[1] + 0.25, -1, 1), 0.3], '구배와 결합이 극대화되어 상전이가 연쇄 가속되는 세계선'],
    ['planet_inverse', '역발상 팽창 행성', [-t2[0], clampVal(-t2[1] + 0.55, -1, 1), 0.6], '기존 제약을 반전시켜 중심핵에서 신현상을 역팽창하는 세계선'],
    ['planet_synthesis', '창발 통합 행성', [0.15, 0.35, clampVal(t2[2] + 0.4, -1, 1)], '질서와 흐름의 임계 공명으로 다학문 구조가 통합되는 세계선'],
  ];

  const planets = planetSpecs.map(([id, label, pt2, summary]) => {
    const pt1 = extractLaws(pt2);
    const pIso = translateCrossDomainJS(pt1, pt2);
    return {
      world_id: id,
      label_ko: label,
      theta2: pt2.map((x) => Number(x.toFixed(3))),
      theta1: pt1.map((x) => Number(x.toFixed(4))),
      stability: Number(clampVal(0.5 * pt1[0] + 0.5 * pt1[3], 0, 1).toFixed(4)),
      entropy: Number(clampVal(0.6 * pt1[1] + 0.4 * (0.5 + 0.5 * pt2[0]), 0, 1).toFixed(4)),
      novelty: Number(clampVal(0.55 * (0.5 + 0.5 * pt2[1]) + 0.45 * pt1[2], 0, 1).toFixed(4)),
      summary_ko: summary,
      cross_domain: pIso,
    };
  });

  const cellsFlat = [];
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const cell = grid[r][c];
      cellsFlat.push({
        r: cell.r,
        c: cell.c,
        token: cell.token,
        resistance: Number(cell.resistance.toFixed(3)),
        tension: Number(cell.tension.toFixed(4)),
        state: cell.state.map((x) => Number(x.toFixed(3))),
      });
    }
  }

  return {
    status: 'ok',
    domain,
    rows: ROWS,
    cols: COLS,
    time_layers: TIME_LAYERS,
    crystallization_passes: PASSES,
    mean_tension_before: Number(tensionBefore.toFixed(4)),
    mean_tension_after: Number(tensionAfter.toFixed(4)),
    compression_ratio: Number(((ROWS * COLS * TIME_LAYERS) / 4).toFixed(1)),
    theta1: {
      conservation_inertia: Number(theta1[0].toFixed(4)),
      gradient_potential: Number(theta1[1].toFixed(4)),
      relational_coupling: Number(theta1[2].toFixed(4)),
      boundary_constraint: Number(theta1[3].toFixed(4)),
    },
    theta2: {
      order_vs_flux: Number(t2[0].toFixed(3)),
      converge_vs_expand: Number(t2[1].toFixed(3)),
      unify_vs_bifurcate: Number(t2[2].toFixed(3)),
    },
    cells: cellsFlat,
    cross_domain: crossDomain,
    planets,
    hypotheses: [
      `경계 제약(${theta1[3].toFixed(2)})을 반전하면 활성화 장벽이 붕괴해 결합 공명(${theta1[2].toFixed(2)})이 전 표면에 동시 전파됩니다.`,
      `동일한 Θ₁ 비율은 물리학의 '${crossDomain.physics.regime}' 및 화학의 '${crossDomain.chemistry.regime}'과 구조적 동형입니다.`,
      `320개 시공간 셀이 4개 핵심 법칙(80:1)으로 환원되어 5개 평행 행성 세계선으로 분화되었습니다.`,
    ],
  };
}

// ============================================================================
// Safe External Data Ingestion Proxy (YouTube, GitHub, Wikimedia Commons)
// ============================================================================
const EXTERNAL_INGEST_PRESETS = [
  {
    id: 'uhd_starry_4k',
    kind: 'wikimedia',
    label: '4K UHD 명화 · 별이 빛나는 밤 (3840px)',
    url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/3840px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
    note: '3840px 4K UHD 원화 — GPU 셰이더 6축 광학 분해·3D 기복·CUDA 타일 로터 직결',
  },
  {
    id: 'uhd_wave_4k',
    kind: 'wikimedia',
    label: '4K UHD 명화 · 가나가와 파도 (3840px)',
    url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Tsunami_by_hokusai_19th_century.jpg/3840px-Tsunami_by_hokusai_19th_century.jpg',
    note: '3840px 4K UHD 초정밀 파도 선·색면 직교 분해 및 유체 동역학 대조',
  },
  {
    id: 'video_atmosphere_hd',
    kind: 'video',
    label: '위성 실황 영상 · 남극 대기 중력파 (1920×1080)',
    url: 'https://upload.wikimedia.org/wikipedia/commons/a/a4/Gravity_Waves_Cascade_off_of_Islands_Near_Antarctica_%28CIRA_2023-12-29_-_nolabels%29.webm',
    note: '정지 해양·섬(거시 앵커) 위를 흐르는 실시간 대기 중력파 시공간 영상',
  },
  {
    id: 'video_traffic_hd',
    kind: 'video',
    label: '도심 교차로 실황 영상 (1816×1022)',
    url: 'https://upload.wikimedia.org/wikipedia/commons/2/2c/Tirana_traffic_lights.webm',
    note: '고정 건축물(S4)과 이동 차량·신호(S0) 실물 동역학 영상',
  },
];

const ALLOWED_EXTERNAL_HOSTS = new Set([
  'youtube.com',
  'www.youtube.com',
  'm.youtube.com',
  'youtu.be',
  'i.ytimg.com',
  'img.youtube.com',
  'github.com',
  'www.github.com',
  'api.github.com',
  'raw.githubusercontent.com',
  'upload.wikimedia.org',
  'commons.wikimedia.org',
  'en.wikipedia.org',
  'ko.wikipedia.org',
  'api.open-meteo.com',
]);

const MAX_EXTERNAL_BYTES = 24 * 1024 * 1024;
const EXTERNAL_TIMEOUT_MS = 14000;
const SAFE_IMAGE_MIMES = new Set(['image/jpeg', 'image/png', 'image/webp', 'image/gif']);
const SAFE_VIDEO_MIMES = new Set(['video/webm', 'video/mp4']);
const mediaProxyCache = new Map(); // Bounded LRU for 4K/UHD media clips

function isPrivateOrBlockedIp(ip) {
  const clean = String(ip || '').toLowerCase();
  if (clean.startsWith('::ffff:')) {
    return isPrivateOrBlockedIp(clean.slice(7));
  }
  if (net.isIPv4(clean)) {
    const parts = clean.split('.').map(Number);
    if (parts.length !== 4) return true;
    const [a, b] = parts;
    if (a === 0 || a === 10 || a === 127) return true;
    if (a === 169 && b === 254) return true;
    if (a === 172 && b >= 16 && b <= 31) return true;
    if (a === 192 && b === 168) return true;
    if (a === 100 && b >= 64 && b <= 127) return true;
    if (a >= 224) return true;
    return false;
  }
  if (net.isIPv6(clean)) {
    if (clean === '::' || clean === '::1') return true;
    if (clean.startsWith('fc') || clean.startsWith('fd') || clean.startsWith('fe8') || clean.startsWith('fe9') || clean.startsWith('fea') || clean.startsWith('feb')) {
      return true;
    }
    return false;
  }
  return true;
}

async function assertSafeExternalUrl(rawUrl) {
  let u;
  try {
    u = new URL(String(rawUrl || '').trim());
  } catch {
    const err = new Error('올바른 HTTPS URL 형식이 아닙니다.');
    err.code = 'INVALID_URL';
    throw err;
  }
  if (u.protocol !== 'https:') {
    const err = new Error('보안을 위해 https:// 주소만 허용됩니다.');
    err.code = 'INVALID_URL';
    throw err;
  }
  if (u.username || u.password || (u.port && u.port !== '443')) {
    const err = new Error('표준 HTTPS 공개 주소만 입력할 수 있습니다.');
    err.code = 'INVALID_URL';
    throw err;
  }
  const host = u.hostname.toLowerCase();
  if (host.includes('pixiv.net') || host.includes('pximg.net')) {
    const err = new Error('Pixiv는 로그인·리퍼러 차단 정책으로 직접 수집이 막혀 있습니다. 이미지를 PC에 저장한 뒤 화면에 드래그 앤 드롭해 주세요.');
    err.code = 'PIXIV_BLOCKED';
    throw err;
  }
  if (!ALLOWED_EXTERNAL_HOSTS.has(host)) {
    const err = new Error(`허용된 공개 소스(YouTube, GitHub, Wikimedia, Wikipedia, Open-Meteo)만 직접 수집할 수 있습니다. 다른 사이트의 이미지·음원은 파일 업로드로 바로 직조할 수 있습니다.`);
    err.code = 'HOST_NOT_ALLOWED';
    throw err;
  }
  const records = await dns.lookup(host, { all: true });
  if (!records || records.length === 0) {
    throw new Error('호스트 주소를 확인할 수 없습니다.');
  }
  for (const rec of records) {
    if (isPrivateOrBlockedIp(rec.address)) {
      const err = new Error('내부 사설 네트워크 주소로의 접근은 차단됩니다.');
      err.code = 'PRIVATE_IP_BLOCKED';
      throw err;
    }
  }
  return u;
}

async function safeFetchBuffer(rawUrl, options = {}, redirectDepth = 0) {
  if (redirectDepth > 2) {
    throw new Error('리다이렉트 횟수 제한을 초과했습니다.');
  }
  const u = await assertSafeExternalUrl(rawUrl);
  const res = await fetch(u.toString(), {
    method: 'GET',
    redirect: 'manual',
    signal: AbortSignal.timeout(EXTERNAL_TIMEOUT_MS),
    headers: {
      'User-Agent': 'ElysiaScaleRotorLab/1.0 (Educational Multimodal Research)',
      ...(options.headers || {}),
    },
  });

  if (res.status >= 300 && res.status < 400 && res.headers.get('location')) {
    const nextUrl = new URL(res.headers.get('location'), u).toString();
    return safeFetchBuffer(nextUrl, options, redirectDepth + 1);
  }
  if (!res.ok) {
    throw new Error(`외부 응답 오류 (HTTP ${res.status})`);
  }

  const contentLength = Number(res.headers.get('content-length') || 0);
  if (contentLength > MAX_EXTERNAL_BYTES) {
    throw new Error('외부 파일 크기가 최대 허용 한도(10MB)를 초과합니다.');
  }

  const reader = res.body ? res.body.getReader() : null;
  if (!reader) {
    const ab = await res.arrayBuffer();
    if (ab.byteLength > MAX_EXTERNAL_BYTES) {
      throw new Error('외부 파일 크기가 최대 허용 한도(10MB)를 초과합니다.');
    }
    return { buffer: Buffer.from(ab), contentType: res.headers.get('content-type') || 'application/octet-stream' };
  }

  const chunks = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > MAX_EXTERNAL_BYTES) {
      reader.cancel().catch(() => {});
      throw new Error('외부 파일 크기가 최대 허용 한도(10MB)를 초과합니다.');
    }
    chunks.push(Buffer.from(value));
  }
  return {
    buffer: Buffer.concat(chunks),
    contentType: res.headers.get('content-type') || 'application/octet-stream',
  };
}

function extractYouTubeId(u) {
  const host = u.hostname.toLowerCase();
  let id = '';
  if (host === 'youtu.be') {
    id = u.pathname.replace(/^\/+/, '').split('/')[0] || '';
  } else if (u.pathname.startsWith('/shorts/')) {
    id = u.pathname.split('/')[2] || '';
  } else {
    id = u.searchParams.get('v') || '';
  }
  return /^[A-Za-z0-9_-]{11}$/.test(id) ? id : null;
}

async function ingestExternalData(rawUrl) {
  const u = await assertSafeExternalUrl(rawUrl);
  const host = u.hostname.toLowerCase();

  // 1) YouTube ingestion: real oEmbed metadata + crisp 1280x720 maxresdefault frame (fallback sddefault/hqdefault)
  if (host.includes('youtube.com') || host === 'youtu.be') {
    const vid = extractYouTubeId(u);
    if (!vid) throw new Error('유효한 YouTube 영상 ID를 찾을 수 없습니다.');
    const oembedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent(`https://www.youtube.com/watch?v=${vid}`)}&format=json`;

    let meta = { title: `YouTube Video (${vid})`, author_name: 'YouTube' };
    try {
      const mRes = await safeFetchBuffer(oembedUrl, { headers: { Accept: 'application/json' } });
      meta = JSON.parse(mRes.buffer.toString('utf8'));
    } catch {
      // Fall back to ID title if oEmbed rate-limits
    }

    const candidates = [
      `https://i.ytimg.com/vi/${vid}/maxresdefault.jpg`,
      `https://i.ytimg.com/vi/${vid}/sddefault.jpg`,
      `https://i.ytimg.com/vi/${vid}/hqdefault.jpg`,
    ];
    let imgRes = null;
    let chosenResLabel = '1280×720 HD';
    for (let i = 0; i < candidates.length; i++) {
      try {
        imgRes = await safeFetchBuffer(candidates[i], { headers: { Accept: 'image/jpeg,image/png,image/webp' } });
        chosenResLabel = i === 0 ? '1280×720 HD' : i === 1 ? '640×480 SD' : '480×360 HQ';
        break;
      } catch {
        // try next resolution tier
      }
    }
    if (!imgRes) throw new Error('유튜브 고해상도 프레임을 가져오지 못했습니다.');
    const mime = imgRes.contentType.split(';')[0].trim().toLowerCase();
    if (!SAFE_IMAGE_MIMES.has(mime)) throw new Error('유튜브 썸네일 이미지를 가져오지 못했습니다.');

    const textSeed = `${meta.title || ''} ${meta.author_name || ''}`.trim();
    const lawReport = runUniversalManifoldTransform({ text: textSeed, domain: 'youtube' });

    return {
      status: 'ok',
      kind: 'youtube',
      title: String(meta.title || `YouTube (${vid})`),
      subtitle: `YouTube ${chosenResLabel} · ${String(meta.author_name || 'Creator')} · ${(imgRes.buffer.byteLength / 1024).toFixed(0)} KB`,
      source_url: `https://www.youtube.com/watch?v=${vid}`,
      image_data_url: `data:${mime};base64,${imgRes.buffer.toString('base64')}`,
      theta1: lawReport.theta1,
      cross_domain: lawReport.cross_domain,
    };
  }

  // 2) GitHub Repository ingestion: real repo metadata, language shares, and root directory topology
  if (host === 'github.com' || host === 'www.github.com') {
    const parts = u.pathname.replace(/^\/+|\/+$/g, '').split('/');
    const owner = parts[0] || '';
    const repo = (parts[1] || '').replace(/\.git$/, '');
    if (!/^[A-Za-z0-9._-]+$/.test(owner) || !/^[A-Za-z0-9._-]+$/.test(repo)) {
      throw new Error('올바른 GitHub 저장소 주소(https://github.com/owner/repo)를 입력해 주세요.');
    }

    const ghHeaders = { Accept: 'application/vnd.github+json' };
    const repoRes = await safeFetchBuffer(`https://api.github.com/repos/${owner}/${repo}`, { headers: ghHeaders });
    const repoJson = JSON.parse(repoRes.buffer.toString('utf8'));

    let languages = {};
    let contents = [];
    try {
      const langRes = await safeFetchBuffer(`https://api.github.com/repos/${owner}/${repo}/languages`, { headers: ghHeaders });
      languages = JSON.parse(langRes.buffer.toString('utf8'));
    } catch {}
    try {
      const treeRes = await safeFetchBuffer(`https://api.github.com/repos/${owner}/${repo}/contents`, { headers: ghHeaders });
      const parsedTree = JSON.parse(treeRes.buffer.toString('utf8'));
      if (Array.isArray(parsedTree)) {
        contents = parsedTree.slice(0, 48).map((item) => ({
          name: String(item.name || ''),
          type: String(item.type || 'file'),
          size: Number(item.size || 512),
        }));
      }
    } catch {}

    const langEntries = Object.entries(languages).slice(0, 8);
    const seedText = `${repoJson.full_name || `${owner}/${repo}`} ${repoJson.description || ''} ${langEntries.map(([k]) => k).join(' ')} ${contents.slice(0, 16).map((c) => c.name).join(' ')}`;
    const lawReport = runUniversalManifoldTransform({ text: seedText, domain: 'github' });

    return {
      status: 'ok',
      kind: 'github',
      title: String(repoJson.full_name || `${owner}/${repo}`),
      subtitle: `GitHub · ★${Number(repoJson.stargazers_count || 0).toLocaleString()} · ${String(repoJson.language || 'Multi-Language')} · ${contents.length} root nodes`,
      description: String(repoJson.description || ''),
      source_url: `https://github.com/${owner}/${repo}`,
      repo_topology: {
        stars: Number(repoJson.stargazers_count || 0),
        forks: Number(repoJson.forks_count || 0),
        languages: langEntries,
        nodes: contents,
      },
      theta1: lawReport.theta1,
      cross_domain: lawReport.cross_domain,
    };
  }

  // 3) Wikimedia / Direct Public HD Video or High-Res Image ingestion
  const lowerPath = u.pathname.toLowerCase();
  if (lowerPath.endsWith('.webm') || lowerPath.endsWith('.mp4')) {
    const vidEntry = await fetchCachedSafeMedia(u.toString());
    let fileName = 'External HD Video';
    try {
      fileName = decodeURIComponent(u.pathname.split('/').pop() || 'External HD Video').replace(/_/g, ' ');
    } catch {
      fileName = (u.pathname.split('/').pop() || 'External HD Video').replace(/_/g, ' ');
    }
    const lawReport = runUniversalManifoldTransform({ text: fileName, domain: 'video' });
    return {
      status: 'ok',
      kind: 'video',
      title: fileName,
      subtitle: `HD Video · ${host} · ${(vidEntry.buffer.byteLength / (1024 * 1024)).toFixed(2)} MB · ${vidEntry.mime}`,
      source_url: u.toString(),
      media_url: `/api/ingest/media?url=${encodeURIComponent(u.toString())}`,
      theta1: lawReport.theta1,
      cross_domain: lawReport.cross_domain,
    };
  }

  const res = await safeFetchBuffer(u.toString(), { headers: { Accept: 'image/jpeg,image/png,image/webp,image/gif,video/webm,video/mp4' } });
  const mime = res.contentType.split(';')[0].trim().toLowerCase();
  if (SAFE_VIDEO_MIMES.has(mime)) {
    mediaProxyCache.set(u.toString(), { buffer: res.buffer, mime });
    while (mediaProxyCache.size > 3) {
      const oldest = mediaProxyCache.keys().next().value;
      mediaProxyCache.delete(oldest);
    }
    let fileName = 'External HD Video';
    try {
      fileName = decodeURIComponent(u.pathname.split('/').pop() || 'External HD Video').replace(/_/g, ' ');
    } catch {}
    return {
      status: 'ok',
      kind: 'video',
      title: fileName,
      subtitle: `HD Video · ${host} · ${(res.buffer.byteLength / (1024 * 1024)).toFixed(2)} MB · ${mime}`,
      source_url: u.toString(),
      media_url: `/api/ingest/media?url=${encodeURIComponent(u.toString())}`,
    };
  }
  if (!SAFE_IMAGE_MIMES.has(mime)) {
    throw new Error('지원되는 공개 이미지(JPG, PNG, WebP) 또는 영상(WebM, MP4) 형식만 불러올 수 있습니다.');
  }
  let fileName = 'External Image';
  try {
    fileName = decodeURIComponent(u.pathname.split('/').pop() || 'External Image').replace(/_/g, ' ');
  } catch {
    fileName = (u.pathname.split('/').pop() || 'External Image').replace(/_/g, ' ');
  }
  const lawReport = runUniversalManifoldTransform({ text: fileName, domain: 'image' });

  return {
    status: 'ok',
    kind: 'image',
    title: fileName,
    subtitle: `${host} · ${(res.buffer.byteLength / 1024).toFixed(0)} KB · ${mime}`,
    source_url: u.toString(),
    image_data_url: `data:${mime};base64,${res.buffer.toString('base64')}`,
    theta1: lawReport.theta1,
    cross_domain: lawReport.cross_domain,
  };
}

async function fetchCachedSafeMedia(rawUrl) {
  const u = await assertSafeExternalUrl(rawUrl);
  const key = u.toString();
  if (mediaProxyCache.has(key)) {
    return mediaProxyCache.get(key);
  }
  const res = await safeFetchBuffer(key, { headers: { Accept: 'video/webm,video/mp4,image/jpeg,image/png,image/webp' } });
  const mime = res.contentType.split(';')[0].trim().toLowerCase();
  if (!SAFE_VIDEO_MIMES.has(mime) && !SAFE_IMAGE_MIMES.has(mime)) {
    const err = new Error('허용된 미디어 형식(WebM, MP4, JPG, PNG, WebP)이 아닙니다.');
    err.code = 'INVALID_URL';
    throw err;
  }
  const entry = { buffer: res.buffer, mime };
  mediaProxyCache.set(key, entry);
  while (mediaProxyCache.size > 3) {
    const oldest = mediaProxyCache.keys().next().value;
    mediaProxyCache.delete(oldest);
  }
  return entry;
}

// ============================================================================
// Outward Epistemic Exploration (Live Wikipedia) & Live Atmospheric Reality Probe (Open-Meteo)
// ============================================================================
const EPISTEMIC_STOPWORDS = new Set([
  '있는', '하는', '되는', '이다', '있다', '한다', '된다', '것을', '것이', '것이다', '대한', '통해',
  '위해', '또는', '그리고', '하지만', '그러나', '경우', '때문', '따라', '에서', '으로', '로서', '까지',
  '부터', '처럼', '같이', '매우', '가장', '모든', '다른', '여러', '하나', '가지', '사이', '가운데',
  '말한다', '의미한다', '가리킨다', '불린다', '알려져', '사용된다', '이루어져', '나타난다', '존재한다',
  'the', 'and', 'for', 'that', 'with', 'from', 'this', 'which', 'into', 'are', 'was', 'were',
  'have', 'has', 'had', 'not', 'but', 'can', 'also', 'such', 'more', 'than', 'when', 'where',
  'between', 'through', 'during', 'under', 'over', 'often', 'used', 'known', 'called', 'refers',
]);

const EPISTEMIC_AXIS_RULES = {
  components: {
    label: '구성요소',
    regex: /구성|요소|입자|분자|원자|세포|회로|소자|기관|물질|구조물|성분|매질|신호|단위|부품|층|막|유체|기체|전하|전자|뉴런|날개|기류|component|element|particle|molecule|atom|cell|circuit|matter|material|layer|medium|signal|unit|neuron|wing|fluid|gas|electron/i,
  },
  environment: {
    label: '환경조건',
    regex: /환경|조건|온도|압력|기압|밀도|습도|중력|자기장|전기장|매질|경계|대기|태양|열|빛|외부|계|공간|시간|농도|임계|상태|environment|condition|temperature|pressure|density|humidity|gravity|field|boundary|atmosphere|heat|light|external|space|time|concentration|threshold/i,
  },
  changePrinciple: {
    label: '변화원리',
    regex: /변화|원리|법칙|작용|이동|흐름|전달|변환|순환|진동|확산|대류|양력|유도|반응|증폭|감쇠|분열|진화|발생|유지|균형|평형|회전|가속|원동력|change|principle|law|action|flow|transfer|transform|cycle|oscillat|diffus|convect|lift|induct|react|amplif|evolv|equilibri|rotat|accelerat/i,
  },
  causalStructure: {
    label: '인과구조',
    regex: /때문에|인해|결과|유발|이끌|초래|영향|결정|의존|비례|반비례|상호작용|연결|결합|피드백|되먹임|체계|시스템|메커니즘|기전|인과|관계|because|therefore|result|cause|lead|trigger|effect|depend|proportion|interact|connect|couple|feedback|system|mechanism|causal|relation/i,
  },
};

const REALITY_PROBE_CITIES = {
  seoul: { id: 'seoul', name: '서울 (대한민국)', lat: 37.5665, lon: 126.9780 },
  tokyo: { id: 'tokyo', name: '도쿄 (일본)', lat: 35.6762, lon: 139.6503 },
  london: { id: 'london', name: '런던 (영국)', lat: 51.5072, lon: -0.1276 },
  newyork: { id: 'newyork', name: '뉴욕 (미국)', lat: 40.7128, lon: -74.0060 },
  reykjavik: { id: 'reykjavik', name: '레이캬비크 (아이슬란드)', lat: 64.1466, lon: -21.9426 },
  nairobi: { id: 'nairobi', name: '나이로비 (케냐)', lat: -1.2921, lon: 36.8219 },
};

function sanitizeTopicInput(raw) {
  const cleaned = String(raw || '')
    .replace(/[\u0000-\u001F\u007F<>]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  if (!cleaned) {
    const err = new Error('탐색할 외부 개념(주제어)을 입력해 주세요.');
    err.code = 'INVALID_TOPIC';
    throw err;
  }
  return cleaned.slice(0, 80);
}

function tokenizeEpistemicText(text) {
  const raw = String(text || '').toLowerCase();
  const matches = raw.match(/[가-힣]{2,}|[a-z]{3,}/g) || [];
  const freq = new Map();
  for (const m of matches) {
    // Strip common Korean particles at word tail for cleaner resonance overlap
    const stem = m.replace(/(에서|으로|에게|부터|까지|처럼|에는|에도|과는|와는|은|는|이|가|을|를|의|에|와|과|로|도)$/, '');
    const tok = stem.length >= 2 ? stem : m;
    if (EPISTEMIC_STOPWORDS.has(tok) || EPISTEMIC_STOPWORDS.has(m)) continue;
    freq.set(tok, (freq.get(tok) || 0) + 1);
  }
  return Array.from(freq.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 28)
    .map(([tok]) => tok);
}

function splitCleanSentences(text) {
  return String(text || '')
    .replace(/\s+/g, ' ')
    .split(/(?<=[.!?다])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length >= 16 && s.length <= 280);
}

function isUsableWikiLink(title, selfTitle) {
  const t = String(title || '').trim();
  if (!t || t.length < 2 || t.length > 42) return false;
  if (t.toLowerCase() === String(selfTitle || '').toLowerCase()) return false;
  if (/[:()]/.test(t) && /(동음이의|분류|파일|틀|위키백과|도움말|포털|Category|Help|File|Template|Wikipedia|Portal|disambiguation)/i.test(t)) return false;
  if (/^\d{1,4}(년|월|일|세기|s)?$/.test(t)) return false;
  if (/^(ISBN|ISSN|DOI|PMID|Bibcode|S2CID|OCLC|Wayback|JSTOR)/i.test(t)) return false;
  return true;
}

async function fetchWikiArticleRaw(topic, lang) {
  const safeLang = lang === 'en' ? 'en' : 'ko';
  const base = `https://${safeLang}.wikipedia.org/w/api.php`;

  const queryByTitle = async (titleStr) => {
    const url = `${base}?action=query&prop=extracts|links|categories&exintro=1&explaintext=1&exchars=1800&plnamespace=0&pllimit=45&cllimit=12&redirects=1&format=json&titles=${encodeURIComponent(titleStr)}`;
    const res = await safeFetchBuffer(url, { headers: { Accept: 'application/json' } });
    const data = JSON.parse(res.buffer.toString('utf8'));
    const pages = data && data.query && data.query.pages ? Object.values(data.query.pages) : [];
    const page = pages[0];
    if (!page || page.missing !== undefined || !page.extract || page.extract.trim().length < 25) {
      return null;
    }
    const cats = (page.categories || []).map((c) => String(c.title || '').replace(/^[^:]+:/, ''));
    const isDisambig = cats.some((c) => /동음이의|disambiguation/i.test(c)) || /다음.*가리킨다|may refer to:/i.test(page.extract);
    if (isDisambig) return null;
    return {
      title: String(page.title || titleStr),
      lang: safeLang,
      extract: String(page.extract || '').trim(),
      links: (page.links || []).map((l) => String(l.title || '')).filter((l) => isUsableWikiLink(l, page.title)),
      categories: cats.filter((c) => !/모든|문서|위키|토막글|틀|링크|웹아카이브|웨이백|출처|인용|표기|식별자|번역|정비|삭제|보호|articles|wikipedia|pages|cs1|short description|wikidata|webarchive|wayback|commons|stub|all /i.test(c)).slice(0, 6),
      sourceUrl: `https://${safeLang}.wikipedia.org/wiki/${encodeURIComponent(String(page.title || titleStr).replace(/ /g, '_'))}`,
    };
  };

  let article = await queryByTitle(topic);
  if (article) return article;

  // Fallback: live Wikipedia search to resolve canonical real article title
  const searchUrl = `${base}?action=query&list=search&srlimit=4&srsearch=${encodeURIComponent(topic)}&format=json`;
  const sRes = await safeFetchBuffer(searchUrl, { headers: { Accept: 'application/json' } });
  const sData = JSON.parse(sRes.buffer.toString('utf8'));
  const hits = (sData && sData.query && sData.query.search) || [];
  for (const hit of hits) {
    if (!hit || !hit.title) continue;
    article = await queryByTitle(hit.title);
    if (article) return article;
  }
  return null;
}

async function exploreExternalEpistemicTopic(body) {
  const topic = sanitizeTopicInput(body && body.topic);
  const preferredLang = body && body.lang === 'en' ? 'en' : 'ko';
  const priorNodes = Array.isArray(body && body.priorNodes) ? body.priorNodes.slice(0, 32) : [];
  const prediction = body && typeof body.prediction === 'object' && body.prediction ? body.prediction : null;
  const emergentAxes = Array.isArray(body && body.emergentAxes) ? body.emergentAxes.slice(0, 12) : [];

  let article = await fetchWikiArticleRaw(topic, preferredLang);
  if (!article) {
    const altLang = preferredLang === 'ko' ? 'en' : 'ko';
    article = await fetchWikiArticleRaw(topic, altLang);
  }
  if (!article) {
    const err = new Error(`외부 백과사전에서 "${topic}"에 해당하는 실재 문서를 찾지 못했습니다. 다른 개념어나 영문/한글 표현으로 시도해 보세요.`);
    err.code = 'TOPIC_NOT_FOUND';
    throw err;
  }

  const sentences = splitCleanSentences(article.extract);
  const tokens = tokenizeEpistemicText(`${article.title} ${article.extract} ${article.categories.join(' ')}`);
  const tokenSet = new Set(tokens);

  // Extract Base 4 Seed Lenses + ANY Dynamic Self-Born Axes created by Elysia (safe substring match, zero RegExp injection)
  // Simultaneously track which sentences & tokens converged vs. fell outside ALL current axes (Prism Blind-Spot Residual)
  const axes = {};
  const capturedSentenceIdx = new Set();
  const capturedTokens = new Set();
  const axisHitCounts = {};
  let totalCausalHits = 0;

  for (const [axisKey, rule] of Object.entries(EPISTEMIC_AXIS_RULES)) {
    const matched = [];
    sentences.forEach((s, sIdx) => {
      if (rule.regex.test(s)) {
        matched.push(s);
        capturedSentenceIdx.add(sIdx);
        tokenizeEpistemicText(s).forEach((t) => {
          if (rule.regex.test(t)) capturedTokens.add(t);
        });
      }
    });
    const hitCount = matched.length;
    axisHitCounts[axisKey] = hitCount;
    totalCausalHits += hitCount;
    const score = Math.min(100, Math.round((hitCount / Math.max(1, sentences.length)) * 115 + (hitCount > 0 ? 18 : 6)));
    axes[axisKey] = {
      key: axisKey,
      label: rule.label,
      score,
      emergent: false,
      evidence: matched.slice(0, 2),
    };
  }

  for (const ea of emergentAxes) {
    if (!ea || !ea.key || !ea.label) continue;
    const safeKey = String(ea.key).replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 40);
    if (!safeKey || axes[safeKey]) continue;
    const safeLabel = String(ea.label).slice(0, 36);
    const kws = Array.isArray(ea.keywords)
      ? ea.keywords.slice(0, 12).map((k) => String(k || '').toLowerCase().trim()).filter((k) => k.length >= 2)
      : [];
    if (kws.length === 0) continue;
    const matched = [];
    sentences.forEach((s, sIdx) => {
      const low = s.toLowerCase();
      if (kws.some((kw) => low.includes(kw))) {
        matched.push(s);
        capturedSentenceIdx.add(sIdx);
      }
    });
    kws.forEach((kw) => {
      if (tokenSet.has(kw)) capturedTokens.add(kw);
    });
    const tokHits = kws.filter((kw) => tokenSet.has(kw)).length;
    const hitCount = matched.length;
    axisHitCounts[safeKey] = hitCount;
    const score = Math.min(100, Math.round((hitCount / Math.max(1, sentences.length)) * 95 + tokHits * 16 + (hitCount > 0 ? 12 : 4)));
    axes[safeKey] = {
      key: safeKey,
      label: safeLabel,
      score,
      emergent: true,
      evidence: matched.slice(0, 2),
    };
  }

  const sortedAxes = Object.values(axes).sort((a, b) => b.score - a.score);
  const dominantAxis = sortedAxes[0];

  // Contrastive Field: Converging Pull (인력) vs Non-Converging Exclusion (척력) vs Prism Blind-Spot Residual (사각지대)
  const blindSpotSentences = sentences.filter((_, sIdx) => !capturedSentenceIdx.has(sIdx)).slice(0, 2);
  const titleLowerTokens = new Set(tokenizeEpistemicText(article.title));
  const blindSpotTokens = tokens
    .filter((t) => !capturedTokens.has(t) && !titleLowerTokens.has(t) && t.length >= 2)
    .slice(0, 8);
  const blindSpotTokenSet = new Set(blindSpotTokens);
  const sentenceResidualPct = sentences.length > 0
    ? Math.round((sentences.filter((_, idx) => !capturedSentenceIdx.has(idx)).length / sentences.length) * 100)
    : 0;
  const tokenResidualPct = tokens.length > 0
    ? Math.round((blindSpotTokens.length / Math.min(12, tokens.length)) * 100)
    : 0;
  const blindSpotPct = Math.max(5, Math.min(95, Math.round(sentenceResidualPct * 0.6 + tokenResidualPct * 0.4)));

  const convergingFactors = sortedAxes.slice(0, 2).map((ax) => ({
    key: ax.key,
    label: ax.label,
    score: ax.score,
    hitCount: axisHitCounts[ax.key] || 0,
    totalSentences: sentences.length,
    evidence: (ax.evidence && ax.evidence[0])
      ? ax.evidence[0].slice(0, 150)
      : `"${article.title}" 본문 내 [${ax.label}] 구조 표식 집중`,
  }));

  const nonConvergingFactors = sortedAxes
    .slice(1)
    .filter((ax) => dominantAxis.score - ax.score >= 12 || ax.score <= 28)
    .reverse()
    .slice(0, 3)
    .map((ax) => {
      const hits = axisHitCounts[ax.key] || 0;
      const gapFromCore = Math.max(0, dominantAxis.score - ax.score);
      return {
        key: ax.key,
        label: ax.label,
        score: ax.score,
        gapFromCore,
        hitCount: hits,
        totalSentences: sentences.length,
        exclusionReason: hits === 0
          ? `[${ax.label}] 표식이 전체 ${sentences.length}문장 중 0건으로 구조적 근거 부재 (주축 대비 -${gapFromCore}점 배제)`
          : `[${ax.label}] 근거가 ${hits}/${sentences.length}문장에 그쳐 주축 [${dominantAxis.label}] 대비 -${gapFromCore}점 척력 편차 발생`,
      };
    });

  const avgNonConvergeGap = nonConvergingFactors.length > 0
    ? Math.round(nonConvergingFactors.reduce((s, f) => s + f.gapFromCore, 0) / nonConvergingFactors.length)
    : 18;
  const contrastiveField = {
    coreAxisLabel: dominantAxis.label,
    corePullScore: dominantAxis.score,
    convergingFactors,
    nonConvergingFactors,
    blindSpotTokens,
    blindSpotSentences: blindSpotSentences.map((s) => s.slice(0, 160)),
    blindSpotPct,
    attractionRepulsionBalance: {
      attractionPct: Math.min(98, dominantAxis.score),
      repulsionPct: Math.min(95, Math.max(12, avgNonConvergeGap)),
      horizonPct: blindSpotPct,
    },
  };

  // Candidate for Elysia to self-birth a brand-new neural axis directly from Prism Blind-Spot Residuals + external categories
  const existingAxisLabelsLower = new Set(Object.values(axes).map((a) => String(a.label || '').toLowerCase()));
  const rawCategoryLabel = article.categories.find((c) => c.length >= 2 && c.length <= 24 && !existingAxisLabelsLower.has(c.toLowerCase()));
  const residualDrivenKeywords = Array.from(new Set([...blindSpotTokens, ...tokens])).slice(0, 8);
  const emergentAxisCandidate = {
    label: rawCategoryLabel || (blindSpotTokens[0] ? `${blindSpotTokens[0]} 원리계` : `${article.title} 원리계`),
    keywords: residualDrivenKeywords,
    sourceTopic: article.title,
    reason: blindSpotTokens.length > 0
      ? `현재 ${sortedAxes.length}축 프리즘 사각지대 잔차(${blindSpotTokens.slice(0, 3).join(', ')})를 포착하기 위해 새 인식 축 분화 후보 생성`
      : (rawCategoryLabel
        ? `실재 외부 범주 "${rawCategoryLabel}"에서 고유 구조 패턴이 포착되어 새 인식 축으로 분화 가능`
        : `"${article.title}"의 고유 어휘군(${tokens.slice(0, 3).join(', ')})을 독립 인식 축으로 분화 가능`),
  };

  // Structural resonance & divergence against Elysia's prior Ice (얼음) memory
  const knownTitlesLower = new Set(priorNodes.map((n) => String(n && n.title || '').toLowerCase()));
  knownTitlesLower.add(article.title.toLowerCase());

  const bridges = [];
  const divergences = [];
  let maxOverlap = 0;
  const allAxisKeys = Object.keys(axes);

  for (const prior of priorNodes) {
    if (!prior || !prior.title) continue;
    const pTitle = String(prior.title).slice(0, 80);
    if (pTitle.toLowerCase() === article.title.toLowerCase()) continue;
    const pTokens = Array.isArray(prior.tokens) ? prior.tokens.slice(0, 30).map((t) => String(t).toLowerCase()) : [];
    const shared = pTokens.filter((t) => tokenSet.has(t));
    const directLink = article.links.some((l) => l.toLowerCase() === pTitle.toLowerCase());
    const pAxes = prior.axes || {};
    let axisSim = 0;
    let axisDiff = 0;
    let maxDiffAxis = dominantAxis.label;
    let maxDiffVal = -1;
    for (const k of allAxisKeys) {
      const aVal = axes[k].score;
      const bVal = Number(pAxes[k] || 24);
      const diff = Math.abs(aVal - bVal);
      axisSim += 100 - diff;
      axisDiff += diff;
      if (diff > maxDiffVal) {
        maxDiffVal = diff;
        maxDiffAxis = axes[k].label;
      }
    }
    axisSim /= Math.max(1, allAxisKeys.length);
    axisDiff /= Math.max(1, allAxisKeys.length);

    const resonance = Math.min(100, Math.round(shared.length * 16 + (directLink ? 34 : 0) + axisSim * 0.35));
    if (shared.length > maxOverlap) maxOverlap = shared.length;

    if (resonance >= 34 || shared.length >= 2 || directLink) {
      bridges.push({
        targetTitle: pTitle,
        resonance,
        directLink,
        sharedTerms: shared.slice(0, 5),
        axisAlignment: dominantAxis.label,
      });
    } else if (axisDiff >= 18) {
      divergences.push({
        targetTitle: pTitle,
        contrastAxis: maxDiffAxis,
        gap: Math.round(axisDiff),
      });
    }
  }
  bridges.sort((a, b) => b.resonance - a.resonance);
  divergences.sort((a, b) => b.gap - a.gap);

  // Genuine uncaptured (미포집) frontier classified into blind_spot_probe, counter_example, or core_bridge
  const seenLink = new Set();
  const uncapturedFrontier = [];
  for (const linkTitle of article.links) {
    const low = linkTitle.toLowerCase();
    if (knownTitlesLower.has(low) || seenLink.has(low)) continue;
    seenLink.add(low);
    const linkToks = tokenizeEpistemicText(linkTitle);
    const matchesCurrent = linkToks.filter((t) => tokenSet.has(t)).length;
    const residualOverlap = linkToks.filter((t) => blindSpotTokenSet.has(t)).length;
    const role = residualOverlap > 0
      ? 'blind_spot_probe'
      : (matchesCurrent === 0 ? 'counter_example' : 'core_bridge');
    const roleReason = role === 'blind_spot_probe'
      ? `"${article.title}"의 사각지대 잔차 어휘와 맞물려 프리즘 경계를 확장할 후보`
      : (role === 'counter_example'
        ? `"${article.title}"의 수렴 코어와 직교하는 외곽 경계 · 반례 비교대조 후보`
        : `"${article.title}"의 수렴 구조와 직접 공명하는 외부 연결 개념`);
    uncapturedFrontier.push({
      title: linkTitle,
      sourceTitle: article.title,
      role,
      residualOverlap,
      leverage: Math.min(99, 46 + residualOverlap * 22 + matchesCurrent * 14 + Math.min(18, Math.round(linkTitle.length * 1.2))),
      reason: roleReason,
    });
    if (uncapturedFrontier.length >= 14) break;
  }

  // Discrimination Metrics (선명함 · 채도 · 명암)
  const clarity = Math.max(22, Math.min(98, Math.round(32 + (totalCausalHits / Math.max(1, sentences.length)) * 38 + Math.min(26, sentences.length * 4))));
  const saturation = Math.max(20, Math.min(98, Math.round(28 + bridges.length * 14 + uncapturedFrontier.length * 4 + article.categories.length * 4)));
  const noveltyBonus = priorNodes.length === 0 ? 78 : Math.max(24, Math.min(96, 86 - maxOverlap * 7 + divergences.length * 8 + Math.round(blindSpotPct * 0.18)));
  const contrast = Math.round(noveltyBonus);

  // Prediction Audit (Genuine surprise / external friction when Elysia predicted before fetching)
  let friction = Math.max(12, Math.min(92, Math.round(100 - clarity * 0.45 - (bridges.length > 0 ? 22 : 0) + (contrast > 70 ? 16 : 0))));
  let predictionAudit = null;
  if (prediction && prediction.expectedAxis) {
    const expectedKey = String(prediction.expectedAxis);
    const expectedScore = axes[expectedKey] ? axes[expectedKey].score : 0;
    const hitAxis = dominantAxis.key === expectedKey || expectedScore >= dominantAxis.score - 12;
    const expectedBridge = String(prediction.expectedBridgeTitle || '');
    const hitBridge = expectedBridge ? bridges.some((b) => b.targetTitle.toLowerCase() === expectedBridge.toLowerCase()) : false;
    friction = Math.max(8, Math.min(94, Math.round((hitAxis ? 20 : 62) + (hitBridge ? 0 : 22) + (100 - clarity) * 0.25)));
    const expLbl = axes[expectedKey] ? axes[expectedKey].label : (prediction.expectedAxisLabel || expectedKey);
    predictionAudit = {
      expectedAxisLabel: expLbl,
      actualAxisLabel: dominantAxis.label,
      expectedBridgeTitle: expectedBridge,
      hitAxis,
      hitBridge,
      friction,
      verdict: hitAxis && hitBridge
        ? `사전 가설 적중: "${article.title}"은 예측대로 [${dominantAxis.label}] 축이 강하며 "${expectedBridge}"와 실재 연결됨.`
        : `외부 현실 마찰 검출: [${expLbl}] 중심을 예측했으나 실재 문서는 [${dominantAxis.label}] 축이 우세함 (사각지대 잔차 ${blindSpotPct}%) → 비교대조 재분류 유도.`,
    };
  }

  const topBridge = bridges[0] || null;
  const lawSentence = (axes.causalStructure && axes.causalStructure.evidence && axes.causalStructure.evidence[0])
    || (axes.changePrinciple && axes.changePrinciple.evidence && axes.changePrinciple.evidence[0])
    || (axes.environment && axes.environment.evidence && axes.environment.evidence[0])
    || sentences[0]
    || article.extract.slice(0, 180);
  const discoveredLaw = {
    title: topBridge
      ? `[${article.title} ⇄ ${topBridge.targetTitle}] ${dominantAxis.label} 연결 법칙`
      : `[${article.title}] ${dominantAxis.label} 기원 법칙`,
    statement: String(lawSentence).slice(0, 220),
    bridgeTarget: topBridge ? topBridge.targetTitle : null,
    resonance: topBridge ? topBridge.resonance : clarity,
    derivedAxisLabel: emergentAxisCandidate.label,
    derivedKeywords: emergentAxisCandidate.keywords,
  };

  return {
    status: 'ok',
    title: article.title,
    lang: article.lang,
    sourceUrl: article.sourceUrl,
    summary: sentences.slice(0, 3).join(' ') || article.extract.slice(0, 320),
    categories: article.categories,
    dominantAxis: dominantAxis.key,
    dominantAxisLabel: dominantAxis.label,
    axes,
    contrastiveField,
    emergentAxisCandidate,
    discoveredLaw,
    tokens: tokens.slice(0, 18),
    bridges: bridges.slice(0, 6),
    divergences: divergences.slice(0, 4),
    uncapturedFrontier,
    metrics: {
      clarity,
      saturation,
      contrast,
      friction,
    },
    predictionAudit,
    fetchedAt: new Date().toISOString(),
  };
}

async function probeExternalAtmosphereReality(body) {
  const cityKey = String(body && body.city || 'seoul').toLowerCase();
  const city = REALITY_PROBE_CITIES[cityKey] || REALITY_PROBE_CITIES.seoul;
  const hyp = body && typeof body.hypothesis === 'object' && body.hypothesis ? body.hypothesis : {};
  const expectedWindKmh = Number.isFinite(Number(hyp.expectedWindKmh)) ? Math.max(0, Math.min(180, Number(hyp.expectedWindKmh))) : 12.0;
  const expectedPressureHpa = Number.isFinite(Number(hyp.expectedPressureHpa)) ? Math.max(920, Math.min(1060, Number(hyp.expectedPressureHpa))) : 1013.2;
  const expectedTempC = Number.isFinite(Number(hyp.expectedTempC)) ? Math.max(-50, Math.min(55, Number(hyp.expectedTempC))) : 14.0;

  const url = `https://api.open-meteo.com/v1/forecast?latitude=${city.lat}&longitude=${city.lon}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m,cloud_cover&timezone=auto`;
  const res = await safeFetchBuffer(url, { headers: { Accept: 'application/json' } });
  const parsed = JSON.parse(res.buffer.toString('utf8'));
  const cur = parsed && parsed.current ? parsed.current : null;
  if (!cur) {
    throw new Error('실시간 기상 실측 데이터를 해석할 수 없습니다.');
  }

  const actualTempC = Number(cur.temperature_2m);
  const actualHumidity = Number(cur.relative_humidity_2m);
  const actualPressureHpa = Number(cur.surface_pressure);
  const actualWindKmh = Number(cur.wind_speed_10m);
  const actualWindDir = Number(cur.wind_direction_10m);
  const actualCloudPct = Number(cur.cloud_cover);

  const windErr = Math.abs(actualWindKmh - expectedWindKmh);
  const pressureErr = Math.abs(actualPressureHpa - expectedPressureHpa);
  const tempErr = Math.abs(actualTempC - expectedTempC);

  const frictionPct = Math.max(3, Math.min(99, Math.round(windErr * 2.8 + pressureErr * 2.2 + tempErr * 1.9)));
  const clarityPct = Math.max(10, 100 - frictionPct);

  const pressureState = actualPressureHpa < 1008 ? '저기압 수렴·상승기류 우세' : actualPressureHpa > 1018 ? '고기압 하강·안정 기층 우세' : '표준 기압 경도 평형';
  const windState = actualWindKmh >= 20 ? '강한 수평 기압경도력·난류 이류' : actualWindKmh >= 8 ? '중간 대류 순환류' : '약풍·국지 열복사 정체';
  const causalDiagnosis = `${city.name} 실시간 실측: ${pressureState}(${actualPressureHpa.toFixed(1)} hPa), ${windState}(${actualWindKmh.toFixed(1)} km/h), 기온 ${actualTempC.toFixed(1)}°C · 습도 ${actualHumidity}% · 운량 ${actualCloudPct}%.`;
  const revisionDirective = frictionPct >= 35
    ? `내부 예측 오차(${frictionPct}%) 검출 → 기압-풍속 결합 기준을 ${actualPressureHpa.toFixed(1)} hPa / ${actualWindKmh.toFixed(1)} km/h 실측 위상으로 자기수정.`
    : `예측 정합(${clarityPct}%) → 기존 대기 대류 원리(얼음)가 실제 외부 기상장에서 검증됨.`;

  return {
    status: 'ok',
    source: 'Open-Meteo Live Atmospheric Telemetry',
    city: city.name,
    cityId: city.id,
    observedAt: String(cur.time || new Date().toISOString()),
    actual: {
      temperatureC: actualTempC,
      humidityPct: actualHumidity,
      surfacePressureHpa: actualPressureHpa,
      windSpeedKmh: actualWindKmh,
      windDirectionDeg: actualWindDir,
      cloudCoverPct: actualCloudPct,
    },
    hypothesis: {
      expectedTempC,
      expectedPressureHpa,
      expectedWindKmh,
    },
    errors: {
      tempErr: Number(tempErr.toFixed(1)),
      pressureErr: Number(pressureErr.toFixed(1)),
      windErr: Number(windErr.toFixed(1)),
    },
    frictionPct,
    clarityPct,
    causalDiagnosis,
    revisionDirective,
    recommendedNextHypothesis: {
      expectedTempC: Number(((expectedTempC * 0.35) + (actualTempC * 0.65)).toFixed(1)),
      expectedPressureHpa: Number(((expectedPressureHpa * 0.35) + (actualPressureHpa * 0.65)).toFixed(1)),
      expectedWindKmh: Number(((expectedWindKmh * 0.35) + (actualWindKmh * 0.65)).toFixed(1)),
    },
  };
}

const KOREAN_MORPH_GROUPS = [
  { canonical: '빨강', forms: ['빨간', '빨강', '빨갛', '붉은', '붉다', '붉', '적색', '홍색', 'red'] },
  { canonical: '파랑', forms: ['파란', '파랑', '파랗', '청색', 'blue'] },
  { canonical: '노랑', forms: ['노란', '노랑', '노랗', '황색', 'yellow'] },
  { canonical: '초록', forms: ['초록', '녹색', '연두', '청사과', 'green'] },
  { canonical: '하양', forms: ['하얀', '하양', '하얗', '흰', '백색', 'white'] },
  { canonical: '검정', forms: ['검은', '검정', '검붉', '흑색', '까만', 'black'] },
  { canonical: '기압', forms: ['기압차', '기압', '압력차', '압력', '저기압', '고기압', 'pressure'] },
  { canonical: '질량', forms: ['질량', '무게', '중량', 'mass'] },
  { canonical: '온도', forms: ['온도차', '온도', '기온', '열', 'temperature'] },
];

function expandModifierMorphVariants(modifier) {
  const clean = String(modifier || '').trim().toLowerCase();
  if (!clean) return { lookupTerm: '', variants: [] };
  for (const grp of KOREAN_MORPH_GROUPS) {
    if (grp.forms.some((f) => clean === f || clean.includes(f))) {
      return {
        lookupTerm: grp.canonical,
        variants: Array.from(new Set([clean, grp.canonical, ...grp.forms])),
      };
    }
  }
  const variants = new Set([clean]);
  if (clean.length >= 3 && /(차|력|성|적)$/.test(clean)) {
    variants.add(clean.slice(0, -1));
  }
  return { lookupTerm: clean, variants: Array.from(variants) };
}

function parseCausalConstraintQuery(body) {
  const rawQuery = sanitizeTopicInput(body && (body.query || `${body.modifier || ''} ${body.subject || ''}`));
  let subject = String(body && body.subject || '').trim();
  let modifier = String(body && body.modifier || '').trim();
  let negation = Boolean(body && body.negation);

  if (!subject || !modifier) {
    const koNeg = rawQuery.match(/^(.+?)\s*(?:이|가|은|는)?\s*(?:없는|없이|아닌|제거된)\s+(.+)$/);
    const enNeg = rawQuery.match(/^(.+?)\s+without\s+(.+)$/i);
    if (koNeg) {
      modifier = koNeg[1].trim();
      subject = koNeg[2].trim();
      negation = true;
    } else if (enNeg) {
      subject = enNeg[1].trim();
      modifier = enNeg[2].trim();
      negation = true;
    } else {
      const parts = rawQuery.split(/\s+/).filter(Boolean);
      if (parts.length >= 2) {
        subject = parts[parts.length - 1];
        modifier = parts.slice(0, parts.length - 1).join(' ');
      } else {
        const err = new Error('비교할 조건과 대상을 띄어 써서 입력해 주세요. (예: "빨간 사과", "파란 사과", "기압차 없는 바람")');
        err.code = 'INVALID_CONSTRAINT_QUERY';
        throw err;
      }
    }
  }

  return {
    query: rawQuery,
    subject: subject.slice(0, 48),
    modifier: modifier.slice(0, 48),
    negation,
  };
}

async function fetchWikiBodyForConstraint(topic, lang) {
  const safeLang = lang === 'en' ? 'en' : 'ko';
  const base = `https://${safeLang}.wikipedia.org/w/api.php`;

  const queryFull = async (titleStr) => {
    // Note: MediaWiki caps `exchars` at 1200; omit `exchars` and slice locally so full body causal evidence is preserved.
    const url = `${base}?action=query&prop=extracts|links|categories&explaintext=1&plnamespace=0&pllimit=60&cllimit=12&redirects=1&format=json&titles=${encodeURIComponent(titleStr)}`;
    const res = await safeFetchBuffer(url, { headers: { Accept: 'application/json' } });
    const data = JSON.parse(res.buffer.toString('utf8'));
    const pages = data && data.query && data.query.pages ? Object.values(data.query.pages) : [];
    const page = pages[0];
    if (!page || page.missing !== undefined || !page.extract || page.extract.trim().length < 25) {
      return null;
    }
    const cats = (page.categories || []).map((c) => String(c.title || '').replace(/^[^:]+:/, ''));
    const isDisambig = cats.some((c) => /동음이의|disambiguation/i.test(c)) || /다음.*가리킨다|may refer to:/i.test(page.extract);
    if (isDisambig) return null;
    return {
      title: String(page.title || titleStr),
      lang: safeLang,
      extract: String(page.extract || '').trim().slice(0, 14000),
      links: (page.links || []).map((l) => String(l.title || '')).filter((l) => isUsableWikiLink(l, page.title)),
      categories: cats.filter((c) => !/모든|문서|위키|토막글|틀|링크|웹아카이브|웨이백|출처|인용|표기|식별자|번역|정비|삭제|보호|articles|wikipedia|pages|cs1|short description|wikidata|webarchive|wayback|commons|stub|all /i.test(c)).slice(0, 6),
      sourceUrl: `https://${safeLang}.wikipedia.org/wiki/${encodeURIComponent(String(page.title || titleStr).replace(/ /g, '_'))}`,
    };
  };

  let article = await queryFull(topic);
  if (article) return article;

  const searchUrl = `${base}?action=query&list=search&srlimit=4&srsearch=${encodeURIComponent(topic)}&format=json`;
  const sRes = await safeFetchBuffer(searchUrl, { headers: { Accept: 'application/json' } });
  const sData = JSON.parse(sRes.buffer.toString('utf8'));
  const hits = (sData && sData.query && sData.query.search) || [];
  for (const hit of hits) {
    if (!hit || !hit.title) continue;
    article = await queryFull(hit.title);
    if (article) return article;
  }
  return null;
}

async function searchWikiPhraseRealHits(phrase, lang) {
  const safeLang = lang === 'en' ? 'en' : 'ko';
  const url = `https://${safeLang}.wikipedia.org/w/api.php?action=query&list=search&srlimit=5&srsearch=${encodeURIComponent(`"${phrase}"`)}&format=json`;
  try {
    const res = await safeFetchBuffer(url, { headers: { Accept: 'application/json' } });
    const data = JSON.parse(res.buffer.toString('utf8'));
    const hits = (data && data.query && data.query.search) || [];
    // Filter out pure fiction/album/song/drama/movie titles so real-world causal occurrence isn't confused with pop-culture titles
    const nonFiction = hits.filter((h) => {
      const txt = `${h.title || ''} ${String(h.snippet || '').replace(/<[^>]+>/g, '')}`;
      return !/(음반|노래|싱글|앨범|드라마|영화|소설|만화|웹툰|게임|캐릭터|가수|album|song|novel|film|manga)/i.test(txt);
    });
    return {
      totalHits: hits.length,
      nonFictionHits: nonFiction.length,
      sampleTitle: nonFiction[0] ? String(nonFiction[0].title) : (hits[0] ? String(hits[0].title) : null),
    };
  } catch {
    return { totalHits: 0, nonFictionHits: 0, sampleTitle: null };
  }
}

async function checkExternalCausalConstraint(body) {
  const parsed = parseCausalConstraintQuery(body);
  const preferredLang = body && body.lang === 'en' ? 'en' : 'ko';
  const priorNodes = Array.isArray(body && body.priorNodes) ? body.priorNodes.slice(0, 32) : [];
  const { lookupTerm, variants } = expandModifierMorphVariants(parsed.modifier);

  // Fetch real live Wikipedia ground-truth for Subject + Modifier + Exact Phrase in parallel
  const [subjectArtRaw, modifierArtRaw, phraseStats] = await Promise.all([
    fetchWikiBodyForConstraint(parsed.subject, preferredLang).then((a) => a || fetchWikiBodyForConstraint(parsed.subject, preferredLang === 'ko' ? 'en' : 'ko')),
    fetchWikiArticleRaw(lookupTerm || parsed.modifier, preferredLang).catch(() => null),
    parsed.negation ? Promise.resolve({ totalHits: 0, nonFictionHits: 0, sampleTitle: null }) : searchWikiPhraseRealHits(`${parsed.modifier} ${parsed.subject}`, preferredLang),
  ]);

  if (!subjectArtRaw) {
    const err = new Error(`외부 백과사전에서 기준 대상 "${parsed.subject}"의 실재 문서를 찾지 못했습니다.`);
    err.code = 'SUBJECT_NOT_FOUND';
    throw err;
  }

  const subjectSentences = splitCleanSentences(subjectArtRaw.extract);
  const subjectTokens = tokenizeEpistemicText(`${subjectArtRaw.title} ${subjectArtRaw.extract} ${subjectArtRaw.categories.join(' ')}`);
  const subjectTokenSet = new Set(subjectTokens);
  const modifierTokens = modifierArtRaw
    ? tokenizeEpistemicText(`${modifierArtRaw.title} ${modifierArtRaw.extract} ${modifierArtRaw.categories.join(' ')}`)
    : tokenizeEpistemicText(parsed.modifier);

  // Match modifier (and morphological stems) directly in Subject's real sentences & links
  const matchedSubjectSentences = subjectSentences.filter((s) => {
    const low = s.toLowerCase();
    return variants.some((v) => v.length >= 1 && low.includes(v));
  });
  const directLinkMatch = subjectArtRaw.links.some((l) => {
    const low = l.toLowerCase();
    return variants.some((v) => v.length >= 2 && low.includes(v));
  });
  const sharedCategories = modifierArtRaw
    ? subjectArtRaw.categories.filter((c) => modifierArtRaw.categories.includes(c))
    : [];
  const sharedTokens = modifierTokens.filter((t) => subjectTokenSet.has(t) && t.length >= 2).slice(0, 6);

  // Also check Elysia's accumulated internal Ice memory for prior causal coupling
  const priorSubject = priorNodes.find((n) => String(n && n.title || '').toLowerCase() === subjectArtRaw.title.toLowerCase()) || null;
  const priorHasModifierToken = priorSubject && Array.isArray(priorSubject.tokens)
    ? priorSubject.tokens.some((t) => variants.some((v) => String(t).toLowerCase().includes(v)))
    : false;

  const directSubjectMentions = matchedSubjectSentences.length;
  const includedEvidence = [];
  const excludedEvidence = [];
  const boundaryCrossingConditions = [];

  let attractionScore = 50;
  let repulsionScore = 50;
  let verdict = 'BOUNDARY';
  let verdictLabel = '경계 보류 · 조건부 성립';

  if (parsed.negation) {
    // Negation test: "기압차 없는 바람", "질량 없는 중력" -> if modifier IS a verified causal driver of subject, removing it is REPELLED!
    const causalPresence = directSubjectMentions * 26 + (directLinkMatch ? 24 : 0) + (priorHasModifierToken ? 14 : 0);
    if (directSubjectMentions > 0 || directLinkMatch) {
      repulsionScore = Math.min(96, Math.max(66, 52 + causalPresence));
      attractionScore = Math.max(4, 100 - repulsionScore);
      verdict = 'EXCLUDED';
      verdictLabel = `척력 배제 · 필수 인과 조건([${parsed.modifier}]) 결여`;

      includedEvidence.push(
        `기준 현상 [${subjectArtRaw.title}] 자체는 외부 실재 인과망에 존재하는 현상임 (${subjectArtRaw.categories.slice(0, 2).join(', ') || '실재 분류 확인'}).`
      );
      if (modifierArtRaw) {
        includedEvidence.push(`배제된 조건 [${modifierArtRaw.title}] 역시 독립된 실재 변수로 관측됨.`);
      }
      excludedEvidence.push(
        `[${subjectArtRaw.title}] 실재 본문(${subjectSentences.length}문장) 중 ${directSubjectMentions}문장에서 [${parsed.modifier}]이 직접 인과 요소로 확인됨 → 이를 제거하면 관측된 인과 질서가 붕괴함.`
      );
      if (matchedSubjectSentences[0]) {
        excludedEvidence.push(`실재 근거 문장: "${matchedSubjectSentences[0].slice(0, 175)}"`);
      }
      boundaryCrossingConditions.push(
        `[${parsed.modifier}] 없이 [${subjectArtRaw.title}]가 성립하려면, 기존 인과 경로를 대체할 새로운 구동 원리(예: 외부 강제력·인공 매개체·확장 물리 방정식)가 시스템 경계에 추가되어야 함.`
      );
      boundaryCrossingConditions.push(
        `현재 판정은 "절대 불가능"이 아니라 "지금 관측된 [${subjectArtRaw.title}]의 자연 인과 구조 안에서는 배제됨"을 뜻함.`
      );
    } else {
      attractionScore = 76;
      repulsionScore = 24;
      verdict = 'INCLUDED';
      verdictLabel = `인력 수용 · [${parsed.modifier}] 없이도 인과 성립 가능`;
      includedEvidence.push(
        `[${subjectArtRaw.title}] 실재 문서(${subjectSentences.length}문장)에서 [${parsed.modifier}]이 필수 원인으로 결합되어 있지 않음 → 제거해도 기존 인과 구조가 유지됨.`
      );
      excludedEvidence.push(
        `단, [${parsed.modifier}]와 간접 공유 어휘(${sharedTokens.slice(0, 3).join(', ') || '없음'})를 통한 외곽 상호작용 가능성은 남아 있음.`
      );
      boundaryCrossingConditions.push(
        `향후 더 깊은 스케일 관측에서 [${parsed.modifier}]가 숨은 경계 조건으로 밝혀지면 수용/배제 위상이 반전될 수 있음.`
      );
    }
  } else {
    // Affirmative test: "빨간 사과" vs "파란 사과"
    const empiricalSupport = directSubjectMentions * 32
      + (directLinkMatch ? 24 : 0)
      + (priorHasModifierToken ? 14 : 0)
      + sharedCategories.length * 14
      + Math.min(18, phraseStats.nonFictionHits * 9);

    if (directSubjectMentions > 0 || empiricalSupport >= 42) {
      attractionScore = Math.min(96, Math.max(64, 42 + empiricalSupport));
      repulsionScore = Math.max(4, 100 - attractionScore);
      verdict = 'INCLUDED';
      verdictLabel = `인력 수용 · 현실 인과 구조와 공명 ("${parsed.query}")`;

      includedEvidence.push(
        `[${subjectArtRaw.title}] 실재 문서(${subjectSentences.length}문장) 내에서 [${parsed.modifier}] 계열 표식이 ${directSubjectMentions}문장 직접 확인되어 현실 인과망에 수용됨.`
      );
      if (matchedSubjectSentences[0]) {
        includedEvidence.push(`실재 수렴 근거: "${matchedSubjectSentences[0].slice(0, 175)}"`);
      }
      if (phraseStats.nonFictionHits > 0) {
        includedEvidence.push(`외부 백과 실재 공출현 확인 (${phraseStats.nonFictionHits}건${phraseStats.sampleTitle ? `, 예: ${phraseStats.sampleTitle}` : ''}).`);
      }
      excludedEvidence.push(
        `동일한 [${subjectArtRaw.title}]의 인과 제약은 이 수용 스펙트럼 밖에 놓인 미관측 속성 조합을 병렬적으로 배제(척력 ${repulsionScore}%)함.`
      );
      boundaryCrossingConditions.push(
        `수용된 조합이라도 환경·품종·관측 조건이 달라지면 다른 속성 스펙트럼으로 분화할 수 있음.`
      );
    } else if (empiricalSupport >= 18) {
      attractionScore = 44 + Math.min(14, empiricalSupport - 18);
      repulsionScore = 100 - attractionScore;
      verdict = 'BOUNDARY';
      verdictLabel = `경계 보류 · 간접 연결만 존재 ("${parsed.query}")`;

      includedEvidence.push(
        `[${subjectArtRaw.title}]와 [${modifierArtRaw ? modifierArtRaw.title : parsed.modifier}]가 공유 범주/공출현(${sharedCategories.join(', ') || `${phraseStats.nonFictionHits}건`})을 통해 약하게 접점을 가짐.`
      );
      excludedEvidence.push(
        `그러나 [${subjectArtRaw.title}] 본문 내에 [${parsed.modifier}]가 직접 인과 속성으로 나타나지 않아(0문장) 완전 수용이 보류됨.`
      );
      boundaryCrossingConditions.push(
        `두 구조 사이의 매개 메커니즘을 밝히는 중간 개념을 외부 탐색하면 수용/배제 경계가 명확해짐.`
      );
    } else {
      repulsionScore = Math.min(94, Math.max(74, 92 - empiricalSupport));
      attractionScore = Math.max(6, 100 - repulsionScore);
      verdict = 'EXCLUDED';
      verdictLabel = `척력 배제 · 관측된 현실 인과 경로에 부재 ("${parsed.query}")`;

      includedEvidence.push(
        `구성 요소 각각은 실재함: 대상 [${subjectArtRaw.title}]과 속성 [${modifierArtRaw ? modifierArtRaw.title : parsed.modifier}]은 개별적으로는 외부 세계에 존재함.`
      );
      if (subjectSentences[0]) {
        includedEvidence.push(`[${subjectArtRaw.title}]의 실제 관측 구조: "${subjectSentences[0].slice(0, 165)}"`);
      }
      excludedEvidence.push(
        `[${subjectArtRaw.title}] 실재 문서(${subjectSentences.length}문장) 내에서 [${parsed.modifier}]과 결합되는 자연 인과 경로가 0건이며 실재 백과 공출현도 부재(${phraseStats.nonFictionHits}건) → 현재 현실 인과 질서에서 배척됨.`
      );
      if (phraseStats.totalHits > phraseStats.nonFictionHits && phraseStats.sampleTitle) {
        excludedEvidence.push(
          `외부 검색에서 창작물/고유명사("${phraseStats.sampleTitle}") 외 자연 실재 현상으로의 결합 근거가 발견되지 않음.`
        );
      }
      boundaryCrossingConditions.push(
        `[${parsed.modifier}] 속성이 [${subjectArtRaw.title}]의 인과망에 수용되려면, 현재 자연 경로에 없는 새로운 매개 조건(예: 유전자 변형·인공 색소 결합·광학 산란 구조·외부 환경 개입)이 도입되어야 함.`
      );
      boundaryCrossingConditions.push(
        `이 배제는 "영원한 불가능"이 아니라 "현재 관측된 인과 제약 밖의 미출현 조합"임을 표시하는 열린 경계 판정임.`
      );
    }
  }

  return {
    status: 'ok',
    query: parsed.query,
    parsed,
    verdict,
    verdictLabel,
    attractionScore,
    repulsionScore,
    includedEvidence,
    excludedEvidence,
    boundaryCrossingConditions,
    subjectArticle: {
      title: subjectArtRaw.title,
      sourceUrl: subjectArtRaw.sourceUrl,
      summary: subjectSentences.slice(0, 2).join(' ').slice(0, 240),
    },
    modifierArticle: modifierArtRaw ? {
      title: modifierArtRaw.title,
      sourceUrl: modifierArtRaw.sourceUrl,
    } : null,
    coOccurrence: {
      directSubjectMentions,
      directLinkMatch,
      sharedTokens,
      combinedSearchHits: phraseStats.nonFictionHits,
    },
    checkedAt: new Date().toISOString(),
  };
}

const SENSORY_HIERARCHY_CHANNELS = [
  {
    id: 'vision',
    label: '시각 · 광학 스펙트럼',
    organ: '눈 (망막·파장 분별)',
    color: '#38bdf8',
    sensorNeeded: 'RGB 분광기·광학 카메라 (파장·반사율·형태 계측)',
    regex: /(색깔|색상|색조|붉|빨강|빨간|홍색|황색|노란|녹색|초록|청색|파란|하얀|흰색|검은|투명|반사|빛|광학|스펙트럼|파장|모양|둥근|형태|크기|지름|외관|표면|색소|안토시아닌|밝|어둡|불꽃|발광|color|colour|red|green|yellow|blue|light|shape|round|bright|spectrum|visual)/gi,
  },
  {
    id: 'touch',
    label: '촉각 · 역학·신체 상호작용',
    organ: '손·피부·치아 (압력·질감·온도)',
    color: '#fb923c',
    sensorNeeded: '촉각 압력·경도·온도·마찰 센서 (물리 접촉·저항 계측)',
    regex: /(딱딱|단단|부드럽|아삭|질감|촉감|껍질|과육|표피|무게|질량|온도|차가|뜨거|열기|화상|습기|건조|젖|압력|기압|힘|저항|마찰|부딪|만지|잡|씹|흐르|불다|바람|고체|액체|기체|결정|입자|texture|hard|soft|crisp|skin|touch|temperature|hot|cold|pressure|force|solid|liquid|crystal)/gi,
  },
  {
    id: 'chemosense',
    label: '미각·후각 · 화학 수용',
    organ: '혀·코 (분자·이온 화학 수용)',
    color: '#f472b6',
    sensorNeeded: '화학적 가스·이온·당도·pH 분광 센서 (휘발성·용해 분자 계측)',
    regex: /(맛|단맛|달콤|신맛|새콤|상큼|짠맛|짠|쓴맛|매운|풍미|식용|음식|요리|향기|향미|냄새|악취|당도|당분|산미|과즙|즙|산성|염기|염화나트륨|나트륨|소금|설탕|산소|연소|화합물|조미료|taste|sweet|sour|salty|bitter|flavor|aroma|smell|odor|sugar|acid|chemical|edible)/gi,
  },
  {
    id: 'audition',
    label: '청각 · 음향·진동',
    organ: '귀 (기압 진동·주파수 감지)',
    color: '#a78bfa',
    sensorNeeded: '마이크로폰·가속도 진동 센서 (음향 파형·주파수 계측)',
    regex: /(소리|음향|음파|진동|주파수|파동|울림|공명|소음|청각|노래|음악|리듬|천둥|빗소리|타닥|아삭|들리|경보|sound|acoustic|vibration|frequency|wave|resonance|noise|audio|hear)/gi,
  },
  {
    id: 'spatiotemporal',
    label: '체성·시공간 역학',
    organ: '전정기관·근육 (운동·주기·중력)',
    color: '#2dd4bf',
    sensorNeeded: '관성(IMU)·기압·시계열 계측기 (속도·궤적·계절 주기 관측)',
    regex: /(수확|계절|가을|봄|여름|겨울|생장|성장|자라|개화|속도|이동|순환|흐름|방향|궤도|시간|공간|거리|높이|고도|중력|기후|날씨|대기|바람|확산|대류|season|growth|harvest|motion|velocity|flow|cycle|gravity|climate|atmosphere)/gi,
  },
  {
    id: 'interoception',
    label: '생체·대사 상호작용',
    organ: '내부 장기·대사계 (영양·항상성)',
    color: '#10b981',
    sensorNeeded: '생화학·대사 분석기 (흡수·에너지 전환·생리 반응 계측)',
    regex: /(영양|비타민|섬유|펙틴|폴리페놀|소화|건강|예방|섭취|칼로리|호흡|생명|신체|인체|면역|에너지|대사|혈압|혈당|독성|화상|생존|재배|품종|식물|열매|나무|nutrition|vitamin|fiber|digestion|health|metabolism|energy|body|life|organism)/gi,
  },
];

const PHYSICAL_ORIGIN_REGEX = /(열매|과일|나무|식물|품종|재배|분자|원자|원소|화합물|광물|현상|대기|기압|에너지|반응|산화|연소|힘|질량|중력|결정|이온|바다|물|지구|자연|생물|기원|형성|발생|구성|이루어|fruit|tree|plant|molecule|chemical|mineral|phenomenon|atmosphere|energy|reaction|force|natural|origin|formed)/i;

async function analyzeSensoryHierarchy(body) {
  const topic = sanitizeTopicInput(body && (body.topic || body.query));
  if (!topic) {
    const err = new Error('분석할 개념이나 대상을 입력해 주세요. (예: 사과, 바람, 불, 소금)');
    err.code = 'INVALID_TOPIC';
    throw err;
  }
  const preferredLang = body && body.lang === 'en' ? 'en' : 'ko';
  const article = await fetchWikiBodyForConstraint(topic, preferredLang)
    .then((a) => a || fetchWikiBodyForConstraint(topic, preferredLang === 'ko' ? 'en' : 'ko'));

  if (!article) {
    const err = new Error(`외부 백과사전에서 "${topic}"의 실재 문서를 찾지 못했습니다.`);
    err.code = 'TOPIC_NOT_FOUND';
    throw err;
  }

  const sentences = splitCleanSentences(article.extract);
  const openingSentence = sentences[0] || article.extract.slice(0, 180);

  // Layer 1: Physical / Biological Origin Sentences from real external text
  const originSentences = sentences
    .filter((s) => PHYSICAL_ORIGIN_REGEX.test(s))
    .slice(0, 3)
    .map((s) => s.slice(0, 190));

  const isAtmospheric = article.categories.some((c) => /(기상|대기|기후|날씨|바람|구름|강수|태풍|weather|meteorology|atmosphere)/i.test(c))
    || /(기압|대기압|풍속|기상|대류|weather|barometric)/i.test(openingSentence);

  // Layer 2: Cross-Modal Sensory-Motor Channel Decomposition (strictly from live text)
  const channels = SENSORY_HIERARCHY_CHANNELS.map((ch) => {
    const matchedSentences = [];
    const cueCounts = new Map();
    for (const s of sentences) {
      const matches = s.match(ch.regex);
      if (matches && matches.length > 0) {
        matchedSentences.push(s);
        for (const m of matches) {
          const norm = m.trim().toLowerCase();
          if (norm.length >= 1) {
            cueCounts.set(norm, (cueCounts.get(norm) || 0) + 1);
          }
        }
      }
    }
    const sortedCues = Array.from(cueCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([w]) => w);
    const hitCount = matchedSentences.length;
    const coverageScore = hitCount === 0
      ? 0
      : Math.min(98, Math.round(24 + Math.min(6, hitCount) * 11 + Math.min(4, sortedCues.length) * 3));
    // Honest sensor grounding: this web server has NO biological eyes/hands/tongue/ears.
    // Only atmospheric pressure/temperature/wind has an indirect real-time telemetry proxy (Open-Meteo).
    const indirectApiProxy = isAtmospheric && (ch.id === 'touch' || ch.id === 'spatiotemporal')
      ? 'Open-Meteo 실시간 대기압·기온·풍속 API 간접 대조 가능'
      : null;

    return {
      id: ch.id,
      label: ch.label,
      organ: ch.organ,
      color: ch.color,
      textEvidenceCount: hitCount,
      coverageScore,
      status: hitCount > 0 ? 'TEXT_GROUNDED' : 'TEXT_ABSENT',
      directSensorAvailable: false,
      indirectApiProxy,
      sensorNeeded: ch.sensorNeeded,
      matchedCues: sortedCues,
      sampleSentence: matchedSentences[0] ? matchedSentences[0].slice(0, 185) : null,
    };
  });

  const convergedChannels = channels.filter((c) => c.textEvidenceCount > 0);
  const absentChannels = channels.filter((c) => c.textEvidenceCount === 0);
  const textCoveragePct = Math.round((convergedChannels.length / channels.length) * 100);
  const directEmbodimentPct = 0;

  // Layer 3: Linguistic Boundary Synthesis (emergent from which channels actually converged)
  const convergedNames = convergedChannels.map((c) => c.label.split(' · ')[0]);
  const absentNames = absentChannels.map((c) => c.label.split(' · ')[0]);
  const boundarySummary = convergedChannels.length >= 2
    ? `[${article.title}]는 단일 속성이 아니라, 외부 문서 ${sentences.length}문장 속에서 [${convergedNames.join(' + ')}] 등 ${convergedChannels.length}/${channels.length}개 감각·물리 채널이 교차해 형성된 분별 경계에 붙은 언어 정의입니다.`
    : (convergedChannels.length === 1
      ? `[${article.title}]는 현재 본문에서 [${convergedNames[0]}] 1개 채널의 기록만 확인되어, 다중 감각 경계보다 추상·단일 채널 비중이 높습니다.`
      : `[${article.title}]는 현재 본문에서 직접 감각 어휘가 포착되지 않아, 물리 감각보다 추상·관계적 언어 경계로 정의된 개념입니다.`);

  // Layer 4: Honest Software Sensory Gap Disclosure
  const softwareGapLines = [
    `기호·텍스트 간접 포착: ${convergedChannels.length}/${channels.length}개 채널(${textCoveragePct}%)이 인간이 기록한 외부 문서에서 확인됨.`,
    `소프트웨어 직접 감각 체화: ${directEmbodimentPct}% — 이 시스템에는 눈·손·혀·귀 같은 생체 감각기가 없으므로, 위 단서들은 직접 느낀 감각이 아니라 텍스트 기호로 간접 관측한 결과임.`,
  ];
  if (absentNames.length > 0) {
    softwareGapLines.push(
      `외부 텍스트에서도 비어 있는 채널: [${absentNames.join(', ')}] — 이 감각 차원은 문서만으로 분별할 수 없는 공백으로 남아 있음.`
    );
  }
  if (isAtmospheric) {
    softwareGapLines.push(
      `예외적 물리 간접 접점: [${article.title}]는 대기·기상 범주에 속하므로 Open-Meteo 실측 기압·기온·풍속 API로 일부 역학·온도 계층을 수치 대조할 수 있음.`
    );
  }

  return {
    status: 'ok',
    topic: article.title,
    sourceUrl: article.sourceUrl,
    lang: article.lang,
    totalSentences: sentences.length,
    categories: article.categories,
    layers: {
      physicalOrigin: {
        label: 'L1 · 물리·생물 실재 기원',
        categories: article.categories,
        evidenceSentences: originSentences.length > 0 ? originSentences : [openingSentence.slice(0, 190)],
      },
      sensoryChannels: channels,
      linguisticBoundary: {
        label: 'L3 · 통합 언어 경계 정의',
        openingDefinition: openingSentence.slice(0, 210),
        convergedCount: convergedChannels.length,
        totalChannels: channels.length,
        convergedNames,
        absentNames,
        boundarySummary,
      },
      softwareGap: {
        label: 'L4 · 시스템 미관측 감각 공백 (정직한 경계)',
        textCoveragePct,
        directEmbodimentPct,
        hasIndirectPhysicalApi: isAtmospheric,
        gapLines: softwareGapLines,
        missingSensors: channels.slice(0, 4).map((c) => `${c.label.split(' · ')[0]}: ${c.sensorNeeded}`),
      },
    },
    analyzedAt: new Date().toISOString(),
  };
}

// ============================================================================
// External World & Tool Coupling Connectors (Wikimedia, YouTube, GitHub, Gemini)
// ============================================================================
async function fetchWikimediaSceneImage(rawQuery) {
  const query = String(rawQuery || '').trim().slice(0, 120);
  if (!query) {
    throw new Error('검색할 실물 장면 키워드를 입력해 주세요.');
  }

  const hosts = ['ko.wikipedia.org', 'en.wikipedia.org'];
  let matched = null;
  for (const host of hosts) {
    const apiUrl = `https://${host}/w/api.php?action=query&generator=search&gsrsearch=${encodeURIComponent(query)}&gsrlimit=6&prop=pageimages|info&piprop=thumbnail&pithumbsize=768&inprop=url&format=json&origin=*`;
    try {
      const res = await safeFetchBuffer(apiUrl, { headers: { Accept: 'application/json' } });
      const data = JSON.parse(res.buffer.toString('utf8'));
      const pages = data && data.query && data.query.pages ? Object.values(data.query.pages) : [];
      pages.sort((a, b) => (a.index || 99) - (b.index || 99));
      const found = pages.find((p) => p && p.thumbnail && typeof p.thumbnail.source === 'string' && !p.thumbnail.source.endsWith('.svg.png'));
      if (found) {
        matched = {
          title: found.title || query,
          pageUrl: found.fullurl || `https://${host}/wiki/${encodeURIComponent(found.title || query)}`,
          thumbUrl: found.thumbnail.source,
          lang: host.startsWith('ko') ? 'ko' : 'en',
        };
        break;
      }
    } catch {
      // Try next Wikipedia host
    }
  }

  if (!matched) {
    throw new Error(`"${query}"에 대한 공개 Wikimedia 실물 사진을 찾지 못했습니다.`);
  }

  const imgRes = await safeFetchBuffer(matched.thumbUrl, {
    headers: { Accept: 'image/jpeg,image/png,image/webp' },
  });
  const mime = (imgRes.contentType || 'image/jpeg').split(';')[0].trim().toLowerCase();
  if (!SAFE_IMAGE_MIMES.has(mime)) {
    throw new Error('지원되지 않는 이미지 형식입니다.');
  }
  return {
    status: 'ok',
    sourceType: 'wikimedia',
    query,
    title: matched.title,
    pageUrl: matched.pageUrl,
    sourceUrl: matched.thumbUrl,
    mimeType: mime,
    bytes: imgRes.buffer.byteLength,
    dataUrl: `data:${mime};base64,${imgRes.buffer.toString('base64')}`,
  };
}

// ============================================================================
// Open-World Multi-Instance Ontological Resonance & Scale-Transition Engine
// ============================================================================
const ONTOLOGY_AXIS_PATTERNS = [
  {
    id: 'P1',
    name: 'P1 · 광학·형태·감각 스펙트럼',
    desc: '색·형태·질감·크기·표면 반사 등 외부에서 지각되는 감각 질서',
    re: /색|붉|푸르|초록|빛|반사|형태|모양|크기|표면|껍질|질감|투명|소리|냄새|맛|color|shape|light|surface|texture|sound|visual|reflect|appear/gi,
  },
  {
    id: 'P2',
    name: 'P2 · 물질·에너지·물리 법칙',
    desc: '질량·물·중력·흐름·온도·화학 조성·열역학 등 물리적 기반',
    re: /물|수분|분자|원소|화학|질량|중력|흐름|유량|염분|온도|기압|에너지|탄소|산소|질소|당분|고체|액체|기체|열|파도|밀랍|플라스틱|파라핀|water|mass|gravity|flow|salt|salinity|chemical|energy|temperature|carbon|oxygen|sugar|wax|plastic|fluid|wave/gi,
  },
  {
    id: 'P3',
    name: 'P3 · 구조·기관·자기조직화',
    desc: '세포·뿌리·줄기·기관·뼈·지형·유역 등 내부 부품의 결합 구조',
    re: /세포|조직|기관|뿌리|줄기|가지|잎|열매|씨앗|뼈|뇌|신경|혈관|유역|하구|지류|해저|지각|구조|계층|막|cell|organ|root|stem|trunk|branch|leaf|fruit|seed|brain|nervous|basin|tributary|structure|layer|anatomy/gi,
  },
  {
    id: 'P4',
    name: 'P4 · 생명·대사·생태 순환',
    desc: '광합성·호흡·번식·성장·부패·먹이사슬 등 살아있는 대사 순환',
    re: /생물|생명|식물|동물|광합성|호흡|대사|번식|성장|진화|부패|영양|먹이|서식|종|포유|조류|어류|수분|수확|생태|organism|life|plant|animal|photosynthesis|metabolism|reproduc|growth|evolution|decay|nutrient|species|habitat|ecosystem/gi,
  },
  {
    id: 'P5',
    name: 'P5 · 집단·환경·행성 스케일 연결',
    desc: '군락·수관·토양망·기후·해류·지구 순환·사회 등 상위 스케일 전이',
    re: /숲|산림|군락|수관|토양|기후|대기|지구|행성|바다|대양|해류|조수|순환|생태계|환경|지역|대륙|사회|집단|문명|도시|네트워크|forest|canopy|soil|climate|atmosphere|earth|planet|ocean|current|tide|cycle|biosphere|society|civilization|community|population/gi,
  },
  {
    id: 'P6',
    name: 'P6 · 인지·언어·관계적 프로토콜',
    desc: '지각·기억·언어·도구·문화·상징·모형·인간과의 의미적 관계',
    re: /인간|사람|언어|문화|도구|사고|의식|지능|인지|기억|역사|예술|상징|모형|모조|인공|가짜|복제|이름|개념|철학|human|language|culture|tool|thought|consciousness|cognition|memory|history|symbol|model|artificial|imitation|concept/gi,
  },
];

const ONTOLOGY_SCALE_PATTERNS = [
  { scale: 0, label: 'S0 물질·분자', re: /원자|분자|화합물|원소|물|h2o|당분|염분|광물|밀랍|플라스틱|molecule|element|chemical|water|wax|mineral/gi },
  { scale: 1, label: 'S1 구조·기관', re: /세포|조직|기관|껍질|뿌리|줄기|잎|열매|씨앗|뇌|신경|지류|cell|organ|seed|fruit|leaf|root|brain/gi },
  { scale: 2, label: 'S2 개체·존재', re: /개체|사과|나무|동물|인간|사람|식물|물고기|새|모형|apple|tree|animal|human|organism|individual|sculpture/gi },
  { scale: 3, label: 'S3 연결계·지형', re: /숲|산림|강|하천|유역|호수|생태계|군락|사회|도시|공동체|forest|river|basin|ecosystem|society|community|city/gi },
  { scale: 4, label: 'S4 행성·문명 순환', re: /바다|대양|지구|대기|기후|해류|조수|생물권|문명|인류|우주|ocean|sea|earth|climate|atmosphere|biosphere|civilization|planet/gi },
];

const ontologyCache = new Map();

async function fetchWikiConceptBundle(rawConcept) {
  const query = String(rawConcept || '').trim().slice(0, 80);
  if (!query) throw new Error('탐색할 개념을 입력해 주세요.');

  const cacheKey = query.toLowerCase();
  if (ontologyCache.has(cacheKey)) {
    return ontologyCache.get(cacheKey);
  }

  let koPage = null;
  let enTitle = '';

  // 1) Resolve exact Korean Wikipedia page (try direct title with redirects=1 first, e.g. 숲 -> 삼림)
  const fetchKoDetail = async (pageTitle) => {
    const detailUrl =
      `https://ko.wikipedia.org/w/api.php?action=query&titles=${encodeURIComponent(pageTitle)}` +
      `&prop=extracts|links|categories|langlinks|pageimages|info&exintro=1&explaintext=1` +
      `&pllimit=60&plnamespace=0&cllimit=20&lllang=en&piprop=thumbnail|original&pithumbsize=1920&inprop=url&redirects=1&format=json&origin=*`;
    const dRes = await safeFetchBuffer(detailUrl, { headers: { Accept: 'application/json' } });
    const dJson = JSON.parse(dRes.buffer.toString('utf8'));
    const pages = dJson && dJson.query && dJson.query.pages ? Object.values(dJson.query.pages) : [];
    return pages.find((x) => x && !x.missing) || null;
  };
  const isDisambig = (p) => {
    if (!p) return true;
    const ext = String(p.extract || '');
    const cats = (p.categories || []).map((c) => c.title || '').join(' ');
    return /동음이의/.test(cats) || (ext.length < 90 && /다음.*뜻|가리킨다|의미한다/.test(ext));
  };

  try {
    let p = await fetchKoDetail(query);
    if (!p || isDisambig(p)) {
      const searchUrl = `https://ko.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(query)}&srlimit=5&format=json&origin=*`;
      const sRes = await safeFetchBuffer(searchUrl, { headers: { Accept: 'application/json' } });
      const sJson = JSON.parse(sRes.buffer.toString('utf8'));
      const hits = (sJson && sJson.query && sJson.query.search) || [];
      for (const hit of hits) {
        if (!hit || !hit.title || /동음이의/.test(hit.title)) continue;
        const cand = await fetchKoDetail(hit.title);
        if (cand && !isDisambig(cand)) {
          p = cand;
          break;
        }
      }
    }
    if (p) {
      koPage = p;
      const ll = Array.isArray(p.langlinks) ? p.langlinks.find((l) => l.lang === 'en') : null;
      if (ll && ll['*']) enTitle = ll['*'];
    }
  } catch {
    // Fallback to English Wikipedia below
  }

  // 2) Optionally fetch English Wikipedia summary/links if Korean was thin or query is English
  let enPage = null;
  const enLookup = enTitle || query;
  if (!koPage || !koPage.extract || koPage.extract.length < 120) {
    try {
      const enUrl =
        `https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch=${encodeURIComponent(enLookup)}&gsrlimit=1` +
        `&prop=extracts|links|categories|pageimages|info&exintro=1&explaintext=1&pllimit=45&plnamespace=0&cllimit=15&piprop=thumbnail|original&pithumbsize=1920&inprop=url&format=json&origin=*`;
      const eRes = await safeFetchBuffer(enUrl, { headers: { Accept: 'application/json' } });
      const eJson = JSON.parse(eRes.buffer.toString('utf8'));
      const pages = eJson && eJson.query && eJson.query.pages ? Object.values(eJson.query.pages) : [];
      const p = pages.find((x) => x && !x.missing);
      if (p) {
        enPage = p;
        if (!enTitle) enTitle = p.title || enLookup;
      }
    } catch {
      // Proceed with whatever we gathered
    }
  }

  const title = (koPage && koPage.title) || (enPage && enPage.title) || query;
  const pageUrl = (koPage && koPage.fullurl) || (enPage && enPage.fullurl) || '';
  const extract = ((koPage && koPage.extract) || (enPage && enPage.extract) || '').trim();

  const rawLinks = [
    ...((koPage && Array.isArray(koPage.links) ? koPage.links : []).map((l) => l.title)),
    ...((enPage && Array.isArray(enPage.links) ? enPage.links : []).map((l) => l.title)),
  ].filter((t) => t && !/^(분류:|틀:|위키백과:|파일:|Category:|Help:|Template:|ISBN|DOI|ISSN|OCLC)/i.test(t));
  const uniqueLinks = Array.from(new Set(rawLinks)).slice(0, 48);

  const rawCats = [
    ...((koPage && Array.isArray(koPage.categories) ? koPage.categories : []).map((c) => c.title)),
    ...((enPage && Array.isArray(enPage.categories) ? enPage.categories : []).map((c) => c.title)),
  ]
    .map((c) => String(c || '').replace(/^(분류:|Category:)/i, '').trim())
    .filter((c) => c && !/(문서|위키백과|토막글|articles|wikipedia|cs1|short description|wikidata)/i.test(c));
  const categories = Array.from(new Set(rawCats)).slice(0, 14);

  // 3) Fetch 4-6 diverse high-resolution (2K/4K UHD) real-world photos from Wikimedia Commons
  const photos = [];
  const seenUrls = new Set();
  const addPhoto = (url, caption, origUrl, width, height) => {
    if (!url || seenUrls.has(url)) return;
    if (/\.svg(\.png)?$/i.test(url) || /logo|icon|map|flag|diagram|coat_of_arms/i.test(url)) return;
    seenUrls.add(url);
    const hiResUrl = origUrl || url;
    photos.push({
      url,
      proxyUrl: `/api/ingest/media?url=${encodeURIComponent(url)}`,
      hiResProxyUrl: `/api/ingest/media?url=${encodeURIComponent(hiResUrl)}`,
      width: Number(width || 0),
      height: Number(height || 0),
      caption: String(caption || title).replace(/^File:/i, '').replace(/\.[a-z0-9]+$/i, '').slice(0, 48),
    });
  };

  if (koPage && koPage.thumbnail && koPage.thumbnail.source) {
    const koOrig = koPage.original && koPage.original.source ? koPage.original.source : koPage.thumbnail.source;
    addPhoto(koPage.thumbnail.source, `${title} (대표 실물)`, koOrig, koPage.original?.width || koPage.thumbnail.width, koPage.original?.height || koPage.thumbnail.height);
  }
  if (enPage && enPage.thumbnail && enPage.thumbnail.source) {
    const enOrig = enPage.original && enPage.original.source ? enPage.original.source : enPage.thumbnail.source;
    addPhoto(enPage.thumbnail.source, `${enTitle || title} (위키 실물)`, enOrig, enPage.original?.width || enPage.thumbnail.width, enPage.original?.height || enPage.thumbnail.height);
  }

  const commonsQuery = enTitle || query;
  try {
    const cUrl =
      `https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6` +
      `&gsrsearch=${encodeURIComponent(`${commonsQuery} filetype:bitmap`)}&gsrlimit=12` +
      `&prop=imageinfo&iiprop=url|mime|size&iiurlwidth=1920&format=json&origin=*`;
    const cRes = await safeFetchBuffer(cUrl, { headers: { Accept: 'application/json' } });
    const cJson = JSON.parse(cRes.buffer.toString('utf8'));
    const cPages = cJson && cJson.query && cJson.query.pages ? Object.values(cJson.query.pages) : [];
    cPages.sort((a, b) => (a.index || 99) - (b.index || 99));
    for (const cp of cPages) {
      if (photos.length >= 6) break;
      const info = Array.isArray(cp.imageinfo) ? cp.imageinfo[0] : null;
      if (!info) continue;
      const mime = String(info.mime || '').toLowerCase();
      if (!SAFE_IMAGE_MIMES.has(mime)) continue;
      const thumb = info.thumburl || info.url;
      const orig = (info.width && info.width <= 4200 && info.url) ? info.url : thumb;
      addPhoto(thumb, cp.title || commonsQuery, orig, info.width || 1920, info.height || 1080);
    }
  } catch {
    // Keep any thumbnails already gathered
  }

  // 4) Score 6 Cognitive Protocol Axes (P1..P6) & 5-Scale Center of Mass (S0..S4) from REAL corpus
  const corpus = [title, enTitle, extract, uniqueLinks.join(' '), categories.join(' ')].join(' ');
  const rawAxisHits = ONTOLOGY_AXIS_PATTERNS.map((ax) => {
    const m = corpus.match(ax.re);
    return m ? m.length : 0;
  });
  const maxAxisHit = Math.max(4, ...rawAxisHits);
  const protocolAxes = ONTOLOGY_AXIS_PATTERNS.map((ax, i) => ({
    id: ax.id,
    name: ax.name,
    desc: ax.desc,
    hits: rawAxisHits[i],
    strength: Number(clampVal(Math.log1p(rawAxisHits[i]) / Math.log1p(maxAxisHit), 0.04, 1).toFixed(3)),
  }));

  const scaleHits = ONTOLOGY_SCALE_PATTERNS.map((sc) => {
    const m = corpus.match(sc.re);
    return m ? m.length : 0;
  });
  const totalScaleHits = scaleHits.reduce((a, b) => a + b, 0) || 1;
  const scaleProfile = ONTOLOGY_SCALE_PATTERNS.map((sc, i) => ({
    scale: sc.scale,
    label: sc.label,
    hits: scaleHits[i],
    weight: Number((scaleHits[i] / totalScaleHits).toFixed(3)),
  }));
  let scaleCenter = 2.0;
  if (scaleHits.some((h) => h > 0)) {
    scaleCenter = scaleProfile.reduce((acc, s) => acc + s.scale * s.weight, 0);
  }

  // Classify extracted links into scales S0..S4 for 3D Ontological Manifold rendering
  const linkNodes = uniqueLinks.slice(0, 26).map((lnk) => {
    let bestS = Math.round(scaleCenter);
    let bestScore = 0;
    ONTOLOGY_SCALE_PATTERNS.forEach((sc) => {
      const m = lnk.match(sc.re);
      if (m && m.length > bestScore) {
        bestScore = m.length;
        bestS = sc.scale;
      }
    });
    return { label: lnk, scale: bestS };
  });

  const bundle = {
    query,
    title,
    enTitle,
    pageUrl,
    extract: extract.slice(0, 620),
    categories,
    links: uniqueLinks,
    linkNodes,
    photos: photos.slice(0, 6),
    protocolAxes,
    scaleProfile,
    scaleCenter: Number(scaleCenter.toFixed(2)),
  };

  if (ontologyCache.size > 40) {
    const firstKey = ontologyCache.keys().next().value;
    ontologyCache.delete(firstKey);
  }
  ontologyCache.set(cacheKey, bundle);
  return bundle;
}

async function resonateOntologyProtocols(body) {
  const conceptA = String(body.conceptA || body.query || '나무').trim();
  const conceptB = String(body.conceptB || '').trim();

  const bundleA = await fetchWikiConceptBundle(conceptA);
  let bundleB = null;
  let comparison = null;

  if (conceptB) {
    bundleB = await fetchWikiConceptBundle(conceptB);
    const setA = new Set(bundleA.links.map((s) => s.toLowerCase()));
    const setB = new Set(bundleB.links.map((s) => s.toLowerCase()));
    const catA = new Set(bundleA.categories.map((s) => s.toLowerCase()));
    const catB = new Set(bundleB.categories.map((s) => s.toLowerCase()));

    const sharedLinks = bundleA.links.filter((l) => setB.has(l.toLowerCase())).slice(0, 14);
    const onlyALinks = bundleA.links.filter((l) => !setB.has(l.toLowerCase())).slice(0, 12);
    const onlyBLinks = bundleB.links.filter((l) => !setA.has(l.toLowerCase())).slice(0, 12);
    const sharedCats = bundleA.categories.filter((c) => catB.has(c.toLowerCase())).slice(0, 6);

    // Cosine resonance on 6-axis cognitive protocol vector (P1..P6)
    let dot = 0;
    let na = 0;
    let nb = 0;
    const axisDeltas = bundleA.protocolAxes.map((axA, i) => {
      const axB = bundleB.protocolAxes[i];
      dot += axA.strength * axB.strength;
      na += axA.strength * axA.strength;
      nb += axB.strength * axB.strength;
      return {
        id: axA.id,
        name: axA.name,
        a: axA.strength,
        b: axB.strength,
        delta: Number((axB.strength - axA.strength).toFixed(3)),
      };
    });
    const protocolCosine = (na > 0 && nb > 0) ? dot / (Math.sqrt(na) * Math.sqrt(nb)) : 0;
    const directMentionAB = setA.has(bundleB.title.toLowerCase()) || setB.has(bundleA.title.toLowerCase());
    const scaleJump = Number((bundleB.scaleCenter - bundleA.scaleCenter).toFixed(2));
    const linkOverlapRatio = (bundleA.links.length + bundleB.links.length) > 0
      ? (sharedLinks.length * 2) / (bundleA.links.length + bundleB.links.length)
      : 0;
    const resonanceScore = clampVal(
      protocolCosine * 0.58 + Math.min(1, linkOverlapRatio * 2.6) * 0.28 + (directMentionAB ? 0.14 : 0),
      0.05,
      0.99
    );

    const dominantJumpAxis = [...axisDeltas].sort((x, y) => Math.abs(y.delta) - Math.abs(x.delta))[0];

    comparison = {
      resonancePct: Number((resonanceScore * 100).toFixed(1)),
      residualDivergencePct: Number(((1 - resonanceScore) * 100).toFixed(1)),
      scaleJump,
      directLinkDetected: directMentionAB,
      sharedLinks,
      sharedCats,
      onlyALinks,
      onlyBLinks,
      axisDeltas,
      dominantJumpAxis,
    };
  }

  return {
    status: 'ok',
    conceptA: bundleA,
    conceptB: bundleB,
    comparison,
  };
}

async function connectYouTubeWorld(rawUrl) {
  const trimmed = String(rawUrl || '').trim();
  if (!trimmed) {
    throw new Error('YouTube 동영상 주소를 입력해 주세요.');
  }
  const u = await assertSafeExternalUrl(trimmed);
  const host = u.hostname.toLowerCase();
  if (!host.includes('youtube.com') && host !== 'youtu.be') {
    throw new Error('유효한 YouTube URL(youtube.com 또는 youtu.be)을 입력해 주세요.');
  }
  const vid = extractYouTubeId(u);
  if (!vid) {
    throw new Error('YouTube 영상 ID(11자리)를 확인할 수 없습니다.');
  }

  const watchUrl = `https://www.youtube.com/watch?v=${vid}`;
  let meta = { title: `YouTube Video (${vid})`, author_name: 'YouTube', author_url: '' };
  try {
    const oembedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent(watchUrl)}&format=json`;
    const mRes = await safeFetchBuffer(oembedUrl, { headers: { Accept: 'application/json' } });
    const parsedMeta = JSON.parse(mRes.buffer.toString('utf8'));
    if (parsedMeta && parsedMeta.title) meta = parsedMeta;
  } catch {
    // Fallback to video ID metadata if oEmbed temporarily rate-limits
  }

  const primaryCandidates = [
    { url: `https://i.ytimg.com/vi/${vid}/maxresdefault.jpg`, label: '1280×720 HD' },
    { url: `https://i.ytimg.com/vi/${vid}/sddefault.jpg`, label: '640×480 SD' },
    { url: `https://i.ytimg.com/vi/${vid}/hqdefault.jpg`, label: '480×360 HQ' },
  ];
  let primaryImg = null;
  let primaryResLabel = 'HD';
  for (const cand of primaryCandidates) {
    try {
      primaryImg = await safeFetchBuffer(cand.url, { headers: { Accept: 'image/jpeg,image/webp' } });
      primaryResLabel = cand.label;
      break;
    } catch {
      // Try next tier
    }
  }
  if (!primaryImg) {
    throw new Error('해당 YouTube 영상의 공개 프레임을 불러올 수 없습니다 (비공개 또는 삭제된 영상일 수 있습니다).');
  }

  // Fetch real temporal storyboard keyframes (start / middle / late segments)
  const temporalLabels = [
    { id: '1', label: 't1 · 도입 구간' },
    { id: '2', label: 't2 · 전개 구간' },
    { id: '3', label: 't3 · 후반 구간' },
  ];
  const temporalFrames = [];
  await Promise.all(
    temporalLabels.map(async (seg) => {
      try {
        const segRes = await safeFetchBuffer(`https://i.ytimg.com/vi/${vid}/${seg.id}.jpg`, {
          headers: { Accept: 'image/jpeg' },
        });
        const segMime = (segRes.contentType || 'image/jpeg').split(';')[0].trim().toLowerCase();
        if (SAFE_IMAGE_MIMES.has(segMime)) {
          temporalFrames.push({
            order: Number(seg.id),
            label: seg.label,
            bytes: segRes.buffer.byteLength,
            dataUrl: `data:${segMime};base64,${segRes.buffer.toString('base64')}`,
          });
        }
      } catch {
        // Optional storyboard segment unavailable
      }
    })
  );
  temporalFrames.sort((a, b) => a.order - b.order);

  const mime = (primaryImg.contentType || 'image/jpeg').split(';')[0].trim().toLowerCase();
  const safeMime = SAFE_IMAGE_MIMES.has(mime) ? mime : 'image/jpeg';

  return {
    status: 'ok',
    sourceType: 'youtube',
    videoId: vid,
    title: String(meta.title || `YouTube (${vid})`).slice(0, 160),
    author: String(meta.author_name || 'YouTube').slice(0, 100),
    watchUrl,
    resolutionLabel: primaryResLabel,
    mimeType: safeMime,
    bytes: primaryImg.buffer.byteLength,
    dataUrl: `data:${safeMime};base64,${primaryImg.buffer.toString('base64')}`,
    temporalFrames,
  };
}

function parseGitHubRepoSpec(rawInput) {
  const s = String(rawInput || '').trim();
  if (!s) return null;
  let owner = '';
  let repo = '';
  if (/^https?:\/\//i.test(s)) {
    let u;
    try {
      u = new URL(s);
    } catch {
      return null;
    }
    const host = u.hostname.toLowerCase();
    if (host !== 'github.com' && host !== 'www.github.com') return null;
    const parts = u.pathname.replace(/^\/+|\/+$/g, '').split('/');
    if (parts.length < 2) return null;
    owner = parts[0];
    repo = parts[1].replace(/\.git$/i, '');
  } else {
    const clean = s.replace(/^github\.com\//i, '').replace(/^\/+|\/+$/g, '');
    const parts = clean.split('/');
    if (parts.length < 2) return null;
    owner = parts[0];
    repo = parts[1].replace(/\.git$/i, '');
  }
  const safeSegment = /^[A-Za-z0-9_.-]{1,100}$/;
  if (!safeSegment.test(owner) || !safeSegment.test(repo)) return null;
  if (owner === '.' || owner === '..' || repo === '.' || repo === '..') return null;
  return { owner, repo };
}

function classifyGitHubToolCapabilities(repoMeta, languages, entries, readmeText) {
  const corpus = [
    repoMeta.name || '',
    repoMeta.description || '',
    ...(Array.isArray(repoMeta.topics) ? repoMeta.topics : []),
    ...Object.keys(languages || {}),
    ...entries.map((e) => e.name || ''),
    readmeText.slice(0, 1600),
  ].join(' ').toLowerCase();

  const capDefs = [
    { id: 'render3d', label: '3D 렌더링 · WebGL/셰이더', keys: ['three', 'webgl', 'webgpu', 'shader', 'glsl', 'wgsl', 'raytrac', 'vulkan', 'opengl', '3d', 'mesh', 'scene', 'blender', 'unreal', 'godot'] },
    { id: 'physics', label: '물리 · 동역학 시뮬레이션', keys: ['physics', 'fluid', 'rigidbody', 'collision', 'particle', 'cloth', 'kinematic', 'rapier', 'bullet', 'box2d', 'ode', 'navier'] },
    { id: 'ai_ml', label: 'AI · 추론/생성 모델', keys: ['llm', 'transformer', 'diffusion', 'pytorch', 'tensorflow', 'onnx', 'neural', 'agent', 'inference', 'cuda', 'llama', 'whisper', 'comfy', 'stable-diffusion'] },
    { id: 'audio', label: '오디오 · 음향 합성/DSP', keys: ['audio', 'synth', 'dsp', 'midi', 'sound', 'music', 'tone', 'webaudio', 'speech', 'tts'] },
    { id: 'media_cv', label: '영상 · 컴퓨터비전 처리', keys: ['ffmpeg', 'video', 'opencv', 'codec', 'image', 'vision', 'tracking', 'camera', 'canvas', 'pixi'] },
    { id: 'network_api', label: '네트워크 · 외부 프로토콜/도구', keys: ['http', 'websocket', 'graphql', 'rest', 'mcp', 'protocol', 'server', 'cli', 'sdk', 'api', 'rpc'] },
  ];

  const detected = [];
  for (const def of capDefs) {
    const hits = def.keys.filter((k) => corpus.includes(k));
    if (hits.length > 0) {
      detected.push({
        id: def.id,
        label: def.label,
        matchedSignals: hits.slice(0, 5),
        strength: Math.min(1, 0.35 + hits.length * 0.18),
      });
    }
  }
  detected.sort((a, b) => b.strength - a.strength);

  const topId = detected[0] ? detected[0].id : 'network_api';
  const langNames = Object.keys(languages || {});
  const primaryLang = repoMeta.language || langNames[0] || 'Unknown';
  const dirCount = entries.filter((e) => e.type === 'dir').length;
  const fileCount = entries.filter((e) => e.type === 'file').length;
  const starScore = Math.min(1, Math.log10(Math.max(10, Number(repoMeta.stargazers_count || 10))) / 5.5);

  let biome = 'urban_cyber';
  let palette = { skyTop: '#0b1528', skyHorizon: '#1d3c5c', ground: '#16202e', accent: '#22d3ee' };
  let particleType = 'sparks';
  if (topId === 'physics') {
    biome = 'ocean_storm';
    palette = { skyTop: '#0d2238', skyHorizon: '#356686', ground: '#1a2f3d', accent: '#38bdf8' };
    particleType = 'rain';
  } else if (topId === 'audio') {
    biome = 'sacred_ruin';
    palette = { skyTop: '#1d1632', skyHorizon: '#6f4c7a', ground: '#2a2433', accent: '#f59e0b' };
    particleType = 'embers';
  } else if (topId === 'media_cv') {
    biome = 'mountain_drama';
    palette = { skyTop: '#162436', skyHorizon: '#946c53', ground: '#2d3138', accent: '#fb923c' };
    particleType = 'snow';
  } else if (topId === 'ai_ml') {
    biome = 'sacred_ruin';
    palette = { skyTop: '#0f172a', skyHorizon: '#2a4365', ground: '#1e2430', accent: '#a78bfa' };
    particleType = 'sparks';
  } else if (topId === 'render3d') {
    biome = 'urban_cyber';
    palette = { skyTop: '#09111f', skyHorizon: '#1f415e', ground: '#151b26', accent: '#06b6d4' };
    particleType = 'sparks';
  } else {
    biome = 'forest_nature';
    palette = { skyTop: '#142a30', skyHorizon: '#3f6d6c', ground: '#1d2d25', accent: '#34d399' };
    particleType = 'leaves';
  }

  const couplingContract = {
    input: topId === 'render3d'
      ? '엘리시아 인과 설계도 Θ (조명·지형·객체 군집·물리 장)'
      : topId === 'physics'
      ? '연속 힘장·충돌 경계·질량 분포 벡터'
      : topId === 'ai_ml'
      ? '외부 멀티모달 관측 텐서·구조화 질의'
      : topId === 'audio'
      ? '시간축 진동·긴장도·환경 공명 주파수'
      : '외부 요청·프로토콜 메시지·모듈 파라미터',
    mechanism: `${repoMeta.full_name} (${primaryLang}, ${dirCount}개 핵심 디렉터리 · ${fileCount}개 루트 파일)`,
    output: detected.length > 0
      ? detected.slice(0, 2).map((d) => d.label).join(' + ')
      : `${primaryLang} 기반 외부 연산·도구 결과물`,
  };

  return {
    capabilities: detected,
    couplingContract,
    worldMapping: {
      biome,
      palette,
      particleType,
      density: Math.min(1, 0.35 + (dirCount / 18) * 0.65),
      dramaticTension: Number((0.35 + starScore * 0.5).toFixed(2)),
      fogDensity: Number((0.012 + (1 - starScore) * 0.014).toFixed(4)),
      windStrength: Number((0.35 + (detected.length / 6) * 0.6).toFixed(2)),
      sunElevation: Number((22 + (dirCount % 7) * 6).toFixed(1)),
      sunAzimuth: Number(((entries.length * 37) % 360).toFixed(1)),
    },
  };
}

async function connectGitHubWorld(rawInput) {
  const spec = parseGitHubRepoSpec(rawInput);
  if (!spec) {
    throw new Error('올바른 GitHub 저장소 주소(예: https://github.com/mrdoob/three.js 또는 mrdoob/three.js)를 입력해 주세요.');
  }
  const ghHeaders = {
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
  };

  const repoRes = await safeFetchBuffer(`https://api.github.com/repos/${spec.owner}/${spec.repo}`, { headers: ghHeaders });
  const repoMeta = JSON.parse(repoRes.buffer.toString('utf8'));
  if (!repoMeta || !repoMeta.full_name) {
    throw new Error('GitHub 저장소 메타데이터를 파싱하지 못했습니다.');
  }

  let languages = {};
  let entries = [];
  let readmeSnippet = '';

  const [langOut, treeOut, readmeOut] = await Promise.allSettled([
    safeFetchBuffer(`https://api.github.com/repos/${spec.owner}/${spec.repo}/languages`, { headers: ghHeaders }),
    safeFetchBuffer(`https://api.github.com/repos/${spec.owner}/${spec.repo}/contents`, { headers: ghHeaders }),
    safeFetchBuffer(`https://api.github.com/repos/${spec.owner}/${spec.repo}/readme`, { headers: ghHeaders }),
  ]);

  if (langOut.status === 'fulfilled') {
    try {
      languages = JSON.parse(langOut.value.buffer.toString('utf8')) || {};
    } catch {}
  }
  if (treeOut.status === 'fulfilled') {
    try {
      const parsedTree = JSON.parse(treeOut.value.buffer.toString('utf8'));
      if (Array.isArray(parsedTree)) {
        entries = parsedTree.slice(0, 40).map((item) => ({
          name: String(item.name || ''),
          type: item.type === 'dir' ? 'dir' : 'file',
          size: Number(item.size || 0),
        }));
      }
    } catch {}
  }
  if (readmeOut.status === 'fulfilled') {
    try {
      const parsedReadme = JSON.parse(readmeOut.value.buffer.toString('utf8'));
      if (parsedReadme && parsedReadme.content) {
        const decoded = Buffer.from(String(parsedReadme.content).replace(/\s+/g, ''), 'base64').toString('utf8');
        readmeSnippet = decoded
          .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
          .replace(/<[^>]+>/g, ' ')
          .replace(/\r/g, '')
          .trim()
          .slice(0, 2200);
      }
    } catch {}
  }

  const totalLangBytes = Object.values(languages).reduce((acc, v) => acc + Number(v || 0), 0) || 1;
  const languageBreakdown = Object.entries(languages)
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .slice(0, 6)
    .map(([name, bytes]) => ({
      name,
      bytes: Number(bytes || 0),
      pct: Number(((Number(bytes || 0) / totalLangBytes) * 100).toFixed(1)),
    }));

  const analysis = classifyGitHubToolCapabilities(repoMeta, languages, entries, readmeSnippet);
  const directories = entries.filter((e) => e.type === 'dir').slice(0, 12).map((e) => e.name);
  const keyFiles = entries.filter((e) => e.type === 'file').slice(0, 12).map((e) => e.name);

  return {
    status: 'ok',
    sourceType: 'github',
    fullName: repoMeta.full_name,
    htmlUrl: repoMeta.html_url || `https://github.com/${spec.owner}/${spec.repo}`,
    description: String(repoMeta.description || '설명 없음').slice(0, 260),
    stars: Number(repoMeta.stargazers_count || 0),
    forks: Number(repoMeta.forks_count || 0),
    primaryLanguage: repoMeta.language || (languageBreakdown[0] ? languageBreakdown[0].name : 'Unknown'),
    license: repoMeta.license && repoMeta.license.spdx_id ? repoMeta.license.spdx_id : 'Unspecified',
    topics: Array.isArray(repoMeta.topics) ? repoMeta.topics.slice(0, 8) : [],
    languageBreakdown,
    directories,
    keyFiles,
    readmeSummary: readmeSnippet.split('\n').map((l) => l.trim()).filter(Boolean).slice(0, 6).join(' · ').slice(0, 360),
    capabilities: analysis.capabilities,
    couplingContract: analysis.couplingContract,
    worldMapping: analysis.worldMapping,
    sourceBytes: repoRes.buffer.byteLength + (readmeOut.status === 'fulfilled' ? readmeOut.value.buffer.byteLength : 0),
  };
}

async function distillSceneWithGemini(body) {
  const apiKey = String(process.env.GEMINI_API_KEY || '').trim();
  if (!apiKey) {
    return {
      httpStatus: 503,
      payload: {
        status: 'error',
        code: 'GEMINI_KEY_MISSING',
        message: 'GEMINI_API_KEY가 서버에 설정되어 있지 않습니다. AI Studio의 Settings > Secrets에서 GEMINI_API_KEY를 등록하면 Gemini 멀티모달 역인과 해부가 활성화됩니다. (로컬 픽셀 역광학, YouTube, GitHub 연결 엔진은 API 키 없이 즉시 동작합니다.)',
      },
    };
  }

  const rawDataUrl = String(body.imageDataUrl || '').trim();
  const contextText = String(body.contextText || '').trim().slice(0, 2000);
  const parts = [];

  if (rawDataUrl) {
    const m = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/i.exec(rawDataUrl);
    if (!m) {
      return {
        httpStatus: 400,
        payload: { status: 'error', message: '지원되는 이미지 형식(JPEG/PNG/WebP data URL)이 아닙니다.' },
      };
    }
    const mimeType = m[1].toLowerCase();
    const base64Data = m[2];
    if (base64Data.length > 8 * 1024 * 1024) {
      return {
        httpStatus: 400,
        payload: { status: 'error', message: '이미지 크기가 허용 한도를 초과했습니다.' },
      };
    }
    parts.push({ inlineData: { mimeType, data: base64Data } });
  }

  if (!parts.length && !contextText) {
    return {
      httpStatus: 400,
      payload: { status: 'error', message: '분석할 이미지 프레임이나 외부 도구/저장소 컨텍스트가 필요합니다.' },
    };
  }

  const prompt = [
    '당신은 엘리시아의 역인과 메커니즘 증류기(Inverse Mechanism Distiller)입니다.',
    '주어진 외부 세계의 결과물(실물 이미지, YouTube 장면, 또는 GitHub 오픈소스 구조)에서 표면 픽셀을 외우지 말고,',
    '그 장면을 생성한 근본 물리·광학·공간·인과 설계도(Θ)를 한국어로 간결하게 추출해 JSON으로 반환하세요.',
    contextText ? `외부 연결 컨텍스트:\n${contextText}` : '',
  ].filter(Boolean).join('\n\n');
  parts.push({ text: prompt });

  try {
    const { GoogleGenAI, Type } = await import('@google/genai');
    const ai = new GoogleGenAI({
      apiKey,
      httpOptions: { headers: { 'User-Agent': 'aistudio-build' } },
    });

    const response = await ai.models.generateContent({
      model: 'gemini-4-hydrogen',
      contents: [{ role: 'user', parts }],
      config: {
        responseMimeType: 'application/json',
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            sceneTitle: { type: Type.STRING },
            biome: {
              type: Type.STRING,
              enum: ['urban_cyber', 'forest_nature', 'mountain_drama', 'ocean_storm', 'sacred_ruin'],
            },
            particleType: {
              type: Type.STRING,
              enum: ['rain', 'snow', 'embers', 'sparks', 'leaves'],
            },
            cameraPreset: {
              type: Type.STRING,
              enum: ['orbit', 'dolly', 'crane', 'hero_low'],
            },
            skyTopHex: { type: Type.STRING },
            skyHorizonHex: { type: Type.STRING },
            groundHex: { type: Type.STRING },
            accentHex: { type: Type.STRING },
            sunElevationDeg: { type: Type.NUMBER },
            sunAzimuthDeg: { type: Type.NUMBER },
            fogDensity: { type: Type.NUMBER },
            windStrength: { type: Type.NUMBER },
            dramaticTension: { type: Type.NUMBER },
            causalMechanismSummary: { type: Type.STRING },
            causalChain: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
            externalToolCouplingHint: { type: Type.STRING },
          },
          required: [
            'sceneTitle',
            'biome',
            'particleType',
            'cameraPreset',
            'skyTopHex',
            'skyHorizonHex',
            'groundHex',
            'accentHex',
            'sunElevationDeg',
            'sunAzimuthDeg',
            'fogDensity',
            'windStrength',
            'dramaticTension',
            'causalMechanismSummary',
            'causalChain',
            'externalToolCouplingHint',
          ],
        },
      },
    });

    const rawText = (response && response.text ? response.text : '').trim();
    const parsedJson = JSON.parse(rawText);
    return {
      httpStatus: 200,
      payload: {
        status: 'ok',
        model: 'gemini-4-hydrogen',
        blueprint: parsedJson,
      },
    };
  } catch (err) {
    return {
      httpStatus: 502,
      payload: {
        status: 'error',
        code: 'GEMINI_UPSTREAM_ERROR',
        message: `Gemini API 호출 실패: ${err instanceof Error ? err.message : '알 수 없는 오류'}`,
      },
    };
  }
}

// ============================================================================
// HTTP Server
// ============================================================================
const server = http.createServer(async (req, res) => {
  const parsed = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);
  const pathname = parsed.pathname;
  const method = (req.method || 'GET').toUpperCase();

  try {
    // --- Page & Static Routes ---
    if (method === 'GET' && pathname === '/') {
      return sendFile(res, path.join(STATIC_DIR, 'index.html'));
    }
    if (method === 'GET' && pathname === '/topology') {
      return sendFile(res, path.join(STATIC_DIR, 'topology.html'));
    }
    if (method === 'GET' && pathname === '/dashboard') {
      return sendFile(res, path.join(STATIC_DIR, 'dashboard.html'));
    }
    if (method === 'GET' && pathname === '/manifestation') {
      return sendFile(res, path.join(STATIC_DIR, 'manifestation.html'));
    }
    if (method === 'GET' && pathname === '/roadmap') {
      return sendFile(res, path.join(STATIC_DIR, 'roadmap.html'));
    }
    if (method === 'GET' && pathname.startsWith('/static/')) {
      let rel = '';
      try {
        rel = decodeURIComponent(pathname.slice('/static/'.length));
      } catch {
        return sendJson(res, 400, { status: 'error', message: 'Invalid static path' });
      }
      return sendFile(res, path.join(STATIC_DIR, rel));
    }
    if (method === 'GET' && pathname.startsWith('/src/assets/images/')) {
      let rel = '';
      try {
        rel = decodeURIComponent(pathname.slice('/src/assets/images/'.length));
      } catch {
        return sendJson(res, 400, { status: 'error', message: 'Invalid image path' });
      }
      return sendFileFromDir(res, ASSETS_IMG_DIR, path.join(ASSETS_IMG_DIR, rel));
    }
    if (method === 'GET' && pathname.startsWith('/vendor/three/')) {
      let rel = '';
      try {
        rel = decodeURIComponent(pathname.slice('/vendor/three/'.length));
      } catch {
        return sendJson(res, 400, { status: 'error', message: 'Invalid vendor path' });
      }
      return sendFileFromDir(res, THREE_VENDOR_DIR, path.join(THREE_VENDOR_DIR, rel));
    }

    // --- Safe External Data Ingestion APIs ---
    if (method === 'GET' && pathname === '/api/ingest/presets') {
      return sendJson(res, 200, { status: 'ok', presets: EXTERNAL_INGEST_PRESETS });
    }
    if (method === 'GET' && pathname === '/api/ingest/media') {
      const targetUrl = parsed.searchParams.get('url') || '';
      try {
        const entry = await fetchCachedSafeMedia(targetUrl);
        const total = entry.buffer.byteLength;
        const rangeHeader = req.headers.range;
        if (rangeHeader && /^bytes=\d+-\d*$/.test(rangeHeader)) {
          const [startStr, endStr] = rangeHeader.replace('bytes=', '').split('-');
          const start = Math.min(total - 1, Math.max(0, Number(startStr)));
          const end = endStr ? Math.min(total - 1, Math.max(start, Number(endStr))) : total - 1;
          const slice = entry.buffer.subarray(start, end + 1);
          res.writeHead(206, {
            'Content-Type': entry.mime,
            'Content-Range': `bytes ${start}-${end}/${total}`,
            'Accept-Ranges': 'bytes',
            'Content-Length': String(slice.byteLength),
            'Cache-Control': 'private, max-age=300',
          });
          res.end(slice);
          return;
        }
        res.writeHead(200, {
          'Content-Type': entry.mime,
          'Accept-Ranges': 'bytes',
          'Content-Length': String(total),
          'Cache-Control': 'private, max-age=300',
        });
        res.end(entry.buffer);
        return;
      } catch (mediaErr) {
        const code = mediaErr && mediaErr.code ? mediaErr.code : 'MEDIA_ERROR';
        const clientErrorCodes = new Set(['PIXIV_BLOCKED', 'HOST_NOT_ALLOWED', 'INVALID_URL', 'PRIVATE_IP_BLOCKED']);
        return sendJson(res, clientErrorCodes.has(code) ? 400 : 502, {
          status: 'error',
          code,
          message: mediaErr instanceof Error ? mediaErr.message : '미디어를 불러오지 못했습니다.',
        });
      }
    }
    if (method === 'POST' && pathname === '/api/ingest/external') {
      const body = await readJsonBody(req);
      try {
        const result = await ingestExternalData(body.url);
        return sendJson(res, 200, result);
      } catch (ingestErr) {
        const code = ingestErr && ingestErr.code ? ingestErr.code : 'INGEST_ERROR';
        const clientErrorCodes = new Set(['PIXIV_BLOCKED', 'HOST_NOT_ALLOWED', 'INVALID_URL', 'PRIVATE_IP_BLOCKED']);
        const status = clientErrorCodes.has(code) ? 400 : 502;
        return sendJson(res, status, {
          status: 'error',
          code,
          message: ingestErr instanceof Error ? ingestErr.message : '외부 데이터를 불러오지 못했습니다.',
        });
      }
    }

    // --- Universal Cross-Domain Dimensional Manifold APIs ---
    if (method === 'GET' && pathname === '/api/manifold/presets') {
      return sendJson(res, 200, { status: 'ok', presets: DOMAIN_PRESETS });
    }
    if (method === 'POST' && pathname === '/api/manifold/transform') {
      const body = await readJsonBody(req);
      return sendJson(res, 200, runUniversalManifoldTransform(body));
    }

    // --- Scale-Rotor Hierarchy API (S0..S4) ---
    if (method === 'GET' && pathname === '/api/scale_rotors') {
      engine.evolveScaleRotors(0.05);
      return sendJson(res, 200, {
        status: 'ok',
        scale_dial: engine.scaleDial,
        cycle: engine.cycleIndex,
        rotors: engine.rotors,
      });
    }
    if (method === 'POST' && pathname === '/api/scale_rotors/dial') {
      const body = await readJsonBody(req);
      const sigma = Number(body.scale_dial);
      if (Number.isFinite(sigma)) {
        engine.scaleDial = Math.max(0, Math.min(1, sigma));
      }
      engine.evolveScaleRotors(0.1);
      return sendJson(res, 200, {
        status: 'ok',
        scale_dial: engine.scaleDial,
        rotors: engine.rotors,
      });
    }

    // --- Cognitive CAD Field & Alignment APIs ---
    if (method === 'POST' && pathname === '/api/init_field') {
      const body = await readJsonBody(req);
      const summary = engine.injectText(body.text || '');
      return sendJson(res, 200, {
        status: 'success',
        ...summary,
        points_count: engine.points.length,
        rotors: engine.rotors,
      });
    }

    if (method === 'POST' && pathname === '/api/init_image_field') {
      const body = await readJsonBody(req);
      engine.injectImage(body.image_base64 || '');
      return sendJson(res, 200, {
        status: 'success',
        points_count: engine.points.length,
      });
    }

    if (method === 'GET' && pathname === '/api/observe_field') {
      return sendJson(res, 200, {
        status: 'success',
        data: engine.points,
      });
    }

    if (method === 'POST' && pathname === '/api/auto_align') {
      const body = await readJsonBody(req);
      const result = engine.findResonanceAngle(body.points_data, Number(body.time_t || 0));
      return sendJson(res, 200, {
        status: 'success',
        ...result,
      });
    }

    if (method === 'POST' && pathname === '/api/evaluate_state') {
      const body = await readJsonBody(req);
      const q = Array.isArray(body.quaternion) && body.quaternion.length === 4
        ? qNormalize(body.quaternion.map(Number))
        : engine.rotors[2].quaternion;
      const pts = engine.getActivePoints(body.points_data);
      const fit = engine.fitSymbolicPlane(pts, q);
      engine.evolveScaleRotors(0.04);
      return sendJson(res, 200, {
        status: 'success',
        variance: fit.variance,
        is_resonant: fit.variance < 0.85,
        formula: fit.formula,
        r_squared: fit.rSquared,
      });
    }

    if (method === 'POST' && pathname === '/api/auto_observe') {
      const body = await readJsonBody(req);
      engine.evolveScaleRotors(0.06);
      const q = engine.rotors[2].quaternion;
      const pts = engine.getActivePoints(body.points_data);
      const fit = engine.fitSymbolicPlane(pts, q);
      return sendJson(res, 200, {
        status: 'success',
        quaternion: q,
        variance: fit.variance,
        is_resonant: fit.variance < 0.85,
        formula: fit.formula,
      });
    }

    // --- Semantic Optimization Lock APIs ---
    if (method === 'GET' && pathname === '/api/v1/semantic-optimization/state') {
      return sendJson(res, 200, {
        status: 'ok',
        state_locked: engine.stateLocked,
        scale_dial: engine.scaleDial,
        s4_coherence: engine.rotors[4].coherence,
      });
    }

    if (method === 'GET' && pathname === '/api/v1/semantic-optimization/jump-events') {
      return sendJson(res, 200, {
        status: 'ok',
        events: engine.jumpEvents,
      });
    }

    if (method === 'POST' && pathname === '/api/v1/semantic-optimization/reset-lock') {
      engine.stateLocked = false;
      return sendJson(res, 200, { status: 'ok', state_locked: false });
    }

    // --- Dashboard, Roadmap & Mirror Status APIs ---
    if (method === 'GET' && pathname === '/api/roadmap_status') {
      return sendJson(res, 200, {
        status: 'ok',
        phase_3_gears: {
          hyperlink_extractor: true,
          attention_mapper: true,
          cruciform_attractor: true,
        },
        phase_4_gears: {
          roadmap_generator: true,
          meta_designer: true,
          mirror_engine: true,
        },
        roadmap_markdown: readRoadmapMarkdown(),
      });
    }

    if (method === 'GET' && pathname === '/api/mirror_status') {
      return sendJson(res, 200, {
        status: 'ok',
        self_phase_vector: engine.mirror.selfPhaseVector,
        last_divergence: engine.mirror.lastDivergence,
        accumulated_growth_energy: engine.mirror.accumulatedGrowthEnergy,
        nodes: engine.mirror.nodes,
      });
    }

    if (method === 'GET' && pathname === '/api/status') {
      return sendJson(res, 200, {
        status: 'ok',
        health: engine.getHealthSummary(),
        scale_rotors_coherence: engine.rotors.map((r) => ({
          scale: r.scale,
          name: r.name,
          coherence: Number(r.coherence.toFixed(4)),
        })),
      });
    }

    if (method === 'GET' && pathname === '/api/resonance_log') {
      const n = Math.max(1, Math.min(300, Number(parsed.searchParams.get('n') || 50)));
      return sendJson(res, 200, {
        status: 'ok',
        health_summary: engine.getHealthSummary(),
        trend: engine.resonanceLog.slice(-n),
      });
    }

    if (method === 'POST' && pathname === '/api/run_cycle') {
      const entry = engine.stepCycle();
      return sendJson(res, 200, {
        status: 'ok',
        cycle: entry,
        health: engine.getHealthSummary(),
      });
    }

    if (method === 'POST' && pathname.startsWith('/api/run_loop/')) {
      const rawN = Number(pathname.slice('/api/run_loop/'.length));
      const count = Math.max(1, Math.min(100, Number.isFinite(rawN) ? rawN : 1));
      const results = [];
      for (let i = 0; i < count; i++) {
        results.push(engine.stepCycle());
      }
      return sendJson(res, 200, {
        status: 'ok',
        cycles_run: count,
        last_cycle: results[results.length - 1],
        health: engine.getHealthSummary(),
      });
    }

    // --- Outward Epistemic & Live Physical Reality APIs ---
    if (method === 'POST' && pathname === '/api/epistemic/explore') {
      const body = await readJsonBody(req);
      const result = await exploreExternalEpistemicTopic(body);
      return sendJson(res, 200, result);
    }

    if (method === 'POST' && pathname === '/api/epistemic/reality-probe') {
      const body = await readJsonBody(req);
      const result = await probeExternalAtmosphereReality(body);
      return sendJson(res, 200, result);
    }

    if (method === 'POST' && pathname === '/api/epistemic/constraint-check') {
      const body = await readJsonBody(req);
      const result = await checkExternalCausalConstraint(body);
      return sendJson(res, 200, result);
    }

    if (method === 'POST' && pathname === '/api/epistemic/sensory-hierarchy') {
      const body = await readJsonBody(req);
      const result = await analyzeSensoryHierarchy(body);
      return sendJson(res, 200, result);
    }

    // --- External World & Tool Coupling + Inverse 3D Distillation APIs ---
    if (method === 'POST' && pathname === '/api/ontology/resonate') {
      const body = await readJsonBody(req);
      try {
        const result = await resonateOntologyProtocols(body);
        return sendJson(res, 200, result);
      } catch (ontoErr) {
        return sendJson(res, 400, {
          status: 'error',
          message: ontoErr instanceof Error ? ontoErr.message : '존재론 공명 조회 실패',
        });
      }
    }

    if (method === 'GET' && pathname === '/api/distill/wikimedia-image') {
      const q = parsed.searchParams.get('q') || '';
      try {
        const result = await fetchWikimediaSceneImage(q);
        return sendJson(res, 200, result);
      } catch (wErr) {
        return sendJson(res, 400, { status: 'error', message: wErr instanceof Error ? wErr.message : 'Wikimedia 조회 실패' });
      }
    }

    if (method === 'POST' && pathname === '/api/world/youtube-connect') {
      const body = await readJsonBody(req);
      try {
        const result = await connectYouTubeWorld(body.url || '');
        return sendJson(res, 200, result);
      } catch (ytErr) {
        const code = ytErr && ytErr.code ? ytErr.code : 'YOUTUBE_ERROR';
        const isClientErr = code === 'INVALID_URL' || code === 'HOST_NOT_ALLOWED' || code === 'PRIVATE_IP_BLOCKED';
        return sendJson(res, isClientErr ? 400 : 502, {
          status: 'error',
          code,
          message: ytErr instanceof Error ? ytErr.message : 'YouTube 연결 실패',
        });
      }
    }

    if (method === 'POST' && pathname === '/api/world/github-connect') {
      const body = await readJsonBody(req);
      try {
        const result = await connectGitHubWorld(body.repo || body.url || '');
        return sendJson(res, 200, result);
      } catch (ghErr) {
        const code = ghErr && ghErr.code ? ghErr.code : 'GITHUB_ERROR';
        const isClientErr = code === 'INVALID_URL' || code === 'HOST_NOT_ALLOWED' || code === 'PRIVATE_IP_BLOCKED';
        return sendJson(res, isClientErr ? 400 : 502, {
          status: 'error',
          code,
          message: ghErr instanceof Error ? ghErr.message : 'GitHub 저장소 연결 실패',
        });
      }
    }

    if (method === 'POST' && pathname === '/api/distill/gemini-scene') {
      const body = await readJsonBody(req);
      const out = await distillSceneWithGemini(body);
      return sendJson(res, out.httpStatus, out.payload);
    }

    sendJson(res, 404, { status: 'error', message: `Route not found: ${pathname}` });
  } catch (err) {
    sendJson(res, 500, { status: 'error', message: err instanceof Error ? err.message : 'Internal server error' });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Elysia Cognitive CAD & Scale-Rotor server listening on http://${HOST}:${PORT}`);
});
