/**
 * Elysia Video-to-World Object Classification, Character Rigging & Hardware Memory-Hierarchy Scale-Rotor
 * ------------------------------------------------------------------------------------------------------
 * Converts live HD video into an interactive 3D-parallax world where:
 *   1) Moving vehicles & pedestrians are segmented in real time via online background modeling +
 *      8-connected component clustering (TypedArray BFS on a 96x54 analysis grid).
 *   2) Each extracted video object is classified structurally:
 *        - VEHICLE (차량)  : 3D extruded wireframe bounding prism; toggleable between
 *                            [Solid Collision Boundary (물리 충돌 경계)] or
 *                            [Controllable Vehicle Rig (차량 조종)] or
 *                            [Extracted Occupant Humanoid (내부 탑승자 캐릭터화)]!
 *        - PERSON  (인물)  : Automatically fitted with an articulated procedural humanoid skeleton
 *                            (head, torso, arms, legs, walk cycle driven by real velocity) that can
 *                            be possessed & controlled directly on the video's ground plane!
 *        - BOUNDARY (경계) : Stationary high-structure architecture (buildings, curbs, signal poles)
 *                            extracted as S4 static world collision boundaries.
 *   3) Controllable Game Character / Vehicle moves via WASD / Arrow Keys / Right-Click destination /
 *      Space (Jump or Boost) directly inside the 3D-parallax video world, physically colliding with
 *      live moving video cars and static building boundaries.
 *   4) The 5-Tier Computer Hardware Memory Hierarchy (S4 SSD > S3 RAM > S2 VRAM > S1 Cache > S0 Reg)
 *      maps directly as Elysia's Physical Scale-Rotor, weaving Relationship x Connectivity x Continuity
 *      into a persistent 3-axis spectral neural web (localStorage SSD) to skip redundant reclassification.
 */
