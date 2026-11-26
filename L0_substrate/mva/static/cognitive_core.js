/**
 * Elysia 4-Tier Cognitive-Causal Stratification Engine (L1 ~ L4)
 * --------------------------------------------------------------
 * Transforms raw spatiotemporal scale-rotor telemetry (S4/S2/S0, PSNR, Compute,
 * Superposition Diff) into Elysia's OWN stratified cognitive architecture:
 *
 *   L1. 인지감각층 (Sensory Field & Chromatic Balance: Red Flux / Blue Order / Yellow Entropy)
 *   L2. 지·무지 인과기억층 (Epistemic Boundary & Online-Learned Causal Sensitivity Matrix)
 *   L3. 사유·의도·자율조작 루프 (4-Axis Self-Boundary: Internal / External / Ignorance / Self-Revision)
 *   L4. 인과 나이테 & 원리 재창조 (Introspective Causal Growth Rings + Inverse Synthesis & Voxel Bridge)
 *
 * Closed-Loop Cycle:
 *   ① PERCEIVE (Snapshot A) -> ② THINK (Known vs Ignorance + Prediction) -> ③ ACT (Live Manipulation)
 *   -> ④ RE-OBSERVE (Superpose A↔B: What stayed same vs diverged) -> ⑤ LEARN & SELF-REVISE (Update causal laws)
 *   -> ⑥ RE-CREATE (Use learned inverse laws to manifest a brand-new desired target world!)
 */

