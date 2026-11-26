/**
 * Elysia 3×3×3 Atomic Voxel Virtualized Memory & Communication Superposition Lab
 * -------------------------------------------------------------------------------
 * Uses the 3×3×3 (27-cell) Cube as the atomic Voxel unit representing a unified
 * Virtual Memory & Communication Hierarchy anchored at Origin (0,0,0):
 *
 *   - Shell 0 (r = 0.00,  1 cell) : CPU L1/L2 Cache  (Active hottest register core)
 *   - Shell 1 (r = 1.00,  6 cells): GPU VRAM         (Parallel tensor/frame workspace)
 *   - Shell 2 (r = √2,   12 cells): System RAM       (Working memory & bus lanes)
 *   - Shell 3 (r = √3,    8 cells): NVMe SSD         (Persistent macro archive blocks)
 *
 * Superimposes two virtualized memory states (Baseline State A vs Mutated/Transferred State B):
 *   - Identical voxels (A === B) fade into calm translucent emerald/glass.
 *   - Diverged / transferred voxels (A !== B) glow amber/rose with animated 3D Data-Bus
 *     Transfer Arcs connecting exact source tier -> destination tier.
 *   - Supports smooth A<->B Superposition sliding (0% Side-by-Side -> 100% Overlaid),
 *     Cube <-> Concentric Ring-Buffer <-> Continuous Delta Spectrum morphing,
 *     cross-section cutting, Rubik-style slice rotations on State B, and live custom A/B array diffing.
 */

const container = document.getElementById('three-container');
const specCanvas = document.getElementById('spectrum-canvas');
const specCtx = specCanvas.getContext('2d', { alpha: false });

const TIER_META = [
    { shell: 0, code: 'L1', name: 'CPU L1/L2 캐시', radiusLabel: 'r=0.00', color: 0xf43f5e, hex: '#f43f5e', slots: 1 },
    { shell: 1, code: 'VRAM', name: 'GPU VRAM 버퍼', radiusLabel: 'r=1.00', color: 0x06b6d4, hex: '#06b6d4', slots: 6 },
    { shell: 2, code: 'RAM', name: '시스템 RAM (DRAM)', radiusLabel: 'r=√2', color: 0x10b981, hex: '#10b981', slots: 12 },
    { shell: 3, code: 'SSD', name: 'NVMe SSD 스토리지', radiusLabel: 'r=√3', color: 0x64748b, hex: '#94a3b8', slots: 8 },
];

function shellOf(x, y, z) {
    const r2 = x * x + y * y + z * z;
    if (r2 === 0) return 0;
    if (r2 === 1) return 1;
    if (r2 === 2) return 2;
    return 3;
}

// ============================================================================
// 1. Virtualized 27-Voxel Dual-State Model (State A Baseline vs State B Target)
// ============================================================================
const state = {
    cellsA: [], // 27 baseline voxels: { id, x, y, z, shell, addr, val, numVal }
    cellsB: [], // 27 target voxels
    busTransfers: [], // Array of { fromId, toId, label } showing active data bus movement arcs
    superpose: 1.0, // 0.0 (Side-by-Side A & B) -> 1.0 (Overlaid Superposition)
    morph: 0.0,     // 0.0 (3x3x3 Voxel) -> 0.5 (Concentric Ring Buffer) -> 1.0 (Continuous Delta Sphere)
    cutMode: 'unified',
    cutGap: 0.0,
    probeDepth: 0.0,
    inspectY: 0,
    scenario: 'ssd_to_gpu',
    bRotCount: 0,
    activeAnim: null, // { axis, layer, dir, progress, cellIds }
};

function strHash01(s) {
    let h = 2166136261;
    const str = String(s || '');
    for (let i = 0; i < str.length; i++) {
        h = Math.imul(h ^ str.charCodeAt(i), 16777619) >>> 0;
    }
    return (h % 1000) / 1000;
}

function buildBase27Cells() {
    const arr = [];
    const tierCounters = [0, 0, 0, 0];
    let id = 0;
    for (let y = 1; y >= -1; y--) {
        for (let z = 1; z >= -1; z--) {
            for (let x = -1; x <= 1; x++) {
                const shell = shellOf(x, y, z);
                const tCode = TIER_META[shell].code;
                const localIdx = tierCounters[shell]++;
                const addr = `${tCode}_${String(localIdx).padStart(2, '0')}`;
                const val = `${tCode}:${(0x10 + id * 5).toString(16).toUpperCase()}`;
                arr.push({
                    id,
                    x,
                    y,
                    z,
                    shell,
                    addr,
                    val,
                    numVal: strHash01(val),
                });
                id += 1;
            }
        }
    }
    return arr;
}

function findCellAt(arr, x, y, z) {
    return arr.find((c) => c.x === x && c.y === y && c.z === z);
}