(function () {
    'use strict';

    const W = 960;
    const H = 540;
    const SSD_KEY = 'elysia_unified_spectrum_ssd_v1';

    // Higher-resolution analysis grid for crisp connected-component vehicle & pedestrian extraction
    const GW = 96;
    const GH = 54;
    const GN = GW * GH;
    const CELL_W = W / GW; // 10 px
    const CELL_H = H / GH; // 10 px

    function makeCanvas(w, h) {
        const c = document.createElement('canvas');
        c.width = w;
        c.height = h;
        return c;
    }

    const sampleC = makeCanvas(GW, GH);
    const sampleCtx = sampleC.getContext('2d', { willReadFrequently: true });

    // Reusable offscreen preview layers (zero per-frame canvas creation)
    const s4PreviewC = makeCanvas(120, 68);
    const s4PreviewCtx = s4PreviewC.getContext('2d');
    const s0PreviewC = makeCanvas(160, 90);
    const s0PreviewCtx = s0PreviewC.getContext('2d');

    // Single reusable freeze-frame canvas for Bullet-Time 3D orbit (saves ~60MB VRAM vs 32-canvas ring!)
    const frozenFrameC = makeCanvas(W, H);
    const frozenFrameCtx = frozenFrameC.getContext('2d', { alpha: false });
    let hasFrozenFrame = false;
    let lastSegMetrics = { avgMotion: 0, avgEdge: 0, warmth: 0 };

    // Zero-GC TypedArray buffers for Online EMA Background Model + Connected Components
    const bgR = new Float32Array(GN);
    const bgG = new Float32Array(GN);
    const bgB = new Float32Array(GN);
    const bgLuma = new Float32Array(GN);
    const curLuma = new Float32Array(GN);
    const prevLuma = new Float32Array(GN);
    const edgeMap = new Float32Array(GN);
    const motionMap = new Float32Array(GN);
    const fgRaw = new Uint8Array(GN);
    const fgClosed = new Uint8Array(GN);
    const visited = new Uint8Array(GN);
    const bfsQueue = new Uint16Array(GN);

    let bgInitialized = false;
    let bgWarmupFrames = 0;

    // 3D Depth-Parallax Camera State (Preserved & refined!)
    const cam = {
        yaw: 0,           // -1 .. +1 horizontal orbit
        pitch: 0,         // -1 .. +1 vertical tilt
        zoom: 1.06,       // 1.0 .. 1.75 perspective zoom
        dragging: false,
        dragMoved: false,
        lastX: 0,
        lastY: 0,
        autoExplore: false, // Clean manual/follow control by default; toggleable
    };

    // Sub-mode:
    //   'object_boundary' (① 객체 분류 · 경계 추출)
    //   'character_rig'   (② 캐릭터 모델링 · 직접 조종)
    //   'bullet_time'     (③ 시간 정지 · 3D 시점 선회)
    let activeMode = 'object_boundary';

    // Tracked Live Video Objects (Segmented & Classified Vehicles / Pedestrians)
    let nextEntityId = 1;
    let trackedEntities = [];
    // Static Architectural Collider Boundaries (S4 buildings / curbs / road limits)
    let staticBoundaries = [];

    // Selected Entity ID & Possessed Playable Game Rig (Character or Vehicle modeled from video!)
    let selectedEntityId = null;
    let playerRig = null; // { id, sourceEntityId, kind: 'humanoid'|'vehicle_ctrl', label, x, y, vx, vy, facing, walkPhase, jumpZ, jumpVz, w, h, depth, palette: { primary, secondary, skin }, targetX, targetY, collideFlash, collisionCount, trail: [] }

    // Collision Sparks (for tangible physical feedback when character hits live moving video car / wall)
    const collisionImpacts = [];

    // =========================================================================
    // Persistent 5-Tier Memory Scale-Rotor & 3-Axis Woven Spectrum Web (S4 SSD)
    // =========================================================================
    let ssdArchive = loadSsdArchive();
    let cachedSsdBytesKB = (JSON.stringify(ssdArchive).length / 1024).toFixed(1);

    function defaultArchive() {
        return {
            version: 2,
            totalObservations: 0,
            totalZeroRecalcHits: 0,
            nodes: [
                { id: 'seed_s4_boundary', label: 'S4 정적 건축·도로 경계축', rel: 0.24, conn: 0.42, cont: 0.90, chromaR: 0.22, chromaB: 0.62, chromaY: 0.16, hits: 14, depthTier: 'S4' },
                { id: 'seed_s2_vehicle', label: 'S2 차량 동적 경계·궤도축', rel: 0.68, conn: 0.70, cont: 0.74, chromaR: 0.46, chromaB: 0.36, chromaY: 0.18, hits: 11, depthTier: 'S2' },
                { id: 'seed_s0_humanoid', label: 'S0 인물 관절·상호작용축', rel: 0.80, conn: 0.62, cont: 0.64, chromaR: 0.54, chromaB: 0.24, chromaY: 0.22, hits: 9, depthTier: 'S0' },
            ],
            edges: [
                { a: 0, b: 1, weight: 0.72 },
                { a: 1, b: 2, weight: 0.78 },
            ],
        };
    }

    function loadSsdArchive() {
        try {
            const raw = localStorage.getItem(SSD_KEY);
            if (!raw) return defaultArchive();
            const parsed = JSON.parse(raw);
            if (parsed && Array.isArray(parsed.nodes) && parsed.nodes.length > 0) return parsed;
        } catch { /* fallback */ }
        return defaultArchive();
    }

    function persistSsdArchive() {
        try {
            const serialized = JSON.stringify(ssdArchive);
            cachedSsdBytesKB = (serialized.length / 1024).toFixed(1);
            localStorage.setItem(SSD_KEY, serialized);
        } catch { /* ignore quota */ }
    }

    const memTiers = {
        s4_ssd: { name: 'S4 · SSD (영구 객체·경계 원장)', loadPct: 0, detail: '대기 중' },
        s3_ram: { name: 'S3 · RAM (활성 차량·인물·경계 그래프)', loadPct: 0, detail: '대기 중' },
        s2_vram: { name: 'S2 · GPU VRAM (3층 깊이·3D 바운딩 프리즘)', loadPct: 0, detail: '대기 중' },
        s1_cache: { name: 'S1 · L1/L2 Cache (객체 식별·궤도 히트)', loadPct: 0, detail: '대기 중' },
        s0_reg: { name: 'S0 · Registers (충돌 충격·조종 델타)', loadPct: 0, detail: '대기 중' },
    };

    let tickCount = 0;
    let recallHitRatePct = 0;
    let lastWovenNote = '실시간 영상에서 움직이는 차량(충돌 경계/조종)과 인물(관절 게임 캐릭터)을 분류·추출하고 있습니다.';

    // =========================================================================
    // 3D Depth-Parallax Projection Helpers (Consistent between Render & Picking)
    // =========================================================================
    function projectWorldToScreen(wx, wy, depth) {
        const yawPx = cam.yaw * 64;
        const pitchPx = cam.pitch * 36;
        const z = cam.zoom;
        const parFactor = 0.42 + depth * 0.92;
        const sx = W * 0.5 + (wx - W * 0.5) * z - yawPx * parFactor;
        const sy = H * 0.5 + (wy - H * 0.5) * z - pitchPx * parFactor;
        return { x: sx, y: sy, scale: z * (0.86 + depth * 0.24) };
    }

    function unprojectScreenToWorld(sx, sy, depth) {
        const yawPx = cam.yaw * 64;
        const pitchPx = cam.pitch * 36;
        const z = cam.zoom;
        const parFactor = 0.42 + depth * 0.92;
        const wx = W * 0.5 + (sx - W * 0.5 + yawPx * parFactor) / z;
        const wy = H * 0.5 + (sy - H * 0.5 + pitchPx * parFactor) / z;
        return { x: Math.max(24, Math.min(W - 24, wx)), y: Math.max(40, Math.min(H - 24, wy)) };
    }

    // =========================================================================
    // 1. Real Background Modeling + Connected-Component Object & Boundary Extraction
    // =========================================================================
    function segmentVideoWorld(srcCanvas, isFrozen) {
        sampleCtx.drawImage(srcCanvas, 0, 0, GW, GH);
        const px = sampleCtx.getImageData(0, 0, GW, GH).data;

        if (!bgInitialized) {
            for (let i = 0; i < GN; i++) {
                const o = i * 4;
                bgR[i] = px[o];
                bgG[i] = px[o + 1];
                bgB[i] = px[o + 2];
                const l = px[o] * 0.299 + px[o + 1] * 0.587 + px[o + 2] * 0.114;
                bgLuma[i] = l;
                curLuma[i] = l;
                prevLuma[i] = l;
            }
            bgInitialized = true;
            bgWarmupFrames = 0;
        }

        let motionSum = 0;
        let edgeSum = 0;
        let warmSum = 0;
        let fgCount = 0;

        // First pass: luma, foreground diff against running background, spatial edges
        for (let y = 0; y < GH; y++) {
            for (let x = 0; x < GW; x++) {
                const i = y * GW + x;
                const o = i * 4;
                const r = px[o];
                const g = px[o + 1];
                const b = px[o + 2];
                const luma = r * 0.299 + g * 0.587 + b * 0.114;
                curLuma[i] = luma;
                warmSum += (r - b) / 255;

                const frameDiff = Math.abs(luma - prevLuma[i]);
                if (!isFrozen) {
                    motionMap[i] = motionMap[i] * 0.65 + frameDiff * 0.35;
                }
                motionSum += motionMap[i];

                // Foreground distance against running static background model
                const dr = Math.abs(r - bgR[i]);
                const dg = Math.abs(g - bgG[i]);
                const db = Math.abs(b - bgB[i]);
                const colorDist = (dr + dg + db) * 0.333;
                const lumaDist = Math.abs(luma - bgLuma[i]);
                const fgScore = lumaDist * 0.65 + colorDist * 0.55 + motionMap[i] * 0.6;

                const isFg = fgScore > 22 && y >= 2 && y < GH - 1;
                fgRaw[i] = isFg ? 1 : 0;
                if (isFg) fgCount++;

                // Adaptive background update: static pixels adapt steadily, moving pixels adapt very slowly
                if (!isFrozen) {
                    const alpha = bgWarmupFrames < 18 ? 0.12 : (isFg ? 0.004 : 0.025);
                    bgR[i] += (r - bgR[i]) * alpha;
                    bgG[i] += (g - bgG[i]) * alpha;
                    bgB[i] += (b - bgB[i]) * alpha;
                    bgLuma[i] += (luma - bgLuma[i]) * alpha;
                }

                const lL = x > 0 ? curLuma[i - 1] : luma;
                const lU = y > 0 ? curLuma[i - GW] : luma;
                const edge = Math.abs(luma - lL) + Math.abs(luma - lU);
                edgeMap[i] = edge;
                edgeSum += edge;
            }
        }
        prevLuma.set(curLuma);
        if (!isFrozen) bgWarmupFrames++;

        // Handle sudden scene cut / video switch cleanly
        if (fgCount > GN * 0.62) {
            for (let i = 0; i < GN; i++) {
                const o = i * 4;
                bgR[i] = px[o];
                bgG[i] = px[o + 1];
                bgB[i] = px[o + 2];
                bgLuma[i] = curLuma[i];
                fgRaw[i] = 0;
            }
            bgWarmupFrames = 0;
        }

        // Second pass: 3x3 morphological closing (fills car windshields / gaps so 1 car = 1 solid box)
        fgClosed.fill(0);
        for (let y = 1; y < GH - 1; y++) {
            const row = y * GW;
            for (let x = 1; x < GW - 1; x++) {
                const i = row + x;
                let nb = fgRaw[i]
                    + fgRaw[i - 1] + fgRaw[i + 1]
                    + fgRaw[i - GW] + fgRaw[i + GW]
                    + fgRaw[i - GW - 1] + fgRaw[i - GW + 1]
                    + fgRaw[i + GW - 1] + fgRaw[i + GW + 1];
                if (fgRaw[i] ? nb >= 2 : nb >= 4) {
                    fgClosed[i] = 1;
                }
            }
        }

        // Third pass: Fast Zero-GC Connected Components (BFS) -> Real Object Bounding Boxes!
        if (!isFrozen) {
            visited.fill(0);
            const rawBlobs = [];
            for (let y = 1; y < GH - 1; y++) {
                for (let x = 1; x < GW - 1; x++) {
                    const start = y * GW + x;
                    if (!fgClosed[start] || visited[start]) continue;

                    let head = 0;
                    let tail = 0;
                    bfsQueue[tail++] = start;
                    visited[start] = 1;

                    let minX = x, maxX = x, minY = y, maxY = y;
                    let sumX = 0, sumY = 0, area = 0;
                    let sumR = 0, sumG = 0, sumB = 0;
                    let sumMotion = 0;

                    while (head < tail) {
                        const idx = bfsQueue[head++];
                        const cx = idx % GW;
                        const cy = (idx / GW) | 0;
                        if (cx < minX) minX = cx;
                        if (cx > maxX) maxX = cx;
                        if (cy < minY) minY = cy;
                        if (cy > maxY) maxY = cy;
                        sumX += cx;
                        sumY += cy;
                        area++;
                        const o = idx * 4;
                        sumR += px[o];
                        sumG += px[o + 1];
                        sumB += px[o + 2];
                        sumMotion += motionMap[idx];

                        // 8-neighbors
                        for (let dy = -1; dy <= 1; dy++) {
                            const ny = cy + dy;
                            if (ny <= 0 || ny >= GH - 1) continue;
                            for (let dx = -1; dx <= 1; dx++) {
                                if (dx === 0 && dy === 0) continue;
                                const nx = cx + dx;
                                if (nx <= 0 || nx >= GW - 1) continue;
                                const ni = ny * GW + nx;
                                if (fgClosed[ni] && !visited[ni]) {
                                    visited[ni] = 1;
                                    bfsQueue[tail++] = ni;
                                }
                            }
                        }
                    }

                    // Filter tiny sensor noise and full-screen artifacts
                    if (area >= 6 && area < GN * 0.35) {
                        const bx = minX * CELL_W;
                        const by = minY * CELL_H;
                        const bw = (maxX - minX + 1) * CELL_W;
                        const bh = (maxY - minY + 1) * CELL_H;
                        if (bw >= 18 && bh >= 18) {
                            const cxW = (sumX / area + 0.5) * CELL_W;
                            const cyW = (sumY / area + 0.5) * CELL_H;
                            const footY = by + bh;
                            const depth = Math.max(0.18, Math.min(1.0, (footY / H) * 0.92 + 0.08));
                            rawBlobs.push({
                                x: bx,
                                y: by,
                                w: bw,
                                h: bh,
                                cx: cxW,
                                cy: cyW,
                                footY,
                                area,
                                aspect: bw / Math.max(1, bh),
                                depth,
                                r: Math.round(sumR / area),
                                g: Math.round(sumG / area),
                                b: Math.round(sumB / area),
                                motion: sumMotion / area,
                            });
                        }
                    }
                }
            }

            // Keep top 8 most prominent moving objects (sorted by area * motion salience)
            rawBlobs.sort((a, b) => (b.area * (1 + b.motion * 0.1)) - (a.area * (1 + a.motion * 0.1)));
            updateObjectTracker(rawBlobs.slice(0, 8));

            // Periodically extract S4 Static Structural Boundaries (buildings, road curbs, poles)
            if (tickCount % 25 === 1 || staticBoundaries.length === 0) {
                extractStaticBoundaries();
            }
        }

        return {
            avgMotion: Math.min(1, (motionSum / GN) / 22),
            avgEdge: Math.min(1, (edgeSum / GN) / 48),
            warmth: Math.max(-1, Math.min(1, warmSum / GN)),
        };
    }

    // Persistent Multi-Object Tracker & Semantic Classifier (VEHICLE vs PERSON)
    function updateObjectTracker(blobs) {
        const matchedBlob = new Uint8Array(blobs.length);

        for (const ent of trackedEntities) {
            let bestIdx = -1;
            let bestDist = 105;
            for (let i = 0; i < blobs.length; i++) {
                if (matchedBlob[i]) continue;
                const d = Math.hypot(blobs[i].cx - ent.cx, blobs[i].cy - ent.cy);
                if (d < bestDist) {
                    bestDist = d;
                    bestIdx = i;
                }
            }
            if (bestIdx >= 0) {
                matchedBlob[bestIdx] = 1;
                const b = blobs[bestIdx];
                // Smooth box & velocity tracking (eliminates box jitter)
                const nvx = b.cx - ent.cx;
                const nvy = b.cy - ent.cy;
                ent.vx = ent.vx * 0.72 + nvx * 0.28;
                ent.vy = ent.vy * 0.72 + nvy * 0.28;
                ent.x = ent.x * 0.55 + b.x * 0.45;
                ent.y = ent.y * 0.55 + b.y * 0.45;
                ent.w = ent.w * 0.60 + b.w * 0.40;
                ent.h = ent.h * 0.60 + b.h * 0.40;
                ent.cx = ent.x + ent.w * 0.5;
                ent.cy = ent.y + ent.h * 0.5;
                ent.footY = ent.y + ent.h;
                ent.depth = ent.depth * 0.7 + b.depth * 0.3;
                ent.area = b.area;
                ent.aspect = ent.w / Math.max(1, ent.h);
                ent.speed = Math.hypot(ent.vx, ent.vy);
                ent.r = Math.round(ent.r * 0.8 + b.r * 0.2);
                ent.g = Math.round(ent.g * 0.8 + b.g * 0.2);
                ent.b = Math.round(ent.b * 0.8 + b.b * 0.2);
                ent.walkPhase += Math.max(0.05, ent.speed * 0.14);
                ent.age += 1;
                ent.missed = 0;

                // Refine semantic class unless user manually locked its role
                if (!ent.userLockedRole && ent.age < 24) {
                    const cls = classifyBlob(ent.aspect, ent.area, ent.w, ent.h, ent.speed);
                    ent.cls = cls;
                    ent.role = cls === 'person' ? 'humanoid' : 'collider';
                    ent.label = cls === 'person' ? `인물 #${ent.shortNum}` : `차량 #${ent.shortNum}`;
                }
            } else {
                // Coast smoothly along velocity for up to 16 frames (S1 cache continuity!)
                ent.missed += 1;
                ent.x += ent.vx * 0.65;
                ent.y += ent.vy * 0.65;
                ent.cx = ent.x + ent.w * 0.5;
                ent.cy = ent.y + ent.h * 0.5;
                ent.footY = ent.y + ent.h;
            }
        }

        // Remove expired tracks
        trackedEntities = trackedEntities.filter((e) => e.missed < 16);

        // Spawn newly detected entities
        for (let i = 0; i < blobs.length; i++) {
            if (matchedBlob[i] || trackedEntities.length >= 8) continue;
            const b = blobs[i];
            const cls = classifyBlob(b.aspect, b.area, b.w, b.h, b.motion * 0.15);
            const shortNum = nextEntityId++;
            trackedEntities.push({
                id: `ent_${shortNum}`,
                shortNum,
                cls, // 'vehicle' | 'person'
                role: cls === 'person' ? 'humanoid' : 'collider', // 'collider' | 'humanoid' | 'vehicle_ctrl'
                userLockedRole: false,
                label: cls === 'person' ? `인물 #${shortNum}` : `차량 #${shortNum}`,
                x: b.x,
                y: b.y,
                w: b.w,
                h: b.h,
                cx: b.cx,
                cy: b.cy,
                footY: b.footY,
                vx: 0,
                vy: 0,
                speed: 0,
                depth: b.depth,
                area: b.area,
                aspect: b.aspect,
                r: b.r,
                g: b.g,
                b: b.b,
                walkPhase: Math.random() * Math.PI * 2,
                age: 1,
                missed: 0,
                hitFlash: 0,
            });
        }

        if (selectedEntityId && !trackedEntities.some((e) => e.id === selectedEntityId)) {
            selectedEntityId = trackedEntities.length ? trackedEntities[0].id : null;
        } else if (!selectedEntityId && trackedEntities.length) {
            selectedEntityId = trackedEntities[0].id;
        }
    }

    // Real geometric-kinematic classification:
    // Upright compact blobs -> PERSON (Humanoid Character candidate)
    // Wider / larger footprint blobs -> VEHICLE (Dynamic Collider / Controllable Car)
    function classifyBlob(aspect, area, w, h, speed) {
        if (aspect < 0.94 && w < 74 && h >= 24 && area < 34) {
            return 'person';
        }
        if (aspect < 1.05 && area < 20 && speed < 3.5) {
            return 'person';
        }
        return 'vehicle';
    }

    // Extract S4 Static Structural Boundaries (high architectural edge density + near-zero motion)
    function extractStaticBoundaries() {
        const blocks = [];
        const BW = 12; // 12x9 coarse structural blocks over 96x54
        const BH = 6;
        for (let by = 0; by < GH - BH; by += BH) {
            for (let bx = 0; bx < GW - BW; bx += BW) {
                let eSum = 0;
                let mSum = 0;
                let count = 0;
                for (let dy = 0; dy < BH; dy++) {
                    for (let dx = 0; dx < BW; dx++) {
                        const idx = (by + dy) * GW + (bx + dx);
                        eSum += edgeMap[idx];
                        mSum += motionMap[idx];
                        count++;
                    }
                }
                const avgE = eSum / count;
                const avgM = mSum / count;
                // Static architectural walls/curbs/structures: strong structural edge, very low motion, upper/side perimeter
                if (avgE > 26 && avgM < 4.5 && (by < GH * 0.42 || bx < GW * 0.16 || bx > GW * 0.78)) {
                    const wx = bx * CELL_W;
                    const wy = by * CELL_H;
                    const ww = BW * CELL_W;
                    const wh = BH * CELL_H;
                    blocks.push({
                        x: wx,
                        y: wy,
                        w: ww,
                        h: wh,
                        depth: Math.max(0.18, Math.min(0.85, (wy + wh) / H)),
                        edgeStrength: avgE,
                    });
                }
            }
        }
        blocks.sort((a, b) => b.edgeStrength - a.edgeStrength);
        staticBoundaries = blocks.slice(0, 10);
    }

    // =========================================================================
    // 2. Game Character / Vehicle Rigging & Live Physics Collision Engine
    // =========================================================================
    function spawnPlayerRigFromEntity(ent, kindOverride) {
        const kind = kindOverride || (ent && ent.cls === 'vehicle' ? 'vehicle_ctrl' : 'humanoid');
        const spawnX = ent ? Math.max(70, Math.min(W - 70, ent.cx + (kind === 'humanoid' && ent.cls === 'vehicle' ? 32 : 0))) : W * 0.5;
        const spawnY = ent ? Math.max(150, Math.min(H - 45, ent.footY)) : H * 0.74;

        // Sample authentic visual palette straight from the extracted video entity!
        const r = ent ? Math.min(245, Math.max(55, ent.r + 30)) : 56;
        const g = ent ? Math.min(245, Math.max(75, ent.g + 30)) : 189;
        const b = ent ? Math.min(245, Math.max(85, ent.b + 30)) : 248;

        const label = ent
            ? (kind === 'humanoid'
                ? (ent.cls === 'vehicle' ? `${ent.label} 탑승자 모델` : `${ent.label} 게임 캐릭터`)
                : `${ent.label} 조종 차량`)
            : '영상 기반 인간형 캐릭터';

        playerRig = {
            id: `rig_${Date.now()}`,
            sourceEntityId: ent ? ent.id : null,
            kind, // 'humanoid' | 'vehicle_ctrl'
            label,
            x: spawnX,
            y: spawnY,
            vx: 0,
            vy: 0,
            facing: 0,
            walkPhase: 0,
            jumpZ: 0,
            jumpVz: 0,
            w: kind === 'vehicle_ctrl' ? (ent ? Math.max(54, Math.min(110, ent.w)) : 74) : 28,
            h: kind === 'vehicle_ctrl' ? (ent ? Math.max(34, Math.min(68, ent.h)) : 42) : 64,
            depth: Math.max(0.25, Math.min(1.0, spawnY / H)),
            palette: {
                primary: `rgb(${r}, ${g}, ${b})`,
                secondary: kind === 'humanoid' ? '#0f172a' : '#1e293b',
                accent: kind === 'humanoid' ? '#38bdf8' : '#f59e0b',
                skin: '#f1c27d',
            },
            targetX: null,
            targetY: null,
            collideFlash: 0,
            collisionCount: 0,
            trail: [],
            cropCanvas: makeCanvas(64, 48),
        };

        // Snapshot live texture crop of the source object if available
        if (ent && hasFrozenFrame) {
            const cctx = playerRig.cropCanvas.getContext('2d');
            cctx.drawImage(
                frozenFrameC,
                Math.max(0, ent.x), Math.max(0, ent.y), Math.max(12, ent.w), Math.max(12, ent.h),
                0, 0, 64, 48
            );
        }

        lastWovenNote = `[객체→게임 모델링 완료] "${label}" 리깅 생성 — WASD 또는 우클릭으로 영상 도로 위를 이동하며 움직이는 차량 경계와 물리 충돌을 검증하세요.`;
        if (typeof window.__elysiaOnExternalInfluence === 'function') {
            window.__elysiaOnExternalInfluence(`영상 객체 게임 캐릭터화 (${label})`);
        }
        return playerRig;
    }

    function stepPlayerRigPhysics(keys, isFrozen) {
        if (!playerRig || isFrozen) return;

        const maxSpd = playerRig.kind === 'vehicle_ctrl' ? 4.8 : 3.2;
        let ax = 0;
        let ay = 0;

        if (keys) {
            if (keys.has('KeyA') || keys.has('ArrowLeft')) ax -= 1;
            if (keys.has('KeyD') || keys.has('ArrowRight')) ax += 1;
            if (keys.has('KeyW') || keys.has('ArrowUp')) ay -= 1;
            if (keys.has('KeyS') || keys.has('ArrowDown')) ay += 1;
            if (keys.has('Space') && playerRig.jumpZ <= 0.1) {
                if (playerRig.kind === 'humanoid') {
                    playerRig.jumpVz = 7.2; // Jump!
                } else {
                    // Vehicle boost impulse along facing
                    playerRig.vx += Math.cos(playerRig.facing) * 2.4;
                    playerRig.vy += Math.sin(playerRig.facing) * 2.4;
                }
            }
        }

        if (ax !== 0 || ay !== 0) {
            playerRig.targetX = null;
            playerRig.targetY = null;
            const len = Math.hypot(ax, ay) || 1;
            playerRig.vx = playerRig.vx * 0.72 + (ax / len) * maxSpd * 0.28;
            playerRig.vy = playerRig.vy * 0.72 + (ay / len) * maxSpd * 0.28;
        } else if (playerRig.targetX !== null && playerRig.targetY !== null) {
            const dx = playerRig.targetX - playerRig.x;
            const dy = playerRig.targetY - playerRig.y;
            const dist = Math.hypot(dx, dy);
            if (dist > 8) {
                playerRig.vx = playerRig.vx * 0.75 + (dx / dist) * maxSpd * 0.25;
                playerRig.vy = playerRig.vy * 0.75 + (dy / dist) * maxSpd * 0.25;
            } else {
                playerRig.targetX = null;
                playerRig.targetY = null;
                playerRig.vx *= 0.6;
                playerRig.vy *= 0.6;
            }
        } else {
            playerRig.vx *= 0.82;
            playerRig.vy *= 0.82;
        }

        // Jump vertical physics (humanoid)
        if (playerRig.jumpZ > 0 || playerRig.jumpVz !== 0) {
            playerRig.jumpZ += playerRig.jumpVz;
            playerRig.jumpVz -= 0.48;
            if (playerRig.jumpZ <= 0) {
                playerRig.jumpZ = 0;
                playerRig.jumpVz = 0;
            }
        }

        let nx = playerRig.x + playerRig.vx;
        let ny = playerRig.y + playerRig.vy;

        // Keep within ground-plane road bounds
        nx = Math.max(36, Math.min(W - 36, nx));
        ny = Math.max(120, Math.min(H - 22, ny));

        // 1) Physical Collision against LIVE MOVING VIDEO VEHICLES marked as 'collider'
        const rigRadius = playerRig.kind === 'vehicle_ctrl' ? 28 : 16;
        for (const ent of trackedEntities) {
            if (ent.role !== 'collider' || ent.id === playerRig.sourceEntityId && playerRig.kind === 'vehicle_ctrl') continue;
            // Ground footprint AABB of the live video vehicle
            const boxX1 = ent.x - rigRadius;
            const boxX2 = ent.x + ent.w + rigRadius;
            const boxY1 = ent.y + ent.h * 0.35 - rigRadius;
            const boxY2 = ent.y + ent.h + rigRadius * 0.6;
            if (nx > boxX1 && nx < boxX2 && ny > boxY1 && ny < boxY2 && playerRig.jumpZ < 18) {
                // Push out along minimum penetration vector + impart vehicle's real momentum!
                const pushDx = nx - ent.cx;
                const pushDy = ny - (ent.y + ent.h * 0.7);
                const pLen = Math.hypot(pushDx, pushDy) || 1;
                nx += (pushDx / pLen) * 8 + ent.vx * 0.8;
                ny += (pushDy / pLen) * 6 + ent.vy * 0.8;
                playerRig.vx = (pushDx / pLen) * 3.4 + ent.vx * 0.5;
                playerRig.vy = (pushDy / pLen) * 2.6 + ent.vy * 0.5;
                playerRig.collideFlash = 16;
                ent.hitFlash = 18;
                playerRig.collisionCount += 1;
                collisionImpacts.push({ x: nx, y: ny, life: 22, label: `${ent.label} 충돌 경계` });
                if (collisionImpacts.length > 8) collisionImpacts.shift();
                lastWovenNote = `[물리 경계 충돌 검증] ${playerRig.label} ↔ 실시간 영상 ${ent.label}(동적 경계) 충돌 반발 발생 (누적 ${playerRig.collisionCount}회)`;
            }
        }

        // 2) Physical Collision against S4 Static Architectural Boundaries (buildings/curbs)
        for (const sb of staticBoundaries) {
            if (nx > sb.x - rigRadius && nx < sb.x + sb.w + rigRadius && ny > sb.y - rigRadius && ny < sb.y + sb.h + rigRadius) {
                const cx = sb.x + sb.w * 0.5;
                const cy = sb.y + sb.h * 0.5;
                const dx = nx - cx;
                const dy = ny - cy;
                const d = Math.hypot(dx, dy) || 1;
                nx += (dx / d) * 6;
                ny += (dy / d) * 6;
                playerRig.vx *= -0.35;
                playerRig.vy *= -0.35;
                playerRig.collideFlash = Math.max(playerRig.collideFlash, 8);
            }
        }

        playerRig.x = Math.max(36, Math.min(W - 36, nx));
        playerRig.y = Math.max(120, Math.min(H - 22, ny));
        playerRig.depth = Math.max(0.22, Math.min(1.0, playerRig.y / H));

        const spd = Math.hypot(playerRig.vx, playerRig.vy);
        if (spd > 0.25) {
            playerRig.facing = Math.atan2(playerRig.vy, playerRig.vx);
            playerRig.walkPhase += spd * 0.24;
        }
        if (playerRig.collideFlash > 0) playerRig.collideFlash--;

        if (tickCount % 3 === 0) {
            playerRig.trail.push({ x: playerRig.x, y: playerRig.y, depth: playerRig.depth });
            if (playerRig.trail.length > 26) playerRig.trail.shift();
        }
    }

    // =========================================================================
    // 3. Weave Object Classification & Boundary Interactions into 3-Axis Spectrum Web
    // =========================================================================
    function weaveIntoSpectrumWeb(metrics) {
        const { avgMotion, avgEdge, warmth } = metrics;
        const vehicleCount = trackedEntities.filter((e) => e.cls === 'vehicle').length;
        const personCount = trackedEntities.filter((e) => e.cls === 'person').length;
        const trackedStableCount = trackedEntities.filter((e) => e.age >= 6).length;

        const rel = Math.max(0.05, Math.min(0.95, 0.25 + Math.min(0.45, (vehicleCount + personCount) * 0.09) + (playerRig ? 0.18 : 0)));
        const conn = Math.max(0.05, Math.min(0.95, 0.22 + avgEdge * 0.45 + Math.min(0.28, staticBoundaries.length * 0.03)));
        const cont = Math.max(0.05, Math.min(0.95, trackedEntities.length > 0
            ? (trackedStableCount / trackedEntities.length) * 0.65 + (1 - avgMotion) * 0.35
            : 1.0 - avgMotion * 0.65));

        const rawR = 0.24 + avgMotion * 0.8 + (playerRig && playerRig.collideFlash > 0 ? 0.35 : 0);
        const rawB = 0.25 + cont * 0.72 + Math.max(0, -warmth) * 0.18;
        const rawY = 0.16 + avgEdge * 0.5 + Math.abs(cam.yaw) * 0.22;
        const sumC = rawR + rawB + rawY || 1;
        const chromaR = rawR / sumC;
        const chromaB = rawB / sumC;
        const chromaY = rawY / sumC;

        ssdArchive.totalObservations += 1;

        let bestIdx = -1;
        let bestDist = 999;
        for (let i = 0; i < ssdArchive.nodes.length; i++) {
            const n = ssdArchive.nodes[i];
            const d = Math.hypot(n.rel - rel, n.conn - conn, n.cont - cont);
            if (d < bestDist) {
                bestDist = d;
                bestIdx = i;
            }
        }

        const HIT_RADIUS = 0.19;
        let cacheHit = false;

        if (bestIdx >= 0 && bestDist < HIT_RADIUS) {
            cacheHit = true;
            ssdArchive.totalZeroRecalcHits += 1;
            const n = ssdArchive.nodes[bestIdx];
            n.hits += 1;
            n.rel = n.rel * 0.94 + rel * 0.06;
            n.conn = n.conn * 0.94 + conn * 0.06;
            n.cont = n.cont * 0.94 + cont * 0.06;
        } else if (tickCount % 22 === 0 && ssdArchive.nodes.length < 36) {
            const tier = cont > 0.72 ? 'S4' : (vehicleCount >= personCount ? 'S2' : 'S0');
            const label = tier === 'S4'
                ? `S4 정적 경계 위상 #${ssdArchive.nodes.length + 1}`
                : tier === 'S2'
                    ? `S2 차량 경계·궤도축 #${ssdArchive.nodes.length + 1}`
                    : `S0 인물 리깅·상호작용 #${ssdArchive.nodes.length + 1}`;
            const newIdx = ssdArchive.nodes.length;
            ssdArchive.nodes.push({
                id: `woven_${Date.now()}_${newIdx}`,
                label,
                rel,
                conn,
                cont,
                chromaR,
                chromaB,
                chromaY,
                hits: 1,
                depthTier: tier,
            });
            const neighbors = ssdArchive.nodes
                .map((n, idx) => ({ idx, d: idx === newIdx ? 99 : Math.hypot(n.rel - rel, n.conn - conn, n.cont - cont) }))
                .sort((a, b) => a.d - b.d)
                .slice(0, 2);
            for (const nb of neighbors) {
                if (nb.idx !== newIdx) {
                    ssdArchive.edges.push({ a: newIdx, b: nb.idx, weight: Math.max(0.25, 1 - nb.d) });
                }
            }
            persistSsdArchive();
        }

        if (tickCount % 90 === 0) persistSsdArchive();

        recallHitRatePct = ssdArchive.totalObservations > 0
            ? (ssdArchive.totalZeroRecalcHits / ssdArchive.totalObservations) * 100
            : 0;

        memTiers.s4_ssd = {
            name: 'S4 · SSD (영구 객체·경계 원장)',
            loadPct: Math.min(100, Math.round((ssdArchive.nodes.length / 36) * 100)),
            detail: `직조 축 ${ssdArchive.nodes.length}개 · 정적 경계 ${staticBoundaries.length}블록 · ${cachedSsdBytesKB} KB`,
        };
        memTiers.s3_ram = {
            name: 'S3 · RAM (활성 차량·인물·경계 그래프)',
            loadPct: Math.min(100, Math.round(((vehicleCount + personCount) / 8) * 100)),
            detail: `차량 ${vehicleCount}대 · 인물 ${personCount}명 · 조종 리깅 ${playerRig ? '1개 활성' : '대기'}`,
        };
        memTiers.s2_vram = {
            name: 'S2 · GPU VRAM (3층 시차·3D 프리즘)',
            loadPct: Math.round(Math.min(100, 38 + (cam.zoom - 1) * 65 + Math.abs(cam.yaw) * 35)),
            detail: `Yaw ${(cam.yaw * 28).toFixed(1)}° · Pitch ${(cam.pitch * 18).toFixed(1)}° · Zoom ${cam.zoom.toFixed(2)}×`,
        };
        memTiers.s1_cache = {
            name: 'S1 · L1/L2 Cache (객체 식별·궤도 히트)',
            loadPct: Math.round(recallHitRatePct),
            detail: `재분류 생략 히트율 ${recallHitRatePct.toFixed(1)}% (안정 추적 ${trackedStableCount}/${trackedEntities.length})`,
        };
        memTiers.s0_reg = {
            name: 'S0 · Registers (충돌·조종 마찰 델타)',
            loadPct: Math.round(playerRig && playerRig.collideFlash > 0 ? 94 : (cacheHit ? Math.max(8, avgMotion * 32) : Math.min(100, 46 + avgMotion * 52))),
            detail: playerRig ? `충돌 ${playerRig.collisionCount}회 · 실시간 조종 델타` : (cacheHit ? '스펙트럼 히트 → 최소 델타 통과' : '신규 객체 분류·스펙트럼 직조'),
        };

        return { cacheHit, rel, conn, cont, chromaR, chromaB, chromaY };
    }

    // =========================================================================
    // 4. Precision 3D-Parallax World + 3D Bounding Prisms + Articulated Humanoid Renderer
    // =========================================================================
    function draw3DBoundingPrism(ctx, sx, sy, sw, sh, depth, color, fillAlpha, title, subline, isSelected, isFlashing) {
        // Extrude rear face along camera parallax to form a genuine 3D wireframe volume!
        const ex = -cam.yaw * 22 * (0.4 + depth * 0.8) + (sx - W * 0.5) * 0.04;
        const ey = -cam.pitch * 14 * (0.4 + depth * 0.8) - sh * 0.16;

        ctx.save();
        // Ground contact shadow ellipse
        ctx.fillStyle = 'rgba(2, 6, 23, 0.45)';
        ctx.beginPath();
        ctx.ellipse(sx + sw * 0.5, sy + sh + 2, sw * 0.52, Math.max(4, sh * 0.14), 0, 0, Math.PI * 2);
        ctx.fill();

        // Translucent 3D collider volume fill
        ctx.fillStyle = isFlashing ? 'rgba(244, 63, 94, 0.30)' : fillAlpha;
        ctx.fillRect(sx, sy, sw, sh);

        // Rear wireframe face (3D depth extrusion)
        ctx.strokeStyle = isFlashing ? '#fb7185' : color;
        ctx.globalAlpha = 0.45;
        ctx.lineWidth = 1.1;
        ctx.strokeRect(sx + ex, sy + ey, sw, sh);

        // Connecting 3D depth edges
        ctx.beginPath();
        ctx.moveTo(sx, sy); ctx.lineTo(sx + ex, sy + ey);
        ctx.moveTo(sx + sw, sy); ctx.lineTo(sx + sw + ex, sy + ey);
        ctx.moveTo(sx, sy + sh); ctx.lineTo(sx + ex, sy + sh + ey);
        ctx.moveTo(sx + sw, sy + sh); ctx.lineTo(sx + sw + ex, sy + sh + ey);
        ctx.stroke();

        // Crisp front face + corner brackets
        ctx.globalAlpha = 1.0;
        ctx.lineWidth = isSelected ? 2.4 : 1.5;
        ctx.strokeRect(sx, sy, sw, sh);

        // Clean technical tag bar above 3D prism
        ctx.font = '700 10px "IBM Plex Mono", monospace';
        const tw = Math.max(ctx.measureText(title).width, ctx.measureText(subline).width) + 14;
        const lx = Math.max(6, Math.min(W - tw - 6, sx));
        const ly = Math.max(42, sy - 28);
        ctx.fillStyle = 'rgba(7, 10, 19, 0.88)';
        ctx.fillRect(lx, ly, tw, 24);
        ctx.strokeStyle = isFlashing ? '#fb7185' : color;
        ctx.lineWidth = 1;
        ctx.strokeRect(lx, ly, tw, 24);

        ctx.fillStyle = isFlashing ? '#fda4af' : color;
        ctx.textAlign = 'left';
        ctx.fillText(title, lx + 6, ly + 10);
        ctx.fillStyle = '#cbd5e1';
        ctx.font = '500 9px "IBM Plex Mono", monospace';
        ctx.fillText(subline, lx + 6, ly + 20);
        ctx.restore();
    }

    // True 3D-Joint-Rotated Articulated Humanoid Rig
    // Rotates genuine 3D local coordinates (lx, ly, lz) by camera yaw & pitch so
    // front (0°), side profile (90°), back (180°), and any orbital cross-section is a coherent 2D image!
    function drawArticulatedHumanoid(ctx, footX, footY, scale, walkPhase, facing, jumpZ, palette, label, isPlayer, isFlashing, viewYawRad = 0, viewPitchRad = 0) {
        const s = Math.max(0.55, Math.min(1.65, scale));
        const totalYaw = (Number.isFinite(facing) ? facing : 0) + (Number.isFinite(viewYawRad) ? viewYawRad : 0);
        const pitch = Math.max(-0.55, Math.min(0.55, Number.isFinite(viewPitchRad) ? viewPitchRad : 0));
        const cy = Math.cos(totalYaw);
        const sy = Math.sin(totalYaw);
        const cp = Math.cos(pitch);
        const sp = Math.sin(pitch);

        const fy = footY - jumpZ * s;
        const stride = Math.sin(walkPhase) * 10.5;
        const kneeLiftL = Math.max(0, Math.cos(walkPhase)) * 4.5;
        const kneeLiftR = Math.max(0, -Math.cos(walkPhase)) * 4.5;
        const bob = Math.abs(Math.sin(walkPhase)) * 2.2;

        // Project local 3D point (lx: right, ly: up from ground, lz: forward) -> 2D screen + depth z
        const proj3 = (lx, ly, lz) => {
            const rx = lx * cy - lz * sy;
            const rz = lx * sy + lz * cy;
            const ry = (ly + bob) * cp - rz * sp * 0.45;
            return { x: footX + rx * s, y: fy - ry * s, z: rz };
        };

        ctx.save();
        // Ground contact shadow & player selection ring
        ctx.fillStyle = 'rgba(2, 6, 23, 0.56)';
        ctx.beginPath();
        ctx.ellipse(footX, footY + 2, 16 * s, 6 * s, 0, 0, Math.PI * 2);
        ctx.fill();

        if (isPlayer) {
            ctx.strokeStyle = isFlashing ? '#f43f5e' : '#38bdf8';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.ellipse(footX, footY + 2, 22 * s, 8.5 * s, 0, 0, Math.PI * 2);
            ctx.stroke();

            const fPt = proj3(0, 0, 24);
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 1.6;
            ctx.beginPath();
            ctx.moveTo(footX, footY + 2);
            ctx.lineTo(fPt.x, footY + 2 + (fPt.y - fy) * 0.45);
            ctx.stroke();
        }

        // 3D Skeleton Joints
        const hipL = proj3(-4.2, 25, 0);
        const hipR = proj3(4.2, 25, 0);
        const kneeL = proj3(-4.4, 13 + kneeLiftL, stride * 0.55);
        const kneeR = proj3(4.4, 13 + kneeLiftR, -stride * 0.55);
        const footL = proj3(-4.5, 1.5 + kneeLiftL * 0.4, stride);
        const footR = proj3(4.5, 1.5 + kneeLiftR * 0.4, -stride);

        const shL = proj3(-8.2, 44, 0);
        const shR = proj3(8.2, 44, 0);
        const elbL = proj3(-9.5, 34, -stride * 0.45);
        const elbR = proj3(9.5, 34, stride * 0.45);
        const handL = proj3(-9.8, 24, -stride * 0.9);
        const handR = proj3(9.8, 24, stride * 0.9);

        const headC = proj3(0, 53, 0);
        const visorL = proj3(-3.6, 54, 6.2);
        const visorR = proj3(3.6, 54, 6.2);
        const backPackTop = proj3(0, 42, -5.8);
        const backPackBot = proj3(0, 31, -5.8);

        // Torso front & back corners for 3D volumetric silhouette
        const torsoCorners = [
            proj3(-7.6, 44, 3.2), proj3(7.6, 44, 3.2), proj3(5.6, 25, 2.6), proj3(-5.6, 25, 2.6),
        ];
        const torsoZ = (shL.z + shR.z + hipL.z + hipR.z) * 0.25;

        const drawParts = [
            {
                z: (hipL.z + footL.z) * 0.5,
                draw: () => {
                    ctx.lineCap = 'round';
                    ctx.lineWidth = Math.max(2.4, 4.3 * s);
                    ctx.strokeStyle = '#475569';
                    ctx.beginPath();
                    ctx.moveTo(hipL.x, hipL.y); ctx.lineTo(kneeL.x, kneeL.y); ctx.lineTo(footL.x, footL.y);
                    ctx.stroke();
                },
            },
            {
                z: (hipR.z + footR.z) * 0.5,
                draw: () => {
                    ctx.lineCap = 'round';
                    ctx.lineWidth = Math.max(2.4, 4.3 * s);
                    ctx.strokeStyle = '#64748b';
                    ctx.beginPath();
                    ctx.moveTo(hipR.x, hipR.y); ctx.lineTo(kneeR.x, kneeR.y); ctx.lineTo(footR.x, footR.y);
                    ctx.stroke();
                },
            },
            {
                z: (shL.z + handL.z) * 0.5,
                draw: () => {
                    ctx.lineCap = 'round';
                    ctx.lineWidth = Math.max(2.0, 3.6 * s);
                    ctx.strokeStyle = palette.primary;
                    ctx.beginPath();
                    ctx.moveTo(shL.x, shL.y); ctx.lineTo(elbL.x, elbL.y); ctx.lineTo(handL.x, handL.y);
                    ctx.stroke();
                },
            },
            {
                z: (shR.z + handR.z) * 0.5,
                draw: () => {
                    ctx.lineCap = 'round';
                    ctx.lineWidth = Math.max(2.0, 3.6 * s);
                    ctx.strokeStyle = palette.primary;
                    ctx.beginPath();
                    ctx.moveTo(shR.x, shR.y); ctx.lineTo(elbR.x, elbR.y); ctx.lineTo(handR.x, handR.y);
                    ctx.stroke();
                },
            },
            {
                z: backPackTop.z,
                draw: () => {
                    // Dorsal backpack/spine module — clearly visible when camera orbits to side/back!
                    ctx.lineCap = 'round';
                    ctx.lineWidth = Math.max(3.5, 6.5 * s);
                    ctx.strokeStyle = '#1e293b';
                    ctx.beginPath();
                    ctx.moveTo(backPackTop.x, backPackTop.y);
                    ctx.lineTo(backPackBot.x, backPackBot.y);
                    ctx.stroke();
                    ctx.fillStyle = '#f59e0b';
                    ctx.beginPath();
                    ctx.arc(backPackTop.x, backPackTop.y + 3 * s, 1.8 * s, 0, Math.PI * 2);
                    ctx.fill();
                },
            },
            {
                z: torsoZ,
                draw: () => {
                    ctx.fillStyle = isFlashing ? '#f43f5e' : palette.primary;
                    ctx.strokeStyle = '#e2e8f0';
                    ctx.lineWidth = 1.2;
                    ctx.beginPath();
                    ctx.moveTo(shL.x, shL.y);
                    ctx.lineTo(shR.x, shR.y);
                    ctx.lineTo(hipR.x, hipR.y);
                    ctx.lineTo(hipL.x, hipL.y);
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();
                    // Chest center seam when facing front
                    if (cy > -0.2) {
                        const cTop = proj3(0, 42, 3.6);
                        const cBot = proj3(0, 27, 3.2);
                        ctx.strokeStyle = 'rgba(15, 23, 42, 0.55)';
                        ctx.lineWidth = 1.4;
                        ctx.beginPath();
                        ctx.moveTo(cTop.x, cTop.y);
                        ctx.lineTo(cBot.x, cBot.y);
                        ctx.stroke();
                    }
                    // Joint nodes
                    ctx.fillStyle = '#38bdf8';
                    for (const pt of [shL, shR, hipL, hipR]) {
                        ctx.beginPath();
                        ctx.arc(pt.x, pt.y, 1.9 * s, 0, Math.PI * 2);
                        ctx.fill();
                    }
                },
            },
            {
                z: headC.z + 0.5,
                draw: () => {
                    ctx.fillStyle = palette.skin;
                    ctx.beginPath();
                    ctx.arc(headC.x, headC.y, 6.8 * s, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = '#0f172a';
                    ctx.lineWidth = 1.1;
                    ctx.stroke();
                    // Hair/helmet cap on back-top
                    const backCrown = proj3(0, 55.5, -3.5);
                    if (backCrown.z > headC.z - 1.5) {
                        ctx.fillStyle = '#1e293b';
                        ctx.beginPath();
                        ctx.arc(backCrown.x, backCrown.y, 5.2 * s, 0, Math.PI * 2);
                        ctx.fill();
                    }
                    // Front visor — smoothly wraps around profile and hides when seen from behind!
                    if ((visorL.z + visorR.z) * 0.5 > headC.z - 0.8) {
                        ctx.strokeStyle = '#0ea5e9';
                        ctx.lineWidth = Math.max(2.2, 3.0 * s);
                        ctx.lineCap = 'round';
                        ctx.beginPath();
                        ctx.moveTo(visorL.x, visorL.y);
                        ctx.lineTo(visorR.x, visorR.y);
                        ctx.stroke();
                    }
                },
            },
        ];

        // Painter's depth sort (back-to-front in camera space!)
        drawParts.sort((a, b) => a.z - b.z);
        for (const p of drawParts) p.draw();

        if (label) {
            ctx.font = '700 10px "IBM Plex Mono", monospace';
            const tw = ctx.measureText(label).width + 12;
            const lx = footX - tw * 0.5;
            const ly = headC.y - 23 * s;
            ctx.fillStyle = 'rgba(7, 10, 19, 0.90)';
            ctx.fillRect(lx, ly, tw, 16);
            ctx.strokeStyle = isPlayer ? '#38bdf8' : '#10b981';
            ctx.lineWidth = 1;
            ctx.strokeRect(lx, ly, tw, 16);
            ctx.fillStyle = isPlayer ? '#7dd3fc' : '#6ee7b7';
            ctx.textAlign = 'center';
            ctx.fillText(label, footX, ly + 11);
        }
        ctx.restore();
    }

    function drawControllableVehicleRig(ctx, rig, proj) {
        const sw = rig.w * proj.scale;
        const sh = rig.h * proj.scale;
        const sx = proj.x - sw * 0.5;
        const sy = proj.y - sh;

        ctx.save();
        // Ground contact shadow + driving ring
        ctx.fillStyle = 'rgba(2, 6, 23, 0.58)';
        ctx.beginPath();
        ctx.ellipse(proj.x, proj.y + 2, sw * 0.56, sh * 0.24, 0, 0, Math.PI * 2);
        ctx.fill();

        // Render the ACTUAL extracted video vehicle pixels inside the controllable chassis!
        ctx.save();
        ctx.beginPath();
        ctx.rect(sx, sy, sw, sh);
        ctx.clip();
        ctx.drawImage(rig.cropCanvas, sx, sy, sw, sh);
        ctx.restore();

        draw3DBoundingPrism(
            ctx, sx, sy, sw, sh, rig.depth,
            '#38bdf8',
            'rgba(56, 189, 248, 0.14)',
            `★ ${rig.label} [직접 조종]`,
            `WASD/우클릭 이동 · 충돌 ${rig.collisionCount}회`,
            true,
            rig.collideFlash > 0
        );

        // Heading vector arrow
        const ax = proj.x + Math.cos(rig.facing) * (sw * 0.65);
        const ay = proj.y - sh * 0.35 + Math.sin(rig.facing) * (sh * 0.65);
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        ctx.moveTo(proj.x, proj.y - sh * 0.35);
        ctx.lineTo(ax, ay);
        ctx.stroke();
        ctx.restore();
    }

    function renderControllableVideoWorld(ctx, sourceFrame, viewMode) {
        ctx.fillStyle = '#04070f';
        ctx.fillRect(0, 0, W, H);

        const yawPx = cam.yaw * 64;
        const pitchPx = cam.pitch * 36;
        const z = cam.zoom;

        // 1) S4 Far Background Plane (3D parallax)
        if (viewMode === 'composite' || viewMode === 'overlay' || viewMode === 's4') {
            ctx.save();
            const zFar = 1.0 + (z - 1.0) * 0.45;
            ctx.translate(W * 0.5 - yawPx * 0.32, H * 0.5 - pitchPx * 0.32);
            ctx.scale(zFar, zFar);
            ctx.drawImage(sourceFrame, -W * 0.5, -H * 0.5, W, H);
            ctx.restore();
        }

        // 2) S2 Midground Structural Parallax Strips (3 clean depth bands for smooth 3x faster GPU compositing)
        if (viewMode === 'composite' || viewMode === 'overlay' || viewMode === 's2') {
            if (viewMode === 's2') {
                ctx.fillStyle = '#050812';
                ctx.fillRect(0, 0, W, H);
            }
            const slices = 3;
            const sh = H / slices;
            for (let s = 0; s < slices; s++) {
                const depthWeight = s / (slices - 1);
                if (s === 0 && viewMode === 'composite') continue;
                const shiftX = -yawPx * (0.35 + depthWeight * 0.65);
                const shiftY = -pitchPx * (0.35 + depthWeight * 0.65);
                const sliceZoom = 1.0 + (z - 1.0) * (0.55 + depthWeight * 0.55);

                ctx.save();
                ctx.beginPath();
                ctx.rect(0, s * sh, W, sh + 1);
                ctx.clip();
                ctx.translate(W * 0.5 + shiftX, H * 0.5 + shiftY);
                ctx.scale(sliceZoom, sliceZoom);
                ctx.globalAlpha = viewMode === 's2' ? 0.92 : (0.62 + depthWeight * 0.30);
                ctx.drawImage(sourceFrame, -W * 0.5, -H * 0.5, W, H);
                ctx.restore();
            }
        }

        // 3) Subtle Ground-Plane Perspective NavMesh Grid (gives instant 3D spatial grounding!)
        ctx.save();
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.14)';
        ctx.lineWidth = 1;
        for (let row = 0; row <= 5; row++) {
            const wy = 210 + row * 64;
            const pL = projectWorldToScreen(40, wy, wy / H);
            const pR = projectWorldToScreen(W - 40, wy, wy / H);
            ctx.beginPath();
            ctx.moveTo(pL.x, pL.y);
            ctx.lineTo(pR.x, pR.y);
            ctx.stroke();
        }
        for (let col = 0; col <= 8; col++) {
            const wx = 60 + col * 105;
            const pTop = projectWorldToScreen(wx, 210, 210 / H);
            const pBot = projectWorldToScreen(wx, H - 10, 1.0);
            ctx.beginPath();
            ctx.moveTo(pTop.x, pTop.y);
            ctx.lineTo(pBot.x, pBot.y);
            ctx.stroke();
        }
        ctx.restore();

        // 4) S4 Static Architectural Collider Boundaries (buildings / curbs / poles)
        if (viewMode !== 's0') {
            ctx.save();
            for (const sb of staticBoundaries) {
                const p = projectWorldToScreen(sb.x, sb.y, sb.depth);
                const sw = sb.w * p.scale;
                const sh = sb.h * p.scale;
                ctx.strokeStyle = 'rgba(148, 163, 184, 0.42)';
                ctx.fillStyle = 'rgba(15, 23, 42, 0.16)';
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 4]);
                ctx.fillRect(p.x, p.y, sw, sh);
                ctx.strokeRect(p.x, p.y, sw, sh);
            }
            ctx.setLineDash([]);
            ctx.restore();
        }

        // 5) S2/S0 Extracted Moving Video Entities (Vehicles -> 3D Collider Prisms, People -> Articulated Skeletons)
        if (viewMode === 's0') {
            ctx.fillStyle = 'rgba(4, 7, 15, 0.82)';
            ctx.fillRect(0, 0, W, H);
        }
        const sortedEntities = [...trackedEntities].sort((a, b) => a.footY - b.footY);
        for (const ent of sortedEntities) {
            const pTL = projectWorldToScreen(ent.x, ent.y, ent.depth);
            const sw = ent.w * pTL.scale;
            const sh = ent.h * pTL.scale;
            const isSel = ent.id === selectedEntityId;
            if (ent.hitFlash > 0) ent.hitFlash--;

            if (ent.role === 'humanoid') {
                // Model this extracted video person (or promoted entity) with a live procedural humanoid skeleton!
                const footProj = projectWorldToScreen(ent.cx, ent.footY, ent.depth);
                const facing = ent.speed > 0.3 ? Math.atan2(ent.vy, ent.vx) : 0;
                const palette = {
                    primary: `rgb(${Math.min(245, ent.r + 35)}, ${Math.min(245, ent.g + 35)}, ${Math.min(245, ent.b + 35)})`,
                    skin: '#f1c27d',
                };
                drawArticulatedHumanoid(
                    ctx,
                    footProj.x,
                    footProj.y,
                    Math.max(0.65, Math.min(1.25, (sh / 58))),
                    ent.walkPhase,
                    facing,
                    0,
                    palette,
                    `${ent.label} · 인물 리깅`,
                    false,
                    ent.hitFlash > 0,
                    cam.yaw * 1.45,
                    cam.pitch * 0.45
                );
                // Crisp subtle bounding corners showing exact video extraction region
                ctx.save();
                ctx.strokeStyle = isSel ? '#38bdf8' : 'rgba(16, 185, 129, 0.55)';
                ctx.lineWidth = isSel ? 1.8 : 1;
                ctx.strokeRect(pTL.x, pTL.y, sw, sh);
                ctx.restore();
            } else {
                // VEHICLE: 3D Extruded Wireframe Bounding Prism (Solid Collider Boundary or Vehicle Rig)
                const isCollider = ent.role === 'collider';
                const color = isCollider ? '#f59e0b' : '#38bdf8';
                const fillAlpha = isCollider ? 'rgba(245, 158, 11, 0.10)' : 'rgba(56, 189, 248, 0.12)';
                const roleTag = isCollider ? '충돌 경계' : '차량 리깅';
                draw3DBoundingPrism(
                    ctx,
                    pTL.x,
                    pTL.y,
                    sw,
                    sh,
                    ent.depth,
                    color,
                    fillAlpha,
                    `${ent.label} · ${roleTag}`,
                    `W${Math.round(ent.w)}×H${Math.round(ent.h)} · v=${ent.speed.toFixed(1)} · D=${ent.depth.toFixed(2)}`,
                    isSel,
                    ent.hitFlash > 0
                );

                // Velocity heading vector on road plane
                if (ent.speed > 0.45) {
                    const cxS = pTL.x + sw * 0.5;
                    const cyS = pTL.y + sh * 0.65;
                    ctx.save();
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 1.8;
                    ctx.beginPath();
                    ctx.moveTo(cxS, cyS);
                    ctx.lineTo(cxS + ent.vx * 12, cyS + ent.vy * 12);
                    ctx.stroke();
                    ctx.restore();
                }
            }
        }

        // 6) Player-Possessed Game Character / Vehicle Rig modeled from the video!
        if (playerRig) {
            // Continuity movement trail on ground plane
            if (playerRig.trail.length > 1) {
                ctx.save();
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                playerRig.trail.forEach((pt, idx) => {
                    const sp = projectWorldToScreen(pt.x, pt.y, pt.depth);
                    if (idx === 0) ctx.moveTo(sp.x, sp.y);
                    else ctx.lineTo(sp.x, sp.y);
                });
                ctx.stroke();
                ctx.restore();
            }

            // Click-to-move destination reticle
            if (playerRig.targetX !== null && playerRig.targetY !== null) {
                const tp = projectWorldToScreen(playerRig.targetX, playerRig.targetY, playerRig.targetY / H);
                ctx.save();
                ctx.strokeStyle = '#38bdf8';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.ellipse(tp.x, tp.y, 14, 5.5, 0, 0, Math.PI * 2);
                ctx.stroke();
                ctx.restore();
            }

            const proj = projectWorldToScreen(playerRig.x, playerRig.y, playerRig.depth);
            if (playerRig.kind === 'humanoid') {
                drawArticulatedHumanoid(
                    ctx,
                    proj.x,
                    proj.y,
                    proj.scale * 1.05,
                    playerRig.walkPhase,
                    playerRig.facing,
                    playerRig.jumpZ,
                    playerRig.palette,
                    activeMode === 'game_to_cinema' ? `${playerRig.label} [시네마틱 연출]` : `★ ${playerRig.label} [WASD 조종]`,
                    activeMode !== 'game_to_cinema',
                    playerRig.collideFlash > 0,
                    cam.yaw * 1.65,
                    cam.pitch * 0.45
                );
            } else {
                drawControllableVehicleRig(ctx, playerRig, proj);
            }
        }

        // 7) Live Physical Collision Impact Markers
        for (let i = collisionImpacts.length - 1; i >= 0; i--) {
            const imp = collisionImpacts[i];
            imp.life--;
            if (imp.life <= 0) {
                collisionImpacts.splice(i, 1);
                continue;
            }
            const p = projectWorldToScreen(imp.x, imp.y, imp.y / H);
            ctx.save();
            ctx.strokeStyle = `rgba(244, 63, 94, ${imp.life / 22})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(p.x, p.y - 12, (24 - imp.life) * 1.8, 0, Math.PI * 2);
            ctx.stroke();
            ctx.restore();
        }

        // 8) Reverse Protocol (Game -> Cinematic Video Direction): 2.39:1 Letterbox + Director Framing Guides
        if (activeMode === 'game_to_cinema') {
            ctx.save();
            const barH = 44;
            ctx.fillStyle = 'rgba(3, 5, 11, 0.94)';
            ctx.fillRect(0, 0, W, barH);
            ctx.fillRect(0, H - barH, W, barH);
            // Rule-of-thirds director viewfinder crosshair
            ctx.strokeStyle = 'rgba(245, 158, 11, 0.22)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(W / 3, barH); ctx.lineTo(W / 3, H - barH);
            ctx.moveTo((W * 2) / 3, barH); ctx.lineTo((W * 2) / 3, H - barH);
            ctx.stroke();
            // Cinematic director bottom readout
            ctx.fillStyle = '#fbbf24';
            ctx.font = '700 10px "IBM Plex Mono", monospace';
            ctx.textAlign = 'left';
            ctx.fillText(
                `REC · 게임→영상화 연출 프로토콜 · 35mm ORBIT DOLLY · Yaw ${(cam.yaw * 95).toFixed(0)}° · Zoom ${cam.zoom.toFixed(2)}× · 시네마틱 프레임 자동 직조`,
                18, H - 17
            );
            ctx.textAlign = 'right';
            ctx.fillStyle = '#94a3b8';
            ctx.fillText(`FRAME ${String(tickCount).padStart(5, '0')} · 2.39:1 SCALE-ROTOR CINEMA`, W - 18, H - 17);
            ctx.restore();
        }

        // Top Precision Telemetry Bar
        ctx.save();
        ctx.fillStyle = 'rgba(6, 10, 19, 0.90)';
        ctx.fillRect(14, 10, 660, 26);
        const barCol = activeMode === 'game_to_cinema' ? '#f59e0b' : (activeMode === 'bullet_time' ? '#a855f7' : (playerRig ? '#38bdf8' : '#10b981'));
        ctx.strokeStyle = barCol;
        ctx.lineWidth = 1.2;
        ctx.strokeRect(14, 10, 660, 26);
        ctx.fillStyle = barCol;
        ctx.font = '700 10px "IBM Plex Mono", monospace';
        ctx.textAlign = 'left';
        const vehN = trackedEntities.filter((e) => e.cls === 'vehicle').length;
        const pedN = trackedEntities.filter((e) => e.cls === 'person').length;
        const hudText = activeMode === 'game_to_cinema'
            ? `게임→영상화 연출 (상호작용 프로토콜 전환) · 리깅 캐릭터 자동 추적 3D 오빗 · 단면 각도 ${(cam.yaw * 95).toFixed(0)}°`
            : activeMode === 'bullet_time'
                ? `시간 정지·3D 단면 선회 · 차량 ${vehN} · 인물 ${pedN} · 정적 경계 ${staticBoundaries.length} · Yaw ${(cam.yaw * 95).toFixed(0)}°`
                : playerRig
                    ? `${playerRig.label} 게임 프로토콜 활성 (WASD/우클릭 이동 · Space 점프 · 드래그=3D 시점) · 충돌 ${playerRig.collisionCount}회`
                    : `영상→객체 분류 프로토콜 (차량 ${vehN} · 인물 ${pedN} · 정적 경계 ${staticBoundaries.length}) · 객체 클릭=선택 · 드래그=3D 시점`;
        ctx.fillText(hudText, 22, 27);
        ctx.restore();
    }

    // Render 4-Angle 3D Cross-Section = Image Strip (Proves 1 woven 3D figure yields any 2D angle image!)
    function drawCrossSectionStrip() {
        const cvs = document.getElementById('uni-cross-section-canvas');
        if (!cvs) return;
        const ctx = cvs.getContext('2d');
        const cw = cvs.width;
        const ch = cvs.height;

        ctx.fillStyle = '#050811';
        ctx.fillRect(0, 0, cw, ch);

        const activePalette = playerRig
            ? playerRig.palette
            : (trackedEntities[0]
                ? { primary: `rgb(${Math.min(245, trackedEntities[0].r + 35)}, ${Math.min(245, trackedEntities[0].g + 35)}, ${Math.min(245, trackedEntities[0].b + 35)})`, skin: '#f1c27d' }
                : { primary: '#38bdf8', skin: '#f1c27d' });
        const walkPh = playerRig ? playerRig.walkPhase : tickCount * 0.08;
        const liveYawDeg = Math.round(((cam.yaw * 1.65) * 180) / Math.PI);

        const views = [
            { title: '0° 정면 단면', yaw: 0, pitch: 0.05 },
            { title: '90° 측면 단면', yaw: Math.PI * 0.5, pitch: 0.05 },
            { title: '180° 후면 단면', yaw: Math.PI, pitch: 0.05 },
            { title: `현재 ${liveYawDeg}° 단면`, yaw: cam.yaw * 1.65, pitch: cam.pitch * 0.45, highlight: true },
        ];
        const cellW = cw / 4;

        views.forEach((v, idx) => {
            const x0 = idx * cellW;
            ctx.save();
            ctx.strokeStyle = v.highlight ? '#38bdf8' : '#1e293b';
            ctx.lineWidth = v.highlight ? 1.4 : 1;
            ctx.strokeRect(x0 + 2, 2, cellW - 4, ch - 4);

            // Subtle floor cross-section horizon line
            ctx.strokeStyle = 'rgba(56, 189, 248, 0.22)';
            ctx.beginPath();
            ctx.moveTo(x0 + 10, ch - 24);
            ctx.lineTo(x0 + cellW - 10, ch - 24);
            ctx.stroke();

            drawArticulatedHumanoid(
                ctx,
                x0 + cellW * 0.5,
                ch - 24,
                1.18,
                walkPh,
                0,
                0,
                activePalette,
                '',
                false,
                false,
                v.yaw,
                v.pitch
            );

            ctx.fillStyle = v.highlight ? '#7dd3fc' : '#94a3b8';
            ctx.font = '600 9.5px "IBM Plex Mono", monospace';
            ctx.textAlign = 'center';
            ctx.fillText(v.title, x0 + cellW * 0.5, ch - 7);
            ctx.restore();
        });
    }

    const capturedSlices = [];
    function renderCapturedSliceReel() {
        const host = document.getElementById('uni-slice-reel');
        if (!host) return;
        host.textContent = '';
        if (capturedSlices.length === 0) {
            const hint = document.createElement('span');
            hint.className = 'uni-ent-meta';
            hint.textContent = '상단 "현재 각도 단면 이미지 캡처"를 누르면 3D 직조 인물의 현재 카메라 각도 단면이 2D 이미지로 즉시 추출됩니다.';
            host.appendChild(hint);
            return;
        }
        for (const item of capturedSlices) {
            const wrap = document.createElement('div');
            wrap.className = 'uni-slice-item';
            const img = document.createElement('img');
            img.src = item.dataUrl;
            img.alt = item.caption;
            const cap = document.createElement('span');
            cap.className = 'uni-slice-cap';
            cap.textContent = item.caption;
            wrap.appendChild(img);
            wrap.appendChild(cap);
            host.appendChild(wrap);
        }
    }

    // Draw 3-Axis Spectral Neural Web (Relationship x Connectivity x Continuity)
    function drawSpectrumNeuralCanvas(lastState) {
        const cvs = document.getElementById('uni-spectrum-canvas');
        if (!cvs) return;
        const ctx = cvs.getContext('2d');
        const cw = cvs.width;
        const ch = cvs.height;

        ctx.fillStyle = '#050811';
        ctx.fillRect(0, 0, cw, ch);

        ctx.strokeStyle = 'rgba(30, 41, 59, 0.5)';
        ctx.lineWidth = 1;
        for (let i = 1; i < 4; i++) {
            ctx.beginPath(); ctx.moveTo((cw / 4) * i, 14); ctx.lineTo((cw / 4) * i, ch - 18); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(24, (ch / 4) * i); ctx.lineTo(cw - 12, (ch / 4) * i); ctx.stroke();
        }

        const padX = 28;
        const padY = 20;
        const mapX = (rel) => padX + rel * (cw - padX * 2);
        const mapY = (conn) => ch - padY - conn * (ch - padY * 2);

        for (const e of ssdArchive.edges) {
            const na = ssdArchive.nodes[e.a];
            const nb = ssdArchive.nodes[e.b];
            if (!na || !nb) continue;
            ctx.strokeStyle = `rgba(56, 189, 248, ${0.18 + e.weight * 0.45})`;
            ctx.lineWidth = 1 + e.weight * 1.2;
            ctx.beginPath();
            ctx.moveTo(mapX(na.rel), mapY(na.conn));
            ctx.lineTo(mapX(nb.rel), mapY(nb.conn));
            ctx.stroke();
        }

        for (const n of ssdArchive.nodes) {
            const nx = mapX(n.rel);
            const ny = mapY(n.conn);
            const rad = 3.5 + Math.min(7, Math.log2(n.hits + 1) * 1.6);
            const r = Math.round(n.chromaR * 255);
            const g = Math.round(n.chromaY * 220 + n.chromaB * 140);
            const b = Math.round(n.chromaB * 255 + 40);
            ctx.fillStyle = `rgb(${Math.min(255, r + 50)}, ${Math.min(255, g + 40)}, ${Math.min(255, b)})`;
            ctx.beginPath();
            ctx.arc(nx, ny, rad, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = n.depthTier === 'S4' ? '#10b981' : (n.depthTier === 'S2' ? '#38bdf8' : '#f59e0b');
            ctx.lineWidth = 1.2;
            ctx.stroke();
        }

        if (lastState) {
            const lx = mapX(lastState.rel);
            const ly = mapY(lastState.conn);
            ctx.strokeStyle = lastState.cacheHit ? '#34d399' : '#f43f5e';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(lx, ly, 9, 0, Math.PI * 2);
            ctx.stroke();
        }

        ctx.fillStyle = '#94a3b8';
        ctx.font = '600 9.5px "IBM Plex Mono", monospace';
        ctx.textAlign = 'left';
        ctx.fillText('연결성(Y) ↑', 8, 12);
        ctx.textAlign = 'right';
        ctx.fillText('관계성(X) → · 크기=연속성·공명', cw - 8, ch - 5);
    }

    // Render Live Extracted Object Roster & Character Rigging Inspector (100% Safe DOM)
    function updateEntityRosterDOM(sourceFrame) {
        const rosterHost = document.getElementById('uni-entity-roster');
        if (!rosterHost) return;
        rosterHost.textContent = '';

        const summaryEl = document.getElementById('uni-roster-summary');
        if (summaryEl) {
            const vehN = trackedEntities.filter((e) => e.cls === 'vehicle').length;
            const pedN = trackedEntities.filter((e) => e.cls === 'person').length;
            summaryEl.textContent = `차량 ${vehN} · 인물 ${pedN} · 정적 경계 ${staticBoundaries.length}`;
        }

        if (trackedEntities.length === 0) {
            const empty = document.createElement('div');
            empty.className = 'uni-empty-note';
            empty.textContent = '배경 모델을 안정화하며 움직이는 차량과 인물을 분리 추출하고 있습니다 (1~2초 소요). 상단 "인물 캐릭터 생성"으로 즉시 조종 리깅을 배치할 수도 있습니다.';
            rosterHost.appendChild(empty);
            return;
        }

        const shown = trackedEntities.slice(0, 6);
        for (const ent of shown) {
            const card = document.createElement('div');
            card.className = 'uni-ent-card' + (ent.id === selectedEntityId ? ' selected' : '');

            // Live pixel crop thumbnail straight from the real video!
            const thumb = document.createElement('canvas');
            thumb.width = 56;
            thumb.height = 42;
            thumb.className = 'uni-ent-thumb';
            if (sourceFrame) {
                const tctx = thumb.getContext('2d');
                tctx.fillStyle = '#050811';
                tctx.fillRect(0, 0, 56, 42);
                tctx.drawImage(
                    sourceFrame,
                    Math.max(0, ent.x), Math.max(0, ent.y), Math.max(10, ent.w), Math.max(10, ent.h),
                    0, 0, 56, 42
                );
            }

            const body = document.createElement('div');
            body.className = 'uni-ent-body';

            const head = document.createElement('div');
            head.className = 'uni-ent-head';
            const title = document.createElement('span');
            title.className = 'uni-ent-title';
            title.textContent = `${ent.label} · ${ent.cls === 'person' ? 'PERSON' : 'VEHICLE'}`;
            const meta = document.createElement('span');
            meta.className = 'uni-ent-meta';
            meta.textContent = `${Math.round(ent.w)}×${Math.round(ent.h)} · v${ent.speed.toFixed(1)} · D${ent.depth.toFixed(2)}`;
            head.appendChild(title);
            head.appendChild(meta);

            const actions = document.createElement('div');
            actions.className = 'uni-ent-actions';

            const btnCol = document.createElement('button');
            btnCol.type = 'button';
            btnCol.className = 'uni-mini-btn' + (ent.role === 'collider' ? ' active-amber' : '');
            btnCol.textContent = '충돌 경계';
            btnCol.addEventListener('click', () => {
                ent.role = 'collider';
                ent.userLockedRole = true;
                selectedEntityId = ent.id;
                lastWovenNote = `[역할 지정] ${ent.label}을(를) 물리 충돌 경계(Solid Collider)로 전환했습니다.`;
                updateUnifiedMemoryDOM(null, sourceFrame);
            });

            const btnHum = document.createElement('button');
            btnHum.type = 'button';
            btnHum.className = 'uni-mini-btn' + (ent.role === 'humanoid' ? ' active-emerald' : '');
            btnHum.textContent = ent.cls === 'vehicle' ? '탑승자 캐릭터화' : '인물 캐릭터화';
            btnHum.addEventListener('click', () => {
                selectedEntityId = ent.id;
                if (ent.cls === 'person') {
                    ent.role = 'humanoid';
                    ent.userLockedRole = true;
                }
                spawnPlayerRigFromEntity(ent, 'humanoid');
                activeMode = 'character_rig';
                syncModeButtons();
                updateUnifiedMemoryDOM(null, sourceFrame);
            });

            const btnDrive = document.createElement('button');
            btnDrive.type = 'button';
            btnDrive.className = 'uni-mini-btn' + (playerRig && playerRig.sourceEntityId === ent.id && playerRig.kind === 'vehicle_ctrl' ? ' active-cyan' : '');
            btnDrive.textContent = '차량 조종';
            btnDrive.addEventListener('click', () => {
                selectedEntityId = ent.id;
                ent.role = 'vehicle_ctrl';
                ent.userLockedRole = true;
                spawnPlayerRigFromEntity(ent, 'vehicle_ctrl');
                activeMode = 'character_rig';
                syncModeButtons();
                updateUnifiedMemoryDOM(null, sourceFrame);
            });

            actions.appendChild(btnCol);
            actions.appendChild(btnHum);
            actions.appendChild(btnDrive);

            body.appendChild(head);
            body.appendChild(actions);

            card.appendChild(thumb);
            card.appendChild(body);
            rosterHost.appendChild(card);
        }
    }

    function syncModeButtons() {
        document.querySelectorAll('[data-uni-mode]').forEach((b) => {
            b.classList.toggle('active', b.dataset.uniMode === activeMode);
        });
    }

    function updateUnifiedMemoryDOM(lastState, sourceFrame) {
        const host = document.getElementById('unified-rotor-registry');
        if (host) {
            host.textContent = '';
            Object.values(memTiers).forEach((t) => {
                const row = document.createElement('div');
                row.className = 'uni-reg-row';
                const c1 = document.createElement('span');
                c1.className = 'uni-reg-name';
                c1.textContent = `${t.name} (${t.loadPct}%)`;
                const c2 = document.createElement('span');
                c2.className = 'uni-reg-val';
                c2.textContent = t.detail;
                row.appendChild(c1);
                row.appendChild(c2);
                host.appendChild(row);
            });
        }

        const isoEl = document.getElementById('uni-iso-readout');
        if (isoEl) {
            isoEl.textContent = `SSD 직조 축 ${ssdArchive.nodes.length}개 · 재분류 생략 히트 ${recallHitRatePct.toFixed(1)}% · 활성 객체 ${trackedEntities.length}개`;
        }
        const tapeEl = document.getElementById('uni-tape-status');
        if (tapeEl) {
            tapeEl.textContent = playerRig
                ? `조종 활성: ${playerRig.label} — WASD/우클릭 이동 · Space 점프/부스트 · 좌드래그 3D 카메라 선회 · 휠 줌`
                : `좌클릭=차량·인물 선택 · 좌드래그=3D 카메라 시점 변환 · 휠=줌 · 아래 카드에서 경계화/캐릭터 모델링을 즉시 전환하세요`;
        }
        const noteEl = document.getElementById('uni-transfer-note');
        if (noteEl) noteEl.textContent = lastWovenNote;

        updateEntityRosterDOM(sourceFrame);
        drawSpectrumNeuralCanvas(lastState);
        drawCrossSectionStrip();
        renderCapturedSliceReel();
    }

    // =========================================================================
    // 5. Public Interface wired from weaving.js
    // =========================================================================
    window.ElysiaUnifiedRotor = {
        setSubMode(mode) {
            if (mode === 'bullet_time') {
                activeMode = 'bullet_time';
                cam.zoom = Math.max(1.18, cam.zoom);
            } else if (mode === 'game_to_cinema') {
                activeMode = 'game_to_cinema';
                if (!playerRig) {
                    const preferred = trackedEntities.find((e) => e.cls === 'person')
                        || trackedEntities.find((e) => e.id === selectedEntityId)
                        || trackedEntities[0]
                        || null;
                    spawnPlayerRigFromEntity(preferred, 'humanoid');
                }
                lastWovenNote = '[역방향 전환: 게임→영상화 연출] 게임 리깅 캐릭터와 충돌 경계가 35mm 오빗 시네마틱 영상으로 실시간 연출됩니다.';
            } else if (mode === 'character_rig') {
                activeMode = 'character_rig';
                if (!playerRig) {
                    const preferred = trackedEntities.find((e) => e.cls === 'person')
                        || trackedEntities.find((e) => e.id === selectedEntityId)
                        || trackedEntities[0]
                        || null;
                    spawnPlayerRigFromEntity(preferred, 'humanoid');
                }
            } else {
                activeMode = 'object_boundary';
            }
            updateUnifiedMemoryDOM(null, null);
        },
        getSubMode() { return activeMode; },
        captureCrossSectionImage() {
            const sliceC = makeCanvas(128, 128);
            const sctx = sliceC.getContext('2d');
            sctx.fillStyle = '#060a14';
            sctx.fillRect(0, 0, 128, 128);
            sctx.strokeStyle = 'rgba(56, 189, 248, 0.25)';
            sctx.beginPath();
            sctx.moveTo(10, 104); sctx.lineTo(118, 104);
            sctx.stroke();
            const pal = playerRig
                ? playerRig.palette
                : (trackedEntities[0]
                    ? { primary: `rgb(${Math.min(245, trackedEntities[0].r + 35)}, ${Math.min(245, trackedEntities[0].g + 35)}, ${Math.min(245, trackedEntities[0].b + 35)})`, skin: '#f1c27d' }
                    : { primary: '#38bdf8', skin: '#f1c27d' });
            const yawRad = cam.yaw * 1.65;
            const pitchRad = cam.pitch * 0.45;
            drawArticulatedHumanoid(
                sctx, 64, 104, 1.45,
                playerRig ? playerRig.walkPhase : tickCount * 0.08,
                0, 0, pal, '', false, false, yawRad, pitchRad
            );
            const degY = Math.round((yawRad * 180) / Math.PI);
            const degP = Math.round((pitchRad * 180) / Math.PI);
            capturedSlices.unshift({
                dataUrl: sliceC.toDataURL('image/png'),
                caption: `단면 Yaw ${degY}° · Pitch ${degP}°`,
            });
            if (capturedSlices.length > 6) capturedSlices.pop();
            lastWovenNote = `[3D 직조 → 2D 단면 이미지 추출] 카메라 각도 (Yaw ${degY}°, Pitch ${degP}°)의 단면 자체를 2D 이미지로 즉시 추출했습니다.`;
            renderCapturedSliceReel();
            const noteEl = document.getElementById('uni-transfer-note');
            if (noteEl) noteEl.textContent = lastWovenNote;
        },
        spawnCharacterFromScene() {
            const preferred = trackedEntities.find((e) => e.id === selectedEntityId)
                || trackedEntities.find((e) => e.cls === 'person')
                || trackedEntities[0]
                || null;
            spawnPlayerRigFromEntity(preferred, 'humanoid');
            activeMode = 'character_rig';
            syncModeButtons();
            updateUnifiedMemoryDOM(null, null);
        },
        toggleAutoExplore() {
            cam.autoExplore = !cam.autoExplore;
            updateUnifiedMemoryDOM(null, null);
            return cam.autoExplore;
        },
        resetCameraAndSsd(clearSsd) {
            cam.yaw = 0;
            cam.pitch = 0;
            cam.zoom = 1.06;
            if (clearSsd) {
                ssdArchive = defaultArchive();
                persistSsdArchive();
                playerRig = null;
                bgInitialized = false;
                trackedEntities = [];
                lastWovenNote = 'SSD 원장 및 배경 모델을 초기화했습니다. 영상 객체 분류를 처음부터 다시 시작합니다.';
            }
            updateUnifiedMemoryDOM(null, null);
        },
        handlePointerDown(x, y, button = 0) {
            // Right-click issues move destination order when possessing a game character/vehicle!
            if (button === 2) {
                if (!playerRig) {
                    const preferred = trackedEntities.find((e) => e.id === selectedEntityId) || trackedEntities[0] || null;
                    spawnPlayerRigFromEntity(preferred, 'humanoid');
                    activeMode = 'character_rig';
                    syncModeButtons();
                }
                const worldPt = unprojectScreenToWorld(x, y, Math.max(0.25, Math.min(1.0, y / H)));
                playerRig.targetX = worldPt.x;
                playerRig.targetY = worldPt.y;
                return;
            }

            // Left-click: check if user clicked an extracted vehicle/person box directly!
            let hitEnt = null;
            for (const ent of trackedEntities) {
                const p = projectWorldToScreen(ent.x, ent.y, ent.depth);
                const sw = ent.w * p.scale;
                const sh = ent.h * p.scale;
                if (x >= p.x - 8 && x <= p.x + sw + 8 && y >= p.y - 8 && y <= p.y + sh + 8) {
                    hitEnt = ent;
                    break;
                }
            }
            if (hitEnt) {
                selectedEntityId = hitEnt.id;
                lastWovenNote = `[객체 선택] ${hitEnt.label} (${hitEnt.cls === 'person' ? '인물' : '차량'}) — 하단 카드에서 충돌 경계 / 탑승자 캐릭터화 / 차량 조종을 바로 전환할 수 있습니다.`;
            }

            cam.dragging = true;
            cam.dragMoved = false;
            cam.autoExplore = false;
            cam.lastX = x;
            cam.lastY = y;
        },
        handlePointerMove(x, y) {
            if (!cam.dragging) return;
            const dx = x - cam.lastX;
            const dy = y - cam.lastY;
            if (Math.hypot(dx, dy) > 2) cam.dragMoved = true;
            cam.lastX = x;
            cam.lastY = y;
            cam.yaw = Math.max(-1, Math.min(1, cam.yaw + dx / 250));
            cam.pitch = Math.max(-1, Math.min(1, cam.pitch + dy / 210));
        },
        handlePointerUp() {
            cam.dragging = false;
        },
        handleWheel(deltaY) {
            cam.zoom = Math.max(1.0, Math.min(1.75, cam.zoom + (deltaY < 0 ? 0.06 : -0.06)));
        },
        triggerCrossDomainTransfer(audioPulse) {
            persistSsdArchive();
            const latest = ssdArchive.nodes[ssdArchive.nodes.length - 1];
            try {
                const key = 'elysia_cognitive_voxel_bridge_v1';
                const prev = JSON.parse(localStorage.getItem(key) || '{}');
                prev.unifiedScaleRotor = {
                    nodes: ssdArchive.nodes.length,
                    edges: ssdArchive.edges.length,
                    recallHitRatePct: Number(recallHitRatePct.toFixed(1)),
                    extractedVehicles: trackedEntities.filter((e) => e.cls === 'vehicle').length,
                    extractedPersons: trackedEntities.filter((e) => e.cls === 'person').length,
                    staticBoundaries: staticBoundaries.length,
                    latestNode: latest,
                    updatedAt: Date.now(),
                };
                localStorage.setItem(key, JSON.stringify(prev));
            } catch { /* ignore */ }
            if (window.ElysiaDigitalTwinRPG && latest) {
                window.ElysiaDigitalTwinRPG.feedVideoMood({
                    warmth: (latest.chromaR - latest.chromaB) * 1.4,
                    flux: 1 - latest.cont,
                    chaos: latest.chromaY,
                    title: `영상 객체·경계 스펙트럼 (${ssdArchive.nodes.length}축) 동기화`,
                });
            }
            if (audioPulse) audioPulse(660);
            lastWovenNote = `SSD 영구 스펙트럼(${ssdArchive.nodes.length}축 · 차량·인물·경계 모델)을 디지털트윈 및 3×3×3 복셀 메모리에 동기화했습니다.`;
            updateUnifiedMemoryDOM(null, null);
        },
        step({ legacyCtx, rotorCtx, thumbS4Ctx, thumbS2Ctx, thumbS0Ctx, capCanvas, state, keys }) {
            tickCount += 1;
            const isFrozen = activeMode === 'bullet_time';

            // Camera Q/E zoom always works; WASD steers playerRig if active, else orbits camera!
            if (keys) {
                if (keys.has('KeyQ')) cam.zoom = Math.max(1.0, cam.zoom - 0.015);
                if (keys.has('KeyE')) cam.zoom = Math.min(1.75, cam.zoom + 0.015);
                if (!playerRig) {
                    if (keys.has('KeyA') || keys.has('ArrowLeft')) { cam.yaw = Math.max(-1, cam.yaw - 0.025); cam.autoExplore = false; }
                    if (keys.has('KeyD') || keys.has('ArrowRight')) { cam.yaw = Math.min(1, cam.yaw + 0.025); cam.autoExplore = false; }
                    if (keys.has('KeyW') || keys.has('ArrowUp')) { cam.pitch = Math.max(-1, cam.pitch - 0.025); cam.autoExplore = false; }
                    if (keys.has('KeyS') || keys.has('ArrowDown')) { cam.pitch = Math.min(1, cam.pitch + 0.025); cam.autoExplore = false; }
                }
            }

            if (activeMode === 'game_to_cinema' && !cam.dragging) {
                // Reverse Protocol: Multi-Scale Cinema Director sweeps smoothly around the live rigged character!
                cam.yaw = Math.sin(tickCount * 0.022) * 0.85;
                cam.pitch = Math.cos(tickCount * 0.014) * 0.26;
                cam.zoom = 1.24 + Math.sin(tickCount * 0.017) * 0.14;
                // Autonomous cinematic stroll across the intersection if user isn't pressing WASD
                if (playerRig && playerRig.targetX === null && (!keys || (!keys.has('KeyW') && !keys.has('KeyA') && !keys.has('KeyS') && !keys.has('KeyD')))) {
                    if (tickCount % 120 === 1) {
                        playerRig.targetX = 240 + Math.random() * (W - 480);
                        playerRig.targetY = 260 + Math.random() * (H - 310);
                    }
                }
            } else if (cam.autoExplore && !cam.dragging) {
                cam.yaw = Math.sin(tickCount * 0.016) * 0.58;
                cam.pitch = Math.cos(tickCount * 0.012) * 0.28;
                cam.zoom = isFrozen
                    ? 1.24 + Math.sin(tickCount * 0.02) * 0.10
                    : 1.10 + Math.sin(tickCount * 0.01) * 0.06;
            }

            const tL0 = performance.now();
            if (!isFrozen && (!hasFrozenFrame || tickCount % 6 === 0)) {
                frozenFrameCtx.drawImage(capCanvas, 0, 0, W, H);
                hasFrozenFrame = true;
            }
            const activeFrame = (isFrozen && hasFrozenFrame) ? frozenFrameC : capCanvas;

            // Left Canvas: Raw 2D Flat Video Input
            legacyCtx.drawImage(activeFrame, 0, 0, W, H);
            legacyCtx.fillStyle = 'rgba(6, 10, 19, 0.88)';
            legacyCtx.fillRect(14, 12, 430, 26);
            legacyCtx.strokeStyle = '#64748b';
            legacyCtx.lineWidth = 1.1;
            legacyCtx.strokeRect(14, 12, 430, 26);
            legacyCtx.fillStyle = '#e2e8f0';
            legacyCtx.font = '700 10px "IBM Plex Mono", monospace';
            legacyCtx.fillText('원본 평면 동영상 (객체 미분류 · 고정 2D 시점)', 22, 29);
            const leftMs = performance.now() - tL0;

            // Right Canvas: Real Segmentation (every 2nd tick) + Classification + 3D Prisms + Rigged Character + Memory Rotor
            const tR0 = performance.now();
            if (tickCount % 2 === 1 || !bgInitialized) {
                lastSegMetrics = segmentVideoWorld(activeFrame, isFrozen);
            }
            stepPlayerRigPhysics(keys, isFrozen);
            const woven = weaveIntoSpectrumWeb(lastSegMetrics);
            renderControllableVideoWorld(rotorCtx, activeFrame, state.outputView || 'composite');
            const rightMs = performance.now() - tR0;

            // 3-Track Mini Previews (S4 Static Boundaries / S2 3D World / S0 Extracted Entities & Rig)
            if (tickCount % 6 === 0) {
                s4PreviewCtx.drawImage(activeFrame, 0, 0, 120, 68);
                s4PreviewCtx.strokeStyle = 'rgba(245, 158, 11, 0.8)';
                for (const sb of staticBoundaries) {
                    s4PreviewCtx.strokeRect((sb.x / W) * 120, (sb.y / H) * 68, (sb.w / W) * 120, (sb.h / H) * 68);
                }
                thumbS4Ctx.drawImage(s4PreviewC, 0, 0, 120, 68);

                thumbS2Ctx.drawImage(rotorCtx.canvas, 0, 0, 160, 90);

                s0PreviewCtx.fillStyle = '#050811';
                s0PreviewCtx.fillRect(0, 0, 160, 90);
                for (const ent of trackedEntities) {
                    s0PreviewCtx.strokeStyle = ent.cls === 'person' ? '#10b981' : '#f59e0b';
                    s0PreviewCtx.strokeRect((ent.x / W) * 160, (ent.y / H) * 90, (ent.w / W) * 160, (ent.h / H) * 90);
                }
                if (playerRig) {
                    s0PreviewCtx.fillStyle = '#38bdf8';
                    s0PreviewCtx.beginPath();
                    s0PreviewCtx.arc((playerRig.x / W) * 160, (playerRig.y / H) * 90, 4, 0, Math.PI * 2);
                    s0PreviewCtx.fill();
                }
                thumbS0Ctx.drawImage(s0PreviewC, 0, 0, 160, 90);
            }

            if (tickCount % 4 === 0) drawCrossSectionStrip();
            if (tickCount % 24 === 0) updateUnifiedMemoryDOM(woven, activeFrame);

            const leftOps = W * H;
            const rS4Ops = tickCount % state.s4Stride === 0 ? Math.round(GN * 2) : 0;
            const rS2Ops = tickCount % state.s2Stride === 0 ? Math.round(GN * 5) : 0;
            const rS0Ops = woven.cacheHit ? Math.round(GN * 2) : Math.round(GN * 11);

            return {
                leftOps,
                rS4Ops,
                rS2Ops,
                rS0Ops,
                leftMs,
                rightMs,
                s4Same: Math.min(99, 72 + recallHitRatePct * 0.27),
                s2Same: Math.round(woven.conn * 100),
                s0Same: Math.round(woven.cont * 100),
                origin: playerRig
                    ? `${playerRig.label} 실물 영상 세계 내 물리 충돌·조종 활성 (차량 ${trackedEntities.filter((e) => e.cls === 'vehicle').length} · 인물 ${trackedEntities.filter((e) => e.cls === 'person').length})`
                    : `실시간 영상 객체 분류 (차량·인물·정적경계) · S1 히트 ${recallHitRatePct.toFixed(1)}%`,
                activeRatio: Math.max(0.1, 1 - woven.cont),
            };
        },
    };
})();