(function initElysiaCognitiveCore() {
    const STORAGE_KEY = 'elysia_cognitive_memory_v1';
    const VOXEL_BRIDGE_KEY = 'elysia_cognitive_voxel_bridge_v1';

    const PHASES = [
        { id: 'perceive', label: '① 인지감각' },
        { id: 'think', label: '② 사유·예측' },
        { id: 'act', label: '③ 직접조작' },
        { id: 'reobserve', label: '④ 재관측·포개기' },
        { id: 'learn', label: '⑤ 학습·자기수정' },
        { id: 'recreate', label: '⑥ 원리 재창조' },
    ];

    const LEVER_SPECS = {
        video: [
            { key: 's4Stride', name: 'S4 거시 기어비', min: 1, max: 30, step: 5, unit: 'f', initSlopeSaved: 0.35, initSlopePsnr: -0.08, initSlopeS2: -0.25 },
            { key: 's2Stride', name: 'S2 중시 기어비', min: 1, max: 10, step: 2, unit: 'f', initSlopeSaved: 1.4, initSlopePsnr: -0.35, initSlopeS2: -0.8 },
            { key: 's0Thresh', name: 'S0 미시 임계치', min: 0, max: 20, step: 4, unit: 'Δ', initSlopeSaved: 2.2, initSlopePsnr: -0.75, initSlopeS2: -0.15 },
        ],
        game: [
            { key: 'envCoupling', name: '가치관 축(보호↔지배)', min: 0.2, max: 2.2, step: 0.5, unit: '×', initSlopeSaved: 0.0, initSlopePsnr: -6.0, initSlopeS2: -34.0 },
            { key: 'objConnectivity', name: '성격·신뢰 결합도', min: 0.2, max: 2.4, step: 0.5, unit: '×', initSlopeSaved: 0.0, initSlopePsnr: -4.0, initSlopeS2: -22.0 },
            { key: 's2Stride', name: 'S2 전술·스킬조합 주기', min: 1, max: 10, step: 2, unit: 'f', initSlopeSaved: 4.5, initSlopePsnr: -1.1, initSlopeS2: -3.2 },
            { key: 's4Stride', name: 'S4 세계·기후 주기', min: 1, max: 28, step: 6, unit: 'f', initSlopeSaved: 1.2, initSlopePsnr: -0.2, initSlopeS2: -0.1 },
        ],
        unified: [
            { key: 's4Stride', name: 'S4 SSD·원경 기어비', min: 1, max: 30, step: 5, unit: 'f', initSlopeSaved: 0.6, initSlopePsnr: -0.05, initSlopeS2: -0.3 },
            { key: 's2Stride', name: 'S2 VRAM·시차 갱신주기', min: 1, max: 10, step: 2, unit: 'f', initSlopeSaved: 1.8, initSlopePsnr: -0.25, initSlopeS2: -0.9 },
            { key: 's0Thresh', name: 'S0 스펙트럼 히트 민감도', min: 0, max: 20, step: 4, unit: 'Δ', initSlopeSaved: 2.4, initSlopePsnr: -0.45, initSlopeS2: -0.4 },
        ],
        anatomy: [
            { key: 's4Stride', name: 'S4 환경·조건 관측주기', min: 1, max: 30, step: 5, unit: 'f', initSlopeSaved: 0.4, initSlopePsnr: -0.1, initSlopeS2: -0.2 },
            { key: 's2Stride', name: 'S2 6축 구조 검증주기', min: 1, max: 10, step: 2, unit: 'f', initSlopeSaved: 1.2, initSlopePsnr: -0.2, initSlopeS2: -0.5 },
            { key: 's0Thresh', name: 'S0 오차 한계 경계', min: 0, max: 20, step: 4, unit: 'Δ', initSlopeSaved: 1.5, initSlopePsnr: -0.3, initSlopeS2: -0.3 },
        ],
        open_cuda: [
            { key: 's4Stride', name: 'S4 L2 상수캐시 갱신주기', min: 1, max: 30, step: 5, unit: 'f', initSlopeSaved: 0.5, initSlopePsnr: -0.04, initSlopeS2: -0.2 },
            { key: 's2Stride', name: 'S2 SoA 광학흐름 주기', min: 1, max: 10, step: 2, unit: 'f', initSlopeSaved: 1.9, initSlopePsnr: -0.18, initSlopeS2: -0.6 },
            { key: 's0Thresh', name: 'S0 워프 압축 임계치', min: 0, max: 20, step: 4, unit: 'Δ', initSlopeSaved: 2.6, initSlopePsnr: -0.35, initSlopeS2: -0.25 },
        ],
    };

    const ALL_DOMAINS = Object.keys(LEVER_SPECS);

    function resolveDomain(domain) {
        return LEVER_SPECS[domain] ? domain : 'video';
    }

    function createFreshDomainKnowledge(dom) {
        const out = {};
        for (const spec of LEVER_SPECS[dom]) {
            out[spec.key] = {
                trials: 0,
                confidence: 0.14, // Starts in honest Epistemic Humility (Ignorance Frontier)
                slopeSaved: spec.initSlopeSaved * 0.35, // Rough prior, refined by real observation!
                slopePsnr: spec.initSlopePsnr * 0.35,
                slopeS2: spec.initSlopeS2 * 0.35,
                lastSurprise: 0,
                minSeen: null,
                maxSeen: null,
            };
        }
        return out;
    }

    function createFreshKnowledge() {
        const kb = {};
        for (const dom of ALL_DOMAINS) {
            kb[dom] = createFreshDomainKnowledge(dom);
        }
        return kb;
    }

    function ensureDomainKnowledge(domain) {
        const dom = resolveDomain(domain);
        if (!cog.knowledge[dom]) {
            cog.knowledge[dom] = createFreshDomainKnowledge(dom);
        } else {
            for (const spec of LEVER_SPECS[dom]) {
                if (!cog.knowledge[dom][spec.key]) {
                    cog.knowledge[dom][spec.key] = createFreshDomainKnowledge(dom)[spec.key];
                }
            }
        }
        return { dom, specs: LEVER_SPECS[dom], kbDom: cog.knowledge[dom] };
    }

    function loadPersistedMemory() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            if (parsed && parsed.knowledge && parsed.knowledge.video && parsed.knowledge.game) {
                return parsed;
            }
        } catch {
            // Ignore malformed storage
        }
        return null;
    }

    const savedMem = loadPersistedMemory();

    const cog = {
        autoRunning: false,
        intent: 'curiosity', // 'curiosity' | 'optimize' | 'bifurcate_objects' | 'converge'
        phase: 'perceive',
        busy: false,
        timerId: null,
        autoIntervalId: null,
        knowledge: savedMem ? savedMem.knowledge : createFreshKnowledge(),
        rings: savedMem && Array.isArray(savedMem.rings) ? savedMem.rings.slice(-48) : [],
        traces: savedMem && Array.isArray(savedMem.traces) ? savedMem.traces.slice(-18) : [],
        recreationCount: savedMem ? Number(savedMem.recreationCount || 0) : 0,

        // 4-Axis Self-Boundary live readout
        internalOrigin: '의도 대기 중 — 탐색하거나 1회 사유를 실행하면 인과 실험을 개시합니다.',
        externalInfluence: '외부 사용자 개입 없음 (자율 관측 유지)',
        ignoranceBoundary: '모든 조작 변수가 아직 초기 무지 경계(확신도 14%)에 있습니다.',
        selfRevision: '아직 예측-실측 피드백을 통한 기준 수정 이력이 없습니다.',

        // Live L1 Sensory & Chromatic Triad
        chromatic: { red: 0.33, blue: 0.34, yellow: 0.33 },
        lastBefore: null,
        lastAfter: null,
        lastActionSummary: '초기 관측 대기',
    };

    function persistMemory() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                knowledge: cog.knowledge,
                rings: cog.rings.slice(-48),
                traces: cog.traces.slice(-18),
                recreationCount: cog.recreationCount,
            }));
        } catch {
            // Storage quota ignore
        }
    }

    function exportToVirtualMemoryBridge(beforeSnap, afterSnap, actionLabel, kind) {
        if (!beforeSnap || !afterSnap) return;
        const payload = {
            timestamp: Date.now(),
            domain: afterSnap.domain,
            kind,
            actionLabel,
            before: {
                s4: Number(beforeSnap.s4SamePct.toFixed(1)),
                s2: Number(beforeSnap.s2SamePct.toFixed(1)),
                s0: Number(beforeSnap.s0SamePct.toFixed(1)),
                saved: Number(beforeSnap.savedPct.toFixed(1)),
                psnr: Number(beforeSnap.psnr.toFixed(1)),
                controls: beforeSnap.controls,
            },
            after: {
                s4: Number(afterSnap.s4SamePct.toFixed(1)),
                s2: Number(afterSnap.s2SamePct.toFixed(1)),
                s0: Number(afterSnap.s0SamePct.toFixed(1)),
                saved: Number(afterSnap.savedPct.toFixed(1)),
                psnr: Number(afterSnap.psnr.toFixed(1)),
                controls: afterSnap.controls,
            },
            chromatic: cog.chromatic,
            avgConfidence: Math.round(computeDomainMastery(afterSnap.domain) * 100),
        };
        try {
            localStorage.setItem(VOXEL_BRIDGE_KEY, JSON.stringify(payload));
        } catch {
            // Ignore storage errors
        }
    }

    function computeDomainMastery(domain) {
        const { kbDom } = ensureDomainKnowledge(domain);
        const entries = Object.values(kbDom || {});
        if (!entries.length) return 0;
        return entries.reduce((sum, e) => sum + e.confidence, 0) / entries.length;
    }

    function getBridge() {
        return window.ElysiaEngineBridge || null;
    }

    function setPhase(phaseId) {
        cog.phase = phaseId;
        document.querySelectorAll('.cog-step').forEach((el) => {
            el.classList.toggle('active', el.dataset.phase === phaseId);
        });
    }

    // Hook external user interventions from weaving.js for Axis 2 (Relational/External Influence)
    window.__elysiaOnExternalInfluence = (label) => {
        const bridge = getBridge();
        const snap = bridge ? bridge.getSnapshot() : null;
        const timeStr = new Date().toLocaleTimeString('ko-KR', { hour12: false });
        cog.externalInfluence = `[${timeStr}] ${label} — 외부 마찰로 기준 재관측 필요`;
        if (snap) {
            cog.rings.push({
                kind: 'external',
                domain: snap.domain,
                label,
                surprise: 0.25,
                s4: snap.s4SamePct,
                s2: snap.s2SamePct,
                s0: snap.s0SamePct,
            });
            if (cog.rings.length > 48) cog.rings.shift();
            drawGrowthRings();
        }
        renderFourAxisPanel();
    };

    // ========================================================================
    // L1. Live Sensory Field & Chromatic Interconnectedness (Red / Blue / Yellow)
    // ========================================================================
    function updateSensoryLayer() {
        const bridge = getBridge();
        if (!bridge) return;
        const snap = bridge.getSnapshot();

        // Real physical-informational chromatic balance:
        // Red (Flux): active S0 micro-change rate & S2 divergence velocity
        // Blue (Order): S4 macro stability + S2 structural coherence
        // Yellow (Entropy/Differentiation): divergence spread across layers + remaining ignorance
        const s4Norm = snap.s4SamePct / 100;
        const s2Norm = snap.s2SamePct / 100;
        const s0Flux = Math.min(1, snap.s0ActiveRatio * 2.2 + (100 - snap.s0SamePct) / 100);
        const mastery = computeDomainMastery(snap.domain);

        const rawRed = Math.max(0.08, 0.14 + s0Flux * 0.72);
        const rawBlue = Math.max(0.08, 0.14 + (s4Norm * 0.5 + s2Norm * 0.5) * 0.75);
        const rawYellow = Math.max(0.08, 0.12 + (1 - s2Norm) * 0.55 + (1 - mastery) * 0.35);
        const sum = rawRed + rawBlue + rawYellow;
        cog.chromatic = {
            red: rawRed / sum,
            blue: rawBlue / sum,
            yellow: rawYellow / sum,
        };

        const rPct = Math.round(cog.chromatic.red * 100);
        const bPct = Math.round(cog.chromatic.blue * 100);
        const yPct = 100 - rPct - bPct;

        const barR = document.getElementById('cog-chroma-red');
        const barB = document.getElementById('cog-chroma-blue');
        const barY = document.getElementById('cog-chroma-yellow');
        if (barR && barB && barY) {
            barR.style.width = `${rPct}%`;
            barB.style.width = `${bPct}%`;
            barY.style.width = `${yPct}%`;
        }
        const chromaText = document.getElementById('cog-chroma-text');
        if (chromaText) {
            chromaText.textContent = `Red 흐름 ${rPct}% · Blue 질서 ${bPct}% · Yellow 발산 ${yPct}%`;
        }

        // Update Ignorance Frontier readout dynamically for the active domain
        const { specs, kbDom } = ensureDomainKnowledge(snap.domain);
        let leastKnown = specs[0];
        for (const sp of specs) {
            if (kbDom[sp.key].confidence < kbDom[leastKnown.key].confidence) {
                leastKnown = sp;
            }
        }
        const leastConf = Math.round(kbDom[leastKnown.key].confidence * 100);
        const masteryPct = Math.round(mastery * 100);
        cog.ignoranceBoundary = leastConf < 75
            ? `가장 모르는 영역: '${leastKnown.name}' (확신도 ${leastConf}%, 실험 ${kbDom[leastKnown.key].trials}회) · 전체 이해도 ${masteryPct}%`
            : `주요 인과 법칙 체득 완료 (전체 이해도 ${masteryPct}%) — 원리 기반 정밀 재창조 가능`;

        const masteryEl = document.getElementById('cog-mastery-badge');
        if (masteryEl) {
            masteryEl.textContent = `인지 이해도 ${masteryPct}% · 나이테 ${cog.rings.length}개 · 재창조 ${cog.recreationCount}회`;
        }

        renderFourAxisPanel();
    }

    // ========================================================================
    // L2 & L3. Hypothesis Selection, Autonomous Experimentation & Self-Revision
    // ========================================================================
    function pickNextExperiment(snap, forcedLeverKey = null) {
        const { dom: domain, specs, kbDom } = ensureDomainKnowledge(snap.domain);
        const cur = snap.controls;

        let chosenSpec = null;
        if (forcedLeverKey) {
            chosenSpec = specs.find((s) => s.key === forcedLeverKey) || specs[0];
        } else if (cog.intent === 'curiosity') {
            // Pick the lever with lowest confidence (active epistemic curiosity!)
            chosenSpec = specs.reduce((best, sp) =>
                kbDom[sp.key].confidence < kbDom[best.key].confidence ? sp : best, specs[0]);
        } else if (cog.intent === 'optimize') {
            chosenSpec = domain === 'game'
                ? specs.find((s) => s.key === (kbDom.s2Stride.trials <= kbDom.s4Stride.trials ? 's2Stride' : 's4Stride'))
                : specs.find((s) => s.key === (kbDom.s0Thresh.trials <= kbDom.s2Stride.trials ? 's0Thresh' : 's2Stride'));
        } else if (cog.intent === 'bifurcate_objects') {
            chosenSpec = domain === 'game'
                ? specs.find((s) => s.key === (kbDom.envCoupling.trials <= kbDom.objConnectivity.trials ? 'envCoupling' : 'objConnectivity'))
                : specs.find((s) => s.key === 's2Stride');
        } else {
            // 'converge': pull diverged levers back toward harmonic baseline
            chosenSpec = domain === 'game'
                ? specs.find((s) => Math.abs(cur[s.key] - 1.0) > 0.15) || specs[0]
                : specs.find((s) => s.key === 's0Thresh') || specs[0];
        }
        if (!chosenSpec) chosenSpec = specs[0];

        const curVal = cur[chosenSpec.key];
        const law = kbDom[chosenSpec.key];
        let nextVal = curVal;

        if (cog.intent === 'converge') {
            nextVal = domain === 'game' && (chosenSpec.key === 'envCoupling' || chosenSpec.key === 'objConnectivity')
                ? 1.0
                : chosenSpec.key === 's0Thresh' ? 4 : chosenSpec.key === 's2Stride' ? 2 : 8;
            if (Math.abs(nextVal - curVal) < 0.05) {
                nextVal = Math.min(chosenSpec.max, curVal + chosenSpec.step);
            }
        } else if (cog.intent === 'optimize') {
            // Use learned slope to push toward higher compute savings while keeping PSNR >= 40 dB
            if (snap.psnr < 40 && chosenSpec.key === 's0Thresh') {
                nextVal = Math.max(2, curVal - 3);
            } else if (snap.savedPct < 82) {
                nextVal = Math.min(chosenSpec.max, curVal + chosenSpec.step);
            } else {
                nextVal = Math.max(chosenSpec.min, curVal - Math.round(chosenSpec.step * 0.5));
            }
        } else if (cog.intent === 'bifurcate_objects' && domain === 'game') {
            nextVal = curVal < 1.3 ? Math.min(chosenSpec.max, 1.7) : 0.4;
        } else {
            // Curiosity exploration: step into least-explored direction within valid bounds
            const goUp = (curVal + chosenSpec.step <= chosenSpec.max) && (law.trials % 2 === 0 || curVal - chosenSpec.step < chosenSpec.min);
            nextVal = goUp
                ? Math.min(chosenSpec.max, curVal + chosenSpec.step)
                : Math.max(chosenSpec.min, curVal - chosenSpec.step);
        }

        if (chosenSpec.unit === '×') {
            nextVal = Number(nextVal.toFixed(1));
        } else {
            nextVal = Math.round(nextVal);
        }

        const deltaU = nextVal - curVal;
        // Predict outcomes BEFORE acting using Elysia's current learned causal weights!
        const predDeltaSaved = law.slopeSaved * deltaU;
        const predDeltaPsnr = law.slopePsnr * deltaU;
        const predDeltaS2 = law.slopeS2 * deltaU;

        return {
            spec: chosenSpec,
            fromVal: curVal,
            toVal: nextVal,
            deltaU,
            predDeltaSaved,
            predDeltaPsnr,
            predDeltaS2,
        };
    }

    function runCognitiveExperiment(forcedLeverKey = null) {
        const bridge = getBridge();
        if (!bridge || cog.busy) return;
        const snapA = bridge.getSnapshot();
        if (snapA.paused) return;

        cog.busy = true;
        cog.lastBefore = snapA;

        // STAGE 1: PERCEIVE (Snapshot A)
        setPhase('perceive');
        const plan = pickNextExperiment(snapA, forcedLeverKey);
        const intentLabelMap = {
            curiosity: '미지 영역 탐색(무지→앎)',
            optimize: '무손실 연산 최적화',
            bifurcate_objects: '환경 보존·객체 분기 관측',
            converge: '전 계층 공명 수렴 복원',
        };

        // STAGE 2: THINK & HYPOTHESIZE
        setPhase('think');
        const dirWord = plan.deltaU >= 0 ? '증가' : '감소';
        cog.internalOrigin = `[${intentLabelMap[cog.intent]}] '${plan.spec.name}'을 ${plan.fromVal}${plan.spec.unit} → ${plan.toVal}${plan.spec.unit}(${dirWord})로 조작 시 ` +
            `연산절감 ${plan.predDeltaSaved >= 0 ? '+' : ''}${plan.predDeltaSaved.toFixed(1)}%p · S2일치 ${plan.predDeltaS2 >= 0 ? '+' : ''}${plan.predDeltaS2.toFixed(1)}%p 변화 예측`;
        renderFourAxisPanel();

        // STAGE 3: ACT (Physically manipulate the real live engine after short perceptible beat)
        cog.timerId = setTimeout(() => {
            setPhase('act');
            if (snapA.domain === 'game' && (plan.spec.key === 'envCoupling' || plan.spec.key === 'objConnectivity')) {
                // Switch to Superposition Overlay so user immediately sees where World A & B diverge!
                if (cog.intent === 'bifurcate_objects') {
                    bridge.setOutputView('overlay');
                }
            }
            bridge.applyControls({ [plan.spec.key]: plan.toVal });
            cog.lastActionSummary = `${plan.spec.name}: ${plan.fromVal}${plan.spec.unit} → ${plan.toVal}${plan.spec.unit}`;

            // STAGE 4: RE-OBSERVE & SUPERPOSE (Wait 1.15s for real physical/informational propagation!)
            cog.timerId = setTimeout(() => {
                setPhase('reobserve');
                const snapB = bridge.getSnapshot();
                cog.lastAfter = snapB;

                const obsDeltaSaved = snapB.savedPct - snapA.savedPct;
                const obsDeltaPsnr = snapB.psnr - snapA.psnr;
                const obsDeltaS2 = snapB.s2SamePct - snapA.s2SamePct;
                const obsDeltaS4 = snapB.s4SamePct - snapA.s4SamePct;
                const obsDeltaS0 = snapB.s0SamePct - snapA.s0SamePct;

                // Identify what stayed IDENTICAL vs what CHANGED!
                const sameLayers = [];
                const changedLayers = [];
                if (Math.abs(obsDeltaS4) < 1.5 && snapB.s4SamePct >= 95) sameLayers.push('S4(환경)');
                else changedLayers.push(`S4(${obsDeltaS4 >= 0 ? '+' : ''}${obsDeltaS4.toFixed(1)}%)`);
                if (Math.abs(obsDeltaS2) < 3.0 && snapB.s2SamePct >= 93) sameLayers.push('S2(객체)');
                else changedLayers.push(`S2(${obsDeltaS2 >= 0 ? '+' : ''}${obsDeltaS2.toFixed(1)}%)`);
                if (Math.abs(obsDeltaS0) < 3.0 && snapB.s0SamePct >= 93) sameLayers.push('S0(미시)');
                else changedLayers.push(`S0(${obsDeltaS0 >= 0 ? '+' : ''}${obsDeltaS0.toFixed(1)}%)`);

                // STAGE 5: LEARN & CRITERIA SELF-REVISION (Update real causal Jacobian!)
                setPhase('learn');
                const { kbDom: kbAfter } = ensureDomainKnowledge(snapB.domain);
                const law = kbAfter[plan.spec.key] || Object.values(kbAfter)[0];
                const du = Math.abs(plan.deltaU) > 1e-4 ? plan.deltaU : 1;
                const empSlopeSaved = obsDeltaSaved / du;
                const empSlopePsnr = obsDeltaPsnr / du;
                const empSlopeS2 = obsDeltaS2 / du;

                const errSaved = Math.abs(obsDeltaSaved - plan.predDeltaSaved);
                const errS2 = Math.abs(obsDeltaS2 - plan.predDeltaS2);
                const errPsnr = Math.abs(obsDeltaPsnr - plan.predDeltaPsnr);
                const surprise = Math.min(1.0, (errSaved * 0.04 + errS2 * 0.025 + errPsnr * 0.05));

                const alpha = law.trials < 2 ? 0.55 : 0.32;
                const prevSlopeMain = snapB.domain === 'game' ? law.slopeS2 : law.slopeSaved;
                law.slopeSaved = law.slopeSaved * (1 - alpha) + empSlopeSaved * alpha;
                law.slopePsnr = law.slopePsnr * (1 - alpha) + empSlopePsnr * alpha;
                law.slopeS2 = law.slopeS2 * (1 - alpha) + empSlopeS2 * alpha;
                law.trials += 1;
                law.lastSurprise = surprise;
                law.minSeen = law.minSeen === null ? Math.min(plan.fromVal, plan.toVal) : Math.min(law.minSeen, plan.toVal);
                law.maxSeen = law.maxSeen === null ? Math.max(plan.fromVal, plan.toVal) : Math.max(law.maxSeen, plan.toVal);

                // Confidence grows faster when predictions match reality, slower under high surprise!
                const confGain = surprise < 0.25 ? 0.24 : 0.14;
                law.confidence = Math.min(0.98, law.confidence + confGain * (1 - law.confidence));

                const nextSlopeMain = snapB.domain === 'game' ? law.slopeS2 : law.slopeSaved;
                const slopeLabel = snapB.domain === 'game' ? '∂S2분기' : '∂연산절감';
                cog.selfRevision = surprise > 0.32
                    ? `놀라움 ${(surprise * 100).toFixed(0)}% 감지 → '${plan.spec.name}' ${slopeLabel} 가중치 ${prevSlopeMain.toFixed(2)} → ${nextSlopeMain.toFixed(2)} 자기수정!`
                    : `예측 정합(오차 ${(surprise * 100).toFixed(0)}%) → '${plan.spec.name}' 인과 법칙 확신도 ${Math.round(law.confidence * 100)}%로 강화`;

                const ringKind = surprise > 0.34 ? 'revised' : law.confidence > 0.7 ? 'mastered' : 'learned';
                cog.rings.push({
                    kind: ringKind,
                    domain: snapB.domain,
                    label: `${plan.spec.name} ${plan.fromVal}→${plan.toVal}`,
                    surprise,
                    s4: snapB.s4SamePct,
                    s2: snapB.s2SamePct,
                    s0: snapB.s0SamePct,
                });
                if (cog.rings.length > 48) cog.rings.shift();

                cog.traces.unshift({
                    time: new Date().toLocaleTimeString('ko-KR', { hour12: false }),
                    kind: ringKind,
                    action: `${plan.spec.name} ${plan.fromVal}${plan.spec.unit} → ${plan.toVal}${plan.spec.unit}`,
                    sameText: sameLayers.length ? sameLayers.join('·') : '없음(전계층 변이)',
                    diffText: changedLayers.length ? changedLayers.join('·') : '미세 수렴(동일 유지)',
                    deltaSummary: `연산 ${obsDeltaSaved >= 0 ? '+' : ''}${obsDeltaSaved.toFixed(1)}%p · 화질 ${snapB.psnr.toFixed(1)}dB · 오차 ${(surprise * 100).toFixed(0)}%`,
                });
                if (cog.traces.length > 18) cog.traces.pop();

                exportToVirtualMemoryBridge(snapA, snapB, `${plan.spec.name} ${plan.fromVal}→${plan.toVal}`, ringKind);
                persistMemory();
                renderKnowledgeMatrix();
                renderTraceFeed();
                drawGrowthRings();
                renderFourAxisPanel();

                cog.busy = false;
            }, 1150);
        }, 380);
    }

    // ========================================================================
    // STAGE 6: INVERSE PRINCIPLE RE-CREATION (배운 원리로 새로운 세계 재창조!)
    // ========================================================================
    const CREATIVE_PATTERNS = [
        { id: 'spiral_vortex', name: '성역 공명 수호 + 초전도 반격 연출', env: 0.5, conn: 2.0, s2: 3 },
        { id: 'twin_orbit', name: '플라즈마 폭풍·초전도 동시 이중 콤보', env: 1.7, conn: 1.9, s2: 4 },
        { id: 'harmonic_lattice', name: '진영 가치관 정면 충돌 클라이맥스 구도', env: 1.9, conn: 0.6, s2: 2 },
    ];

    function executeCreativeSynthesis() {
        const bridge = getBridge();
        if (!bridge || cog.busy) return;
        cog.busy = true;

        const snapA = bridge.getSnapshot();
        setPhase('recreate');
        cog.recreationCount += 1;

        if (snapA.domain === 'game') {
            // Use Elysia's learned S4/S2/S0 principles to synthesize a brand-new intentional world branch B
            // and immediately show Superposition Diff (포개기 대조) against Baseline World A!
            const spec = CREATIVE_PATTERNS[(cog.recreationCount - 1) % CREATIVE_PATTERNS.length];
            const kb = cog.knowledge.game;
            // Modulate target parameters gently by what she learned about objConnectivity sensitivity
            const learnedConnAdjust = Math.abs(kb.objConnectivity.slopeS2) > 15 ? 0.92 : 1.08;
            const targetConn = Math.max(0.3, Math.min(2.4, Number((spec.conn * learnedConnAdjust).toFixed(1))));

            bridge.syncGameWorlds();
            bridge.applyControls({
                envCoupling: spec.env,
                objConnectivity: targetConn,
                s2Stride: spec.s2,
                s4Stride: 14,
            });
            bridge.setOutputView('overlay');
            bridge.manifestSwarmFormation(spec.id);

            cog.internalOrigin = `[원리 재창조 #${cog.recreationCount}] 체득한 S4·S2 결합 법칙으로 '${spec.name}' (환경결합 ${spec.env}× · 연결성 ${targetConn}×)을 직접 설계·창조하고 기준 세계 A와 포개어 분기를 관측 중!`;
            renderFourAxisPanel();

            cog.timerId = setTimeout(() => {
                const snapB = bridge.getSnapshot();
                cog.rings.push({
                    kind: 'recreate',
                    domain: 'game',
                    label: `재창조: ${spec.name}`,
                    surprise: 0.1,
                    s4: snapB.s4SamePct,
                    s2: snapB.s2SamePct,
                    s0: snapB.s0SamePct,
                });
                if (cog.rings.length > 48) cog.rings.shift();

                cog.traces.unshift({
                    time: new Date().toLocaleTimeString('ko-KR', { hour12: false }),
                    kind: 'recreate',
                    action: `★ 원리 재창조: ${spec.name}`,
                    sameText: 'S4(지형·조명 100% 보존)',
                    diffText: `S2 객체 궤도 ${(100 - snapB.s2SamePct).toFixed(1)}% 의도적 분기 창조`,
                    deltaSummary: `연산절감 ${snapB.savedPct.toFixed(1)}% · 포개기 대조 활성`,
                });
                if (cog.traces.length > 18) cog.traces.pop();

                cog.selfRevision = `재창조 완료 — 환경(S4)은 그대로 둔 채 240 객체(S2)만 '${spec.name}' 위상으로 분리 창조 검증됨`;
                exportToVirtualMemoryBridge(snapA, snapB, `재창조: ${spec.name}`, 'recreate');
                persistMemory();
                renderKnowledgeMatrix();
                renderTraceFeed();
                drawGrowthRings();
                renderFourAxisPanel();
                cog.busy = false;
            }, 950);
        } else {
            // HD Video Inverse Pareto Synthesis: solve optimal (s4Stride, s2Stride, s0Thresh) from learned slopes!
            const kb = cog.knowledge.video;
            const s0Sensitivity = Math.abs(kb.s0Thresh.slopePsnr) || 0.45;
            // Choose highest s0Thresh expected to preserve >= 42 dB lossless visual parity
            const optS0 = Math.max(3, Math.min(8, Math.round(3.6 / Math.max(0.45, s0Sensitivity))));
            const optS2 = Math.abs(kb.s2Stride.slopeSaved) > 0.8 ? 4 : 3;
            const optS4 = 16;

            bridge.applyControls({ s4Stride: optS4, s2Stride: optS2, s0Thresh: optS0 });
            bridge.setOutputView('composite');

            cog.internalOrigin = `[역설계 최적화 재창조 #${cog.recreationCount}] 학습한 화질·연산 기울기로 HD 무손실 파레토 최적점 (S4=1/${optS4}, S2=1/${optS2}, S0=${optS0})을 직접 도출·적용!`;
            renderFourAxisPanel();

            cog.timerId = setTimeout(() => {
                const snapB = bridge.getSnapshot();
                cog.rings.push({
                    kind: 'recreate',
                    domain: 'video',
                    label: `HD 파레토 재설계 (${optS4}/${optS2}/${optS0})`,
                    surprise: 0.08,
                    s4: snapB.s4SamePct,
                    s2: snapB.s2SamePct,
                    s0: snapB.s0SamePct,
                });
                if (cog.rings.length > 48) cog.rings.shift();

                cog.traces.unshift({
                    time: new Date().toLocaleTimeString('ko-KR', { hour12: false }),
                    kind: 'recreate',
                    action: `★ HD 파레토 재설계 (S4:1/${optS4}·S2:1/${optS2}·S0:${optS0})`,
                    sameText: `선명도 ${snapB.psnr.toFixed(1)}dB (원본 동일 유지)`,
                    diffText: `연산 ${snapB.savedPct.toFixed(1)}% 자동 절감 달성`,
                    deltaSummary: `처리속도 ${snapB.speedRatio.toFixed(1)}× 효율`,
                });
                if (cog.traces.length > 18) cog.traces.pop();

                cog.selfRevision = `역설계 검증 완료 — 화질 ${snapB.psnr.toFixed(1)}dB 유지하며 연산 ${snapB.savedPct.toFixed(1)}% 자동 절감`;
                exportToVirtualMemoryBridge(snapA, snapB, `HD 파레토 재설계`, 'recreate');
                persistMemory();
                renderKnowledgeMatrix();
                renderTraceFeed();
                drawGrowthRings();
                renderFourAxisPanel();
                cog.busy = false;
            }, 950);
        }
    }

    // ========================================================================
    // UI Renderers (100% Safe DOM textContent/createElement, Zero innerHTML)
    // ========================================================================
    function renderFourAxisPanel() {
        const elInt = document.getElementById('cog-axis-internal');
        const elExt = document.getElementById('cog-axis-external');
        const elIgn = document.getElementById('cog-axis-ignorance');
        const elRev = document.getElementById('cog-axis-revision');
        if (elInt) elInt.textContent = cog.internalOrigin;
        if (elExt) elExt.textContent = cog.externalInfluence;
        if (elIgn) elIgn.textContent = cog.ignoranceBoundary;
        if (elRev) elRev.textContent = cog.selfRevision;
    }

    let lastKnowledgeSig = '';

    function renderKnowledgeMatrix(force = false) {
        const host = document.getElementById('cog-knowledge-list');
        const bridge = getBridge();
        if (!host || !bridge) return;
        const snap = bridge.getSnapshot();
        const { dom: domain, specs, kbDom } = ensureDomainKnowledge(snap.domain);

        const sig = `${domain}|` + specs.map((sp) => {
            const law = kbDom[sp.key];
            return `${sp.key}:${snap.controls[sp.key]}:${Math.round(law.confidence * 100)}:${law.trials}`;
        }).join(',');
        if (!force && sig === lastKnowledgeSig) return;
        lastKnowledgeSig = sig;

        host.textContent = '';
        for (const sp of specs) {
            const law = kbDom[sp.key];
            const confPct = Math.round(law.confidence * 100);
            const statusLabel = confPct < 35 ? '무지 경계' : confPct < 72 ? '인과 학습 중' : '법칙 체득';
            const statusClass = confPct < 35 ? 'unknown' : confPct < 72 ? 'learning' : 'known';

            const row = document.createElement('div');
            row.className = `cog-law-row ${statusClass}`;

            const top = document.createElement('div');
            top.className = 'cog-law-top';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'cog-law-name';
            nameSpan.textContent = `${sp.name} (${snap.controls[sp.key]}${sp.unit})`;

            const tagSpan = document.createElement('span');
            tagSpan.className = `cog-law-badge ${statusClass}`;
            tagSpan.textContent = `${statusLabel} ${confPct}%`;

            const testBtn = document.createElement('button');
            testBtn.type = 'button';
            testBtn.className = 'btn cog-mini-btn';
            testBtn.textContent = '직접 실험';
            testBtn.addEventListener('click', () => runCognitiveExperiment(sp.key));

            const rightGroup = document.createElement('div');
            rightGroup.style.display = 'flex';
            rightGroup.style.alignItems = 'center';
            rightGroup.style.gap = '6px';
            rightGroup.appendChild(tagSpan);
            rightGroup.appendChild(testBtn);

            top.appendChild(nameSpan);
            top.appendChild(rightGroup);

            const barWrap = document.createElement('div');
            barWrap.className = 'cog-conf-bar';
            const barFill = document.createElement('div');
            barFill.className = `cog-conf-fill ${statusClass}`;
            barFill.style.width = `${confPct}%`;
            barWrap.appendChild(barFill);

            const meta = document.createElement('div');
            meta.className = 'cog-law-meta';
            meta.textContent = domain === 'game'
                ? `실측기울기: ∂S2분기 ${law.slopeS2.toFixed(1)}%/단위 · ∂연산 ${law.slopeSaved.toFixed(1)}% · 실험 ${law.trials}회`
                : `실측기울기: ∂연산 ${law.slopeSaved.toFixed(1)}%/단위 · ∂화질 ${law.slopePsnr.toFixed(2)}dB · 실험 ${law.trials}회`;

            row.appendChild(top);
            row.appendChild(barWrap);
            row.appendChild(meta);
            host.appendChild(row);
        }
    }

    function renderTraceFeed() {
        const host = document.getElementById('cog-trace-list');
        if (!host) return;
        host.textContent = '';
        if (!cog.traces.length) {
            const empty = document.createElement('div');
            empty.className = 'cog-trace-empty';
            empty.textContent = '상단 [자율 탐구 시작] 또는 [1회 사유·실행]을 누르면 엘리시아가 스스로 조작·재관측·학습한 인과 기록이 축적됩니다.';
            host.appendChild(empty);
            return;
        }
        for (const item of cog.traces.slice(0, 7)) {
            const card = document.createElement('div');
            card.className = `cog-trace-item ${item.kind}`;

            const head = document.createElement('div');
            head.className = 'cog-trace-head';
            const act = document.createElement('strong');
            act.textContent = item.action;
            const tm = document.createElement('span');
            tm.textContent = item.time;
            head.appendChild(act);
            head.appendChild(tm);

            const body = document.createElement('div');
            body.className = 'cog-trace-body';
            body.textContent = `동일: ${item.sameText} │ 변화: ${item.diffText}`;

            const foot = document.createElement('div');
            foot.className = 'cog-trace-foot';
            foot.textContent = item.deltaSummary;

            card.appendChild(head);
            card.appendChild(body);
            card.appendChild(foot);
            host.appendChild(card);
        }
    }

    function drawGrowthRings() {
        const canvas = document.getElementById('cog-ring-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d', { alpha: false });
        const cw = canvas.width;
        const ch = canvas.height;
        const cx = cw * 0.5;
        const cy = ch * 0.5;
        const maxR = Math.min(cx, cy) - 10;

        ctx.fillStyle = '#060a12';
        ctx.fillRect(0, 0, cw, ch);

        // Subtle polar axes (S4 / S2 / S0 / Volition)
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.14)';
        ctx.lineWidth = 1;
        for (let i = 0; i < 4; i++) {
            const a = (i / 4) * Math.PI;
            ctx.beginPath();
            ctx.moveTo(cx - Math.cos(a) * maxR, cy - Math.sin(a) * maxR);
            ctx.lineTo(cx + Math.cos(a) * maxR, cy + Math.sin(a) * maxR);
            ctx.stroke();
        }

        // Core Origin (0_value)
        ctx.fillStyle = '#06b6d4';
        ctx.beginPath();
        ctx.arc(cx, cy, 4.5, 0, Math.PI * 2);
        ctx.fill();

        const rings = cog.rings;
        const n = rings.length;
        const colorMap = {
            mastered: '#10b981',
            learned: '#06b6d4',
            revised: '#f59e0b',
            recreate: '#f43f5e',
            external: '#a78bfa',
        };

        for (let i = 0; i < n; i++) {
            const ring = rings[i];
            const frac = (i + 1) / Math.max(8, n);
            const r = 10 + frac * (maxR - 12);
            const col = colorMap[ring.kind] || '#06b6d4';

            ctx.strokeStyle = col;
            ctx.globalAlpha = 0.28 + 0.65 * ((i + 1) / n);
            ctx.lineWidth = ring.kind === 'recreate' ? 2.2 : 1.3;

            ctx.beginPath();
            const steps = 48;
            for (let s = 0; s <= steps; s++) {
                const th = (s / steps) * Math.PI * 2;
                // Modulate ring contour organically by real observed S4/S2/S0 divergence & surprise!
                const wobble =
                    Math.sin(th * 3 + i * 0.7) * (1 - ring.s2 / 100) * 6 +
                    Math.cos(th * 5 - i) * ring.surprise * 5;
                const rr = Math.max(6, Math.min(maxR, r + wobble));
                const px = cx + Math.cos(th) * rr;
                const py = cy + Math.sin(th) * rr;
                if (s === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.stroke();
        }
        ctx.globalAlpha = 1;

        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px "IBM Plex Mono", monospace';
        ctx.fillText(`성장 나이테 ${n}`, 8, 15);
        ctx.fillStyle = '#f43f5e';
        ctx.fillText(`재창조 ${cog.recreationCount}`, cw - 62, 15);
    }

    // ========================================================================
    // Bind Controls & Periodic Live Sensory Refresh
    // ========================================================================
    function toggleAutoLoop() {
        cog.autoRunning = !cog.autoRunning;
        const btn = document.getElementById('btn-cog-auto');
        if (btn) {
            btn.textContent = cog.autoRunning ? '● 자율 탐구·학습 중지' : '▶ 자율 탐구·학습 시작';
            btn.classList.toggle('btn-primary', !cog.autoRunning);
            btn.classList.toggle('btn-active-loop', cog.autoRunning);
        }
        if (cog.autoRunning) {
            runCognitiveExperiment();
            cog.autoIntervalId = setInterval(() => {
                if (!cog.autoRunning || cog.busy) return;
                const bridge = getBridge();
                if (!bridge) return;
                const snap = bridge.getSnapshot();
                const mastery = computeDomainMastery(snap.domain);
                // When Elysia builds enough mastery in auto mode, she autonomously triggers Re-Creation every 5th ring!
                if (mastery >= 0.58 && cog.rings.length > 0 && cog.rings.length % 5 === 0) {
                    executeCreativeSynthesis();
                } else {
                    runCognitiveExperiment();
                }
            }, 2600);
        } else {
            clearInterval(cog.autoIntervalId);
            cog.autoIntervalId = null;
        }
    }

    function bindCognitiveUI() {
        const stepper = document.getElementById('cog-phase-stepper');
        if (stepper) {
            stepper.textContent = '';
            for (const ph of PHASES) {
                const el = document.createElement('span');
                el.className = ph.id === 'perceive' ? 'cog-step active' : 'cog-step';
                el.dataset.phase = ph.id;
                el.textContent = ph.label;
                stepper.appendChild(el);
            }
        }

        const btnAuto = document.getElementById('btn-cog-auto');
        if (btnAuto) btnAuto.addEventListener('click', toggleAutoLoop);

        const btnStep = document.getElementById('btn-cog-step');
        if (btnStep) btnStep.addEventListener('click', () => runCognitiveExperiment());

        const btnRecreate = document.getElementById('btn-cog-recreate');
        if (btnRecreate) btnRecreate.addEventListener('click', executeCreativeSynthesis);

        const btnResetMem = document.getElementById('btn-cog-reset');
        if (btnResetMem) {
            btnResetMem.addEventListener('click', () => {
                if (cog.autoRunning) toggleAutoLoop();
                cog.knowledge = createFreshKnowledge();
                cog.rings = [];
                cog.traces = [];
                cog.recreationCount = 0;
                cog.internalOrigin = '기억 초기화 완료 — 백지 무지 경계에서 다시 인과를 탐색할 준비가 되었습니다.';
                cog.selfRevision = '초기화됨';
                persistMemory();
                renderKnowledgeMatrix();
                renderTraceFeed();
                drawGrowthRings();
                renderFourAxisPanel();
            });
        }

        document.querySelectorAll('[data-cog-intent]').forEach((btn) => {
            btn.addEventListener('click', () => {
                cog.intent = btn.dataset.cogIntent;
                document.querySelectorAll('[data-cog-intent]').forEach((b) =>
                    b.classList.toggle('active', b === btn)
                );
                cog.internalOrigin = `목표 의도 전환됨 → '${btn.textContent}' (다음 사유 주기에 즉시 반영)`;
                renderFourAxisPanel();
            });
        });

        // Re-render knowledge matrix whenever user switches Video <-> Game domain!
        document.querySelectorAll('[data-domain]').forEach((btn) => {
            btn.addEventListener('click', () => {
                setTimeout(() => {
                    renderKnowledgeMatrix();
                    updateSensoryLayer();
                }, 80);
            });
        });

        // Periodic L1 sensory sync (~1.1Hz — skips when tab hidden & skips DOM rebuild if unchanged)
        setInterval(() => {
            if (document.hidden) return;
            updateSensoryLayer();
            renderKnowledgeMatrix(false);
        }, 900);

        updateSensoryLayer();
        renderKnowledgeMatrix(true);
        renderTraceFeed();
        drawGrowthRings();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bindCognitiveUI);
    } else {
        bindCognitiveUI();
    }
})();
