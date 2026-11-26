/**
 * Elysia Open Reality Aperture -> Hardware Protocol (CUDA) Scale-Rotor Projection
 * -------------------------------------------------------------------------------
 * 1) OPEN EXTERNAL SENSORY APERTURE (Breaks Closed-Self Solipsism):
 *    Reads real uncontrolled external reality from either:
 *      - Live 1080p HD Video Stream (default, zero permissions needed)
 *      - Live Real Webcam + Microphone (opt-in getUserMedia)
 *    Runs an online unsupervised predictor x_hat(t+1) = advect(x(t), v(t)) against
 *    real incoming frames, measuring genuine External Friction (prediction error)
 *    and dynamically revising Elysia's internal inertia/threshold criteria.
 *
 * 2) HARDWARE-PROTOCOL SCALE-ROTOR DATA LAYOUT (CUDA Warp-32 + Coalesced SoA):
 *    Physically packs live sensory data into TypedArray SoA + Stream-Compacted
 *    index buffers matching CUDA's 32-thread SIMT warp and 128B cache-line rules:
 *      - d_S4_ConstantTile (L2 resident, updated every s4Stride frames)
 *      - d_S2_FlowSoA      (vx[], vy[], energy[], coalesced SoA, every s2Stride)
 *      - d_S0_ActiveTileIdx (stream-compacted contiguous active tiles -> 0% intra-warp divergence)
 */