function applyScenario(key) {
    state.scenario = key;
    state.bRotCount = 0;
    document.getElementById('val-rot-count').textContent = 'B 회전 0회';

    state.cellsA = buildBase27Cells();
    state.cellsB = state.cellsA.map((c) => ({ ...c }));
    state.busTransfers = [];

    const core = findCellAt(state.cellsB, 0, 0, 0);
    const vramCells = state.cellsB.filter((c) => c.shell === 1);
    const ramCells = state.cellsB.filter((c) => c.shell === 2);
    const ssdCells = state.cellsB.filter((c) => c.shell === 3);

    if (key === 'ssd_to_gpu') {
        // SSD blocks remain read-only invariant (100% same); weights stream SSD -> RAM -> GPU VRAM!
        for (let i = 0; i < 4; i++) {
            ramCells[i].val = `WGT_P${i}`;
            ramCells[i].numVal = strHash01(ramCells[i].val);
            vramCells[i].val = `TNS_B${i}`;
            vramCells[i].numVal = strHash01(vramCells[i].val);
            state.busTransfers.push({ fromId: ssdCells[i].id, toId: ramCells[i].id, label: 'NVMe→RAM' });
            state.busTransfers.push({ fromId: ramCells[i].id, toId: vramCells[i].id, label: 'PCIe→VRAM' });
        }
    } else if (key === 'gpu_cpu_burst') {
        // SSD & RAM stay 100% quiet glass; inner GPU VRAM <-> CPU L1 Cache burst hot!
        core.val = 'L1:EXEC!';
        core.numVal = strHash01(core.val);
        for (let i = 0; i < 5; i++) {
            vramCells[i].val = `FRM_K${i}`;
            vramCells[i].numVal = strHash01(vramCells[i].val);
            state.busTransfers.push({ fromId: vramCells[i].id, toId: core.id, label: 'VRAM↔L1' });
        }
    } else if (key === 'ram_cascade') {
        // Single RAM slot diverges -> cascades inward into 2 VRAM buffers and L1 Core!
        ramCells[2].val = 'MUT_0xFF';
        ramCells[2].numVal = strHash01(ramCells[2].val);
        vramCells[0].val = 'BR_V0';
        vramCells[0].numVal = strHash01(vramCells[0].val);
        vramCells[2].val = 'BR_V2';
        vramCells[2].numVal = strHash01(vramCells[2].val);
        core.val = 'L1:SYNC*';
        core.numVal = strHash01(core.val);
        state.busTransfers.push({ fromId: ramCells[2].id, toId: vramCells[0].id, label: 'RAM→VRAM' });
        state.busTransfers.push({ fromId: ramCells[2].id, toId: vramCells[2].id, label: 'RAM→VRAM' });
        state.busTransfers.push({ fromId: vramCells[0].id, toId: core.id, label: 'VRAM→L1' });
    } else if (key === 'bus_swap') {
        // Rotate entire horizontal middle slice Y=0 (affects VRAM + RAM simultaneously while Y=±1 stay identical!)
        for (const c of state.cellsB) {
            if (c.y !== 0) continue;
            const ox = c.x;
            const oz = c.z;
            c.x = oz;
            c.z = -ox;
            c.shell = shellOf(c.x, c.y, c.z);
        }
        state.bRotCount = 1;
        document.getElementById('val-rot-count').textContent = 'B 회전 1회';
        for (let i = 0; i < 4; i++) {
            state.busTransfers.push({ fromId: ramCells[i].id, toId: ramCells[(i + 1) % 4].id, label: 'BUS_ROT' });
        }
    } else if (key === 'elysia_cognitive') {
        // Load Elysia's real L1~L4 Cognitive Before(A) -> After(B) state into CPU L1 / VRAM / RAM / SSD!
        let snap = null;
        try {
            const raw = localStorage.getItem('elysia_cognitive_voxel_bridge_v1');
            if (raw) snap = JSON.parse(raw);
        } catch {
            snap = null;
        }
        const before = snap ? snap.before : { s4: 100, s2: 100, s0: 96, saved: 74, psnr: 44, controls: { s4Stride: 12, s2Stride: 3, s0Thresh: 5, envCoupling: 1.0, objConnectivity: 1.0 } };
        const after = snap ? snap.after : { s4: 100, s2: 64, s0: 88, saved: 83, psnr: 43, controls: { s4Stride: 14, s2Stride: 4, s0Thresh: 5, envCoupling: 1.7, objConnectivity: 1.6 } };
        const actTag = snap ? String(snap.kind || 'LEARN').toUpperCase().slice(0, 7) : 'COG_SIM';

        const coreA = findCellAt(state.cellsA, 0, 0, 0);
        const vramA = state.cellsA.filter((c) => c.shell === 1);
        const ramA = state.cellsA.filter((c) => c.shell === 2);
        const ssdA = state.cellsA.filter((c) => c.shell === 3);

        // Shell 0 (CPU L1 Core) = Volition / Self-Revision Core
        coreA.val = `L1:PRE`;
        core.val = `L1:${actTag}`;
        coreA.numVal = strHash01(coreA.val);
        core.numVal = strHash01(core.val);

        // Shell 1 (GPU VRAM) = Active S0/S2 sensory & output manifold
        const vramPairsA = [`S0:${before.s0}%`, `S2:${before.s2}%`, `OPS:${before.saved}%`, `DB:${before.psnr}`, `ACT:BASE`, `SUP:0%`];
        const vramPairsB = [`S0:${after.s0}%`, `S2:${after.s2}%`, `OPS:${after.saved}%`, `DB:${after.psnr}`, `ACT:${actTag}`, `SUP:${Math.round(100 - after.s2)}%`];
        for (let i = 0; i < 6; i++) {
            vramA[i].val = vramPairsA[i];
            vramA[i].numVal = strHash01(vramA[i].val);
            vramCells[i].val = vramPairsB[i];
            vramCells[i].numVal = strHash01(vramCells[i].val);
            if (vramA[i].val !== vramCells[i].val) {
                state.busTransfers.push({ fromId: vramCells[i].id, toId: core.id, label: 'SENSE→L1' });
            }
        }

        // Shell 2 (System RAM) = Controllable Causal Levers & Learned Weights
        const cA = before.controls || {};
        const cB = after.controls || {};
        const ramLabels = [
            ['S4_T', cA.s4Stride ?? 12, cB.s4Stride ?? 14],
            ['S2_T', cA.s2Stride ?? 3, cB.s2Stride ?? 4],
            ['S0_G', cA.s0Thresh ?? 5, cB.s0Thresh ?? 5],
            ['ENV', cA.envCoupling ?? 1.0, cB.envCoupling ?? 1.7],
            ['CONN', cA.objConnectivity ?? 1.0, cB.objConnectivity ?? 1.6],
            ['CONF', snap ? `${snap.avgConfidence}%` : '42%', snap ? `${snap.avgConfidence}%` : '68%'],
        ];
        for (let i = 0; i < ramLabels.length; i++) {
            const [k, va, vb] = ramLabels[i];
            ramA[i].val = `${k}:${va}`;
            ramA[i].numVal = strHash01(ramA[i].val);
            ramCells[i].val = `${k}:${vb}`;
            ramCells[i].numVal = strHash01(ramCells[i].val);
            if (ramA[i].val !== ramCells[i].val) {
                state.busTransfers.push({ fromId: ramCells[i].id, toId: vramCells[i % 6].id, label: 'LAW→ACT' });
            }
        }

        // Shell 3 (NVMe SSD) = S4 Macro Invariant Environment & Long-term Memory Anchors
        for (let i = 0; i < 8; i++) {
            ssdA[i].val = `S4:${before.s4}%`;
            ssdA[i].numVal = strHash01(ssdA[i].val);
            ssdCells[i].val = i === 0 && Math.abs(after.s4 - before.s4) > 1.5 ? `S4:${after.s4}%` : `S4:${before.s4}%`;
            ssdCells[i].numVal = strHash01(ssdCells[i].val);
        }
    }

    refreshAllVisuals();
}

