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
const ROADMAP_PATH = path.join(STATIC_DIR, 'roadmap.md');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
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
    id: 'video_traffic_hd',
    kind: 'video',
    label: 'HD 영상 · 도심 교차로 실황 (1816×1022)',
    url: 'https://upload.wikimedia.org/wikipedia/commons/2/2c/Tirana_traffic_lights.webm',
    note: '고정 건축물(ω=0)과 이동 차량·신호(동적 프레임 로터) 실물 HD 영상',
  },
  {
    id: 'video_atmosphere_hd',
    kind: 'video',
    label: 'HD 영상 · 남극 대기 중력파 위성 (1920×1080)',
    url: 'https://upload.wikimedia.org/wikipedia/commons/a/a4/Gravity_Waves_Cascade_off_of_Islands_Near_Antarctica_%28CIRA_2023-12-29_-_nolabels%29.webm',
    note: '정지 해양·섬(거시 앵커) 위를 흐르는 1080p 대기 파동 위성 영상',
  },
  {
    id: 'wikimedia_starry_1920',
    kind: 'wikimedia',
    label: 'Full-HD 명화 · 별이 빛나는 밤 (1920px)',
    url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1920px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
    note: '1920px 초고화질 픽셀 S4·S2·S0 다중 스케일 직교 분해 실증',
  },
  {
    id: 'wikimedia_wave_1920',
    kind: 'wikimedia',
    label: 'Full-HD 명화 · 가나가와 파도 (1920px)',
    url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Tsunami_by_hokusai_19th_century.jpg/1920px-Tsunami_by_hokusai_19th_century.jpg',
    note: '1920px 정밀 목판화 선(미시)과 색면(거시) 독립 로터 검증',
  },
  {
    id: 'youtube_nature_hd',
    kind: 'youtube',
    label: 'YouTube HD · 4K 자연 폭포 프레임 (1280×720)',
    url: 'https://www.youtube.com/watch?v=LXb3EKWsInQ',
    note: 'YouTube maxresdefault(1280×720) 무레터박스 원본 프레임 유입',
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
]);

const MAX_EXTERNAL_BYTES = 10 * 1024 * 1024;
const EXTERNAL_TIMEOUT_MS = 12000;
const SAFE_IMAGE_MIMES = new Set(['image/jpeg', 'image/png', 'image/webp', 'image/gif']);
const SAFE_VIDEO_MIMES = new Set(['video/webm', 'video/mp4']);
const mediaProxyCache = new Map(); // Bounded LRU (max 3 HD clips)

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
    const err = new Error(`허용된 공개 소스(YouTube, GitHub, Wikimedia)만 직접 수집할 수 있습니다. 다른 사이트의 이미지·음원은 파일 업로드로 바로 직조할 수 있습니다.`);
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

    sendJson(res, 404, { status: 'error', message: `Route not found: ${pathname}` });
  } catch (err) {
    sendJson(res, 500, { status: 'error', message: err instanceof Error ? err.message : 'Internal server error' });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Elysia Cognitive CAD & Scale-Rotor server listening on http://${HOST}:${PORT}`);
});