(function () {
    'use strict';

    const W = 960;
    const H = 540;
    const TILE = 24;
    const COLS = 40; // 40 * 24 = 960
    const ROWS = 22; // 22 * 24 = 528
    const NUM_TILES = COLS * ROWS; // 880 tiles
    const WARP_SIZE = 32;
    const TOTAL_CONV_WARPS = Math.ceil(NUM_TILES / WARP_SIZE); // 28 warps

    // Offscreen downsample sampler (40 x 22 exact tile grid)
    const sampleCanvas = document.createElement('canvas');
    sampleCanvas.width = COLS;
    sampleCanvas.height = ROWS;
    const sampleCtx = sampleCanvas.getContext('2d', { willReadFrequently: true });

    // Real Protocol-Aligned TypedArray Buffers (Mirroring CUDA Device Memory)
    const curLuma = new Float32Array(NUM_TILES);
    const prevLuma = new Float32Array(NUM_TILES);
    const predLuma = new Float32Array(NUM_TILES);
    const predErr = new Float32Array(NUM_TILES);

    const d_S4_ConstantTile = new Float32Array(NUM_TILES);
    const d_S2_Vx = new Float32Array(NUM_TILES);
    const d_S2_Vy = new Float32Array(NUM_TILES);
    const d_S2_Energy = new Float32Array(NUM_TILES);
    const d_S0_ActiveMask = new Uint8Array(NUM_TILES);
    const d_S0_ActiveTileIdx = new Uint32Array(NUM_TILES); // Stream-compacted contiguous indices!
    const d_S0_DeltaPayload = new Float32Array(NUM_TILES);

    // Live Webcam + Microphone State
    let sensorySource = 'video'; // 'video' | 'webcam'
    let camVideoEl = null;
    let camStream = null;
    let micAudioCtx = null;
    let micAnalyser = null;
    let micFreqBuf = null;
    let micRms = 0;
    let camStatusText = '열린 외부 감각: HD 실물 영상 스트림 수신 중 (웹캠·마이크 개방 가능)';

    // Elysia Online Self-Boundary & Criteria Revision State
    let tickCount = 0;
    let initialized = false;
    let internalAlpha = 0.36; // Adaptive temporal inertia (self-revised by real external friction)
    let adaptiveThreshold = 14.0; // Adaptive S0 dispatch threshold
    let rollingFriction = 0;
    let revisionCount = 0;
    let lastRevisionReason = '외부 실물 스트림 관측 개시 — 예측 오차 기반 기준 자동 보정 대기';

    // Live CUDA Telemetry Snapshot
    let hwStats = {
        activeTiles: 0,
        convWarps: TOTAL_CONV_WARPS,
        convDivergentWarps: 0,
        convWarpEffPct: 100,
        rotorWarps: 0,
        rotorWarpEffPct: 100,
        convHbmKB: (W * H * 4 * 2) / 1024, // Full frame R+W = 4050 KB
        rotorHbmKB: 0,
        hbmSavedPct: 0,
        meanFriction: 0,
        maxFrictionTile: -1,
    };

    function setCamStatus(msg) {
        camStatusText = msg;
        const el = document.getElementById('open-sensory-status');
        if (el) el.textContent = msg;
    }

    async function enableWebcamAndMic() {
        if (camStream) {
            sensorySource = 'webcam';
            setCamStatus('● 열린 현실 감각 활성: 실시간 웹캠 + 마이크(광자·음압) 직접 수신 중');
            return true;
        }
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setCamStatus('✖ 이 브라우저는 웹캠/마이크 API를 지원하지 않아 HD 실물 영상 감각으로 유지합니다.');
            return false;
        }
        try {
            setCamStatus('▲ 현실 외부 감각(웹캠·마이크) 개방 요청 중...');
            camStream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 960 }, height: { ideal: 540 } },
                audio: true,
            });
            if (!camVideoEl) {
                camVideoEl = document.createElement('video');
                camVideoEl.muted = true;
                camVideoEl.playsInline = true;
            }
            camVideoEl.srcObject = camStream;
            await camVideoEl.play();

            // Attach real microphone analyser if audio track present
            if (camStream.getAudioTracks().length > 0) {
                const AC = window.AudioContext || window.webkitAudioContext;
                if (AC) {
                    micAudioCtx = new AC();
                    const src = micAudioCtx.createMediaStreamSource(camStream);
                    micAnalyser = micAudioCtx.createAnalyser();
                    micAnalyser.fftSize = 256;
                    src.connect(micAnalyser);
                    micFreqBuf = new Uint8Array(micAnalyser.frequencyBinCount);
                }
            }
            sensorySource = 'webcam';
            initialized = false;
            setCamStatus('● 열린 현실 감각 활성: 실시간 웹캠 + 마이크(광자·음압) 직접 수신 중');
            if (typeof window.__elysiaOnExternalInfluence === 'function') {
                window.__elysiaOnExternalInfluence('열린 현실 감각(실시간 웹캠·마이크) 개방');
            }
            return true;
        } catch {
            // Try video-only fallback if mic denied
            try {
                camStream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 960 }, height: { ideal: 540 } }, audio: false });
                if (!camVideoEl) {
                    camVideoEl = document.createElement('video');
                    camVideoEl.muted = true;
                    camVideoEl.playsInline = true;
                }
                camVideoEl.srcObject = camStream;
                await camVideoEl.play();
                sensorySource = 'webcam';
                initialized = false;
                setCamStatus('● 열린 현실 감각 활성: 실시간 웹캠(영상 전용) 수신 중');
                return true;
            } catch {
                sensorySource = 'video';
                setCamStatus('● 웹캠 권한 미허용 — 실물 1080p HD 외부 영상 스트림으로 열린 감각 검증 지속');
                return false;
            }
        }
    }

    function stopWebcamAndMic() {
        if (camStream) {
            camStream.getTracks().forEach((t) => t.stop());
            camStream = null;
        }
        if (micAudioCtx) {
            micAudioCtx.close().catch(() => {});
            micAudioCtx = null;
            micAnalyser = null;
            micFreqBuf = null;
        }
        micRms = 0;
        sensorySource = 'video';
        initialized = false;
        setCamStatus('● 열린 외부 감각: HD 실물 영상 스트림 수신 중 (웹캠·마이크 언제든 개방 가능)');
    }

    function sampleMicRms() {
        if (!micAnalyser || !micFreqBuf) {
            micRms *= 0.85;
            return;
        }
        micAnalyser.getByteTimeDomainData(micFreqBuf);
        let sumSq = 0;
        for (let i = 0; i < micFreqBuf.length; i++) {
            const v = (micFreqBuf[i] - 128) / 128;
            sumSq += v * v;
        }
        const rms = Math.sqrt(sumSq / micFreqBuf.length);
        micRms = micRms * 0.65 + Math.min(1, rms * 4.5) * 0.35;
    }

    function buildLiveCudaSnippet(s4Stride, s2Stride) {
        return [
            `// Elysia Hardware-Protocol Scale-Rotor CUDA Layout (Live Generated)`,
            `// Grid: ${COLS}x${ROWS}=${NUM_TILES} tiles | Warp=32 | Active S0=${hwStats.activeTiles} (${hwStats.rotorWarps} coalesced warps)`,
            `struct alignas(128) S2FlowSoA { float vx[${NUM_TILES}]; float vy[${NUM_TILES}]; float energy[${NUM_TILES}]; };`,
            `__constant__ float d_S4_MacroField[${NUM_TILES}]; // Updated 1/${s4Stride} frames (L2/Const Resident)`,
            ``,
            `__global__ void elysia_s0_compacted_rotor_kernel(`,
            `    const uint32_t* __restrict__ d_S0_ActiveTileIdx, // Contiguous compacted [0..${hwStats.activeTiles - 1}]`,
            `    const float*    __restrict__ d_S0_DeltaPayload,  // Zero branch divergence inside 32-lane warp`,
            `    const S2FlowSoA* __restrict__ d_S2,              // Updated 1/${s2Stride} frames (Coalesced SoA)`,
            `    float*          __restrict__ d_OutFrame,`,
            `    uint32_t activeCount) {`,
            `    uint32_t tid = blockIdx.x * blockDim.x + threadIdx.x;`,
            `    if (tid >= activeCount) return; // Only final tail warp pads; 0% intra-warp branch waste!`,
            `    uint32_t tileId = d_S0_ActiveTileIdx[tid];`,
            `    d_OutFrame[tileId] = d_S4_MacroField[tileId] + d_S2->energy[tileId] + d_S0_DeltaPayload[tid];`,
            `}`,
            `// Launch: <<<${Math.max(1, hwStats.rotorWarps)}, 32>>> vs Conventional <<<${TOTAL_CONV_WARPS}, 32>>> (HBM -${hwStats.hbmSavedPct.toFixed(1)}%)`,
        ].join('\n');
    }

    function updateOpenCudaDOM(s4Stride, s2Stride) {
        const setTxt = (id, txt) => {
            const el = document.getElementById(id);
            if (el) el.textContent = txt;
        };
        setTxt('open-sensory-status', camStatusText);
        setTxt('cuda-conv-stat',
            `워프 ${hwStats.convWarps}개 전수 실행 · 분기 손실 워프 ${hwStats.convDivergentWarps}개 · 워프 효율 ${hwStats.convWarpEffPct.toFixed(1)}% · HBM ${hwStats.convHbmKB.toFixed(0)} KB/f`);
        setTxt('cuda-rotor-stat',
            `압축 워프 ${hwStats.rotorWarps}개만 실행 · 내부 분기 0% · 워프 효율 ${hwStats.rotorWarpEffPct.toFixed(1)}% · HBM ${hwStats.rotorHbmKB.toFixed(1)} KB/f (-${hwStats.hbmSavedPct.toFixed(1)}%)`);
        setTxt('open-friction-stat',
            `외부 현실 예측 마찰(평균 오차): ${hwStats.meanFriction.toFixed(1)} · 내부 관성 α=${internalAlpha.toFixed(2)} · S0 문턱 τ=${adaptiveThreshold.toFixed(1)} · 자율 기준수정 ${revisionCount}회`);
        setTxt('open-revision-note', lastRevisionReason);

        const codeEl = document.getElementById('cuda-live-kernel-code');
        if (codeEl) codeEl.textContent = buildLiveCudaSnippet(s4Stride, s2Stride);
    }

    function drawWarpExecutionStrip(ctx, yTop) {
        // Bottom Hardware Monitor Panel inside Right Canvas
        ctx.fillStyle = '#060a14';
        ctx.fillRect(0, yTop, W, H - yTop);
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(0, yTop); ctx.lineTo(W, yTop); ctx.stroke();

        ctx.font = '700 10px "IBM Plex Mono", monospace';
        ctx.textAlign = 'left';

        // Row 1: Conventional Flat CUDA Warps (28 warps x 32 lanes, showing exact lane divergence!)
        ctx.fillStyle = '#fb7185';
        ctx.fillText(
            `기존 평면 CUDA (28 Warps × 32 Lanes · 분기 손실 워프 ${hwStats.convDivergentWarps}개 · 효율 ${hwStats.convWarpEffPct.toFixed(0)}%)`,
            14, yTop + 17
        );

        const stripX = 14;
        const stripW = W - 28;
        const warpGap = 3;
        const warpW = (stripW - (TOTAL_CONV_WARPS - 1) * warpGap) / TOTAL_CONV_WARPS;
        const row1Y = yTop + 24;
        const rowH = 34;

        for (let w = 0; w < TOTAL_CONV_WARPS; w++) {
            const wx = stripX + w * (warpW + warpGap);
            let activeInWarp = 0;
            for (let lane = 0; lane < WARP_SIZE; lane++) {
                const idx = w * WARP_SIZE + lane;
                if (idx < NUM_TILES && d_S0_ActiveMask[idx]) activeInWarp += 1;
            }
            const divergent = activeInWarp > 0 && activeInWarp < WARP_SIZE;
            // Background of warp box
            ctx.fillStyle = activeInWarp === 0 ? '#0f172a' : (divergent ? 'rgba(244, 63, 94, 0.25)' : 'rgba(16, 185, 129, 0.25)');
            ctx.fillRect(wx, row1Y, warpW, rowH);
            // Draw 32 mini-lanes (8x4 grid inside each warp block)
            const cellW = warpW / 8;
            const cellH = rowH / 4;
            for (let lane = 0; lane < WARP_SIZE; lane++) {
                const idx = w * WARP_SIZE + lane;
                const lx = wx + (lane % 8) * cellW;
                const ly = row1Y + Math.floor(lane / 8) * cellH;
                if (idx < NUM_TILES && d_S0_ActiveMask[idx]) {
                    ctx.fillStyle = '#f59e0b';
                    ctx.fillRect(lx + 0.5, ly + 0.5, Math.max(1, cellW - 1), Math.max(1, cellH - 1));
                } else if (divergent) {
                    // Masked/wasted lane inside divergent warp!
                    ctx.fillStyle = 'rgba(244, 63, 94, 0.58)';
                    ctx.fillRect(lx + 0.5, ly + 0.5, Math.max(1, cellW - 1), Math.max(1, cellH - 1));
                }
            }
            ctx.strokeStyle = divergent ? '#f43f5e' : '#334155';
            ctx.lineWidth = 0.8;
            ctx.strokeRect(wx, row1Y, warpW, rowH);
        }

        // Row 2: Elysia Scale-Rotor Compacted CUDA Warps (contiguous packed active lanes!)
        const row2LabelY = row1Y + rowH + 18;
        ctx.fillStyle = '#34d399';
        ctx.fillText(
            `엘리시아 스케일로터 압축 배열 (${hwStats.rotorWarps} Warps만 실행 · 내부 분기 0% · 워프 효율 ${hwStats.rotorWarpEffPct.toFixed(0)}% · HBM -${hwStats.hbmSavedPct.toFixed(1)}%)`,
            14, row2LabelY
        );
        const row2Y = row2LabelY + 7;

        for (let w = 0; w < TOTAL_CONV_WARPS; w++) {
            const wx = stripX + w * (warpW + warpGap);
            if (w < hwStats.rotorWarps) {
                const lanesInThisWarp = Math.min(WARP_SIZE, hwStats.activeTiles - w * WARP_SIZE);
                ctx.fillStyle = 'rgba(16, 185, 129, 0.18)';
                ctx.fillRect(wx, row2Y, warpW, rowH);
                const cellW = warpW / 8;
                const cellH = rowH / 4;
                for (let lane = 0; lane < lanesInThisWarp; lane++) {
                    const lx = wx + (lane % 8) * cellW;
                    const ly = row2Y + Math.floor(lane / 8) * cellH;
                    ctx.fillStyle = '#22d3ee';
                    ctx.fillRect(lx + 0.5, ly + 0.5, Math.max(1, cellW - 1), Math.max(1, cellH - 1));
                }
                ctx.strokeStyle = '#10b981';
                ctx.lineWidth = 1;
                ctx.strokeRect(wx, row2Y, warpW, rowH);
            } else {
                // Unlaunched — hardware power/bandwidth completely saved!
                ctx.fillStyle = '#070c16';
                ctx.fillRect(wx, row2Y, warpW, rowH);
                ctx.strokeStyle = '#1e293b';
                ctx.lineWidth = 0.7;
                ctx.strokeRect(wx, row2Y, warpW, rowH);
            }
        }
    }

    window.ElysiaOpenCudaRotor = {
        enableWebcamAndMic,
        stopWebcamAndMic,
        getSensorySource() { return sensorySource; },
        copyCudaKernel() {
            const el = document.getElementById('cuda-live-kernel-code');
            if (!el || !navigator.clipboard) return false;
            navigator.clipboard.writeText(el.textContent || '').catch(() => {});
            return true;
        },
        step({ legacyCtx, rotorCtx, thumbS4Ctx, thumbS2Ctx, thumbS0Ctx, capCanvas, state }) {
            tickCount += 1;
            sampleMicRms();

            // 1) Draw live OPEN EXTERNAL REALITY onto Left Canvas
            const tL0 = performance.now();
            const usingCam = sensorySource === 'webcam' && camVideoEl && camVideoEl.readyState >= 2 && camVideoEl.videoWidth > 0;
            const srcDrawable = usingCam ? camVideoEl : capCanvas;

            legacyCtx.fillStyle = '#04070f';
            legacyCtx.fillRect(0, 0, W, H);
            if (usingCam) {
                // Mirror webcam naturally
                legacyCtx.save();
                legacyCtx.translate(W, 0);
                legacyCtx.scale(-1, 1);
                legacyCtx.drawImage(camVideoEl, 0, 0, W, H);
                legacyCtx.restore();
            } else {
                legacyCtx.drawImage(capCanvas, 0, 0, W, H);
            }

            // Downsample exact 40x22 reality grid
            sampleCtx.drawImage(legacyCtx.canvas, 0, 0, COLS, ROWS);
            const px = sampleCtx.getImageData(0, 0, COLS, ROWS).data;

            for (let i = 0; i < NUM_TILES; i++) {
                const o = i * 4;
                curLuma[i] = px[o] * 0.299 + px[o + 1] * 0.587 + px[o + 2] * 0.114;
            }
            if (!initialized) {
                prevLuma.set(curLuma);
                predLuma.set(curLuma);
                d_S4_ConstantTile.set(curLuma);
                initialized = true;
            }
            const leftMs = performance.now() - tL0;

            // 2) Elysia Open-Boundary Prediction vs Real External Friction + CUDA Scale-Rotor Packing
            const tR0 = performance.now();
            const s4Stride = Math.max(1, state.s4Stride || 12);
            const s2Stride = Math.max(1, state.s2Stride || 3);
            const updateS4 = tickCount % s4Stride === 0;
            const updateS2 = tickCount % s2Stride === 0;

            // Acoustic sensitivity lowers S0 trigger slightly when real room sound spikes
            const effectiveThresh = Math.max(6, adaptiveThreshold - micRms * 5.5);

            let frictionSum = 0;
            let maxFriction = 0;
            let maxTile = -1;
            let activeCount = 0;

            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    const i = r * COLS + c;
                    if (updateS4) {
                        d_S4_ConstantTile[i] = d_S4_ConstantTile[i] * 0.72 + curLuma[i] * 0.28;
                    }

                    // Spatial gradient optical-flow proxy for S2 Coalesced SoA
                    if (updateS2) {
                        const cL = Math.max(0, c - 1);
                        const cR = Math.min(COLS - 1, c + 1);
                        const rU = Math.max(0, r - 1);
                        const rD = Math.min(ROWS - 1, r + 1);
                        const gx = (curLuma[r * COLS + cR] - curLuma[r * COLS + cL]) * 0.5;
                        const gy = (curLuma[rD * COLS + c] - curLuma[rU * COLS + c]) * 0.5;
                        const dt = curLuma[i] - prevLuma[i];
                        const denom = gx * gx + gy * gy + 18.0;
                        const vx = (-dt * gx) / denom;
                        const vy = (-dt * gy) / denom;
                        d_S2_Vx[i] = d_S2_Vx[i] * (1 - internalAlpha) + Math.max(-2.2, Math.min(2.2, vx * 4.5)) * internalAlpha;
                        d_S2_Vy[i] = d_S2_Vy[i] * (1 - internalAlpha) + Math.max(-2.2, Math.min(2.2, vy * 4.5)) * internalAlpha;
                        d_S2_Energy[i] = Math.hypot(d_S2_Vx[i], d_S2_Vy[i]);
                    }

                    // Internal prediction from previous frame advected by internal S2 velocity
                    const srcC = Math.max(0, Math.min(COLS - 1, Math.round(c - d_S2_Vx[i] * 0.45)));
                    const srcR = Math.max(0, Math.min(ROWS - 1, Math.round(r - d_S2_Vy[i] * 0.45)));
                    predLuma[i] = prevLuma[srcR * COLS + srcC];

                    // Genuine External Friction (uncontrolled reality minus internal prediction)
                    const err = Math.abs(curLuma[i] - predLuma[i]);
                    predErr[i] = err;
                    frictionSum += err;
                    if (err > maxFriction) {
                        maxFriction = err;
                        maxTile = i;
                    }

                    // Stream Compaction into Contiguous CUDA S0 Buffer (Eliminates Intra-Warp Divergence!)
                    if (err > effectiveThresh) {
                        d_S0_ActiveMask[i] = 1;
                        d_S0_ActiveTileIdx[activeCount] = i;
                        d_S0_DeltaPayload[activeCount] = curLuma[i] - d_S4_ConstantTile[i];
                        activeCount += 1;
                    } else {
                        d_S0_ActiveMask[i] = 0;
                    }
                }
            }

            // Online Self-Revision of Elysia's Internal Boundary Criteria from Real External Friction
            const meanFriction = frictionSum / NUM_TILES;
            rollingFriction = rollingFriction * 0.9 + meanFriction * 0.1;
            if (tickCount % 35 === 0) {
                if (rollingFriction > 11.5 && internalAlpha < 0.72) {
                    internalAlpha = Math.min(0.75, internalAlpha + 0.06);
                    adaptiveThreshold = Math.max(9.0, adaptiveThreshold - 0.8);
                    revisionCount += 1;
                    lastRevisionReason = `[자기수정 #${revisionCount}] 외부 현실 급변(마찰 ${rollingFriction.toFixed(1)}) → 내부 관성 α=${internalAlpha.toFixed(2)} 가속, S0 감도 상향`;
                } else if (rollingFriction < 4.5 && internalAlpha > 0.20) {
                    internalAlpha = Math.max(0.18, internalAlpha - 0.04);
                    adaptiveThreshold = Math.min(18.0, adaptiveThreshold + 0.6);
                    revisionCount += 1;
                    lastRevisionReason = `[자기수정 #${revisionCount}] 외부 안정화(마찰 ${rollingFriction.toFixed(1)}) → L2 보존 강화(α=${internalAlpha.toFixed(2)}), 불필요 워프 절감`;
                }
            }

            // Measure Honest Conventional vs Scale-Rotor CUDA Warp Efficiency & HBM Bandwidth
            let convDivWarps = 0;
            let convActiveWarps = 0;
            for (let w = 0; w < TOTAL_CONV_WARPS; w++) {
                let k = 0;
                for (let lane = 0; lane < WARP_SIZE; lane++) {
                    const idx = w * WARP_SIZE + lane;
                    if (idx < NUM_TILES && d_S0_ActiveMask[idx]) k += 1;
                }
                if (k > 0) convActiveWarps += 1;
                if (k > 0 && k < WARP_SIZE) convDivWarps += 1;
            }
            const rotorWarps = Math.ceil(activeCount / WARP_SIZE);
            const convWarpEffPct = convActiveWarps > 0 ? (activeCount / (convActiveWarps * WARP_SIZE)) * 100 : 0;
            const rotorWarpEffPct = rotorWarps > 0 ? (activeCount / (rotorWarps * WARP_SIZE)) * 100 : 100;

            const convHbmKB = (W * H * 4 * 2) / 1024; // 4050 KB/frame
            const s4KB = updateS4 ? (NUM_TILES * 4) / 1024 : 0;
            const s2KB = updateS2 ? (NUM_TILES * 12) / 1024 : 0;
            const s0KB = (activeCount * (TILE * TILE * 4 + 8)) / 1024;
            const rotorHbmKB = Math.max(1.2, s4KB + s2KB + s0KB);
            const hbmSavedPct = Math.max(0, (1 - rotorHbmKB / convHbmKB) * 100);

            hwStats = {
                activeTiles: activeCount,
                convWarps: TOTAL_CONV_WARPS,
                convDivergentWarps: convDivWarps,
                convWarpEffPct,
                rotorWarps,
                rotorWarpEffPct,
                convHbmKB,
                rotorHbmKB,
                hbmSavedPct,
                meanFriction,
                maxFrictionTile: maxTile,
            };

            // Overlay Real External Friction Hotspots & Mic RMS onto Left Canvas
            if (maxTile >= 0 && maxFriction > effectiveThresh) {
                const mr = Math.floor(maxTile / COLS);
                const mc = maxTile % COLS;
                legacyCtx.strokeStyle = '#f43f5e';
                legacyCtx.lineWidth = 2;
                legacyCtx.strokeRect(mc * TILE, mr * TILE, TILE, TILE);
                legacyCtx.fillStyle = 'rgba(244, 63, 94, 0.9)';
                legacyCtx.font = '700 10px "IBM Plex Mono", monospace';
                legacyCtx.fillText(`외부 마찰 정점 Δ=${maxFriction.toFixed(0)}`, Math.min(W - 140, mc * TILE), Math.max(46, mr * TILE - 5));
            }
            legacyCtx.fillStyle = 'rgba(6, 10, 19, 0.86)';
            legacyCtx.fillRect(14, 12, 470, 26);
            legacyCtx.strokeStyle = usingCam ? '#10b981' : '#38bdf8';
            legacyCtx.lineWidth = 1.2;
            legacyCtx.strokeRect(14, 12, 470, 26);
            legacyCtx.fillStyle = usingCam ? '#34d399' : '#38bdf8';
            legacyCtx.font = '700 10px "IBM Plex Mono", monospace';
            legacyCtx.fillText(
                usingCam
                    ? `● 열린 현실 감각 (실시간 웹캠+마이크 RMS ${(micRms * 100).toFixed(0)}%) · 예측 마찰 ${meanFriction.toFixed(1)}`
                    : `● 열린 외부 감각 (1080p 실물 영상) · 내부 예측 vs 현실 마찰 ${meanFriction.toFixed(1)}`,
                22, 29
            );

            // 3) Render Right Canvas: Live CUDA Scale-Rotor Spatial Map (top 406px) + Warp Ribbon (bottom 134px)
            const splitY = 406;
            rotorCtx.fillStyle = '#050811';
            rotorCtx.fillRect(0, 0, W, splitY);

            rotorCtx.save();
            rotorCtx.globalAlpha = 0.42;
            rotorCtx.drawImage(legacyCtx.canvas, 0, 0, W, H, 0, 0, W, splitY);
            rotorCtx.restore();

            const scaleY = splitY / H;
            // Draw S2 Coalesced Flow Vectors & S0 Compacted Active CUDA Tiles
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    const i = r * COLS + c;
                    const tx = c * TILE;
                    const ty = r * TILE * scaleY;
                    const th = TILE * scaleY;

                    if (d_S0_ActiveMask[i]) {
                        rotorCtx.fillStyle = 'rgba(34, 211, 238, 0.24)';
                        rotorCtx.fillRect(tx + 1, ty + 1, TILE - 2, th - 2);
                        rotorCtx.strokeStyle = predErr[i] > effectiveThresh * 2 ? '#f59e0b' : '#22d3ee';
                        rotorCtx.lineWidth = 1.1;
                        rotorCtx.strokeRect(tx + 1, ty + 1, TILE - 2, th - 2);
                    }
                    if (d_S2_Energy[i] > 0.25) {
                        const cx = tx + TILE * 0.5;
                        const cy = ty + th * 0.5;
                        rotorCtx.strokeStyle = '#34d399';
                        rotorCtx.lineWidth = 1.3;
                        rotorCtx.beginPath();
                        rotorCtx.moveTo(cx, cy);
                        rotorCtx.lineTo(cx + d_S2_Vx[i] * 8, cy + d_S2_Vy[i] * 8);
                        rotorCtx.stroke();
                    }
                }
            }

            rotorCtx.fillStyle = 'rgba(6, 10, 19, 0.88)';
            rotorCtx.fillRect(14, 12, 520, 26);
            rotorCtx.strokeStyle = '#10b981';
            rotorCtx.lineWidth = 1.2;
            rotorCtx.strokeRect(14, 12, 520, 26);
            rotorCtx.fillStyle = '#34d399';
            rotorCtx.font = '700 10px "IBM Plex Mono", monospace';
            rotorCtx.fillText(
                `CUDA 스케일로터 투영 · 활성 S0 타일 ${activeCount}/${NUM_TILES} → 압축 워프 ${rotorWarps}/${TOTAL_CONV_WARPS} · HBM -${hbmSavedPct.toFixed(1)}%`,
                22, 29
            );

            drawWarpExecutionStrip(rotorCtx, splitY);
            const rightMs = performance.now() - tR0;

            // Update mini 3-track previews
            if (tickCount % 3 === 0) {
                thumbS4Ctx.drawImage(legacyCtx.canvas, 0, 0, 120, 68);
                thumbS2Ctx.drawImage(rotorCtx.canvas, 0, 0, W, splitY, 0, 0, 160, 90);
                thumbS0Ctx.drawImage(rotorCtx.canvas, 0, splitY, W, H - splitY, 0, 0, 160, 90);
            }

            prevLuma.set(curLuma);
            if (tickCount % 6 === 0) updateOpenCudaDOM(s4Stride, s2Stride);

            return {
                leftOps: NUM_TILES * 64,
                rS4Ops: updateS4 ? NUM_TILES : 0,
                rS2Ops: updateS2 ? NUM_TILES * 4 : 0,
                rS0Ops: activeCount * 32 + rotorWarps * 16,
                leftMs,
                rightMs,
                s4Same: Math.max(60, 100 - meanFriction * 1.4),
                s2Same: rotorWarpEffPct,
                s0Same: Math.max(0, 100 - (activeCount / NUM_TILES) * 100),
                origin: `열린 감각 → CUDA 압축 워프 ${rotorWarps}/${TOTAL_CONV_WARPS}개 (분기 손실 ${convDivWarps}→0개, HBM -${hbmSavedPct.toFixed(1)}%)`,
                activeRatio: Math.max(0.08, Math.min(1, activeCount / NUM_TILES + micRms * 0.25)),
            };
        },
    };
})();