function applyCustomABInputs(strA, strB) {
    const tokA = strA.trim().split(/[\s,]+/).filter(Boolean);
    const tokB = strB.trim().split(/[\s,]+/).filter(Boolean);
    if (!tokA.length && !tokB.length) return;
    state.cellsA = buildBase27Cells();
    state.cellsB = buildBase27Cells();
    state.busTransfers = [];
    for (let i = 0; i < 27; i++) {
        const va = tokA.length ? tokA[i % tokA.length] : state.cellsA[i].val;
        const vb = tokB.length ? tokB[i % tokB.length] : va;
        state.cellsA[i].val = va;
        state.cellsA[i].numVal = strHash01(va);
        state.cellsB[i].val = vb;
        state.cellsB[i].numVal = strHash01(vb);
    }
    refreshAllVisuals();
}

function isCoordDiverged(x, y, z) {
    const a = findCellAt(state.cellsA, x, y, z);
    const b = findCellAt(state.cellsB, x, y, z);
    if (!a || !b) return false;
    return a.val !== b.val;
}

// ============================================================================
// 2. Three.js 3D Scene (Dual Superposition Voxels + Glowing Bus Transfer Arcs)
// ============================================================================
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
camera.position.set(5.8, 4.3, 6.6);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
container.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 3.2;
controls.maxDistance = 18;

scene.add(new THREE.AmbientLight(0xdbeafe, 0.72));
const keyLight = new THREE.DirectionalLight(0xffffff, 0.95);
keyLight.position.set(7, 9, 7);
scene.add(keyLight);
const rimLight = new THREE.DirectionalLight(0x06b6d4, 0.5);
rimLight.position.set(-7, -4, -6);
scene.add(rimLight);

const rootGroup = new THREE.Group();
scene.add(rootGroup);

const boxGeo = new THREE.BoxGeometry(0.80, 0.80, 0.80);
const edgeGeo = new THREE.EdgesGeometry(boxGeo);
const orbGeo = new THREE.SphereGeometry(0.29, 18, 14);

// Build 27 Voxel Meshes for State A (Baseline Reference) and 27 for State B (Active/Superimposed)
function buildVoxelMeshSet(isStateB) {
    const arr = [];
    for (let i = 0; i < 27; i++) {
        const g = new THREE.Group();
        const boxMat = new THREE.MeshStandardMaterial({
            color: isStateB ? 0xf59e0b : 0x10b981,
            roughness: 0.35,
            metalness: 0.15,
            transparent: true,
            opacity: 0.25,
        });
        const box = new THREE.Mesh(boxGeo, boxMat);
        const wireMat = new THREE.LineBasicMaterial({
            color: isStateB ? 0x38bdf8 : 0x10b981,
            transparent: true,
            opacity: 0.35,
        });
        const wire = new THREE.LineSegments(edgeGeo, wireMat);
        const orbMat = new THREE.MeshStandardMaterial({
            color: 0x06b6d4,
            emissive: 0x06b6d4,
            emissiveIntensity: 0.3,
            transparent: true,
            opacity: 0,
        });
        const orb = new THREE.Mesh(orbGeo, orbMat);
        g.add(box, wire, orb);
        rootGroup.add(g);
        arr.push({ g, box, boxMat, wire, wireMat, orb, orbMat });
    }
    return arr;
}

const meshesA = buildVoxelMeshSet(false);
const meshesB = buildVoxelMeshSet(true);

// Concentric Memory Tier Ring Rails (VRAM r=1, RAM r=√2, SSD r=√3)
const ringRails = [];
[1.22, 1.82, 2.40].forEach((r, idx) => {
    const pts = [];
    for (let k = 0; k <= 72; k++) {
        const a = (k / 72) * Math.PI * 2;
        pts.push(new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const mat = new THREE.LineBasicMaterial({ color: TIER_META[idx + 1].color, transparent: true, opacity: 0.0 });
    ringRails.push(mat);
    const eq = new THREE.Line(geo, mat);
    const mer = new THREE.Line(geo, mat);
    mer.rotation.x = Math.PI / 2;
    rootGroup.add(eq, mer);
});

// Data-Bus Transfer Arcs Group (3D Bezier curves + animated packet pulses!)
const busArcGroup = new THREE.Group();
rootGroup.add(busArcGroup);
let busPackets = []; // { curve, mesh, phase }

// Continuous Spherical Delta Manifold (morph = 100%)
const sphereGeo = new THREE.SphereGeometry(2.38, 60, 40);
const spherePosAttr = sphereGeo.attributes.position;
const sphereBasePos = new Float32Array(spherePosAttr.array.length);
sphereBasePos.set(spherePosAttr.array);
const sphereColors = new Float32Array(spherePosAttr.count * 3);
sphereGeo.setAttribute('color', new THREE.BufferAttribute(sphereColors, 3));
const sphereMat = new THREE.MeshStandardMaterial({
    vertexColors: true,
    roughness: 0.3,
    metalness: 0.1,
    transparent: true,
    opacity: 0.0,
    side: THREE.DoubleSide,
});
const deltaSphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
rootGroup.add(deltaSphereMesh);

// ============================================================================
// 3. Position Computation (Superposition Separation + Cut Modes + Morph)
// ============================================================================
function computeCellPos(cell, cellList, sideSign) {
    // sideSign: -1 for State A, +1 for State B; separation shrinks to 0 at superpose=1.0!
    const sepX = (1 - state.superpose) * 2.25 * sideSign;
    const spacing = 1.06;
    const gap = state.cutGap;
    const m = state.morph;

    let cx = cell.x * spacing;
    let cy = cell.y * spacing;
    let cz = cell.z * spacing;

    if (state.cutMode === 'slice-y') {
        cy += cell.y * gap * 1.1;
    } else if (state.cutMode === 'slice-x') {
        cx += cell.x * gap * 1.1;
    } else if (state.cutMode === 'octants' && cell.shell > 0) {
        cx += Math.sign(cell.x) * gap * 0.72;
        cy += Math.sign(cell.y) * gap * 0.72;
        cz += Math.sign(cell.z) * gap * 0.72;
    } else if (state.cutMode === 'shells' && cell.shell > 0) {
        const push = cell.shell * gap * 0.56;
        const r = Math.hypot(cx, cy, cz) || 1;
        cx += (cx / r) * push;
        cy += (cy / r) * push;
        cz += (cz / r) * push;
    }

    // Concentric Ring-Buffer positions (morph = 0.5)
    const shellRadii = [0.0, 1.22, 1.82, 2.40];
    const targetR = shellRadii[cell.shell] + (state.cutMode === 'shells' ? cell.shell * gap * 0.42 : 0);
    const sameShell = cellList.filter((c) => c.shell === cell.shell);
    const orderIdx = sameShell.indexOf(cell);
    const theta = (orderIdx / Math.max(1, sameShell.length)) * Math.PI * 2;
    const rx = cell.shell === 0 ? 0 : Math.cos(theta) * targetR;
    const ry = cell.shell === 0 ? 0 : cell.y * (0.26 + gap * 0.5);
    const rz = cell.shell === 0 ? 0 : Math.sin(theta) * targetR;

    // Continuous Sphere positions (morph = 1.0)
    const baseLen = Math.hypot(cell.x, cell.y, cell.z) || 1;
    const spR = cell.shell === 0 ? 0 : 2.12;
    const sx = (cell.x / baseLen) * spR;
    const sy = (cell.y / baseLen) * spR;
    const sz = (cell.z / baseLen) * spR;

    let tx, ty, tz;
    if (m <= 0.5) {
        const u = m * 2;
        tx = cx + (rx - cx) * u;
        ty = cy + (ry - cy) * u;
        tz = cz + (rz - cz) * u;
    } else {
        const u = (m - 0.5) * 2;
        tx = rx + (sx - rx) * u;
        ty = ry + (sy - ry) * u;
        tz = rz + (sz - rz) * u;
    }
    return new THREE.Vector3(tx + sepX, ty, tz);
}

function makeVoxelTexture(addr, val, diverged, tierHex) {
    const c = document.createElement('canvas');
    c.width = 128;
    c.height = 128;
    const ctx = c.getContext('2d');
    ctx.fillStyle = diverged ? '#2c1706' : '#0b1623';
    ctx.fillRect(0, 0, 128, 128);
    ctx.strokeStyle = diverged ? '#f59e0b' : tierHex;
    ctx.lineWidth = diverged ? 8 : 4;
    ctx.strokeRect(4, 4, 120, 120);

    ctx.fillStyle = diverged ? '#fbbf24' : '#64748b';
    ctx.font = 'bold 18px "IBM Plex Mono", monospace';
    ctx.textAlign = 'center';
    ctx.fillText(addr, 64, 38);

    ctx.fillStyle = diverged ? '#fef3c7' : '#cbd5e1';
    ctx.font = 'bold 22px "IBM Plex Mono", monospace';
    ctx.fillText(String(val).slice(0, 7), 64, 82);

    const tex = new THREE.CanvasTexture(c);
    tex.anisotropy = 4;
    return tex;
}

function rebuildBusTransferArcs() {
    while (busArcGroup.children.length > 0) {
        const ch = busArcGroup.children.pop();
        if (ch.geometry) ch.geometry.dispose();
        if (ch.material) ch.material.dispose();
    }
    busPackets = [];

    const packetGeo = new THREE.SphereGeometry(0.085, 10, 10);
    state.busTransfers.forEach((tr, idx) => {
        const fromCell = state.cellsB.find((c) => c.id === tr.fromId);
        const toCell = state.cellsB.find((c) => c.id === tr.toId);
        if (!fromCell || !toCell) return;

        const p0 = computeCellPos(fromCell, state.cellsB, 1);
        const p1 = computeCellPos(toCell, state.cellsB, 1);
        const mid = p0.clone().add(p1).multiplyScalar(0.5);
        mid.y += 0.55;
        const curve = new THREE.QuadraticBezierCurve3(p0, mid, p1);
        const pts = curve.getPoints(24);
        const geo = new THREE.BufferGeometry().setFromPoints(pts);
        const mat = new THREE.LineBasicMaterial({ color: 0x06b6d4, transparent: true, opacity: 0.78 });
        busArcGroup.add(new THREE.Line(geo, mat));

        const pMat = new THREE.MeshBasicMaterial({ color: 0x22d3ee });
        const pkt = new THREE.Mesh(packetGeo, pMat);
        busArcGroup.add(pkt);
        busPackets.push({ curve, mesh: pkt, phase: (idx * 0.23) % 1 });
    });
}

function evaluateContinuousDelta(px, py, pz) {
    let wSum = 0;
    let diffSum = 0;
    const invTwoSig2 = 1.6;
    for (let i = 0; i < 27; i++) {
        const c = state.cellsB[i];
        const dx = px - c.x;
        const dy = py - c.y;
        const dz = pz - c.z;
        const w = Math.exp(-(dx * dx + dy * dy + dz * dz) * invTwoSig2);
        const div = isCoordDiverged(c.x, c.y, c.z) ? 1.0 : 0.0;
        wSum += w;
        diffSum += w * div;
    }
    return wSum > 1e-8 ? diffSum / wSum : 0;
}

function updateDeltaSphereGeometry() {
    const count = spherePosAttr.count;
    const colAttr = sphereGeo.attributes.color;
    for (let i = 0; i < count; i++) {
        const bx = sphereBasePos[i * 3];
        const by = sphereBasePos[i * 3 + 1];
        const bz = sphereBasePos[i * 3 + 2];
        const len = Math.hypot(bx, by, bz) || 1;
        const div = evaluateContinuousDelta((bx / len) * 1.25, (by / len) * 1.25, (bz / len) * 1.25);
        const radScale = 1.0 + div * 0.14;
        spherePosAttr.setXYZ(i, bx * radScale, by * radScale, bz * radScale);
        // Calm emerald-teal where identical, glowing amber-rose where diverged!
        const r = 0.05 + div * 0.92;
        const g = 0.38 + div * 0.22 - div * div * 0.25;
        const b = 0.42 * (1 - div) + 0.08;
        colAttr.setXYZ(i, r, g, b);
    }
    spherePosAttr.needsUpdate = true;
    colAttr.needsUpdate = true;
    sphereGeo.computeVertexNormals();
}

function renderDeltaSpectrumCanvas() {
    const cw = specCanvas.width;
    const ch = specCanvas.height;
    const img = specCtx.createImageData(cw, ch);
    const data = img.data;
    const d = state.probeDepth;
    const step = 2;

    for (let py = 0; py < ch; py += step) {
        const v = ((py / (ch - 1)) * 2 - 1) * 1.45;
        for (let px = 0; px < cw; px += step) {
            const u = ((px / (cw - 1)) * 2 - 1) * 1.45;
            const div = evaluateContinuousDelta(u, d, v);
            const r = Math.hypot(u, v);
            const ringLine = (Math.abs(r - 1.0) < 0.025 || Math.abs(r - 1.414) < 0.025) ? 26 : 0;

            const R = Math.min(255, Math.round((14 + div * 238) + ringLine));
            const G = Math.min(255, Math.round((78 + div * 84 - div * div * 72) + ringLine));
            const B = Math.min(255, Math.round((96 * (1 - div) + 18) + ringLine));

            for (let oy = 0; oy < step && py + oy < ch; oy++) {
                for (let ox = 0; ox < step && px + ox < cw; ox++) {
                    const idx = ((py + oy) * cw + (px + ox)) * 4;
                    data[idx] = R;
                    data[idx + 1] = G;
                    data[idx + 2] = B;
                    data[idx + 3] = 255;
                }
            }
        }
    }
    specCtx.putImageData(img, 0, 0);
}

function updateVoxelMaterialsAndTransforms() {
    const m = state.morph;
    const sup = state.superpose;
    const boxVis = Math.max(0, 1 - m * 1.65);
    const orbVis = m <= 0.5 ? m * 1.9 : Math.max(0.2, 1 - (m - 0.5) * 1.4);
    const sphereOp = Math.max(0, (m - 0.45) / 0.55) * 0.82;
    const railOp = m <= 0.5 ? m * 1.1 : (1 - (m - 0.5) * 0.9) * 0.5;

    sphereMat.opacity = sphereOp;
    deltaSphereMesh.visible = sphereOp > 0.01;
    ringRails.forEach((rm) => { rm.opacity = railOp; });

    const anim = state.activeAnim;

    for (let i = 0; i < 27; i++) {
        const cA = state.cellsA[i];
        const cB = state.cellsB[i];
        const mA = meshesA[i];
        const mB = meshesB[i];

        const divAtB = isCoordDiverged(cB.x, cB.y, cB.z);
        const divAtA = isCoordDiverged(cA.x, cA.y, cA.z);

        const posA = computeCellPos(cA, state.cellsA, -1);
        const posB = computeCellPos(cB, state.cellsB, 1);

        if (anim && anim.cellIds.has(cB.id)) {
            const eased = anim.progress < 0.5
                ? 2 * anim.progress * anim.progress
                : 1 - Math.pow(-2 * anim.progress + 2, 2) / 2;
            const ang = anim.dir * (Math.PI / 2) * eased;
            const ax = anim.axis === 'x'
                ? new THREE.Vector3(1, 0, 0)
                : anim.axis === 'y' ? new THREE.Vector3(0, 1, 0) : new THREE.Vector3(0, 0, 1);
            const pivotX = (1 - sup) * 2.25;
            posB.x -= pivotX;
            posB.applyAxisAngle(ax, ang);
            posB.x += pivotX;
            mB.g.setRotationFromAxisAngle(ax, ang);
        } else {
            mB.g.rotation.set(0, 0, 0);
        }

        mA.g.position.copy(posA);
        mB.g.position.copy(posB);

        // State A disappears cleanly into State B when fully superimposed (sup -> 1)
        const aAlpha = (1 - sup) * 0.85;
        mA.g.visible = aAlpha > 0.03;
        mA.box.visible = boxVis > 0.03;
        mA.wire.visible = boxVis > 0.03;
        mA.boxMat.opacity = boxVis * aAlpha * (divAtA ? 0.9 : 0.45);
        mA.wireMat.opacity = boxVis * aAlpha * 0.6;
        mA.orb.visible = orbVis > 0.03;
        mA.orbMat.opacity = orbVis * aAlpha;

        // State B (Superimposed Voxel View):
        // Identical cells -> calm translucent glass (0.14 opacity) so diverged amber cells pop out instantly!
        const bBodyAlpha = divAtB ? 0.94 : (0.14 + (1 - sup) * 0.35);
        const bWireAlpha = divAtB ? 0.92 : 0.24;
        mB.box.visible = boxVis > 0.03;
        mB.wire.visible = boxVis > 0.03;
        mB.boxMat.opacity = boxVis * bBodyAlpha;
        mB.boxMat.emissive.setHex(divAtB ? 0xd97706 : 0x000000);
        mB.boxMat.emissiveIntensity = divAtB ? 0.32 : 0.0;
        mB.wireMat.color.setHex(divAtB ? 0xf59e0b : TIER_META[cB.shell].color);
        mB.wireMat.opacity = boxVis * bWireAlpha;

        const bScale = (divAtB ? 1.02 : 0.88) * (1 - m * 0.35);
        mB.box.scale.setScalar(bScale);
        mB.wire.scale.setScalar(bScale);

        mB.orb.visible = orbVis > 0.03;
        mB.orbMat.opacity = orbVis * (divAtB ? 0.96 : 0.32);
        mB.orbMat.color.setHex(divAtB ? 0xf59e0b : 0x10b981);
        mB.orbMat.emissive.setHex(divAtB ? 0xf59e0b : 0x10b981);
        mB.orb.scale.setScalar(divAtB ? 1.25 : 0.72);
    }
}

function refreshTextures() {
    for (let i = 0; i < 27; i++) {
        const cA = state.cellsA[i];
        const cB = state.cellsB[i];
        const divB = isCoordDiverged(cB.x, cB.y, cB.z);
        const texA = makeVoxelTexture(cA.addr, cA.val, false, TIER_META[cA.shell].hex);
        const texB = makeVoxelTexture(cB.addr, cB.val, divB, TIER_META[cB.shell].hex);
        if (meshesA[i].boxMat.map) meshesA[i].boxMat.map.dispose();
        if (meshesB[i].boxMat.map) meshesB[i].boxMat.map.dispose();
        meshesA[i].boxMat.map = texA;
        meshesA[i].boxMat.color.setHex(0xffffff);
        meshesA[i].boxMat.needsUpdate = true;
        meshesB[i].boxMat.map = texB;
        meshesB[i].boxMat.color.setHex(0xffffff);
        meshesB[i].boxMat.needsUpdate = true;
    }
}

// ============================================================================
// 4. Right Panel Instant Recognition Readout (Tier Diff + 3×3 A→B Table)
// ============================================================================
function renderRightInspectors() {
    let totalSame = 0;
    let totalDiff = 0;
    const tierStats = TIER_META.map((t) => ({ ...t, same: 0, diff: 0 }));

    for (let y = 1; y >= -1; y--) {
        for (let z = 1; z >= -1; z--) {
            for (let x = -1; x <= 1; x++) {
                const sh = shellOf(x, y, z);
                if (isCoordDiverged(x, y, z)) {
                    totalDiff += 1;
                    tierStats[sh].diff += 1;
                } else {
                    totalSame += 1;
                    tierStats[sh].same += 1;
                }
            }
        }
    }

    const matchPct = ((totalSame / 27) * 100).toFixed(1);
    document.getElementById('val-total-match').textContent = `동일률 ${matchPct}%`;

    const hudSum = document.getElementById('hud-summary');
    hudSum.textContent = '';
    hudSum.append(document.createTextNode('포개기 진단: '));
    const sSpan = document.createElement('span');
    sSpan.className = 'same-hi';
    sSpan.textContent = `동일 ${totalSame}/27`;
    const dSpan = document.createElement('span');
    dSpan.className = 'diff-hi';
    dSpan.textContent = `변화·분기 ${totalDiff}/27`;
    hudSum.append(sSpan, document.createTextNode(' · '), dSpan);

    const divergedTiers = tierStats.filter((t) => t.diff > 0).map((t) => t.code);
    const originHud = document.getElementById('hud-origin-badge');
    originHud.textContent = '';
    originHud.append(document.createTextNode('분기 범위: '));
    const oStrong = document.createElement('strong');
    oStrong.textContent = divergedTiers.length === 0
        ? '전 계층 100% 동일 (불변 상태)'
        : `${divergedTiers.join(' ↔ ')} 계층 분기 (${totalDiff}셀)`;
    originHud.append(oStrong);

    // 1) Tier-by-tier Identity vs Divergence bars (L1 Cache, GPU VRAM, RAM, NVMe SSD)
    const tierHost = document.getElementById('tier-breakdown-host');
    tierHost.textContent = '';
    tierStats.forEach((t) => {
        const card = document.createElement('div');
        card.className = t.diff > 0 ? 'tier-card has-diff' : 'tier-card';

        const head = document.createElement('div');
        head.className = 'tier-head';
        const leftLbl = document.createElement('span');
        leftLbl.textContent = `${t.name} (${t.radiusLabel})`;
        const rightLbl = document.createElement('span');
        rightLbl.style.color = t.diff > 0 ? '#f59e0b' : '#10b981';
        rightLbl.textContent = t.diff > 0 ? `분기 ${t.diff}/${t.slots}` : `100% 동일 (${t.slots}/${t.slots})`;
        head.append(leftLbl, rightLbl);

        const bar = document.createElement('div');
        bar.className = 'tier-bar';
        const bSame = document.createElement('div');
        bSame.className = 'tier-bar-same';
        bSame.style.width = `${(t.same / t.slots) * 100}%`;
        const bDiff = document.createElement('div');
        bDiff.className = 'tier-bar-diff';
        bDiff.style.width = `${(t.diff / t.slots) * 100}%`;
        bar.append(bSame, bDiff);

        const foot = document.createElement('div');
        foot.className = 'tier-foot';
        const f1 = document.createElement('span');
        f1.textContent = `동일 ${t.same}셀 · 변화 ${t.diff}셀`;
        const f2 = document.createElement('span');
        f2.textContent = t.diff === 0 ? '불변 잠금' : '데이터 이동/변이';
        foot.append(f1, f2);

        card.append(head, bar, foot);
        tierHost.appendChild(card);
    });

    // 2) Active 3×3 Slice A -> B Comparison Matrix
    const matHost = document.getElementById('matrix-3x3-host');
    matHost.textContent = '';
    const sy = state.inspectY;
    for (let z = -1; z <= 1; z++) {
        for (let x = -1; x <= 1; x++) {
            const cA = findCellAt(state.cellsA, x, sy, z);
            const cB = findCellAt(state.cellsB, x, sy, z);
            const diff = cA && cB && cA.val !== cB.val;
            const div = document.createElement('div');
            div.className = diff ? 'matrix-cell is-diff' : 'matrix-cell is-same';

            const top = document.createElement('div');
            top.className = 'cell-top';
            const tierSpan = document.createElement('span');
            tierSpan.textContent = TIER_META[shellOf(x, sy, z)].code;
            const coordSpan = document.createElement('span');
            coordSpan.textContent = `(${x},${sy},${z})`;
            top.append(tierSpan, coordSpan);

            const valDiv = document.createElement('div');
            valDiv.className = 'cell-val';
            valDiv.textContent = diff ? `${cA.val}→${cB.val}` : (cA ? cA.val : '-');

            const tag = document.createElement('div');
            tag.className = 'cell-diff-tag';
            tag.textContent = diff ? '▲ 분기·이동' : '● 동일';

            div.append(top, valDiv, tag);
            matHost.appendChild(div);
        }
    }
}

function refreshAllVisuals() {
    refreshTextures();
    updateVoxelMaterialsAndTransforms();
    rebuildBusTransferArcs();
    updateDeltaSphereGeometry();
    renderDeltaSpectrumCanvas();
    renderRightInspectors();
}

// ============================================================================
// 5. Rubik Slice Rotation on State B (Instant Structural Diff Demonstration)
// ============================================================================
function triggerSliceRotationB(axis, layer, dir) {
    if (state.activeAnim) return;
    const ids = new Set();
    state.cellsB.forEach((c) => { if (c[axis] === layer) ids.add(c.id); });
    state.activeAnim = { axis, layer, dir, progress: 0, cellIds: ids };
}

function commitSliceRotationB(axis, layer, dir) {
    for (const c of state.cellsB) {
        if (c[axis] !== layer) continue;
        const { x, y, z } = c;
        if (axis === 'y') { c.x = dir > 0 ? z : -z; c.z = dir > 0 ? -x : x; }
        else if (axis === 'x') { c.y = dir > 0 ? -z : z; c.z = dir > 0 ? y : -y; }
        else if (axis === 'z') { c.x = dir > 0 ? -y : y; c.y = dir > 0 ? x : -x; }
        c.shell = shellOf(c.x, c.y, c.z);
    }
    state.bRotCount += 1;
    document.getElementById('val-rot-count').textContent = `B 회전 ${state.bRotCount}회`;
    refreshAllVisuals();
}

// ============================================================================
// 6. Resize & Animation Loop
// ============================================================================
function handleResize() {
    const w = container.clientWidth || 640;
    const h = container.clientHeight || 480;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
}
window.addEventListener('resize', handleResize);

let lastTime = performance.now();
function animate(now) {
    requestAnimationFrame(animate);
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;

    if (state.activeAnim) {
        state.activeAnim.progress += dt / 0.24;
        if (state.activeAnim.progress >= 1.0) {
            const { axis, layer, dir } = state.activeAnim;
            state.activeAnim = null;
            commitSliceRotationB(axis, layer, dir);
        }
        updateVoxelMaterialsAndTransforms();
    }

    // Smoothly animate data-bus transfer packets along 3D curves
    for (const p of busPackets) {
        p.phase = (p.phase + dt * 0.55) % 1;
        p.mesh.position.copy(p.curve.getPoint(p.phase));
    }

    controls.update();
    renderer.render(scene, camera);
}

// ============================================================================
// 7. Wire UI Controls
// ============================================================================
function updateSuperposeUI(pct) {
    state.superpose = pct / 100;
    document.getElementById('val-superpose').textContent =
        pct >= 90 ? '100% 포개기' : pct <= 10 ? '0% 나란히 분리' : `${pct}% 반겹침`;
    document.querySelectorAll('#superpose-presets button').forEach((b) =>
        b.classList.toggle('active', Math.abs(Number(b.dataset.sup) - pct) <= 15)
    );
    updateVoxelMaterialsAndTransforms();
    rebuildBusTransferArcs();
}

function updateMorphUI(pct) {
    state.morph = pct / 100;
    document.getElementById('val-morph-pct').textContent =
        pct < 25 ? `${pct}% 복셀` : pct < 75 ? `${pct}% 링버퍼` : `${pct}% 구면장`;
    document.querySelectorAll('#morph-presets button').forEach((b) =>
        b.classList.toggle('active', Math.abs(Number(b.dataset.morph) - pct) <= 18)
    );
    updateVoxelMaterialsAndTransforms();
    rebuildBusTransferArcs();
}

function bindUI() {
    const slSup = document.getElementById('slider-superpose');
    slSup.addEventListener('input', () => updateSuperposeUI(Number(slSup.value)));
    document.querySelectorAll('#superpose-presets button').forEach((btn) => {
        btn.addEventListener('click', () => {
            slSup.value = btn.dataset.sup;
            updateSuperposeUI(Number(btn.dataset.sup));
        });
    });

    document.querySelectorAll('#scenario-btns button').forEach((btn) => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#scenario-btns button').forEach((b) => b.classList.toggle('active', b === btn));
            applyScenario(btn.dataset.scen);
        });
    });

    const inA = document.getElementById('input-arr-a');
    const inB = document.getElementById('input-arr-b');
    const runCustom = (e) => {
        if (e.key === 'Enter') applyCustomABInputs(inA.value, inB.value);
    };
    inA.addEventListener('keydown', runCustom);
    inB.addEventListener('keydown', runCustom);

    const slMorph = document.getElementById('slider-morph');
    slMorph.addEventListener('input', () => updateMorphUI(Number(slMorph.value)));
    document.querySelectorAll('#morph-presets button').forEach((btn) => {
        btn.addEventListener('click', () => {
            slMorph.value = btn.dataset.morph;
            updateMorphUI(Number(btn.dataset.morph));
        });
    });

    const slGap = document.getElementById('slider-cut-gap');
    document.querySelectorAll('#cut-mode-btns button').forEach((btn) => {
        btn.addEventListener('click', () => {
            state.cutMode = btn.dataset.cut;
            document.querySelectorAll('#cut-mode-btns button').forEach((b) => b.classList.toggle('active', b === btn));
            if (state.cutMode !== 'unified' && state.cutGap < 0.45) {
                state.cutGap = 0.65;
                slGap.value = '0.65';
            } else if (state.cutMode === 'unified') {
                state.cutGap = 0.0;
                slGap.value = '0';
            }
            updateVoxelMaterialsAndTransforms();
            rebuildBusTransferArcs();
        });
    });
    slGap.addEventListener('input', () => {
        state.cutGap = Number(slGap.value);
        updateVoxelMaterialsAndTransforms();
        rebuildBusTransferArcs();
    });

    document.querySelectorAll('[data-rot]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const [axis, layerStr, dirStr] = btn.dataset.rot.split(':');
            triggerSliceRotationB(axis, Number(layerStr), Number(dirStr));
        });
    });

    const slProbe = document.getElementById('slider-probe-depth');
    slProbe.addEventListener('input', () => {
        state.probeDepth = Number(slProbe.value);
        document.getElementById('val-probe-depth').textContent = `단면 Y = ${state.probeDepth.toFixed(2)}`;
        renderDeltaSpectrumCanvas();
    });

    document.querySelectorAll('[data-inspect-y]').forEach((btn) => {
        btn.addEventListener('click', () => {
            state.inspectY = Number(btn.dataset.inspectY);
            document.querySelectorAll('[data-inspect-y]').forEach((b) => b.classList.toggle('active', b === btn));
            renderRightInspectors();
        });
    });

    document.getElementById('btn-sync-ab').addEventListener('click', () => {
        state.cellsB = state.cellsA.map((c) => ({ ...c }));
        state.busTransfers = [];
        state.bRotCount = 0;
        document.getElementById('val-rot-count').textContent = 'B 회전 0회';
        refreshAllVisuals();
    });

    document.getElementById('btn-reset-lab').addEventListener('click', () => {
        applyScenario(state.scenario);
    });
}

// Boot
bindUI();
handleResize();
const bootParams = new URLSearchParams(window.location.search);
const initialScenario = bootParams.get('source') === 'elysia' ? 'elysia_cognitive' : 'ssd_to_gpu';
document.querySelectorAll('[data-scen]').forEach((b) =>
    b.classList.toggle('active', b.dataset.scen === initialScenario)
);
applyScenario(initialScenario);
requestAnimationFrame(animate);
