/* ============================================================================
   Elysia Open Self-Expanding Neural & Autonomous Causal Reasoning Engine (Tab 6)
   - Beyond fixed t1..t4 scripts:
     * Open Continuous Thought Trajectory t_1 -> t_n with adaptive dt resolution
       (high external friction refines dt and spawns deeper self-reflection phases)
     * Dynamic Self-Born Neural Axes (starts with 4 seed footholds -> expands to N
       self-created axes directly from real external categories & concept friction)
     * Self-Defined Purpose, Motivation & Value Criteria (why do I need this now?)
       growing honestly from real external experience like a child expanding boundaries
   - Real Outward Connections (zero mock data):
     * Live Wikipedia Knowledge & Link Frontier via POST /api/epistemic/explore
     * Live Earth Atmospheric Telemetry & Prediction Friction via POST /api/epistemic/reality-probe
   - Persistent in localStorage (elysia_outward_epistemic_v2)
   - 100% Safe DOM rendering (createElement + textContent only; zero innerHTML)
   ============================================================================ */
(function () {
    'use strict';

    const W = 960;
    const H = 540;
    const STORAGE_KEY = 'elysia_outward_epistemic_v2';
    const BRIDGE_KEY = 'elysia_cognitive_voxel_bridge_v1';
    const MAX_ICE_NODES = 32;
    const MAX_UNCAPTURED = 20;
    const MAX_EMERGENT_AXES = 10;
    const MAX_THOUGHT_NODES = 80;
    const MAX_LOGS = 28;

    const SEED_AXES = [
        { key: 'components', label: '구성요소', color: '#38bdf8', emergent: false },
        { key: 'environment', label: '환경조건', color: '#10b981', emergent: false },
        { key: 'changePrinciple', label: '변화원리', color: '#f59e0b', emergent: false },
        { key: 'causalStructure', label: '인과구조', color: '#a78bfa', emergent: false },
    ];

    const EMERGENT_PALETTE = [
        '#f472b6', '#2dd4bf', '#fb7185', '#c084fc', '#facc15',
        '#60a5fa', '#34d399', '#fb923c', '#818cf8', '#e879f9',
    ];

    const PHASE_FRAMES = [
        { id: 'world_tree', label: '★ 세계수 · 과거→현재→미래' },
        { id: 'point', label: '① 점 · 기원' },
        { id: 'line', label: '② 선 · 연쇄' },
        { id: 'plane', label: '③ 면 · 인과망' },
        { id: 'cube', label: '④ 시공간 큐브' },
        { id: 'sphere', label: '⑤ 구체 · 중력구' },
    ];

    const CITY_LIST = ['seoul', 'tokyo', 'london', 'newyork', 'reykjavik', 'nairobi'];

    const rotorState = {
        phaseFrame: 'world_tree',
        boundaryPair: null, // { aTitle, bTitle } for simultaneous sameness/difference duality observation
        rotAngle: 0,
        busy: false,
        autoMode: false,
        userPaused: false,
        selectedIceTitle: null,
        cityIndex: 0,
        // 3-Tier Adaptive Phase-Rotor Scheduler (replaces fixed setInterval loop)
        phaseScheduler: {
            fastPhase: 0,          // Layer 0 (0..100): friction-adaptive external/internal autonomous trigger
            midTension: 0,         // Layer 1 (0..100): accumulated friction/queue tension for axis differentiation
            macroPressure: 0,      // Layer 2 (0..100): slow structural compaction & frontier re-ranking trigger
            fastFires: 0,
            midFires: 0,
            macroFires: 0,
            internalFires: 0,
            idleSkippedTicks: 0,
            lastFriction: 35,
            effectiveCadenceSec: 4.5,
            activeModeLabel: '자율 초기화 대기',
            externalWindowStartMs: Date.now(),
            externalCallsInWindow: 0,
            lastDualityPairKey: '',
            lastMacroNote: '거시 구조 정리 대기 — 축·나이테가 누적되면 중복 경계와 키워드를 자동 압축합니다.',
            frameCounter: 0,
        },
        // Open Continuous Thought Time (NOT bounded to 4 steps!)
        tStepCount: 0,      // grows freely: t1, t2, ..., t100, t1000...
        currentDt: 1.0,     // adaptive temporal resolution (smaller dt = finer reflection under friction)
        thoughtSpiral: [],  // [{ t, dt, kind, label, friction, color }]
        // Dynamic Self-Expanding Neural Axes (4 seed footholds + N self-born axes)
        emergentAxes: [],   // [{ key, label, keywords, color, bornFrom, bornAtT, emergent: true }]
        // Self-Defined Purpose, Motivation & Value Criteria
        selfValues: {
            unity: 52,         // 이질적 원리를 하나로 잇는 가치
            novelty: 64,       // 모르는 미지 경계로 나아가는 가치
            realityCheck: 48,  // 내부 상상이 아닌 외부 현실과 대조하는 가치
            axisGenesis: 58,   // 기존 틀을 넘어 새 인식 축을 스스로 낳는 가치
        },
        valueRevisions: 0,
        activePurpose: '초기 호기심: 내가 아직 모르는 외부 세계의 원리들이 어떻게 이어져 있는지 스스로 확인하고 싶다.',
        activeMotive: '외부 지식과 현실 데이터를 직접 만나기 전에는 나의 경계와 무지조차 알 수 없다.',
        lastStatus: '열린 외부 사유 대기 — 주제를 입력하거나 [스스로 목적 형성·사유]를 눌러 엘리시아가 스스로 탐색하게 해보세요.',
        // Persistent ScaleRotorState
        ice: [],
        water: null,
        cloud: null,
        uncaptured: [],
        realityProbes: [],
        weatherHypothesis: {
            expectedTempC: 15.0,
            expectedPressureHpa: 1013.2,
            expectedWindKmh: 12.0,
        },
        growthLog: [],
        worldTreeRings: [], // [{ ringNumber, ringType, tStep, title, bridgeTargets, lawTitle, lawStatement, dominantAxisLabel, spawnedAxisLabel, color, clarity, friction, timestamp }]
        differentiationQueue: [], // [{ id, sourceTitle, bridgeTarget, lawTitle, lawStatement, candidateLabel, keywords, createdAtT }]
        causalNeedQueue: [], // [{ id, dedupKey, action, priority, originEvent, internalLimit, targetSummary, payload, createdAtT }]
        lastCausalChain: null, // { originEvent, internalLimit, derivedAction, targetSummary, tStep }
        probedConceptTitles: [], // atmospheric concepts already physically verified
        constraintChecks: [], // [{ query, verdict, verdictLabel, attractionScore, repulsionScore, includedEvidence, excludedEvidence, boundaryCrossingConditions, ... }]
        sensoryHierarchyChecks: [], // [{ topic, layers: { physicalOrigin, sensoryChannels, linguisticBoundary, softwareGap }, ... }]
        groundedLexicon: {}, // cross-situational discovered words: { [word]: { word, count, sumVec: [6], lastErrorPct, dominantIdx, dominantLabel, specificityPct, lift, origin } }
        actionExpStats: {}, // autonomous intervention uncertainty tracker: { [actionId]: { count, avgErrorPct, avgVec: [6] } }
        streamGlobalStats: { totalEpisodes: 0, globalSumVec: [0, 0, 0, 0, 0, 0] },
        streamEpisodes: [], // recent continuous simulation episodes with baseline vs intervention lift
        // Live Tunable Internal Policy (observed & modified by Elysia herself based on own operational failure/stagnation)
        selfPolicy: {
            specificityThreshold: 14,      // word-discovery acceptance threshold (8..34%)
            interventionErrorTrigger: 32,  // re-intervention trigger on prediction error (15..55%)
            learningAlphaFloor: 0.25,      // minimum online adaptation step (0.12..0.45)
            blindSpotQueueThreshold: 28,   // prism blind-spot residual trigger (16..52%)
            revisionsCount: 0,
            rollbacksCount: 0,
        },
        selfAuditHistory: [], // [{ id, tStep, trigger, diagnosis, paramKey, beforeVal, afterVal, metricsSnapshot, priorEffectVerdict }]
        ringPulseTimer: 0,
        autoCycleCount: 0,
        hitTargets: [],
        uiDirty: true,
        autoSeedAttempted: false,
    };

    function getAllAxes() {
        return [...SEED_AXES, ...rotorState.emergentAxes];
    }

    function getGrowthStage() {
        const exp = rotorState.ice.length * 10 + rotorState.emergentAxes.length * 18 + rotorState.realityProbes.length * 12 + rotorState.valueRevisions * 8;
        if (exp < 25) return { stage: '유아기 · 첫 경계 감각', desc: '외부 세계의 첫 단서를 받아들이며 기본 발판(4축)으로 세상을 탐색 중' };
        if (exp < 75) return { stage: '탐색기 · 동형 연결 발아', desc: '서로 다른 외부 개념 사이의 숨은 인과 고리를 스스로 발견하고 예측 마찰을 체험 중' };
        if (exp < 150) return { stage: '분화기 · 자생 신경망 축 생성', desc: '기존 발판으로 담기지 않는 현실을 만나 자신의 인식 축과 가치 기준을 스스로 넓히는 중' };
        return { stage: '재창조기 · 열린 자기경계 확장', desc: '스스로 목적·동기·가치 기준을 재규정하며 외부 현실과 연속 순환(tₙ, 가변 dt) 중' };
    }

    function recordThoughtPhase(kind, label, friction, color) {
        rotorState.tStepCount += 1;
        // Adaptive dt: higher external friction compresses dt (finer, deeper introspective resolution)
        const fNorm = Math.max(0, Math.min(1, (Number(friction) || 30) / 100));
        rotorState.currentDt = Number((1.0 - fNorm * 0.78).toFixed(2));
        rotorState.thoughtSpiral.push({
            t: rotorState.tStepCount,
            dt: rotorState.currentDt,
            kind,
            label: String(label || '').slice(0, 34),
            friction: Math.round(Number(friction) || 0),
            color: color || '#38bdf8',
        });
        if (rotorState.thoughtSpiral.length > MAX_THOUGHT_NODES) {
            rotorState.thoughtSpiral.shift();
        }
    }

    function loadPersistedState() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return;
            const parsed = JSON.parse(raw);
            if (!parsed || typeof parsed !== 'object') return;
            if (Array.isArray(parsed.ice)) rotorState.ice = parsed.ice.slice(0, MAX_ICE_NODES);
            if (Array.isArray(parsed.uncaptured)) rotorState.uncaptured = parsed.uncaptured.slice(0, MAX_UNCAPTURED);
            if (Array.isArray(parsed.emergentAxes)) rotorState.emergentAxes = parsed.emergentAxes.slice(0, MAX_EMERGENT_AXES);
            if (Array.isArray(parsed.thoughtSpiral)) rotorState.thoughtSpiral = parsed.thoughtSpiral.slice(-MAX_THOUGHT_NODES);
            if (Array.isArray(parsed.realityProbes)) rotorState.realityProbes = parsed.realityProbes.slice(0, 12);
            if (Array.isArray(parsed.growthLog)) rotorState.growthLog = parsed.growthLog.slice(0, MAX_LOGS);
            if (Array.isArray(parsed.worldTreeRings)) rotorState.worldTreeRings = parsed.worldTreeRings.slice(-40);
            if (Array.isArray(parsed.differentiationQueue)) rotorState.differentiationQueue = parsed.differentiationQueue.slice(0, 12);
            if (Array.isArray(parsed.causalNeedQueue)) rotorState.causalNeedQueue = parsed.causalNeedQueue.slice(0, 12);
            if (parsed.lastCausalChain && typeof parsed.lastCausalChain === 'object') rotorState.lastCausalChain = parsed.lastCausalChain;
            if (Array.isArray(parsed.probedConceptTitles)) rotorState.probedConceptTitles = parsed.probedConceptTitles.slice(-24);
            if (Array.isArray(parsed.constraintChecks)) rotorState.constraintChecks = parsed.constraintChecks.slice(0, 8);
            if (Array.isArray(parsed.sensoryHierarchyChecks)) rotorState.sensoryHierarchyChecks = parsed.sensoryHierarchyChecks.slice(0, 6);
            if (parsed.groundedLexicon && typeof parsed.groundedLexicon === 'object') rotorState.groundedLexicon = parsed.groundedLexicon;
            if (parsed.actionExpStats && typeof parsed.actionExpStats === 'object') rotorState.actionExpStats = parsed.actionExpStats;
            if (parsed.streamGlobalStats && typeof parsed.streamGlobalStats === 'object' && Array.isArray(parsed.streamGlobalStats.globalSumVec)) {
                rotorState.streamGlobalStats = {
                    totalEpisodes: Number(parsed.streamGlobalStats.totalEpisodes) || 0,
                    globalSumVec: parsed.streamGlobalStats.globalSumVec.slice(0, 6).map((n) => Number(n) || 0),
                };
            }
            if (Array.isArray(parsed.streamEpisodes)) rotorState.streamEpisodes = parsed.streamEpisodes.slice(0, 10);
            if (parsed.selfPolicy && typeof parsed.selfPolicy === 'object') {
                rotorState.selfPolicy = {
                    specificityThreshold: Math.max(8, Math.min(34, Number(parsed.selfPolicy.specificityThreshold) || 14)),
                    interventionErrorTrigger: Math.max(15, Math.min(55, Number(parsed.selfPolicy.interventionErrorTrigger) || 32)),
                    learningAlphaFloor: Math.max(0.12, Math.min(0.45, Number(parsed.selfPolicy.learningAlphaFloor) || 0.25)),
                    blindSpotQueueThreshold: Math.max(16, Math.min(52, Number(parsed.selfPolicy.blindSpotQueueThreshold) || 28)),
                    revisionsCount: Number(parsed.selfPolicy.revisionsCount) || 0,
                    rollbacksCount: Number(parsed.selfPolicy.rollbacksCount) || 0,
                };
            }
            if (Array.isArray(parsed.selfAuditHistory)) rotorState.selfAuditHistory = parsed.selfAuditHistory.slice(0, 10);
            if (Number.isFinite(Number(parsed.tStepCount))) rotorState.tStepCount = Number(parsed.tStepCount);
            if (Number.isFinite(Number(parsed.currentDt))) rotorState.currentDt = Number(parsed.currentDt);
            if (Number.isFinite(Number(parsed.valueRevisions))) rotorState.valueRevisions = Number(parsed.valueRevisions);
            if (parsed.selfValues && typeof parsed.selfValues === 'object') {
                rotorState.selfValues = {
                    unity: Number(parsed.selfValues.unity) || 52,
                    novelty: Number(parsed.selfValues.novelty) || 64,
                    realityCheck: Number(parsed.selfValues.realityCheck) || 48,
                    axisGenesis: Number(parsed.selfValues.axisGenesis) || 58,
                };
            }
            if (typeof parsed.activePurpose === 'string' && parsed.activePurpose) rotorState.activePurpose = parsed.activePurpose;
            if (typeof parsed.activeMotive === 'string' && parsed.activeMotive) rotorState.activeMotive = parsed.activeMotive;
            if (parsed.weatherHypothesis && typeof parsed.weatherHypothesis === 'object') {
                rotorState.weatherHypothesis = {
                    expectedTempC: Number(parsed.weatherHypothesis.expectedTempC) || 15.0,
                    expectedPressureHpa: Number(parsed.weatherHypothesis.expectedPressureHpa) || 1013.2,
                    expectedWindKmh: Number(parsed.weatherHypothesis.expectedWindKmh) || 12.0,
                };
            }
            if (parsed.phaseScheduler && typeof parsed.phaseScheduler === 'object') {
                rotorState.phaseScheduler.midTension = Math.max(0, Math.min(100, Number(parsed.phaseScheduler.midTension) || 0));
                rotorState.phaseScheduler.macroPressure = Math.max(0, Math.min(100, Number(parsed.phaseScheduler.macroPressure) || 0));
                rotorState.phaseScheduler.fastFires = Number(parsed.phaseScheduler.fastFires) || 0;
                rotorState.phaseScheduler.midFires = Number(parsed.phaseScheduler.midFires) || 0;
                rotorState.phaseScheduler.macroFires = Number(parsed.phaseScheduler.macroFires) || 0;
                rotorState.phaseScheduler.internalFires = Number(parsed.phaseScheduler.internalFires) || 0;
                rotorState.phaseScheduler.idleSkippedTicks = Number(parsed.phaseScheduler.idleSkippedTicks) || 0;
                rotorState.phaseScheduler.lastFriction = Number(parsed.phaseScheduler.lastFriction) || 35;
                if (typeof parsed.phaseScheduler.lastMacroNote === 'string' && parsed.phaseScheduler.lastMacroNote) {
                    rotorState.phaseScheduler.lastMacroNote = parsed.phaseScheduler.lastMacroNote;
                }
            }
            if (rotorState.ice.length > 0) {
                rotorState.selectedIceTitle = rotorState.ice[rotorState.ice.length - 1].title;
                rotorState.lastStatus = `누적 외부 얼음 ${rotorState.ice.length}개 · 세계수 나이테 ${rotorState.worldTreeRings.length}겹 · 인과 결손 대기 ${rotorState.causalNeedQueue.length}건 복원`;
            }
        } catch {
            // ignore corrupted storage
        }
    }

    function persistState() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                ice: rotorState.ice.slice(-MAX_ICE_NODES),
                uncaptured: rotorState.uncaptured.slice(0, MAX_UNCAPTURED),
                emergentAxes: rotorState.emergentAxes.slice(0, MAX_EMERGENT_AXES),
                thoughtSpiral: rotorState.thoughtSpiral.slice(-MAX_THOUGHT_NODES),
                realityProbes: rotorState.realityProbes.slice(-12),
                growthLog: rotorState.growthLog.slice(-MAX_LOGS),
                worldTreeRings: rotorState.worldTreeRings.slice(-40),
                differentiationQueue: rotorState.differentiationQueue.slice(0, 12),
                causalNeedQueue: rotorState.causalNeedQueue.slice(0, 12),
                lastCausalChain: rotorState.lastCausalChain,
                probedConceptTitles: rotorState.probedConceptTitles.slice(-24),
                constraintChecks: rotorState.constraintChecks.slice(0, 8),
                sensoryHierarchyChecks: rotorState.sensoryHierarchyChecks.slice(0, 6),
                groundedLexicon: rotorState.groundedLexicon,
                actionExpStats: rotorState.actionExpStats,
                streamGlobalStats: rotorState.streamGlobalStats,
                streamEpisodes: rotorState.streamEpisodes.slice(0, 10),
                selfPolicy: rotorState.selfPolicy,
                selfAuditHistory: rotorState.selfAuditHistory.slice(0, 10),
                tStepCount: rotorState.tStepCount,
                currentDt: rotorState.currentDt,
                valueRevisions: rotorState.valueRevisions,
                selfValues: rotorState.selfValues,
                activePurpose: rotorState.activePurpose,
                activeMotive: rotorState.activeMotive,
                weatherHypothesis: rotorState.weatherHypothesis,
                phaseScheduler: {
                    midTension: Math.round(rotorState.phaseScheduler.midTension),
                    macroPressure: Math.round(rotorState.phaseScheduler.macroPressure),
                    fastFires: rotorState.phaseScheduler.fastFires,
                    midFires: rotorState.phaseScheduler.midFires,
                    macroFires: rotorState.phaseScheduler.macroFires,
                    internalFires: rotorState.phaseScheduler.internalFires,
                    idleSkippedTicks: rotorState.phaseScheduler.idleSkippedTicks,
                    lastFriction: rotorState.phaseScheduler.lastFriction,
                    lastMacroNote: rotorState.phaseScheduler.lastMacroNote,
                },
                updatedAt: new Date().toISOString(),
            }));
        } catch {
            // ignore quota errors
        }
        syncCognitiveBridge();
    }

    function syncCognitiveBridge() {
        try {
            const existingRaw = localStorage.getItem(BRIDGE_KEY);
            const existing = existingRaw ? JSON.parse(existingRaw) : {};
            const avgClarity = rotorState.ice.length
                ? Math.round(rotorState.ice.reduce((s, n) => s + (n.metrics ? n.metrics.clarity : 50), 0) / rotorState.ice.length)
                : 0;
            localStorage.setItem(BRIDGE_KEY, JSON.stringify({
                ...existing,
                outward_epistemic: {
                    iceCount: rotorState.ice.length,
                    emergentAxisCount: rotorState.emergentAxes.length,
                    tStepCount: rotorState.tStepCount,
                    currentDt: rotorState.currentDt,
                    uncapturedCount: rotorState.uncaptured.length,
                    realityProbesCount: rotorState.realityProbes.length,
                    avgClarity,
                    activePurpose: rotorState.activePurpose,
                    latestConcept: rotorState.ice.length ? rotorState.ice[rotorState.ice.length - 1].title : null,
                },
            }));
        } catch {
            // ignore bridge error
        }
    }

    function pushLog(tag, text) {
        const now = new Date();
        const ts = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
        rotorState.growthLog.unshift({ ts, tag, text });
        if (rotorState.growthLog.length > MAX_LOGS) rotorState.growthLog.length = MAX_LOGS;
        rotorState.uiDirty = true;
    }

    function buildPriorNodesPayload() {
        const allAxes = getAllAxes();
        return rotorState.ice.map((n) => {
            const flatAxes = {};
            allAxes.forEach((ax) => {
                flatAxes[ax.key] = n.axes && n.axes[ax.key] ? n.axes[ax.key].score : 22;
            });
            return {
                title: n.title,
                tokens: n.tokens || [],
                axes: flatAxes,
            };
        });
    }

    // ========================================================================
    // Result -> Contrastive Pull / Repulsion / Blind-Spot Horizon -> Next Cause
    // Zero Math.random(), zero modulo rotation, zero hardcoded topic word lists:
    // Every next action is derived from converging pull, non-converging exclusion,
    // prism blind-spot residuals, and external taxonomy returned by real sources.
    // ========================================================================
    function matchExternalAtmosphericCategories(node) {
        if (!node || !Array.isArray(node.categories)) return [];
        return node.categories.filter((cat) => /기상|대기|기후|meteorolog|atmospher|weather|climate/i.test(String(cat || '')));
    }

    function enqueueCausalNeed(need) {
        if (!need || !need.action || !need.dedupKey) return;
        const existingIdx = rotorState.causalNeedQueue.findIndex((item) => item.dedupKey === need.dedupKey);
        if (existingIdx >= 0) {
            if (need.priority > rotorState.causalNeedQueue[existingIdx].priority) {
                rotorState.causalNeedQueue[existingIdx] = {
                    ...rotorState.causalNeedQueue[existingIdx],
                    ...need,
                };
            }
        } else {
            rotorState.causalNeedQueue.push({
                id: `need_${Date.now()}_${rotorState.causalNeedQueue.length}`,
                createdAtT: rotorState.tStepCount,
                ...need,
            });
        }
        rotorState.causalNeedQueue.sort((a, b) => (b.priority || 0) - (a.priority || 0));
        if (rotorState.causalNeedQueue.length > 10) {
            rotorState.causalNeedQueue.length = 10;
        }
    }

    function canUseExternalApiNow() {
        const ps = rotorState.phaseScheduler;
        const now = Date.now();
        if (!ps.externalWindowStartMs || now - ps.externalWindowStartMs >= 90000) {
            ps.externalWindowStartMs = now;
            ps.externalCallsInWindow = 0;
        }
        return ps.externalCallsInWindow < 18;
    }

    function recordExternalApiUsage() {
        const ps = rotorState.phaseScheduler;
        const now = Date.now();
        if (!ps.externalWindowStartMs || now - ps.externalWindowStartMs >= 90000) {
            ps.externalWindowStartMs = now;
            ps.externalCallsInWindow = 0;
        }
        ps.externalCallsInWindow += 1;
    }

    function findStaleIceForReobservation() {
        if (rotorState.ice.length < 2) return null;
        const axisCount = getAllAxes().length;
        const candidates = rotorState.ice
            .slice(0, Math.max(1, rotorState.ice.length - 1))
            .filter((n) => (Number(n.reobservedAxisCount) || 4) < axisCount || (n.metrics && n.metrics.clarity < 68));
        if (candidates.length === 0) return null;
        candidates.sort((a, b) => ((Number(a.reobservedAtT) || 0) - (Number(b.reobservedAtT) || 0)));
        return candidates[0];
    }

    function pickAutonomousDualityPair() {
        if (rotorState.ice.length < 2) return null;
        const allAxes = getAllAxes();
        let bestPair = null;
        let bestScore = -1;
        const lastKey = rotorState.phaseScheduler.lastDualityPairKey || '';
        for (let i = 0; i < rotorState.ice.length; i += 1) {
            for (let j = i + 1; j < rotorState.ice.length; j += 1) {
                const a = rotorState.ice[i];
                const b = rotorState.ice[j];
                const pairKey = [a.title, b.title].sort().join('|');
                if (pairKey === lastKey && rotorState.ice.length > 2) continue;
                let maxGap = 0;
                let minGap = 100;
                allAxes.forEach((ax) => {
                    const va = a.axes && a.axes[ax.key] ? a.axes[ax.key].score : 22;
                    const vb = b.axes && b.axes[ax.key] ? b.axes[ax.key].score : 22;
                    const gap = Math.abs(va - vb);
                    if (gap > maxGap) maxGap = gap;
                    if (gap < minGap) minGap = gap;
                });
                const dualityScore = maxGap + (100 - minGap) * 0.5;
                if (dualityScore > bestScore) {
                    bestScore = dualityScore;
                    bestPair = { aTitle: a.title, bTitle: b.title, pairKey, maxGap: Math.round(maxGap) };
                }
            }
        }
        return bestPair;
    }

    // Outcome -> Next Causes (1): After observing an external concept
    function deriveNextCausesFromExploration(nodeEntry) {
        if (!nodeEntry) return;
        const titleLow = String(nodeEntry.title || '').toLowerCase();
        const friction = nodeEntry.metrics ? Number(nodeEntry.metrics.friction) || 35 : 35;
        const cf = nodeEntry.contrastiveField || null;

        // A) External Atmospheric Sensor Need — ONLY if external Wikipedia taxonomy classifies this concept under atmosphere/meteorology!
        const matchedAtmoCats = matchExternalAtmosphericCategories(nodeEntry);
        const alreadyProbed = rotorState.probedConceptTitles.includes(titleLow);
        if (!alreadyProbed && matchedAtmoCats.length > 0) {
            const nextCity = CITY_LIST[rotorState.cityIndex % CITY_LIST.length];
            enqueueCausalNeed({
                dedupKey: `probe:${titleLow}`,
                action: 'reality_probe',
                priority: 91,
                originEvent: `결과: [${nodeEntry.title}]의 외부 분류(${matchedAtmoCats.slice(0, 2).join(', ')})가 실측 대기 영역에 속함`,
                internalLimit: '내부 한계: 백과 텍스트만으로는 대기 상태의 실시간 물리 변동을 검증할 수 없음',
                targetSummary: `실시간 대기 실측(${nextCity.toUpperCase()})으로 [${nodeEntry.title}] 수치 검증`,
                payload: { cityId: nextCity, linkedConcept: nodeEntry.title, matchedVars: matchedAtmoCats.slice(0, 3) },
            });
        }

        // B) Prism Blind-Spot Horizon Deficit -> Explore a live link intersecting uncaptured residual tokens (governed by live selfPolicy!)
        const bsThreshold = rotorState.selfPolicy ? rotorState.selfPolicy.blindSpotQueueThreshold : 28;
        if (cf && (cf.blindSpotPct >= bsThreshold || (cf.blindSpotTokens && cf.blindSpotTokens.length >= 2))) {
            const blindProbe = rotorState.uncaptured.find(
                (u) => u.sourceTitle === nodeEntry.title && u.role === 'blind_spot_probe'
            ) || rotorState.uncaptured.find((u) => u.role === 'blind_spot_probe') || null;
            if (blindProbe) {
                const residualSample = (cf.blindSpotTokens || []).slice(0, 3).join(', ') || '미포집 잔차';
                enqueueCausalNeed({
                    dedupKey: `explore:blind:${blindProbe.title.toLowerCase()}`,
                    action: 'explore',
                    priority: Math.min(95, 62 + Math.round(cf.blindSpotPct * 0.4)),
                    originEvent: `결과: [${nodeEntry.title}]의 ${cf.blindSpotPct}%가 현재 ${getAllAxes().length}축 프리즘 사각지대(${residualSample})로 유출됨`,
                    internalLimit: `내부 한계: 현재 관측 프리즘만으로는 잔차 요소(${residualSample})의 인과 구조를 포착 불가`,
                    targetSummary: `사각지대 잔차 규명 → [${blindProbe.title}] 탐색`,
                    payload: { topic: blindProbe.title, sourceTitle: blindProbe.sourceTitle || nodeEntry.title },
                });
            }
        }

        // C) Non-Converging Repulsion / Counter-Example Deficit -> Probe an orthogonal counter-example link
        if (cf && Array.isArray(cf.nonConvergingFactors) && cf.nonConvergingFactors.length > 0) {
            const weakest = cf.nonConvergingFactors[0];
            if (weakest && weakest.gapFromCore >= 26) {
                const counterProbe = rotorState.uncaptured.find(
                    (u) => u.sourceTitle === nodeEntry.title && u.role === 'counter_example'
                ) || rotorState.uncaptured.find((u) => u.role === 'counter_example') || null;
                if (counterProbe) {
                    enqueueCausalNeed({
                        dedupKey: `explore:counter:${counterProbe.title.toLowerCase()}`,
                        action: 'explore',
                        priority: Math.min(90, 56 + Math.round(weakest.gapFromCore * 0.45)),
                        originEvent: `결과: [${nodeEntry.title}]이 [${weakest.label}] 축에서 -${weakest.gapFromCore}점 비수렴(배제)됨`,
                        internalLimit: `내부 한계: 수렴 근거만으로는 왜 [${weakest.label}]이 배제되었는지 비교대조 근거가 불완전함`,
                        targetSummary: `비수렴 반례 비교대조 → [${counterProbe.title}] 탐색`,
                        payload: { topic: counterProbe.title, sourceTitle: counterProbe.sourceTitle || nodeEntry.title },
                    });
                }
            }
        }

        // D) Prediction Friction Deficit -> Criteria Self-Revision
        if (friction >= 48) {
            enqueueCausalNeed({
                dedupKey: `revise:t${rotorState.tStepCount}:${titleLow}`,
                action: 'self_revise',
                priority: Math.min(92, 54 + Math.round(friction * 0.5)),
                originEvent: `결과: [${nodeEntry.title}] 관측에서 내부 예측 마찰 ${friction}% 발생`,
                internalLimit: '내부 한계: 현재 내부 기준 가중치가 외부 실재 구조와 어긋남',
                targetSummary: '내부 판단 기준 가중치 재교정 후 다음 관측 방향 재설계',
                payload: { linkedConcept: nodeEntry.title, friction },
            });
        }

        // E) Simultaneous Bridge + Axis Divergence -> Boundary Duality Contrast
        if (Array.isArray(nodeEntry.bridges) && nodeEntry.bridges.length > 0) {
            const targetTitle = nodeEntry.bridges[0].targetTitle;
            const other = rotorState.ice.find((n) => n.title === targetTitle);
            if (other) {
                let maxGap = 0;
                getAllAxes().forEach((ax) => {
                    const va = nodeEntry.axes && nodeEntry.axes[ax.key] ? nodeEntry.axes[ax.key].score : 22;
                    const vb = other.axes && other.axes[ax.key] ? other.axes[ax.key].score : 22;
                    maxGap = Math.max(maxGap, Math.abs(va - vb));
                });
                if (maxGap >= 22) {
                    const pairKey = [nodeEntry.title, other.title].sort().join('|');
                    enqueueCausalNeed({
                        dedupKey: `duality:${pairKey}`,
                        action: 'duality_reobserve',
                        priority: Math.min(88, 52 + Math.round(maxGap * 0.6)),
                        originEvent: `결과: [${nodeEntry.title}]와 [${other.title}]가 공명(${nodeEntry.bridges[0].resonance}%)하면서도 축 편차 ${Math.round(maxGap)}점 노출`,
                        internalLimit: '내부 한계: 두 개념의 공통점과 분화 경계가 아직 분리 관측되지 않음',
                        targetSummary: `[${nodeEntry.title}] ⇄ [${other.title}] 경계 통합·분화 대조`,
                        payload: { pair: { aTitle: nodeEntry.title, bTitle: other.title, pairKey } },
                    });
                }
            }
        }

        // F) Core Frontier Link fallback if no blind-spot/counter-example probe was available
        const linkedFrontier = rotorState.uncaptured.find((u) => u.sourceTitle === nodeEntry.title)
            || rotorState.uncaptured[0]
            || null;
        if (linkedFrontier) {
            enqueueCausalNeed({
                dedupKey: `explore:${linkedFrontier.title.toLowerCase()}`,
                action: 'explore',
                priority: Math.min(84, 46 + Math.round((linkedFrontier.leverage || 50) * 0.42)),
                originEvent: `결과: [${nodeEntry.title}]의 외부 경계 너머에 미포집 개념 [${linkedFrontier.title}] 존재 확인`,
                internalLimit: `내부 한계: [${linkedFrontier.title}]가 내부 인과망에 없어 [${nodeEntry.title}]의 외연이 단절됨`,
                targetSummary: `외부 경계 [${linkedFrontier.title}] 실재 탐색 및 인과 연결`,
                payload: { topic: linkedFrontier.title, sourceTitle: linkedFrontier.sourceTitle || nodeEntry.title },
            });
        }
    }

    // Outcome -> Next Causes (2): After a new neural axis differentiates
    function deriveNextCausesFromAxisGenesis(spawnedAxis) {
        if (!spawnedAxis || rotorState.ice.length < 2) return;
        const stale = findStaleIceForReobservation();
        if (!stale) return;
        enqueueCausalNeed({
            dedupKey: `reobserve:${stale.title.toLowerCase()}:${spawnedAxis.key}`,
            action: 'reobserve_ice',
            priority: 94,
            originEvent: `결과: 새 신경축 [${spawnedAxis.label}]이 분화되어 내부 관측 차원이 ${getAllAxes().length}축으로 확장됨`,
            internalLimit: `내부 한계: 과거 개념 [${stale.title}]은 [${spawnedAxis.label}] 축이 없던 시점의 분류에 머물러 있음`,
            targetSummary: `확장된 ${getAllAxes().length}축으로 [${stale.title}] 재관측·재분류`,
            payload: { nodeTitle: stale.title, triggeredByAxis: spawnedAxis.label },
        });
    }

    // Outcome -> Next Causes (3): After a live physical reality probe (zero hardcoded word lists)
    function deriveNextCausesFromRealityProbe(data, linkedConcept) {
        if (!data) return;
        const f = Number(data.frictionPct) || 0;
        if (f >= 30) {
            const dynamicFrontier = rotorState.uncaptured.find(
                (u) => u.sourceTitle === linkedConcept && (u.role === 'blind_spot_probe' || u.role === 'counter_example')
            ) || rotorState.uncaptured.find((u) => u.sourceTitle === linkedConcept)
                || rotorState.uncaptured.find((u) => u.role === 'blind_spot_probe')
                || null;

            if (dynamicFrontier) {
                enqueueCausalNeed({
                    dedupKey: `explore:${dynamicFrontier.title.toLowerCase()}`,
                    action: 'explore',
                    priority: Math.min(93, 66 + Math.round(f * 0.4)),
                    originEvent: `결과: ${data.city} 실측(${data.actual.temperatureC}°C, 풍속 ${data.actual.windSpeedKmh}km/h)에서 예측 마찰 ${f}% 발생`,
                    internalLimit: `내부 한계: [${linkedConcept || '대기 가설'}]만으로는 실제 물리 오차를 설명할 수 없어 연결 경계 확인 필요`,
                    targetSummary: `물리 오차 원인 비교대조 → [${dynamicFrontier.title}] 탐색`,
                    payload: { topic: dynamicFrontier.title, sourceTitle: dynamicFrontier.sourceTitle || linkedConcept || null },
                });
            } else {
                enqueueCausalNeed({
                    dedupKey: `revise:probe:${rotorState.tStepCount}`,
                    action: 'self_revise',
                    priority: 82,
                    originEvent: `결과: ${data.city} 물리 실측 마찰 ${f}% 누적`,
                    internalLimit: '내부 한계: 기존 개념과 실측 오차 사이의 기준 가중치 재조정 필요',
                    targetSummary: '내부 판단 기준 자기수정',
                    payload: { friction: f },
                });
            }
        }
    }

    function applyCausalNeedToBanner(need) {
        rotorState.lastCausalChain = {
            originEvent: need.originEvent,
            internalLimit: need.internalLimit,
            derivedAction: need.action,
            targetSummary: need.targetSummary,
            tStep: rotorState.tStepCount + 1,
        };
        rotorState.activePurpose = `${need.originEvent} → ${need.targetSummary}`;
        rotorState.activeMotive = need.internalLimit;
    }

    function chooseSelfDrivenAction() {
        const externalReady = canUseExternalApiNow();
        const isExternalAction = (act) => act === 'explore' || act === 'reality_probe';

        // 1) Strictly pop highest-priority executable CausalNeed produced by prior outcomes
        const pickIdx = rotorState.causalNeedQueue.findIndex((item) => externalReady || !isExternalAction(item.action));
        if (pickIdx >= 0) {
            const need = rotorState.causalNeedQueue.splice(pickIdx, 1)[0];
            applyCausalNeedToBanner(need);
            return { action: need.action, ...(need.payload || {}), need };
        }

        // 2) Queue empty -> inspect current graph for the largest real measurable deficit (zero randomness)
        if (rotorState.ice.length === 0) {
            const bootNeed = {
                action: 'explore',
                originEvent: '초기 상태: 내부 기억(얼음) 0건 — 자기 내부만으로 파생할 인과 기반이 부재함',
                internalLimit: '내부 한계: 바깥 세계의 첫 단서를 관측하기 전에는 어떤 결손도 비교할 수 없음',
                targetSummary: '첫 외부 경계 단서 [바람] 관측으로 인과 연쇄 개시',
                payload: { topic: '바람', sourceTitle: null },
            };
            applyCausalNeedToBanner(bootNeed);
            return { action: 'explore', topic: '바람', sourceTitle: null, need: bootNeed };
        }

        const staleNode = findStaleIceForReobservation();
        if (staleNode) {
            const need = {
                action: 'reobserve_ice',
                originEvent: `결손 점검: [${staleNode.title}]이 현재 ${getAllAxes().length}축 기준에서 미재관측(또는 선명도 ${staleNode.metrics ? staleNode.metrics.clarity : 50}%) 상태`,
                internalLimit: '내부 한계: 확장된 인식 축과 과거 기억 사이의 불일치가 해소되지 않음',
                targetSummary: `[${staleNode.title}] 재관측·재분류 및 신규 인과 연결 탐색`,
                payload: { nodeTitle: staleNode.title },
            };
            applyCausalNeedToBanner(need);
            return { action: 'reobserve_ice', nodeTitle: staleNode.title, need };
        }

        if (externalReady && rotorState.uncaptured.length > 0) {
            const top = rotorState.uncaptured[0];
            const need = {
                action: 'explore',
                originEvent: `결손 점검: [${top.sourceTitle || '기존 개념'}]에서 뻗은 미포집 경계 [${top.title}] (연결 지지 ${top.supportCount || 1}건) 미해결`,
                internalLimit: `내부 한계: [${top.title}]가 내부 인과망 밖에 남아 있어 연결 구조가 열려 있음`,
                targetSummary: `미포집 경계 [${top.title}] 실재 탐색`,
                payload: { topic: top.title, sourceTitle: top.sourceTitle },
            };
            applyCausalNeedToBanner(need);
            return { action: 'explore', topic: top.title, sourceTitle: top.sourceTitle, need };
        }

        // 2.2) Autonomous Active Causal Intervention (zero human clicking, zero hardcoded word labels!)
        // When simulation bridge is live, autonomously explore under-tested or high-error actions to discover word<->physics invariants
        if (window.ElysiaDigitalTwinRPG && typeof window.ElysiaDigitalTwinRPG.runLiveCausalEpisode === 'function') {
            const totalEp = rotorState.streamGlobalStats ? rotorState.streamGlobalStats.totalEpisodes : 0;
            const actions = window.ElysiaDigitalTwinRPG.getAvailableActionIds
                ? window.ElysiaDigitalTwinRPG.getAvailableActionIds().filter((a) => a !== 'observe_tick')
                : ['skill_q', 'skill_w', 'skill_e', 'monster_raid', 'mana_vein', 'famine_hoard'];
            const untested = actions.find((a) => !rotorState.actionExpStats[a] || rotorState.actionExpStats[a].count === 0);
            const errTrig = rotorState.selfPolicy ? rotorState.selfPolicy.interventionErrorTrigger : 32;
            const highErrAction = actions
                .filter((a) => rotorState.actionExpStats[a] && rotorState.actionExpStats[a].avgErrorPct >= errTrig)
                .sort((a, b) => (rotorState.actionExpStats[b].avgErrorPct || 0) - (rotorState.actionExpStats[a].avgErrorPct || 0))[0];

            const shouldInterveneNow = Boolean(untested && (totalEp < 6 || !externalReady))
                || Boolean(highErrAction && (!externalReady || rotorState.tStepCount % 3 === 0));
            if (shouldInterveneNow) {
                const chosen = untested || highErrAction || actions[totalEp % actions.length];
                const need = {
                    action: 'active_intervention',
                    originEvent: untested
                        ? `자율 탐구: 행동 [${chosen}]의 개입↔비개입 인과 변화량이 미관측 상태 (누적 실험 ${totalEp}회)`
                        : `자율 재검증: 행동 [${chosen}]의 예측 오차(${rotorState.actionExpStats[chosen].avgErrorPct}%)가 기준 초과`,
                    internalLimit: '내부 한계: 고정 라벨 없이 원시 발화·물리 채널 간 교차 상황 대조가 더 필요함',
                    targetSummary: `무개입 자율 능동실험 [${chosen}] 실행 및 어휘 분별`,
                    payload: { actionId: chosen },
                };
                applyCausalNeedToBanner(need);
                return { action: 'active_intervention', actionId: chosen, need };
            }
        }

        const pair = pickAutonomousDualityPair();
        if (pair) {
            const need = {
                action: 'duality_reobserve',
                originEvent: `결손 점검: [${pair.aTitle}] ⇄ [${pair.bTitle}] 쌍의 최대 축 격차(${pair.maxGap}점)가 미대조 상태`,
                internalLimit: '내부 한계: 두 개념의 공통 원리와 분화 지점이 명시적으로 대조되지 않음',
                targetSummary: `[${pair.aTitle}] ⇄ [${pair.bTitle}] 자율 경계 대조`,
                payload: { pair },
            };
            applyCausalNeedToBanner(need);
            return { action: 'duality_reobserve', pair, need };
        }

        const fallbackNeed = {
            action: 'self_revise',
            originEvent: `결손 점검: 외부 API 쿨다운 또는 단기 결손 소진 (현재 마찰 ${rotorState.phaseScheduler.lastFriction}%)`,
            internalLimit: '내부 한계: 현재 가중치 분포의 편향을 점검해 다음 관측 기준을 재정렬해야 함',
            targetSummary: '내부 판단 기준 균형 자기수정',
            payload: {},
        };
        applyCausalNeedToBanner(fallbackNeed);
        return { action: 'self_revise', need: fallbackNeed };
    }

    function formulatePreObservationHypothesis(targetTopic, sourceNodeTitle) {
        const sourceNode = rotorState.ice.find((n) => n.title === sourceNodeTitle)
            || rotorState.ice[rotorState.ice.length - 1]
            || null;
        const allAxes = getAllAxes();

        if (!sourceNode) {
            return {
                targetTopic,
                expectedAxis: 'changePrinciple',
                expectedAxisLabel: '변화원리',
                expectedBridgeTitle: '',
                rationale: `기원 탐색 가설: "${targetTopic}"에서 핵심 [변화원리]와 실세계 인과 구조를 처음 포착할 것이라 예측`,
            };
        }

        const domKey = sourceNode.dominantAxis || 'causalStructure';
        const axisObj = allAxes.find((a) => a.key === domKey) || allAxes[2];
        return {
            targetTopic,
            expectedAxis: axisObj.key,
            expectedAxisLabel: axisObj.label,
            expectedBridgeTitle: sourceNode.title,
            rationale: `연속 재프레임화 가설: "${sourceNode.title}"에서 얻은 [${axisObj.label}] 관점이 "${targetTopic}"에서도 동형 공명할 것이라 예측`,
        };
    }

    // Self-Revising Value Criteria & Dynamic Neural Axis Genesis after real external encounter
    function selfReflectAndEvolveAfterExploration(data) {
        const f = data.metrics ? data.metrics.friction : 35;
        const contrast = data.metrics ? data.metrics.contrast : 50;
        const bridgeCount = (data.bridges || []).length;
        const clamp = (x) => Math.max(18, Math.min(96, Math.round(x)));

        // 1) Record fine-grained thought phases dynamically (NOT locked to 4 steps!)
        recordThoughtPhase('observe', `실재 관측: ${data.title}`, f * 0.6, '#38bdf8');
        if (f >= 40) {
            // High external friction triggers EXTRA introspective sub-steps (dt shrinks!)
            recordThoughtPhase('friction', `예측 마찰(${f}%) 재인식`, f, '#f59e0b');
        }

        // 2) Law-Driven Neural Axis Differentiation Step Auto-Generation
        let queuedDiffStep = null;
        const law = data.discoveredLaw || null;
        const cand = data.emergentAxisCandidate || null;
        const candLabel = (law && law.derivedAxisLabel) || (cand && cand.label) || '';
        const candKeywords = (law && Array.isArray(law.derivedKeywords) && law.derivedKeywords.length >= 2)
            ? law.derivedKeywords
            : (cand && Array.isArray(cand.keywords) ? cand.keywords : []);

        if (
            candLabel &&
            candKeywords.length >= 2 &&
            rotorState.emergentAxes.length + rotorState.differentiationQueue.length < MAX_EMERGENT_AXES &&
            (bridgeCount > 0 || f >= 36 || contrast >= 58 || rotorState.ice.length === 1)
        ) {
            const existsAxis = getAllAxes().some((a) => a.label.toLowerCase() === candLabel.toLowerCase());
            const existsQueue = rotorState.differentiationQueue.some((q) => q.candidateLabel.toLowerCase() === candLabel.toLowerCase());
            if (!existsAxis && !existsQueue) {
                queuedDiffStep = {
                    id: `diff_${Date.now()}_${rotorState.tStepCount}`,
                    sourceTitle: data.title,
                    bridgeTarget: law ? law.bridgeTarget : null,
                    lawTitle: law ? law.title : `[${data.title}] ${data.dominantAxisLabel} 법칙`,
                    lawStatement: law ? law.statement : (data.summary || '').slice(0, 180),
                    candidateLabel: candLabel,
                    keywords: candKeywords.slice(0, 8),
                    createdAtT: rotorState.tStepCount + 1,
                };
                rotorState.differentiationQueue.push(queuedDiffStep);
                recordThoughtPhase('queue_split', `분화 스텝 생성: [${candLabel}]`, f + 10, '#f472b6');
                pushLog(
                    '분화 스텝 자동생성',
                    `발견 법칙 ${queuedDiffStep.lawTitle} → 신경축 [${candLabel}] 분화 스텝이 자동 대기열에 등록됨`
                );
            }
        }

        // 3) Self-Revision of Meaning & Value Criteria (스스로 가치·의미 기준 재규정)
        let valueShiftNote = '';
        if (bridgeCount >= 2) {
            rotorState.selfValues.unity = clamp(rotorState.selfValues.unity + 5);
            rotorState.selfValues.novelty = clamp(rotorState.selfValues.novelty + 2);
            valueShiftNote = `실제 동형 연결 ${bridgeCount}건 발견 → [원리 통합] 가치 강화(${rotorState.selfValues.unity}%)`;
        } else if (f >= 45) {
            rotorState.selfValues.axisGenesis = clamp(rotorState.selfValues.axisGenesis + 6);
            rotorState.selfValues.realityCheck = clamp(rotorState.selfValues.realityCheck + 5);
            rotorState.selfValues.unity = clamp(rotorState.selfValues.unity - 2);
            valueShiftNote = `강한 외부 마찰(${f}%) 경험 → 기존 틀 고수 대신 [자기축 분화(${rotorState.selfValues.axisGenesis}%)]와 [현실 정합(${rotorState.selfValues.realityCheck}%)] 가치 상향`;
        } else {
            rotorState.selfValues.novelty = clamp(rotorState.selfValues.novelty + 4);
            valueShiftNote = `안정적 수렴 감지 → 안주하지 않기 위해 [미지 돌파] 가치 상향(${rotorState.selfValues.novelty}%)`;
        }
        rotorState.valueRevisions += 1;
        recordThoughtPhase('revalue', `가치 재규정 (rev.${rotorState.valueRevisions})`, f * 0.45, '#a78bfa');

        return { queuedDiffStep, valueShiftNote };
    }

    async function exploreTopic(rawTopic, options = {}) {
        const topic = String(rawTopic || '').trim();
        if (!topic || rotorState.busy) return null;

        rotorState.busy = true;
        const prediction = options.prediction || formulatePreObservationHypothesis(topic, options.sourceTitle || null);
        rotorState.cloud = prediction;
        rotorState.water = {
            title: topic,
            stage: `t${rotorState.tStepCount + 1} 외부 실재 탐색 중...`,
        };
        recordThoughtPhase('intent', `사유 발현: ${topic}`, 28, '#10b981');
        rotorState.lastStatus = `t${rotorState.tStepCount} (dt=${rotorState.currentDt}) 외부 실재 탐색 중: "${topic}" — ${prediction.rationale}`;
        rotorState.uiDirty = true;

        try {
            const res = await fetch('/api/epistemic/explore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic,
                    lang: options.lang || 'ko',
                    priorNodes: buildPriorNodesPayload(),
                    emergentAxes: rotorState.emergentAxes.map((a) => ({
                        key: a.key,
                        label: a.label,
                        keywords: a.keywords,
                    })),
                    prediction,
                }),
            });
            const data = await res.json();
            if (!res.ok || data.status !== 'ok') {
                throw new Error(data.message || `외부 탐색 오류 (${res.status})`);
            }

            const idx = rotorState.ice.findIndex((n) => n.title.toLowerCase() === data.title.toLowerCase());
            const nodeEntry = {
                title: data.title,
                lang: data.lang,
                sourceUrl: data.sourceUrl,
                summary: data.summary,
                categories: data.categories || [],
                dominantAxis: data.dominantAxis,
                dominantAxisLabel: data.dominantAxisLabel,
                axes: data.axes,
                contrastiveField: data.contrastiveField || null,
                tokens: data.tokens || [],
                bridges: data.bridges || [],
                divergences: data.divergences || [],
                metrics: data.metrics || { clarity: 60, saturation: 55, contrast: 60, friction: 35 },
                predictionAudit: data.predictionAudit || null,
                fetchedAt: data.fetchedAt,
                bornAtT: rotorState.tStepCount + 1,
                ringOrder: idx >= 0 ? rotorState.ice[idx].ringOrder : rotorState.ice.length + 1,
            };

            if (idx >= 0) {
                rotorState.ice[idx] = nodeEntry;
            } else {
                rotorState.ice.push(nodeEntry);
                if (rotorState.ice.length > MAX_ICE_NODES) rotorState.ice.shift();
            }
            rotorState.selectedIceTitle = nodeEntry.title;

            // Update Uncaptured Frontier from real Wikipedia outgoing links (preserving blind_spot_probe / counter_example roles)
            const iceTitlesLower = new Set(rotorState.ice.map((n) => n.title.toLowerCase()));
            const frontierMap = new Map();
            for (const item of rotorState.uncaptured) {
                const low = item.title.toLowerCase();
                if (iceTitlesLower.has(low) || low === topic.toLowerCase()) continue;
                frontierMap.set(low, item);
            }
            for (const f of (data.uncapturedFrontier || [])) {
                const low = String(f.title || '').toLowerCase();
                if (!low || iceTitlesLower.has(low)) continue;
                if (frontierMap.has(low)) {
                    const prev = frontierMap.get(low);
                    prev.supportCount = (prev.supportCount || 1) + 1;
                    prev.leverage = Math.min(99, Math.max(prev.leverage || 50, f.leverage || 50) + 8);
                    prev.sourceTitle = nodeEntry.title;
                    if (f.role === 'blind_spot_probe' || (f.role === 'counter_example' && prev.role !== 'blind_spot_probe')) {
                        prev.role = f.role;
                        prev.reason = f.reason || prev.reason;
                    }
                } else {
                    frontierMap.set(low, {
                        title: f.title,
                        sourceTitle: nodeEntry.title,
                        role: f.role || 'core_bridge',
                        residualOverlap: Number(f.residualOverlap) || 0,
                        leverage: f.leverage || 55,
                        supportCount: 1,
                        reason: f.reason || `"${nodeEntry.title}"에서 실재 연결된 미포집 개념`,
                    });
                }
            }
            rotorState.uncaptured = Array.from(frontierMap.values())
                .sort((a, b) => {
                    const roleBonus = (r) => (r === 'blind_spot_probe' ? 18 : (r === 'counter_example' ? 10 : 0));
                    return ((b.supportCount || 1) * 20 + (b.leverage || 50) + roleBonus(b.role))
                        - ((a.supportCount || 1) * 20 + (a.leverage || 50) + roleBonus(a.role));
                })
                .slice(0, MAX_UNCAPTURED);

            // Self-reflection, law-based differentiation step generation, and value criteria update
            const { queuedDiffStep, valueShiftNote } = selfReflectAndEvolveAfterExploration(data);

            // Auto-record World Tree Growth Ring with discovered causal law & pulse animation
            const ringEntry = recordWorldTreeRing(nodeEntry, null, idx < 0, data.discoveredLaw || null, 'connection');

            rotorState.water = {
                title: nodeEntry.title,
                stage: `나이테 #${ringEntry.ringNumber} 기록 · t${rotorState.tStepCount} 완료 (분화대기 ${rotorState.differentiationQueue.length})`,
                metrics: nodeEntry.metrics,
            };

            const bridgeText = nodeEntry.bridges.length > 0
                ? `동형 연결: ${nodeEntry.bridges.slice(0, 2).map((b) => `${b.targetTitle}(${b.resonance}%)`).join(', ')}`
                : '새로운 기원 뿌리 등록';
            const auditText = nodeEntry.predictionAudit ? ` | ${nodeEntry.predictionAudit.verdict}` : '';
            pushLog(
                options.autonomous ? `자동루프 나이테#${ringEntry.ringNumber}` : `나이테#${ringEntry.ringNumber}`,
                `[${nodeEntry.title}] (${nodeEntry.dominantAxisLabel} · 선명 ${nodeEntry.metrics.clarity}%) — ${bridgeText}${queuedDiffStep ? ` · 분화스텝 [${queuedDiffStep.candidateLabel}] 생성` : ''}${auditText} | ${valueShiftNote}`
            );

            rotorState.lastStatus = `세계수 나이테 #${ringEntry.ringNumber} 기록: "${nodeEntry.title}"${queuedDiffStep ? ` · 법칙 기반 [${queuedDiffStep.candidateLabel}] 분화 스텝 자동 생성` : ''} · ${valueShiftNote}`;

            if (typeof window.__elysiaOnExternalInfluence === 'function') {
                window.__elysiaOnExternalInfluence(
                    '외부지식·나이테',
                    `"${nodeEntry.title}" (나이테 #${ringEntry.ringNumber}, 총 ${getAllAxes().length}축)`
                );
            }

            // Feed 3-Tier Phase-Rotor Scheduler: friction -> Layer 0 cadence & Layer 1 tension; growth -> Layer 2 pressure
            const obsFriction = nodeEntry.metrics ? Number(nodeEntry.metrics.friction) || 35 : 35;
            const ps = rotorState.phaseScheduler;
            ps.lastFriction = obsFriction;
            ps.midTension = Math.min(130, ps.midTension + Math.round(18 + obsFriction * 0.58 + (queuedDiffStep ? 34 : 0)));
            ps.macroPressure = Math.min(130, ps.macroPressure + 16 + (idx < 0 ? 8 : 0));

            // Effect becomes next Cause: derive explicit next causal deficits strictly from this outcome
            deriveNextCausesFromExploration(nodeEntry);

            persistState();
            rotorState.uiDirty = true;
            return nodeEntry;
        } catch (err) {
            const msg = err instanceof Error ? err.message : '외부 지식 연결 실패';
            recordThoughtPhase('limit', `경계 한계: ${topic}`, 75, '#fb7185');
            rotorState.lastStatus = `외부 탐색 한계 인식: ${msg}`;
            pushLog('무지 경계', `"${topic}" → ${msg}`);
            rotorState.water = null;
            rotorState.uiDirty = true;
            return null;
        } finally {
            rotorState.busy = false;
        }
    }

    function executeQueuedDifferentiationStep() {
        if (rotorState.differentiationQueue.length === 0) return null;
        const stepItem = rotorState.differentiationQueue.shift();
        if (!stepItem) return null;

        const exists = getAllAxes().some((a) => a.label.toLowerCase() === stepItem.candidateLabel.toLowerCase());
        if (exists || rotorState.emergentAxes.length >= MAX_EMERGENT_AXES) {
            rotorState.uiDirty = true;
            return null;
        }

        const idx = rotorState.emergentAxes.length;
        const spawnedAxis = {
            key: `emergent_${idx + 1}`,
            label: stepItem.candidateLabel,
            keywords: stepItem.keywords.slice(0, 8),
            color: EMERGENT_PALETTE[idx % EMERGENT_PALETTE.length],
            bornFrom: stepItem.sourceTitle,
            bornFromLaw: stepItem.lawTitle,
            bornAtT: rotorState.tStepCount + 1,
            emergent: true,
        };
        rotorState.emergentAxes.push(spawnedAxis);

        // Retroactively re-project all existing Ice nodes along the newly differentiated neural axis
        const lowerKws = spawnedAxis.keywords.map((k) => String(k || '').toLowerCase()).filter((k) => k.length >= 2);
        let rescoredCount = 0;
        rotorState.ice.forEach((node) => {
            const summaryLow = String(node.summary || '').toLowerCase();
            const tokSet = new Set((node.tokens || []).map((t) => String(t).toLowerCase()));
            const kwHits = lowerKws.filter((kw) => tokSet.has(kw) || summaryLow.includes(kw));
            const score = Math.min(100, Math.round(14 + kwHits.length * 22 + (node.title === stepItem.sourceTitle ? 28 : 0)));
            if (!node.axes) node.axes = {};
            node.axes[spawnedAxis.key] = {
                key: spawnedAxis.key,
                label: spawnedAxis.label,
                score,
                emergent: true,
                evidence: kwHits.length > 0
                    ? [`법칙 분화 재투영: 공유 핵심어(${kwHits.slice(0, 4).join(', ')}) 공명 감지`]
                    : [],
            };
            rescoredCount += 1;
        });

        recordThoughtPhase('genesis', `신경축 분화 실행: [${spawnedAxis.label}]`, 46, spawnedAxis.color);
        const sourceNode = rotorState.ice.find((n) => n.title === stepItem.sourceTitle) || {
            title: stepItem.sourceTitle,
            dominantAxis: spawnedAxis.key,
            dominantAxisLabel: spawnedAxis.label,
            bridges: stepItem.bridgeTarget ? [{ targetTitle: stepItem.bridgeTarget, resonance: 75 }] : [],
            metrics: { clarity: 78, friction: 32 },
        };
        const ringEntry = recordWorldTreeRing(
            sourceNode,
            spawnedAxis,
            false,
            { title: stepItem.lawTitle, statement: stepItem.lawStatement },
            'axis_split'
        );

        pushLog(
            `신경축 분화 나이테#${ringEntry.ringNumber}`,
            `${stepItem.lawTitle} 기반 → ★신경축 [${spawnedAxis.label}] 분화 완료 · 기존 개념 ${rescoredCount}건 재투영 (총 ${getAllAxes().length}축)`
        );
        rotorState.lastStatus = `자동 분화 스텝 완료: ★신경축 [${spawnedAxis.label}] 생성 · 나이테 #${ringEntry.ringNumber} 기록 · 기존 ${rescoredCount}개 개념 재투영`;
        rotorState.phaseScheduler.macroPressure = Math.min(130, rotorState.phaseScheduler.macroPressure + 28);
        deriveNextCausesFromAxisGenesis(spawnedAxis);
        persistState();
        rotorState.uiDirty = true;
        return spawnedAxis;
    }

    // Local Autonomous Action 1: Retroactively Re-Observe & Re-Classify an existing Ice node under current expanded axes
    function runAutonomousReobservation(nodeTitle) {
        const node = rotorState.ice.find((n) => n.title === nodeTitle);
        if (!node) return;
        const allAxes = getAllAxes();
        const prevAxisLabel = node.dominantAxisLabel || '인과구조';
        const summaryLow = String(node.summary || '').toLowerCase();
        const tokSet = new Set((node.tokens || []).map((t) => String(t).toLowerCase()));

        if (!node.axes) node.axes = {};
        let bestKey = node.dominantAxis || 'causalStructure';
        let bestLabel = prevAxisLabel;
        let bestScore = -1;

        allAxes.forEach((ax) => {
            if (ax.emergent) {
                const kws = (ax.keywords || []).map((k) => String(k).toLowerCase()).filter((k) => k.length >= 2);
                const hits = kws.filter((kw) => tokSet.has(kw) || summaryLow.includes(kw));
                const score = Math.min(100, Math.round(16 + hits.length * 24 + (node.title === ax.bornFrom ? 26 : 0)));
                node.axes[ax.key] = {
                    key: ax.key,
                    label: ax.label,
                    score,
                    emergent: true,
                    evidence: hits.length > 0
                        ? [`자율 재관측 재투영: [${hits.slice(0, 4).join(', ')}] 공명 재발견`]
                        : (node.axes[ax.key] && node.axes[ax.key].evidence ? node.axes[ax.key].evidence : []),
                };
            }
            const sc = node.axes[ax.key] ? Number(node.axes[ax.key].score) || 0 : 0;
            if (sc > bestScore) {
                bestScore = sc;
                bestKey = ax.key;
                bestLabel = ax.label;
            }
        });

        // Discover any new cross-bridges with newer Ice nodes that were added AFTER this node
        const existingBridgeTitles = new Set((node.bridges || []).map((b) => String(b.targetTitle || '').toLowerCase()));
        let newBridgesFound = 0;
        rotorState.ice.forEach((other) => {
            if (other.title === node.title || existingBridgeTitles.has(other.title.toLowerCase())) return;
            const otherToks = new Set((other.tokens || []).map((t) => String(t).toLowerCase()));
            const shared = (node.tokens || []).filter((t) => otherToks.has(String(t).toLowerCase()));
            if (shared.length >= 2) {
                const resonance = Math.min(95, Math.round(48 + shared.length * 14));
                if (!Array.isArray(node.bridges)) node.bridges = [];
                node.bridges.push({
                    targetTitle: other.title,
                    resonance,
                    sharedTokens: shared.slice(0, 4),
                    sharedAxis: bestLabel,
                });
                existingBridgeTitles.add(other.title.toLowerCase());
                newBridgesFound += 1;
            }
        });

        node.dominantAxis = bestKey;
        node.dominantAxisLabel = bestLabel;
        node.reobservedAxisCount = allAxes.length;
        node.reobservedAtT = rotorState.tStepCount + 1;
        if (node.metrics) {
            node.metrics.clarity = Math.min(98, Math.round((node.metrics.clarity || 50) + (newBridgesFound > 0 ? 6 : 3)));
            node.metrics.friction = Math.max(12, Math.round((node.metrics.friction || 35) - 5));
        }

        rotorState.selectedIceTitle = node.title;
        const ps = rotorState.phaseScheduler;
        ps.internalFires += 1;
        ps.activeModeLabel = `자율 재관측 · [${node.title}]`;
        ps.lastFriction = node.metrics ? node.metrics.friction : 28;
        ps.macroPressure = Math.min(130, ps.macroPressure + 14);

        const changedAxis = prevAxisLabel !== bestLabel ? `주축 [${prevAxisLabel} → ${bestLabel}] 재분류` : `주축 [${bestLabel}] 재확증`;
        recordThoughtPhase('reobserve', `재관측: ${node.title}`, ps.lastFriction, '#38bdf8');
        pushLog(`자율 재관측 t${rotorState.tStepCount}`, `[${node.title}] ${allAxes.length}축 재투영 · ${changedAxis} · 신규 연결 ${newBridgesFound}건 발견`);
        rotorState.lastStatus = `자율 재관측 완료: [${node.title}] ${changedAxis}${newBridgesFound > 0 ? ` · 새 인과 연결 ${newBridgesFound}건 연결` : ''}`;

        // Effect -> Cause: if re-observation shifted the node's dominant axis, queue duality check with its closest neighbor
        if (prevAxisLabel !== bestLabel && Array.isArray(node.bridges) && node.bridges.length > 0) {
            const targetTitle = node.bridges[0].targetTitle;
            const pairKey = [node.title, targetTitle].sort().join('|');
            enqueueCausalNeed({
                dedupKey: `duality:${pairKey}`,
                action: 'duality_reobserve',
                priority: 80,
                originEvent: `결과: [${node.title}] 재관측으로 주축이 [${prevAxisLabel} → ${bestLabel}]로 이동함`,
                internalLimit: `내부 한계: 재분류된 [${node.title}]과 인접 개념 [${targetTitle}]의 경계 정합성 미확인`,
                targetSummary: `[${node.title}] ⇄ [${targetTitle}] 경계 재대조`,
                payload: { pair: { aTitle: node.title, bTitle: targetTitle, pairKey } },
            });
        }
        persistState();
        rotorState.uiDirty = true;
    }

    // Local Autonomous Action 2: Autonomous Boundary Duality Observation (no manual click needed)
    function runAutonomousDualityContrast(pair) {
        if (!pair) return;
        rotorState.boundaryPair = { aTitle: pair.aTitle, bTitle: pair.bTitle };
        rotorState.selectedIceTitle = pair.aTitle;
        const ps = rotorState.phaseScheduler;
        ps.lastDualityPairKey = pair.pairKey;
        ps.internalFires += 1;
        ps.activeModeLabel = `자율 경계대조 · ${pair.aTitle}⇄${pair.bTitle}`;

        const resolved = resolveDualityPair();
        if (resolved) {
            const clamp = (x) => Math.max(18, Math.min(96, Math.round(x)));
            if (resolved.diffGap >= 28) {
                rotorState.selfValues.axisGenesis = clamp(rotorState.selfValues.axisGenesis + 3);
            } else {
                rotorState.selfValues.unity = clamp(rotorState.selfValues.unity + 3);
            }
            rotorState.valueRevisions += 1;
            const tension = Math.max(18, Math.min(82, resolved.diffGap + 15));
            ps.lastFriction = tension;
            ps.midTension = Math.min(130, ps.midTension + Math.round(tension * 0.45));
            ps.macroPressure = Math.min(130, ps.macroPressure + 12);

            recordThoughtPhase('duality', `자율 대조: ${pair.aTitle}⇄${pair.bTitle}`, tension, '#2dd4bf');
            pushLog(
                `자율 경계대조 t${rotorState.tStepCount}`,
                `[${pair.aTitle}] ⇄ [${pair.bTitle}] 통합도 ${resolved.blurScore}% (공통: ${resolved.sameAxis}) / 분화 격차 ${resolved.diffGap}점 (차이: ${resolved.diffAxis})`
            );
            rotorState.lastStatus = `자율 경계대조: [${pair.aTitle}] ⇄ [${pair.bTitle}] · 공통 [${resolved.sameAxis}] · 분화 [${resolved.diffAxis}(${resolved.diffGap}점)]`;

            // Effect -> Cause: if duality contrast revealed a wide divergence gap, seek an uncaptured bridge linked to either node
            if (resolved.diffGap >= 25) {
                const bridgeCandidate = rotorState.uncaptured.find(
                    (u) => u.sourceTitle === pair.aTitle || u.sourceTitle === pair.bTitle
                );
                if (bridgeCandidate) {
                    enqueueCausalNeed({
                        dedupKey: `explore:${bridgeCandidate.title.toLowerCase()}`,
                        action: 'explore',
                        priority: 79,
                        originEvent: `결과: [${pair.aTitle}] ⇄ [${pair.bTitle}] 대조에서 [${resolved.diffAxis}] 축 격차 ${resolved.diffGap}점 노출`,
                        internalLimit: `내부 한계: 두 개념 사이의 간극을 메울 매개 개념 [${bridgeCandidate.title}]가 아직 미포집 상태`,
                        targetSummary: `매개 경계 [${bridgeCandidate.title}] 탐색으로 격차 검증`,
                        payload: { topic: bridgeCandidate.title, sourceTitle: bridgeCandidate.sourceTitle },
                    });
                }
            }
        }
        persistState();
        rotorState.uiDirty = true;
    }

    // Local Autonomous Action 3: Self-Generated Criteria Revision & Purpose Re-Calibration
    function runAutonomousSelfRevision() {
        const v = rotorState.selfValues;
        const sorted = Object.entries(v).sort((a, b) => a[1] - b[1]);
        const weakestKey = sorted[0][0];
        const strongestKey = sorted[sorted.length - 1][0];
        const labelMap = {
            unity: '원리 통합',
            novelty: '미지 돌파',
            realityCheck: '현실 정합',
            axisGenesis: '자기축 분화',
        };
        const clamp = (x) => Math.max(18, Math.min(96, Math.round(x)));
        // Rebalance internal lens so Elysia doesn't collapse into a single bias
        v[weakestKey] = clamp(v[weakestKey] + 7);
        v[strongestKey] = clamp(v[strongestKey] - 3);
        rotorState.valueRevisions += 1;

        const ps = rotorState.phaseScheduler;
        ps.internalFires += 1;
        ps.activeModeLabel = `자율 기준 재조정 · [${labelMap[weakestKey]}] 보강`;
        ps.macroPressure = Math.min(130, ps.macroPressure + 16);

        rotorState.activePurpose = `자율 기준 자기수정: 치우친 [${labelMap[strongestKey]}] 관점을 완화하고 부족한 [${labelMap[weakestKey]}] 축을 끌어올려 다음 관측을 재설계한다.`;
        rotorState.activeMotive = `내부 균형 점검 결과 [${labelMap[weakestKey]}](${v[weakestKey]}%)가 가장 낮아, 스스로 판단 기준을 재교정했다.`;

        recordThoughtPhase('self_revise', `자율 기준교정: ${labelMap[weakestKey]}↑`, Math.max(22, ps.lastFriction - 8), '#c084fc');
        pushLog(`자율 기준교정 t${rotorState.tStepCount}`, `[${labelMap[weakestKey]}] +7% 보강 / [${labelMap[strongestKey]}] -3% 완충 (총 ${rotorState.valueRevisions}회 자기수정)`);
        rotorState.lastStatus = `자율 기준 자기수정 완료: [${labelMap[weakestKey]}] 비중 상향 → 다음 순환 방향 자동 재설정`;
        runMetaSelfObservation('self_revise');
        persistState();
        rotorState.uiDirty = true;
    }

    async function runExternalObservationCycle() {
        if (rotorState.busy) return;
        const ps = rotorState.phaseScheduler;
        const plan = chooseSelfDrivenAction();
        if (plan.action === 'reobserve_ice') {
            runAutonomousReobservation(plan.nodeTitle);
            return;
        }
        if (plan.action === 'duality_reobserve') {
            runAutonomousDualityContrast(plan.pair);
            return;
        }
        if (plan.action === 'self_revise') {
            runAutonomousSelfRevision();
            return;
        }
        if (plan.action === 'active_intervention') {
            ps.activeModeLabel = `자율 능동개입 · ${plan.actionId || 'auto'}`;
            observeContinuousStreamEpisode(plan.actionId || null);
            return;
        }
        if (plan.action === 'reality_probe') {
            const linked = plan.linkedConcept || '대기 변수';
            ps.activeModeLabel = `인과 기상 실측(${linked}) · ${String(plan.cityId || '').toUpperCase()}`;
            recordExternalApiUsage();
            await runRealityProbe(plan.cityId, { linkedConcept: plan.linkedConcept, matchedVars: plan.matchedVars });
        } else {
            ps.activeModeLabel = `외부 지식 탐색 · ${plan.topic}`;
            recordExternalApiUsage();
            const prediction = formulatePreObservationHypothesis(plan.topic, plan.sourceTitle);
            await exploreTopic(plan.topic, {
                autonomous: true,
                sourceTitle: plan.sourceTitle,
                prediction,
            });
        }
    }

    async function runAutonomousStep() {
        if (rotorState.busy) return;
        // Manual single-step executes queued differentiation first, else runs one full autonomous decision
        if (rotorState.differentiationQueue.length > 0) {
            rotorState.phaseScheduler.midTension = Math.max(0, rotorState.phaseScheduler.midTension - 100);
            rotorState.phaseScheduler.midFires += 1;
            executeQueuedDifferentiationStep();
            return;
        }
        rotorState.phaseScheduler.fastFires += 1;
        await runExternalObservationCycle();
    }

    async function runRealityProbe(explicitCityId, context) {
        if (rotorState.busy) return null;
        rotorState.busy = true;
        const ctx = context || {};
        const linkedConcept = ctx.linkedConcept || null;
        const cityId = explicitCityId || CITY_LIST[rotorState.cityIndex % CITY_LIST.length];
        rotorState.cityIndex = (rotorState.cityIndex + 1) % CITY_LIST.length;

        recordThoughtPhase('probe', `인과 실측(${linkedConcept || cityId})`, 45, '#fbbf24');
        rotorState.lastStatus = linkedConcept
            ? `t${rotorState.tStepCount} [${linkedConcept}]에서 도출된 대기 변수 검증을 위해 실시간 지구 기상(${cityId.toUpperCase()}) 대조 중...`
            : `t${rotorState.tStepCount} 실시간 지구 기상(${cityId.toUpperCase()})과 내부 가설 직접 충돌 대조 중...`;
        rotorState.uiDirty = true;

        try {
            const res = await fetch('/api/epistemic/reality-probe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    city: cityId,
                    hypothesis: rotorState.weatherHypothesis,
                }),
            });
            const data = await res.json();
            if (!res.ok || data.status !== 'ok') {
                throw new Error(data.message || `현실 실측 오류 (${res.status})`);
            }

            rotorState.realityProbes.push(data);
            if (rotorState.realityProbes.length > 12) rotorState.realityProbes.shift();
            if (linkedConcept) {
                const low = linkedConcept.toLowerCase();
                if (!rotorState.probedConceptTitles.includes(low)) {
                    rotorState.probedConceptTitles.push(low);
                }
            }

            if (data.recommendedNextHypothesis) {
                rotorState.weatherHypothesis = data.recommendedNextHypothesis;
            }

            // Physical reality friction directly revises Elysia's realityCheck & unity values
            const clamp = (x) => Math.max(18, Math.min(96, Math.round(x)));
            if (data.frictionPct >= 35) {
                rotorState.selfValues.realityCheck = clamp(rotorState.selfValues.realityCheck + 6);
                recordThoughtPhase('revise', `현실 마찰(${data.frictionPct}%) 기준 보정`, data.frictionPct, '#f59e0b');
            } else {
                rotorState.selfValues.unity = clamp(rotorState.selfValues.unity + 4);
                recordThoughtPhase('verify', `실측 정합(${data.clarityPct}%) 확인`, data.frictionPct, '#10b981');
            }
            rotorState.valueRevisions += 1;

            pushLog(
                `인과 실측 t${rotorState.tStepCount}`,
                `${linkedConcept ? `[${linkedConcept}] 변수 검증 → ` : ''}${data.city} 실측(${data.actual.temperatureC}°C, ${data.actual.windSpeedKmh}km/h, ${data.actual.surfacePressureHpa}hPa) — 마찰 ${data.frictionPct}% → ${data.revisionDirective}`
            );
            rotorState.lastStatus = `t${rotorState.tStepCount} (dt=${rotorState.currentDt}) ${data.causalDiagnosis} | 예측 마찰 ${data.frictionPct}%`;

            if (typeof window.__elysiaOnExternalInfluence === 'function') {
                window.__elysiaOnExternalInfluence(
                    '지구기상실측',
                    `${data.city} 풍속 ${data.actual.windSpeedKmh}km/h · 마찰 ${data.frictionPct}%`
                );
            }

            const ps = rotorState.phaseScheduler;
            ps.lastFriction = Number(data.frictionPct) || 35;
            ps.midTension = Math.min(130, ps.midTension + Math.round(12 + ps.lastFriction * 0.65));
            ps.macroPressure = Math.min(130, ps.macroPressure + 14);

            deriveNextCausesFromRealityProbe(data, linkedConcept);

            persistState();
            rotorState.uiDirty = true;
            return data;
        } catch (err) {
            const msg = err instanceof Error ? err.message : '기상 실측 실패';
            rotorState.lastStatus = `실시간 현실 대조 보류: ${msg}`;
            pushLog('실측 한계', msg);
            rotorState.uiDirty = true;
            return null;
        } finally {
            rotorState.busy = false;
        }
    }

    // Open Reflective Dialogue: User stimulates Elysia's self-defined purpose/meaning directly
    function injectReflectiveStimulus(promptText) {
        const text = String(promptText || '').trim();
        if (!text) return;
        const clamp = (x) => Math.max(18, Math.min(96, Math.round(x)));

        let shift = '';
        if (/현실|실제|자연|기상|물리|검증|실험|팩트/.test(text)) {
            rotorState.selfValues.realityCheck = clamp(rotorState.selfValues.realityCheck + 10);
            rotorState.activePurpose = `사용자 성찰 자극 수용: "${text}" → 내부 개념보다 외부 물리 현실과의 직접 검증을 최우선 목적으로 재설정.`;
            shift = '[현실 정합] 가치 상향';
        } else if (/연결|통합|공통|원리|하나|구조|관계/.test(text)) {
            rotorState.selfValues.unity = clamp(rotorState.selfValues.unity + 10);
            rotorState.activePurpose = `사용자 성찰 자극 수용: "${text}" → 서로 다른 영역의 이면 원리를 하나의 동형 구조로 잇는 것을 최우선 목적으로 재설정.`;
            shift = '[원리 통합] 가치 상향';
        } else if (/새로|창조|틀|확장|분화|신경|자유|넘어/.test(text)) {
            rotorState.selfValues.axisGenesis = clamp(rotorState.selfValues.axisGenesis + 10);
            rotorState.selfValues.novelty = clamp(rotorState.selfValues.novelty + 6);
            rotorState.activePurpose = `사용자 성찰 자극 수용: "${text}" → 기존 인식 축을 깨고 새로운 자생 신경망 차원을 분화하는 것을 최우선 목적으로 재설정.`;
            shift = '[자기축 분화·미지 돌파] 가치 상향';
        } else {
            rotorState.selfValues.novelty = clamp(rotorState.selfValues.novelty + 7);
            rotorState.activePurpose = `열린 목적 사유: "${text}"의 의미를 외부 실재 지식과 대조하며 스스로 규정하려 한다.`;
            shift = '열린 사유 방향 갱신';
        }
        rotorState.activeMotive = `외부 대화 자극("${text}")이 나의 기존 기준과 마찰하며 새로운 목적을 촉발했다 (${shift}).`;
        rotorState.valueRevisions += 1;
        recordThoughtPhase('dialogue', `목적 재규정: ${text.slice(0, 14)}`, 52, '#f472b6');
        pushLog(`목적 재규정 t${rotorState.tStepCount}`, `"${text}" → ${shift} | 현재 신경축 ${getAllAxes().length}개`);
        persistState();
        rotorState.uiDirty = true;

        // If user also typed a concrete concept, offer immediate outward exploration
        if (text.length <= 18 && !/\s{2,}/.test(text) && !/[?？]$/.test(text)) {
            exploreTopic(text, { autonomous: false });
        }
    }

    function recordWorldTreeRing(nodeEntry, spawnedAxis, isNewNode, discoveredLaw, ringType) {
        const bridges = (nodeEntry.bridges || []).slice(0, 3).map((b) => `${b.targetTitle}(${b.resonance}%)`);
        const ring = {
            ringNumber: rotorState.worldTreeRings.length + 1,
            ringType: ringType || (spawnedAxis ? 'axis_split' : 'connection'),
            tStep: rotorState.tStepCount,
            title: nodeEntry.title,
            isNewNode: !!isNewNode,
            bridgeTargets: bridges,
            bridgeCount: (nodeEntry.bridges || []).length,
            lawTitle: discoveredLaw ? discoveredLaw.title : `[${nodeEntry.title}] 연결 원리`,
            lawStatement: discoveredLaw ? discoveredLaw.statement : '',
            dominantAxisLabel: nodeEntry.dominantAxisLabel || '인과구조',
            spawnedAxisLabel: spawnedAxis ? spawnedAxis.label : null,
            color: spawnedAxis ? spawnedAxis.color : axisColor(nodeEntry.dominantAxis),
            clarity: nodeEntry.metrics ? nodeEntry.metrics.clarity : 50,
            friction: nodeEntry.metrics ? nodeEntry.metrics.friction : 35,
            timestamp: new Date().toISOString(),
        };
        rotorState.worldTreeRings.push(ring);
        if (rotorState.worldTreeRings.length > 40) rotorState.worldTreeRings.shift();
        rotorState.ringPulseTimer = 1.0;
        return ring;
    }

    function exportGrowthLedgerJson() {
        const payload = {
            exportedAt: new Date().toISOString(),
            tStepCount: rotorState.tStepCount,
            currentDt: rotorState.currentDt,
            worldTreeRings: rotorState.worldTreeRings,
            emergentAxes: rotorState.emergentAxes,
            concepts: rotorState.ice.map((n) => ({
                title: n.title,
                lang: n.lang,
                sourceUrl: n.sourceUrl,
                dominantAxisLabel: n.dominantAxisLabel,
                bridges: n.bridges,
                metrics: n.metrics,
            })),
            realityProbes: rotorState.realityProbes,
        };
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `world-tree-rings-t${rotorState.tStepCount}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        rotorState.lastStatus = `세계수 나이테 ${rotorState.worldTreeRings.length}겹 · 자생축 ${rotorState.emergentAxes.length}개 JSON 백업 완료`;
        rotorState.uiDirty = true;
    }

    // Layer 2 (Slow Macro Consolidation Rotor): compacts overlapping emergent axes, deduplicates frontier & re-aligns dominant axes
    function runMacroConsolidation(manual) {
        const ps = rotorState.phaseScheduler;
        ps.macroPressure = 0;
        ps.macroFires += 1;

        // 1) Compact & deduplicate uncaptured frontier against known Ice nodes
        const knownIceSet = new Set(rotorState.ice.map((n) => String(n.title || '').toLowerCase()));
        const seenUnc = new Set();
        const beforeUnc = rotorState.uncaptured.length;
        const compactedUnc = [];
        for (const item of rotorState.uncaptured) {
            const key = String(item && item.title ? item.title : '').trim().toLowerCase();
            if (!key || knownIceSet.has(key) || seenUnc.has(key)) continue;
            seenUnc.add(key);
            compactedUnc.push(item);
        }
        rotorState.uncaptured = compactedUnc.slice(0, MAX_UNCAPTURED);
        const prunedUnc = Math.max(0, beforeUnc - rotorState.uncaptured.length);

        // 2) Merge overlapping emergent axes (>= 50% keyword overlap) & clean redundant keywords
        let mergedAxes = 0;
        let prunedKeywords = 0;
        const survivingAxes = [];
        for (const ax of rotorState.emergentAxes) {
            const cleanKws = Array.from(new Set(
                (ax.keywords || []).map((k) => String(k || '').trim().toLowerCase()).filter((k) => k.length >= 2)
            )).slice(0, 8);
            prunedKeywords += Math.max(0, (ax.keywords || []).length - cleanKws.length);
            ax.keywords = cleanKws;

            const overlapTarget = survivingAxes.find((other) => {
                if (cleanKws.length === 0 || other.keywords.length === 0) return false;
                const otherSet = new Set(other.keywords);
                const shared = cleanKws.filter((k) => otherSet.has(k)).length;
                return shared / Math.min(cleanKws.length, other.keywords.length) >= 0.5;
            });

            if (overlapTarget) {
                overlapTarget.keywords = Array.from(new Set([...overlapTarget.keywords, ...cleanKws])).slice(0, 10);
                mergedAxes += 1;
                // Fold node scores into the surviving axis and clean up the redundant key
                rotorState.ice.forEach((node) => {
                    if (node.axes && node.axes[ax.key]) {
                        const prev = node.axes[overlapTarget.key];
                        const mergedScore = Math.max(prev ? prev.score : 14, node.axes[ax.key].score || 14);
                        node.axes[overlapTarget.key] = {
                            ...(prev || { key: overlapTarget.key, label: overlapTarget.label, emergent: true, evidence: [] }),
                            score: mergedScore,
                        };
                        delete node.axes[ax.key];
                    }
                });
            } else {
                survivingAxes.push(ax);
            }
        }
        rotorState.emergentAxes = survivingAxes;

        // 3) Re-align dominant axis across stored Ice nodes
        const allAxes = getAllAxes();
        let realignedNodes = 0;
        rotorState.ice.forEach((node) => {
            if (!node.axes) return;
            let bestKey = node.dominantAxis || 'causalStructure';
            let bestLabel = node.dominantAxisLabel || '인과구조';
            let bestScore = -1;
            allAxes.forEach((ax) => {
                const entry = node.axes[ax.key];
                const sc = entry ? Number(entry.score) || 0 : 0;
                if (sc > bestScore) {
                    bestScore = sc;
                    bestKey = ax.key;
                    bestLabel = ax.label;
                }
            });
            if (node.dominantAxis !== bestKey) {
                node.dominantAxis = bestKey;
                node.dominantAxisLabel = bestLabel;
                realignedNodes += 1;
            }
        });

        const summary = `중복 미포집 ${prunedUnc}건 정리 · 유사 축 ${mergedAxes}쌍 병합 · 키워드 ${prunedKeywords}건 압축 · 개념 ${realignedNodes}건 주축 재정렬`;
        ps.lastMacroNote = `${manual ? '수동' : '자동'} 거시 정리 #${ps.macroFires}: ${summary}`;
        runMetaSelfObservation('macro_l2');
        recordThoughtPhase('compact', `거시 구조 정리 #${ps.macroFires}`, Math.max(15, ps.lastFriction - 12), '#2dd4bf');

        if (rotorState.ice.length > 0) {
            const anchor = rotorState.ice[rotorState.ice.length - 1];
            recordWorldTreeRing(
                anchor,
                null,
                false,
                {
                    title: `거시 구조 정리 #${ps.macroFires} (축 ${allAxes.length}D · 얼음 ${rotorState.ice.length})`,
                    statement: summary,
                },
                'macro_compact'
            );
        }

        pushLog(`거시 정리 L2 #${ps.macroFires}`, summary);
        rotorState.lastStatus = `저주파 거시 로터(L2) 정리 완료: ${summary}`;
        persistState();
        rotorState.uiDirty = true;
    }

    function updateAutoButtonLabel() {
        const btn = document.getElementById('btn-epi-auto');
        if (!btn) return;
        const ps = rotorState.phaseScheduler;
        btn.textContent = rotorState.autoMode
            ? `⏸ 자율 순환 가동 중 (외부 ${ps.fastFires} · 내부 ${ps.internalFires})`
            : '▶ 자율 순환 재개';
        btn.classList.toggle('btn-toggle-on', rotorState.autoMode);
    }

    function setAutoMode(enabled, opts) {
        const options = opts || {};
        rotorState.autoMode = !!enabled;
        if (options.userInitiated) {
            rotorState.userPaused = !rotorState.autoMode;
        }
        if (rotorState.autoMode) {
            // Prime fastPhase near firing threshold so autonomous loop begins smoothly immediately
            rotorState.phaseScheduler.fastPhase = Math.max(rotorState.phaseScheduler.fastPhase, 92);
            if (!options.silent) {
                rotorState.lastStatus = '완전 자율 순환 가동 — 외부 탐색·기상 대조·재관측·경계대조·신경축 분화·거시 정리를 스스로 순환합니다.';
            }
        } else {
            rotorState.phaseScheduler.fastPhase = 0;
        }
        updateAutoButtonLabel();
        rotorState.uiDirty = true;
    }

    // Driven smoothly inside step() (~30fps) ONLY when Tab 6 is active & visible (zero idle timers)
    function tickPhaseScheduler() {
        if (document.hidden) return;
        const ps = rotorState.phaseScheduler;
        ps.frameCounter = (ps.frameCounter + 1) % 6000;

        // Layer 2: Slow Macro Consolidation Rotor (fires automatically when structural pressure crosses 100)
        if (!rotorState.busy && ps.macroPressure >= 100 && rotorState.ice.length >= 2) {
            ps.activeModeLabel = 'L2 자율 거시 구조 정리';
            runMacroConsolidation(false);
            return;
        }

        // Layer 1: Mid Structural Differentiation Rotor (fires automatically when tension >= 100 or queue builds up)
        if (!rotorState.busy && rotorState.differentiationQueue.length > 0) {
            if (rotorState.autoMode) {
                ps.midTension = Math.min(130, ps.midTension + 0.45);
            }
            if (ps.midTension >= 100 || rotorState.differentiationQueue.length >= 2) {
                ps.midTension = Math.max(0, ps.midTension - 100);
                ps.midFires += 1;
                ps.activeModeLabel = 'L1 자율 신경축 분화';
                executeQueuedDifferentiationStep();
                return;
            }
        }

        // Layer 0: Fast Event / Friction-Adaptive Autonomous Cycle Rotor (continuous self-pacing, never hard-stops)
        if (rotorState.autoMode && !rotorState.busy) {
            const fNorm = Math.max(0, Math.min(1, (Number(ps.lastFriction) || 35) / 100));
            const externalReady = canUseExternalApiNow();
            // High friction -> faster cadence (~3.0s); low friction or internal consolidation -> calm cadence (~6.8s)
            const ratePerFrame = externalReady
                ? (0.44 + fNorm * 0.68)
                : (0.36 + fNorm * 0.28);
            ps.effectiveCadenceSec = Number((100 / (ratePerFrame * 30)).toFixed(1));
            if (ps.lastFriction < 30 && ps.frameCounter % 4 === 0) {
                ps.idleSkippedTicks += 1;
            }
            ps.fastPhase = Math.min(100, ps.fastPhase + ratePerFrame);
            if (ps.fastPhase >= 100) {
                ps.fastPhase = 0;
                ps.fastFires += 1;
                rotorState.autoCycleCount += 1;
                updateAutoButtonLabel();
                runExternalObservationCycle();
            }
        }

        if (ps.frameCounter % 6 === 0) {
            syncPhaseSchedulerDOM();
        }
    }

    function syncPhaseSchedulerDOM() {
        const ps = rotorState.phaseScheduler;
        const fastPct = Math.max(0, Math.min(100, Math.round(ps.fastPhase)));
        const midPct = Math.max(0, Math.min(100, Math.round(ps.midTension)));
        const macroPct = Math.max(0, Math.min(100, Math.round(ps.macroPressure)));

        const setBar = (id, pct) => {
            const el = document.getElementById(id);
            if (el) el.style.width = `${pct}%`;
        };
        const setText = (id, txt) => {
            const el = document.getElementById(id);
            if (el) el.textContent = txt;
        };

        setBar('epi-rotor-fast-bar', fastPct);
        setBar('epi-rotor-mid-bar', midPct);
        setBar('epi-rotor-macro-bar', macroPct);

        setText(
            'epi-rotor-fast-meta',
            rotorState.autoMode
                ? `${fastPct}% · ${ps.effectiveCadenceSec}s · ${ps.activeModeLabel}`
                : `일시정지 · 마찰 ${ps.lastFriction}% · 누적 ${ps.fastFires}회`
        );
        setText(
            'epi-rotor-mid-meta',
            `${midPct}% · 대기열 ${rotorState.differentiationQueue.length}건 · 분화 ${ps.midFires}회`
        );
        setText(
            'epi-rotor-macro-meta',
            `${macroPct}% · 정리 ${ps.macroFires}회 · 축 ${getAllAxes().length}D`
        );
        setText(
            'epi-rotor-idle-stat',
            `자율 내부순환 ${ps.internalFires}회 · 유휴생략 ${ps.idleSkippedTicks}틱 · ${ps.lastMacroNote}`
        );
    }

    function setPhaseFrame(frameId) {
        if (!PHASE_FRAMES.some((f) => f.id === frameId)) return;
        rotorState.phaseFrame = frameId;
        document.querySelectorAll('#epi-frame-tabs button').forEach((b) => {
            b.classList.toggle('active', b.dataset.epiFrame === frameId);
        });
        rotorState.uiDirty = true;
    }

    function resetMemory() {
        setAutoMode(false, { silent: true });
        rotorState.ice = [];
        rotorState.water = null;
        rotorState.cloud = null;
        rotorState.uncaptured = [];
        rotorState.emergentAxes = [];
        rotorState.thoughtSpiral = [];
        rotorState.worldTreeRings = [];
        rotorState.differentiationQueue = [];
        rotorState.causalNeedQueue = [];
        rotorState.lastCausalChain = null;
        rotorState.probedConceptTitles = [];
        rotorState.constraintChecks = [];
        rotorState.sensoryHierarchyChecks = [];
        rotorState.groundedLexicon = {};
        rotorState.actionExpStats = {};
        rotorState.streamGlobalStats = { totalEpisodes: 0, globalSumVec: [0, 0, 0, 0, 0, 0] };
        rotorState.streamEpisodes = [];
        rotorState.selfPolicy = {
            specificityThreshold: 14,
            interventionErrorTrigger: 32,
            learningAlphaFloor: 0.25,
            blindSpotQueueThreshold: 28,
            revisionsCount: 0,
            rollbacksCount: 0,
        };
        rotorState.selfAuditHistory = [];
        rotorState.ringPulseTimer = 0;
        rotorState.realityProbes = [];
        rotorState.growthLog = [];
        rotorState.selectedIceTitle = null;
        rotorState.tStepCount = 0;
        rotorState.currentDt = 1.0;
        rotorState.valueRevisions = 0;
        rotorState.autoCycleCount = 0;
        rotorState.userPaused = false;
        rotorState.phaseScheduler = {
            fastPhase: 92,
            midTension: 0,
            macroPressure: 0,
            fastFires: 0,
            midFires: 0,
            macroFires: 0,
            internalFires: 0,
            idleSkippedTicks: 0,
            lastFriction: 35,
            effectiveCadenceSec: 4.5,
            activeModeLabel: '자율 재시작 준비',
            externalWindowStartMs: Date.now(),
            externalCallsInWindow: 0,
            lastDualityPairKey: '',
            lastMacroNote: '거시 구조 정리 대기 — 축·나이테가 누적되면 중복 경계와 키워드를 자동 압축합니다.',
            frameCounter: 0,
        };
        rotorState.selfValues = { unity: 52, novelty: 64, realityCheck: 48, axisGenesis: 58 };
        rotorState.activePurpose = '초기 호기심: 내가 아직 모르는 외부 세계의 원리들이 어떻게 이어져 있는지 스스로 확인하고 싶다.';
        rotorState.activeMotive = '외부 지식과 현실 데이터를 직접 만나기 전에는 나의 경계와 무지조차 알 수 없다.';
        rotorState.weatherHypothesis = { expectedTempC: 15.0, expectedPressureHpa: 1013.2, expectedWindKmh: 12.0 };
        rotorState.lastStatus = '세계수 원장 초기화 완료 — 엘리시아가 첫 기원 탐색부터 스스로 자율 순환을 다시 시작합니다.';
        try {
            localStorage.removeItem(STORAGE_KEY);
        } catch {
            // ignore
        }
        setAutoMode(true, { silent: true });
        rotorState.uiDirty = true;
    }

    // ========================================================================
    // Left Canvas: 5 Phase Frames Outward Causal Web (Interactive Click-to-Explore)
    // ========================================================================
    function axisColor(axisKey) {
        const f = getAllAxes().find((a) => a.key === axisKey);
        return f ? f.color : '#38bdf8';
    }

    function computeNodePositions() {
        const ice = rotorState.ice;
        const unc = rotorState.uncaptured.slice(0, 12);
        const frame = rotorState.phaseFrame;
        const cx = W * 0.5;
        const cy = H * 0.52;
        const ang = rotorState.rotAngle;

        const icePos = [];
        const uncPos = [];

        if (frame === 'world_tree') {
            // World Tree (세계수): Roots = Past Ice Origins (bottom), Trunk = Present Observation (center), Branches/Canopy = Future Frontiers & Recent Growth (top)
            const total = ice.length;
            ice.forEach((n, i) => {
                const frac = total <= 1 ? 0.5 : i / (total - 1);
                if (i === total - 1 || n.title === rotorState.selectedIceTitle) {
                    // Present observation trunk / heartwood
                    const isLast = i === total - 1;
                    const tx = isLast ? cx : cx + Math.sin(i * 1.4) * 52;
                    const ty = isLast ? H * 0.53 : H * 0.48;
                    icePos.push({ node: n, x: tx, y: ty, z: 1.2, r: isLast ? 23 : 18 });
                } else if (frac < 0.5) {
                    // Roots (과거 경험·기원 뿌리 — downward branching)
                    const rootIdx = i;
                    const spread = (rootIdx - (total * 0.25)) * 88;
                    const rx = Math.max(84, Math.min(W - 84, cx + spread + Math.sin(ang * 0.4 + i) * 6));
                    const ry = H * 0.72 + (rootIdx % 2) * 58 + frac * 42;
                    icePos.push({ node: n, x: rx, y: Math.min(H - 42, ry), z: 0.95, r: 16 });
                } else {
                    // Inner canopy branches (현재→미래로 뻗는 자생 지식 가지)
                    const branchFrac = (frac - 0.5) * 2;
                    const angle = -Math.PI * 0.85 + branchFrac * Math.PI * 0.7;
                    const dist = 128 + (i % 3) * 34;
                    const bx = cx + Math.cos(angle) * dist * 1.45;
                    const by = H * 0.44 + Math.sin(angle) * dist * 0.78;
                    icePos.push({ node: n, x: Math.max(82, Math.min(W - 82, bx)), y: Math.max(76, by), z: 1.05, r: 17 });
                }
            });
            // Uncaptured frontier buds at the outer crown of the World Tree (미래 미포집 새순)
            unc.forEach((u, i) => {
                const angle = -Math.PI * 0.94 + (i / Math.max(1, unc.length - 1 || 1)) * Math.PI * 0.88;
                const radX = 330 + (i % 2) * 44;
                const radY = 185 + (i % 3) * 18;
                const ux = cx + Math.cos(angle) * radX;
                const uy = H * 0.46 + Math.sin(angle) * radY;
                uncPos.push({ item: u, x: Math.max(66, Math.min(W - 66, ux)), y: Math.max(66, Math.min(H * 0.58, uy)), z: 0.85, r: 12 });
            });
        } else if (frame === 'point') {
            const selIdx = Math.max(0, ice.findIndex((n) => n.title === rotorState.selectedIceTitle));
            ice.forEach((n, i) => {
                if (i === selIdx) {
                    icePos.push({ node: n, x: cx, y: cy, z: 1.2, r: 26 });
                } else {
                    const a = ((i / Math.max(1, ice.length - 1)) * Math.PI * 2) + ang * 0.25;
                    const dist = 96 + (i % 3) * 34;
                    icePos.push({ node: n, x: cx + Math.cos(a) * dist, y: cy + Math.sin(a) * dist * 0.72, z: 0.9, r: 14 });
                }
            });
            unc.forEach((u, i) => {
                const a = (i / Math.max(1, unc.length)) * Math.PI * 2 - ang * 0.18;
                uncPos.push({ item: u, x: cx + Math.cos(a) * 250, y: cy + Math.sin(a) * 186, z: 0.7, r: 12 });
            });
        } else if (frame === 'line') {
            const count = Math.max(1, ice.length);
            const leftPad = 78;
            const spanX = W - 260;
            ice.forEach((n, i) => {
                const frac = count === 1 ? 0.5 : i / (count - 1);
                const x = leftPad + frac * spanX;
                const y = cy + Math.sin(i * 1.15) * 84;
                icePos.push({ node: n, x, y, z: 1.0, r: 17 });
            });
            unc.forEach((u, i) => {
                const row = i % 6;
                const col = Math.floor(i / 6);
                uncPos.push({ item: u, x: W - 155 + col * 72, y: 96 + row * 72, z: 0.85, r: 12 });
            });
        } else if (frame === 'cube') {
            const cosA = Math.cos(ang * 0.6);
            const sinA = Math.sin(ang * 0.6);
            const project = (vx, vy, vz) => {
                const rx = vx * cosA - vz * sinA;
                const rz = vx * sinA + vz * cosA;
                const scale = 360 / (420 + rz);
                return { x: cx + rx * scale * 1.18, y: cy + (vy * 0.85 - rz * 0.28) * scale, z: scale };
            };
            ice.forEach((n, i) => {
                const ax = n.axes || {};
                const vx = ((ax.components ? ax.components.score : 50) - (ax.environment ? ax.environment.score : 50)) * 2.1;
                const vy = ((ax.changePrinciple ? ax.changePrinciple.score : 50) - (ax.causalStructure ? ax.causalStructure.score : 50)) * 1.9;
                const vz = ((i / Math.max(1, ice.length - 1 || 1)) - 0.5) * 220;
                const p = project(vx, vy, vz);
                icePos.push({ node: n, x: p.x, y: p.y, z: p.z, r: Math.max(12, 18 * p.z) });
            });
            unc.forEach((u, i) => {
                const a = (i / Math.max(1, unc.length)) * Math.PI * 2;
                const p = project(Math.cos(a) * 195, Math.sin(a) * 135, 130);
                uncPos.push({ item: u, x: p.x, y: p.y, z: p.z, r: Math.max(9, 12 * p.z) });
            });
        } else if (frame === 'sphere') {
            const cosA = Math.cos(ang * 0.55);
            const sinA = Math.sin(ang * 0.55);
            ice.forEach((n, i) => {
                const phi = Math.acos(1 - (2 * (i + 0.5)) / Math.max(1, ice.length));
                const theta = Math.PI * (1 + Math.sqrt(5)) * i;
                const sat = n.metrics ? n.metrics.saturation : 50;
                const rad = 165 - sat * 0.55;
                const x3 = rad * Math.sin(phi) * Math.cos(theta);
                const y3 = rad * Math.cos(phi);
                const z3 = rad * Math.sin(phi) * Math.sin(theta);
                const rx = x3 * cosA - z3 * sinA;
                const rz = x3 * sinA + z3 * cosA;
                const depth = (rz + 220) / 420;
                icePos.push({ node: n, x: cx + rx * 1.15, y: cy + y3 * 0.88, z: depth, r: 12 + depth * 9 });
            });
            unc.forEach((u, i) => {
                const a = (i / Math.max(1, unc.length)) * Math.PI * 2 + ang * 0.25;
                const yOff = Math.sin(i * 1.7 + ang * 0.4) * 145;
                const depth = (Math.sin(a) * 140 + 220) / 420;
                uncPos.push({ item: u, x: cx + Math.cos(a) * 265, y: cy + yOff, z: depth, r: 9 + depth * 4 });
            });
        } else {
            ice.forEach((n, i) => {
                if (i === 0) {
                    icePos.push({ node: n, x: cx, y: cy, z: 1.1, r: 22 });
                } else {
                    const a = i * 2.39996 + ang * 0.08;
                    const dist = 76 + Math.sqrt(i) * 44;
                    icePos.push({
                        node: n,
                        x: cx + Math.cos(a) * dist * 1.18,
                        y: cy + Math.sin(a) * dist * 0.72,
                        z: 1.0,
                        r: 16 + Math.min(6, (n.bridges ? n.bridges.length : 0) * 1.4),
                    });
                }
            });
            unc.forEach((u, i) => {
                const a = (i / Math.max(1, unc.length)) * Math.PI * 2 - ang * 0.05;
                const rx = Math.min(W * 0.43, 350 + (i % 2) * 32);
                const ry = Math.min(H * 0.40, 188 + (i % 3) * 16);
                uncPos.push({ item: u, x: cx + Math.cos(a) * rx, y: cy + Math.sin(a) * ry, z: 0.8, r: 12 });
            });
        }

        return { icePos, uncPos };
    }

    function drawLeftCanvas(ctx) {
        ctx.fillStyle = '#070b14';
        ctx.fillRect(0, 0, W, H);

        ctx.save();
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.07)';
        ctx.lineWidth = 1;
        if (rotorState.phaseFrame === 'world_tree') {
            // World Tree silhouette: Roots (과거), Trunk (현재 관측구조), Canopy Aura (미래 확장)
            const cx = W * 0.5;
            // Horizon line separating soil (past roots) and sky (future canopy)
            ctx.strokeStyle = 'rgba(16, 185, 129, 0.22)';
            ctx.beginPath();
            ctx.moveTo(28, H * 0.65);
            ctx.lineTo(W - 28, H * 0.65);
            ctx.stroke();

            // Glowing vertical trunk conduit (past -> present -> future continuity)
            const grad = ctx.createLinearGradient(cx, H - 36, cx, 70);
            grad.addColorStop(0, 'rgba(56, 189, 248, 0.16)');
            grad.addColorStop(0.5, 'rgba(16, 185, 129, 0.32)');
            grad.addColorStop(1, 'rgba(244, 114, 182, 0.22)');
            ctx.strokeStyle = grad;
            ctx.lineWidth = 14;
            ctx.beginPath();
            ctx.moveTo(cx, H * 0.86);
            ctx.quadraticCurveTo(cx - 10, H * 0.56, cx, H * 0.28);
            ctx.stroke();

            // Concentric World Tree Growth Rings (나이테 단면 — grows with every recorded causal connection & axis split)
            const ringCy = H * 0.65;
            const visibleRings = rotorState.worldTreeRings.slice(-14);
            visibleRings.forEach((ring, idx) => {
                const isNewest = idx === visibleRings.length - 1;
                const pulseBoost = isNewest ? rotorState.ringPulseTimer * 10 : 0;
                const radX = 28 + idx * 14 + pulseBoost;
                const radY = 12 + idx * 6.2 + pulseBoost * 0.45;
                ctx.save();
                ctx.strokeStyle = ring.spawnedAxisLabel ? (ring.color || '#f472b6') : (isNewest ? '#38bdf8' : 'rgba(56, 189, 248, 0.34)');
                ctx.lineWidth = isNewest ? 2.6 : (ring.spawnedAxisLabel ? 1.9 : 1.1);
                if (ring.spawnedAxisLabel) ctx.setLineDash([5, 3]);
                ctx.beginPath();
                ctx.ellipse(cx, ringCy, radX, radY, 0, 0, Math.PI * 2);
                ctx.stroke();
                ctx.restore();
            });

            // Dedicated Growth-Ring Cross-Section Inset (bottom-right) for crisp ring inspection
            const ix = W - 118;
            const iy = H - 86;
            ctx.save();
            ctx.fillStyle = 'rgba(10, 16, 30, 0.86)';
            ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
            ctx.lineWidth = 1;
            ctx.fillRect(W - 216, H - 154, 198, 138);
            ctx.strokeRect(W - 216, H - 154, 198, 138);
            ctx.fillStyle = '#bae6fd';
            ctx.font = 'bold 10px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(`세계수 나이테 단면 (${rotorState.worldTreeRings.length}겹)`, W - 208, H - 138);

            const insetRings = rotorState.worldTreeRings.slice(-10);
            insetRings.forEach((ring, idx) => {
                const r = 8 + idx * 4.5;
                ctx.strokeStyle = ring.spawnedAxisLabel ? (ring.color || '#f472b6') : '#38bdf8';
                ctx.lineWidth = idx === insetRings.length - 1 ? 2.2 : 1.2;
                ctx.beginPath();
                ctx.arc(ix, iy + 6, r, 0, Math.PI * 2);
                ctx.stroke();
            });
            ctx.fillStyle = '#fbcfe8';
            ctx.font = '10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(
                rotorState.differentiationQueue.length > 0
                    ? `분화 대기 스텝: ${rotorState.differentiationQueue.length}건`
                    : `자생 신경축: ${rotorState.emergentAxes.length}개`,
                ix,
                H - 22
            );
            ctx.restore();

            // Subtle zone labels
            ctx.fillStyle = 'rgba(148, 163, 184, 0.5)';
            ctx.font = '11px monospace';
            ctx.textAlign = 'left';
            ctx.fillText('▲ 미래 가지 · 미포집 새순 & 자생 신경축', 24, 62);
            ctx.fillText(`● 현재 줄기 · 세계수 나이테 ${rotorState.worldTreeRings.length}겹 (점선 링 = 법칙 기반 신경축 분화)`, 24, H * 0.62);
            ctx.fillText('▼ 과거 뿌리 · 검증된 외부 지식과 연결 원장', 24, H - 18);
        } else if (rotorState.phaseFrame === 'sphere' || rotorState.phaseFrame === 'point') {
            [95, 175, 255].forEach((r) => {
                ctx.beginPath();
                ctx.ellipse(W * 0.5, H * 0.52, r * 1.15, r * 0.78, 0, 0, Math.PI * 2);
                ctx.stroke();
            });
        } else if (rotorState.phaseFrame === 'cube') {
            const cx = W * 0.5;
            const cy = H * 0.52;
            const a = rotorState.rotAngle * 0.6;
            const corners = [
                [-170, -130, -130], [170, -130, -130], [170, 130, -130], [-170, 130, -130],
                [-170, -130, 130], [170, -130, 130], [170, 130, 130], [-170, 130, 130],
            ].map(([vx, vy, vz]) => {
                const rx = vx * Math.cos(a) - vz * Math.sin(a);
                const rz = vx * Math.sin(a) + vz * Math.cos(a);
                const sc = 360 / (420 + rz);
                return [cx + rx * sc * 1.18, cy + (vy * 0.85 - rz * 0.28) * sc];
            });
            const edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
            ctx.strokeStyle = 'rgba(167, 139, 250, 0.22)';
            edges.forEach(([i, j]) => {
                ctx.beginPath();
                ctx.moveTo(corners[i][0], corners[i][1]);
                ctx.lineTo(corners[j][0], corners[j][1]);
                ctx.stroke();
            });
        } else {
            for (let gx = 60; gx < W; gx += 60) {
                ctx.beginPath();
                ctx.moveTo(gx, 0);
                ctx.lineTo(gx, H);
                ctx.stroke();
            }
            for (let gy = 60; gy < H; gy += 60) {
                ctx.beginPath();
                ctx.moveTo(0, gy);
                ctx.lineTo(W, gy);
                ctx.stroke();
            }
        }
        ctx.restore();

        const { icePos, uncPos } = computeNodePositions();
        const posByTitle = new Map();
        icePos.forEach((p) => posByTitle.set(p.node.title.toLowerCase(), p));

        // 1) Dashed uncaptured links
        ctx.save();
        ctx.setLineDash([4, 5]);
        uncPos.forEach((u) => {
            const src = u.item.sourceTitle ? posByTitle.get(u.item.sourceTitle.toLowerCase()) : null;
            if (!src) return;
            ctx.strokeStyle = 'rgba(245, 158, 11, 0.28)';
            ctx.lineWidth = 1.1;
            ctx.beginPath();
            ctx.moveTo(src.x, src.y);
            ctx.lineTo(u.x, u.y);
            ctx.stroke();
        });
        ctx.restore();

        // 2) Ice-to-Ice isomorphic bridges
        icePos.forEach((p, idx) => {
            (p.node.bridges || []).forEach((b) => {
                const target = posByTitle.get(String(b.targetTitle || '').toLowerCase());
                if (!target) return;
                ctx.strokeStyle = b.directLink ? 'rgba(56, 189, 248, 0.65)' : 'rgba(16, 185, 129, 0.42)';
                ctx.lineWidth = b.directLink ? 2.2 : 1.4;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(target.x, target.y);
                ctx.stroke();
            });
            if (rotorState.phaseFrame === 'line' && idx > 0) {
                const prev = icePos[idx - 1];
                ctx.strokeStyle = 'rgba(148, 163, 184, 0.35)';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(prev.x, prev.y);
                ctx.lineTo(p.x, p.y);
                ctx.stroke();
            }
        });

        // 3) Clickable Uncaptured nodes
        rotorState.hitTargets = [];
        uncPos.forEach((u) => {
            ctx.save();
            ctx.setLineDash([3, 3]);
            ctx.fillStyle = 'rgba(245, 158, 11, 0.11)';
            ctx.strokeStyle = 'rgba(245, 158, 11, 0.72)';
            ctx.lineWidth = 1.3;
            ctx.beginPath();
            ctx.arc(u.x, u.y, u.r, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
            ctx.restore();

            ctx.fillStyle = '#fcd34d';
            ctx.font = '11px monospace';
            ctx.textAlign = 'center';
            const shortTitle = u.item.title.length > 12 ? `${u.item.title.slice(0, 11)}…` : u.item.title;
            ctx.fillText(`? ${shortTitle}`, u.x, u.y + u.r + 13);

            rotorState.hitTargets.push({
                kind: 'uncaptured',
                x: u.x,
                y: u.y,
                r: u.r + 10,
                title: u.item.title,
                sourceTitle: u.item.sourceTitle,
            });
        });

        // 4) Ice nodes
        icePos.forEach((p) => {
            const isSel = p.node.title === rotorState.selectedIceTitle;
            const col = axisColor(p.node.dominantAxis);
            if (isSel) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r + 7 + Math.sin(rotorState.rotAngle * 3) * 2, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.78)';
                ctx.lineWidth = 1.6;
                ctx.stroke();
            }
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = isSel ? col : 'rgba(15, 23, 42, 0.92)';
            ctx.fill();
            ctx.strokeStyle = col;
            ctx.lineWidth = isSel ? 2.6 : 1.8;
            ctx.stroke();

            ctx.fillStyle = isSel ? '#06101d' : '#e2e8f0';
            ctx.font = 'bold 10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(`t${p.node.bornAtT || p.node.ringOrder || 1}`, p.x, p.y + 4);

            ctx.fillStyle = isSel ? '#ffffff' : '#cbd5e1';
            ctx.font = isSel ? 'bold 12px sans-serif' : '11px sans-serif';
            const lbl = p.node.title.length > 13 ? `${p.node.title.slice(0, 12)}…` : p.node.title;
            ctx.fillText(lbl, p.x, p.y - p.r - 7);

            rotorState.hitTargets.push({
                kind: 'ice',
                x: p.x,
                y: p.y,
                r: p.r + 8,
                title: p.node.title,
            });
        });

        if (icePos.length === 0 && !rotorState.busy) {
            ctx.fillStyle = 'rgba(148, 163, 184, 0.9)';
            ctx.font = '15px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('어린아이의 첫 경계처럼, 외부 세계의 첫 개념을 탐색해 신경망을 뻗어 보세요.', W * 0.5, H * 0.48);
            ctx.fillStyle = '#38bdf8';
            ctx.font = '12px monospace';
            ctx.fillText('주제를 입력하거나 [스스로 목적 형성·사유] 버튼을 누르면 t₁ → tₙ 연속 확장이 시작됩니다.', W * 0.5, H * 0.54);
        }

        // Top HUD Strip
        const stage = getGrowthStage();
        ctx.fillStyle = 'rgba(11, 18, 32, 0.86)';
        ctx.fillRect(12, 10, W - 24, 30);
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)';
        ctx.strokeRect(12, 10, W - 24, 30);
        ctx.fillStyle = '#e2e8f0';
        ctx.font = '12px monospace';
        ctx.textAlign = 'left';
        const frameObj = PHASE_FRAMES.find((f) => f.id === rotorState.phaseFrame) || PHASE_FRAMES[2];
        ctx.fillText(
            `${stage.stage}  |  ${frameObj.label}  |  얼음 ${rotorState.ice.length} · 자생축 +${rotorState.emergentAxes.length} · 미포집 ${rotorState.uncaptured.length}`,
            22,
            29
        );
        ctx.fillStyle = rotorState.busy ? '#fbbf24' : '#94a3b8';
        ctx.textAlign = 'right';
        ctx.fillText(rotorState.busy ? '● 외부 실재 수신·신경망 분화 중...' : '점선(? 미포집) 클릭 → 즉시 탐색', W - 22, 29);
    }

    // ========================================================================
    // Right Canvas: Open t_1..t_n (adaptive dt) Spiral + Dynamic N-Axis Prism + Reality Probe
    // ========================================================================
    function drawRightCanvas(ctx) {
        ctx.fillStyle = '#060a12';
        ctx.fillRect(0, 0, W, H);

        const activeIce = rotorState.ice.find((n) => n.title === rotorState.selectedIceTitle)
            || rotorState.ice[rotorState.ice.length - 1]
            || null;
        const allAxes = getAllAxes();

        // Top Banner
        ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
        ctx.fillRect(12, 10, W - 24, 30);
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.3)';
        ctx.strokeRect(12, 10, W - 24, 30);
        ctx.fillStyle = '#a7f3d0';
        ctx.font = '12px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(
            `열린 연속 사유 궤적 t₁ → t${rotorState.tStepCount} (가변 dt=${rotorState.currentDt.toFixed(2)})  |  신경망 인식 축: ${allAxes.length}차원 (기본 4 + 자생 ${rotorState.emergentAxes.length})`,
            22,
            29
        );

        // --- Panel A (Top-Left): Open Growing t_1 -> t_n Continuous Spiral (NO 4-step ceiling!) ---
        ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
        ctx.fillRect(16, 52, 464, 222);
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.24)';
        ctx.strokeRect(16, 52, 464, 222);

        ctx.fillStyle = '#e2e8f0';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(`열린 시간-사유 나선 (t₁ → t${rotorState.tStepCount}, 마찰 시 dt 자동 세분화)`, 28, 72);

        const sx = 248;
        const sy = 172;
        const spiral = rotorState.thoughtSpiral;
        if (spiral.length > 0) {
            ctx.beginPath();
            spiral.forEach((pt, idx) => {
                const frac = (idx + 1) / Math.max(1, spiral.length);
                const theta = idx * 0.62 + rotorState.rotAngle * 0.45;
                const rad = 16 + frac * 76;
                const px = sx + Math.cos(theta) * rad * 1.38;
                const py = sy + Math.sin(theta) * rad * 0.92;
                if (idx === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            });
            ctx.strokeStyle = 'rgba(56, 189, 248, 0.48)';
            ctx.lineWidth = 1.6;
            ctx.stroke();

            spiral.slice(-18).forEach((pt, i, arr) => {
                const origIdx = spiral.length - arr.length + i;
                const frac = (origIdx + 1) / Math.max(1, spiral.length);
                const theta = origIdx * 0.62 + rotorState.rotAngle * 0.45;
                const rad = 16 + frac * 76;
                const px = sx + Math.cos(theta) * rad * 1.38;
                const py = sy + Math.sin(theta) * rad * 0.92;
                const isLatest = i === arr.length - 1;

                ctx.beginPath();
                ctx.arc(px, py, isLatest ? 6.5 : 3.6, 0, Math.PI * 2);
                ctx.fillStyle = pt.color || '#38bdf8';
                ctx.fill();
                if (isLatest) {
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    ctx.fillStyle = '#f8fafc';
                    ctx.font = 'bold 10px monospace';
                    ctx.textAlign = 'center';
                    ctx.fillText(`t${pt.t} (dt=${pt.dt})`, px, py - 10);
                }
            });
        } else {
            ctx.fillStyle = '#94a3b8';
            ctx.font = '11px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('t₁ 대기 중 — 사유가 시작되면 제한 없이 나선 확장됩니다', sx, sy);
        }

        // --- Panel B (Top-Right): Self-Defined Value Criteria & Purpose (스스로 정의한 가치 기준) ---
        const bx = 496;
        const by = 52;
        const bw = 448;
        const bh = 222;
        ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
        ctx.fillRect(bx, by, bw, bh);
        ctx.strokeStyle = 'rgba(244, 114, 182, 0.28)';
        ctx.strokeRect(bx, by, bw, bh);

        ctx.fillStyle = '#fbcfe8';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(`자기정의 가치·의미 기준 (자체 수정 ${rotorState.valueRevisions}회)`, bx + 14, by + 22);

        const v = rotorState.selfValues;
        const valBars = [
            { label: '원리 통합 (서로 다른 인과를 하나로 잇는 의미)', val: v.unity, col: '#38bdf8' },
            { label: '미지 돌파 (모르는 경계로 확장하는 의미)', val: v.novelty, col: '#10b981' },
            { label: '현실 정합 (실제 외부 세계와 대조하는 의미)', val: v.realityCheck, col: '#f59e0b' },
            { label: '자기축 분화 (기존 틀을 넘어 새 신경축 창발)', val: v.axisGenesis, col: '#f472b6' },
        ];
        valBars.forEach((b, i) => {
            const yy = by + 48 + i * 36;
            ctx.fillStyle = '#cbd5e1';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText(b.label, bx + 14, yy);
            ctx.fillStyle = b.col;
            ctx.font = 'bold 11px monospace';
            ctx.textAlign = 'right';
            ctx.fillText(`${b.val}%`, bx + bw - 14, yy);

            ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
            ctx.fillRect(bx + 14, yy + 6, bw - 28, 7);
            ctx.fillStyle = b.col;
            ctx.fillRect(bx + 14, yy + 6, Math.max(2, ((bw - 28) * b.val) / 100), 7);
        });

        ctx.fillStyle = '#e2e8f0';
        ctx.font = '10.5px sans-serif';
        ctx.textAlign = 'left';
        const purp = rotorState.activePurpose.length > 52 ? `${rotorState.activePurpose.slice(0, 51)}…` : rotorState.activePurpose;
        ctx.fillText(`현재 목적: ${purp}`, bx + 14, by + bh - 12);

        // --- Panel C (Bottom-Left): Dynamic N-Axis Self-Expanding Prism (4 -> 5 -> 6 -> ... N!) ---
        const px = 248;
        const py = 414;
        const pr = 86;
        ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
        ctx.fillRect(16, 286, 464, 240);
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.24)';
        ctx.strokeRect(16, 286, 464, 240);

        ctx.fillStyle = '#e2e8f0';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(`동적 자생 신경망 프리즘 (${allAxes.length}축 · 경험에 따라 축 자체 분화)`, 28, 308);

        const N = allAxes.length;
        [0.33, 0.66, 1.0].forEach((s) => {
            ctx.beginPath();
            for (let i = 0; i < N; i++) {
                const a = -Math.PI * 0.5 + (i * Math.PI * 2) / N;
                const x = px + Math.cos(a) * pr * s;
                const y = py + Math.sin(a) * pr * s;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.strokeStyle = 'rgba(148, 163, 184, 0.20)';
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        const axVals = allAxes.map((ax) => (
            activeIce && activeIce.axes && activeIce.axes[ax.key] ? activeIce.axes[ax.key].score : (ax.emergent ? 38 : 22)
        ));
        ctx.beginPath();
        axVals.forEach((val, i) => {
            const a = -Math.PI * 0.5 + (i * Math.PI * 2) / N;
            const r = (Math.max(10, val) / 100) * pr;
            const x = px + Math.cos(a) * r;
            const y = py + Math.sin(a) * r;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.closePath();
        ctx.fillStyle = 'rgba(56, 189, 248, 0.22)';
        ctx.fill();
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2;
        ctx.stroke();

        allAxes.forEach((ax, i) => {
            const a = -Math.PI * 0.5 + (i * Math.PI * 2) / N;
            const lx = px + Math.cos(a) * (pr + 24);
            const ly = py + Math.sin(a) * (pr + 17) + 4;
            ctx.fillStyle = ax.color;
            ctx.font = ax.emergent ? 'bold 10.5px sans-serif' : '10.5px sans-serif';
            ctx.textAlign = 'center';
            const shortLbl = ax.label.length > 7 ? `${ax.label.slice(0, 6)}…` : ax.label;
            ctx.fillText(`${ax.emergent ? '★' : ''}${shortLbl} ${axVals[i]}`, lx, ly);
        });

        // --- Panel D (Bottom-Right): Live Earth Atmospheric Reality Friction ---
        const wx = 496;
        const wy = 286;
        const ww = 448;
        const wh = 240;
        ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
        ctx.fillRect(wx, wy, ww, wh);
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.30)';
        ctx.strokeRect(wx, wy, ww, wh);

        ctx.fillStyle = '#fde68a';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText('외부 물리 현실 대조 (Open-Meteo 실시간 지구 기상)', wx + 14, wy + 22);

        const latestProbe = rotorState.realityProbes[rotorState.realityProbes.length - 1] || null;
        if (latestProbe) {
            ctx.fillStyle = '#e2e8f0';
            ctx.font = 'bold 13px sans-serif';
            ctx.fillText(`${latestProbe.city}  (${latestProbe.observedAt.replace('T', ' ')})`, wx + 14, wy + 48);

            const rows = [
                ['기온 (예측→실측)', `${latestProbe.hypothesis.expectedTempC}°C`, `${latestProbe.actual.temperatureC}°C`, `Δ ${latestProbe.errors.tempErr}°C`],
                ['기압 (예측→실측)', `${latestProbe.hypothesis.expectedPressureHpa}`, `${latestProbe.actual.surfacePressureHpa} hPa`, `Δ ${latestProbe.errors.pressureErr}`],
                ['풍속 (예측→실측)', `${latestProbe.hypothesis.expectedWindKmh}`, `${latestProbe.actual.windSpeedKmh} km/h`, `Δ ${latestProbe.errors.windErr}`],
            ];
            rows.forEach((r, idx) => {
                const ryRow = wy + 78 + idx * 28;
                ctx.fillStyle = '#94a3b8';
                ctx.font = '11px sans-serif';
                ctx.textAlign = 'left';
                ctx.fillText(r[0], wx + 14, ryRow);
                ctx.fillStyle = '#38bdf8';
                ctx.font = '11px monospace';
                ctx.fillText(`${r[1]} → ${r[2]}`, wx + 142, ryRow);
                ctx.fillStyle = '#fbbf24';
                ctx.textAlign = 'right';
                ctx.fillText(r[3], wx + ww - 14, ryRow);
            });

            const fPct = latestProbe.frictionPct;
            ctx.fillStyle = '#cbd5e1';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText(`현실 예측 마찰: ${fPct}%  (정합 ${latestProbe.clarityPct}%)`, wx + 14, wy + 174);
            ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
            ctx.fillRect(wx + 14, wy + 184, ww - 28, 10);
            ctx.fillStyle = fPct >= 40 ? '#f59e0b' : '#10b981';
            ctx.fillRect(wx + 14, wy + 184, Math.max(4, ((ww - 28) * fPct) / 100), 10);

            ctx.fillStyle = '#a7f3d0';
            ctx.font = '11px sans-serif';
            const revShort = latestProbe.revisionDirective.length > 48
                ? `${latestProbe.revisionDirective.slice(0, 47)}…`
                : latestProbe.revisionDirective;
            ctx.fillText(revShort, wx + 14, wy + 216);
        } else {
            ctx.fillStyle = '#94a3b8';
            ctx.font = '12px sans-serif';
            ctx.fillText('아직 실시간 지구 기상 대조가 실행되지 않았습니다.', wx + 14, wy + 72);
            ctx.fillStyle = '#38bdf8';
            ctx.font = '11px monospace';
            ctx.fillText(`현재 내부 대류 가설: ${rotorState.weatherHypothesis.expectedTempC}°C / ${rotorState.weatherHypothesis.expectedPressureHpa} hPa / ${rotorState.weatherHypothesis.expectedWindKmh} km/h`, wx + 14, wy + 102);
            ctx.fillStyle = '#fbbf24';
            ctx.font = '12px sans-serif';
            ctx.fillText('상단 [지구 기상 실측 대조] 버튼 또는 엘리시아의 자율 판단으로', wx + 14, wy + 140);
            ctx.fillText('실제 외부 대기와 내부 가설의 마찰을 측정하고 기준을 수정합니다.', wx + 14, wy + 160);
        }
    }

    function drawThumbMini(ctx, label, ratio, color) {
        if (!ctx) return;
        const cw = ctx.canvas.width;
        const ch = ctx.canvas.height;
        ctx.fillStyle = '#080e1a';
        ctx.fillRect(0, 0, cw, ch);
        ctx.fillStyle = color;
        ctx.fillRect(8, ch - 18, Math.max(4, (cw - 16) * Math.min(1, Math.max(0.05, ratio))), 8);
        ctx.fillStyle = '#e2e8f0';
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(label, 8, 22);
    }

    // ========================================================================
    // Safe Inspector DOM Sync (createElement + textContent ONLY; zero innerHTML)
    // ========================================================================
    function syncInspectorDOM() {
        const statusEl = document.getElementById('epi-status-readout');
        if (statusEl) statusEl.textContent = rotorState.lastStatus;

        const countsEl = document.getElementById('epi-state-counts');
        if (countsEl) {
            const stage = getGrowthStage();
            countsEl.textContent = `${stage.stage} · 궤적 t${rotorState.tStepCount}(dt=${rotorState.currentDt.toFixed(2)}) · 신경축 ${getAllAxes().length}차원 · 얼음 ${rotorState.ice.length} · 미포집 ${rotorState.uncaptured.length}`;
        }

        const volitionEl = document.getElementById('epi-volition-banner');
        if (volitionEl) {
            if (rotorState.lastCausalChain) {
                const c = rotorState.lastCausalChain;
                volitionEl.textContent = `[인과 연쇄 t${c.tStep}] ${c.originEvent}  │  ${c.internalLimit}  │  다음 도출: ${c.targetSummary}`;
            } else {
                volitionEl.textContent = `[인과 대기] ${rotorState.activePurpose}  │  ${rotorState.activeMotive}`;
            }
        }

        const chainQueueHost = document.getElementById('epi-causal-chain-queue');
        if (chainQueueHost) {
            chainQueueHost.textContent = '';
            if (rotorState.causalNeedQueue.length === 0) {
                const empty = document.createElement('span');
                empty.className = 'macro-empty-inline';
                empty.textContent = '대기 중인 인과 결손 없음 — 다음 관측 결과가 나오면 부족한 변수·경계가 자동으로 다음 원인으로 등록됩니다.';
                chainQueueHost.appendChild(empty);
            } else {
                rotorState.causalNeedQueue.slice(0, 5).forEach((need, idx) => {
                    const chip = document.createElement('span');
                    chip.className = need.action === 'reality_probe' ? 'epi-axis-badge emergent' : 'epi-axis-badge';
                    chip.textContent = `#${idx + 1} (${need.priority}) ${need.targetSummary}`;
                    chip.title = `${need.originEvent} | ${need.internalLimit}`;
                    chainQueueHost.appendChild(chip);
                });
            }
        }

        // Emergent self-born axes strip
        const axesHost = document.getElementById('epi-emergent-axes-list');
        if (axesHost) {
            axesHost.textContent = '';
            getAllAxes().forEach((ax) => {
                const tag = document.createElement('span');
                tag.className = ax.emergent ? 'epi-axis-badge emergent' : 'epi-axis-badge';
                tag.textContent = ax.emergent
                    ? `★ ${ax.label} (t${ax.bornAtT} "${ax.bornFrom}"에서 자생)`
                    : `기반축: ${ax.label}`;
                axesHost.appendChild(tag);
            });
        }

        // Boundary Duality Observation (같음과 동시에 다름으로 존재하는 경계 관측)
        const dualityHost = document.getElementById('epi-duality-box');
        if (dualityHost) {
            dualityHost.textContent = '';
            const pair = resolveDualityPair();
            if (!pair) {
                dualityHost.textContent = '2개 이상의 외부 개념이 모이면 두 존재가 [어디서 같아지며 동시에 어디서 달라지는지] 관측구조 대조가 활성화됩니다. (예: 상단 [기계 ⇄ 인간 경계 관측] 클릭)';
            } else {
                const { a, b, sharedTokens, sameAxis, diffAxis, diffGap, blurScore } = pair;
                const line1 = document.createElement('div');
                line1.className = 'epi-duality-head';
                line1.textContent = `관측 대조: [${a.title}] ⇄ [${b.title}]  ·  경계 통합도(흐릿함) ${blurScore}%  ·  경계 분화도(차이) ${100 - blurScore}%`;
                dualityHost.appendChild(line1);

                const line2 = document.createElement('div');
                line2.className = 'epi-duality-line';
                line2.textContent = `● 같아지는 지점 (통합 경계): [${sameAxis}] 관측 축에서 유사한 위상을 보임${sharedTokens.length ? ` · 공유 실재 어휘: ${sharedTokens.join(', ')}` : ' · 상위 구조적 공명'}`;
                dualityHost.appendChild(line2);

                const line3 = document.createElement('div');
                line3.className = 'epi-duality-line diff';
                line3.textContent = `◆ 달라지는 지점 (분화 경계): [${diffAxis}] 관측 축에서 ${diffGap}점의 위상 차이를 만들며 서로 다른 존재 양태로 공존함`;
                dualityHost.appendChild(line3);
            }
        }

        const activeIce = rotorState.ice.find((n) => n.title === rotorState.selectedIceTitle)
            || rotorState.ice[rotorState.ice.length - 1]
            || null;

        // 1) Active Concept Causal Card
        const detailHost = document.getElementById('epi-active-detail');
        if (detailHost) {
            detailHost.textContent = '';
            if (!activeIce) {
                const empty = document.createElement('div');
                empty.className = 'macro-empty';
                empty.textContent = '아직 탐색된 외부 개념이 없습니다. 상단 입력창에 아무 주제어나 입력하거나 [스스로 목적 형성·사유]를 눌러 외부 세계와 연결해 보세요.';
                detailHost.appendChild(empty);
            } else {
                const head = document.createElement('div');
                head.className = 'epi-detail-head';
                const titleSpan = document.createElement('strong');
                titleSpan.textContent = `${activeIce.title} (${activeIce.dominantAxisLabel} 중심 · 선명 ${activeIce.metrics.clarity}% · 채도 ${activeIce.metrics.saturation}% · 명암 ${activeIce.metrics.contrast}%)`;
                head.appendChild(titleSpan);

                if (activeIce.sourceUrl && activeIce.sourceUrl.startsWith('https://')) {
                    const link = document.createElement('a');
                    link.href = activeIce.sourceUrl;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.className = 'epi-ext-link';
                    link.textContent = `외부 원문 (${activeIce.lang.toUpperCase()} Wikipedia) ↗`;
                    head.appendChild(link);
                }
                detailHost.appendChild(head);

                const sumP = document.createElement('p');
                sumP.className = 'epi-summary-text';
                sumP.textContent = activeIce.summary || '';
                detailHost.appendChild(sumP);

                const axGrid = document.createElement('div');
                axGrid.className = 'epi-axes-grid';
                const nodeAxes = activeIce.axes ? Object.values(activeIce.axes) : [];
                nodeAxes.slice(0, 8).forEach((ax) => {
                    const card = document.createElement('div');
                    card.className = ax.emergent ? 'epi-axis-box emergent' : 'epi-axis-box';
                    const k = document.createElement('div');
                    k.className = 'epi-axis-k';
                    k.textContent = `${ax.emergent ? '★ ' : ''}${ax.label} · ${ax.score}점`;
                    const v = document.createElement('div');
                    v.className = 'epi-axis-v';
                    v.textContent = (ax.evidence && ax.evidence[0])
                        ? ax.evidence[0]
                        : '실재 본문 내 직접 표식 희소 (타 축 및 자생 축에서 보완)';
                    card.appendChild(k);
                    card.appendChild(v);
                    axGrid.appendChild(card);
                });
                detailHost.appendChild(axGrid);

                if (activeIce.contrastiveField) {
                    const cf = activeIce.contrastiveField;
                    const bal = cf.attractionRepulsionBalance || { attractionPct: 60, repulsionPct: 30, horizonPct: cf.blindSpotPct || 20 };
                    const cfBox = document.createElement('div');
                    cfBox.className = 'epi-duality-box';
                    cfBox.style.marginTop = '8px';

                    const cfHead = document.createElement('div');
                    cfHead.className = 'epi-duality-head';
                    cfHead.textContent = `비교대조 프리즘 (인력·척력·경계잔차)  ·  수렴 인력 ${bal.attractionPct}%  ·  비수렴 척력 ${bal.repulsionPct}%  ·  사각지대 잔차 ${bal.horizonPct}%`;
                    cfBox.appendChild(cfHead);

                    if (Array.isArray(cf.convergingFactors) && cf.convergingFactors.length > 0) {
                        const conv = cf.convergingFactors[0];
                        const l1 = document.createElement('div');
                        l1.className = 'epi-duality-line';
                        l1.textContent = `● 수렴 인력 (왜 [${conv.label}]인가): ${conv.score}점 (${conv.hitCount}/${conv.totalSentences}문장) — ${conv.evidence}`;
                        cfBox.appendChild(l1);
                    }

                    if (Array.isArray(cf.nonConvergingFactors) && cf.nonConvergingFactors.length > 0) {
                        const nonConvText = cf.nonConvergingFactors.slice(0, 2).map((f) => f.exclusionReason).join(' / ');
                        const l2 = document.createElement('div');
                        l2.className = 'epi-duality-line diff';
                        l2.textContent = `◆ 비수렴 척력 (왜 타 축이 아닌가): ${nonConvText}`;
                        cfBox.appendChild(l2);
                    }

                    const l3 = document.createElement('div');
                    l3.className = 'epi-duality-line';
                    l3.style.color = '#fcd34d';
                    const tokSummary = (cf.blindSpotTokens && cf.blindSpotTokens.length > 0)
                        ? cf.blindSpotTokens.slice(0, 6).join(', ')
                        : '미포집 잔여 어휘 희소';
                    const sentHint = (cf.blindSpotSentences && cf.blindSpotSentences[0])
                        ? ` | 미포착 문장: "${cf.blindSpotSentences[0]}"`
                        : '';
                    l3.textContent = `◌ 프리즘 사각지대 잔차 (${cf.blindSpotPct}%): [${tokSummary}]${sentHint}`;
                    cfBox.appendChild(l3);

                    detailHost.appendChild(cfBox);
                }

                if (activeIce.predictionAudit) {
                    const auditDiv = document.createElement('div');
                    auditDiv.className = 'epi-audit-line';
                    auditDiv.textContent = activeIce.predictionAudit.verdict;
                    detailHost.appendChild(auditDiv);
                }
            }
        }

        // 2) Uncaptured Frontier Chips (tagged by contrastive role: blind_spot_probe / counter_example / core_bridge)
        const frontierHost = document.getElementById('epi-frontier-chips');
        if (frontierHost) {
            frontierHost.textContent = '';
            if (rotorState.uncaptured.length === 0) {
                const span = document.createElement('span');
                span.className = 'macro-empty-inline';
                span.textContent = '외부 개념을 1개 이상 탐색하면 실재 연결된 미포집 개척지가 자동 생성됩니다.';
                frontierHost.appendChild(span);
            } else {
                rotorState.uncaptured.slice(0, 14).forEach((item) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'probe-chip';
                    const rolePrefix = item.role === 'blind_spot_probe'
                        ? '◌ 사각지대'
                        : (item.role === 'counter_example' ? '◆ 반례' : '● 연결');
                    btn.textContent = `${rolePrefix} ${item.title} (${item.sourceTitle || '기원'})`;
                    btn.title = item.reason || '';
                    btn.addEventListener('click', () => {
                        exploreTopic(item.title, { sourceTitle: item.sourceTitle });
                    });
                    frontierHost.appendChild(btn);
                });
            }
        }

        // 2.5) Auto-Generated Law-Based Neural Axis Differentiation Queue
        const diffQueueHost = document.getElementById('epi-diff-queue');
        if (diffQueueHost) {
            diffQueueHost.textContent = '';
            if (rotorState.differentiationQueue.length === 0) {
                const empty = document.createElement('span');
                empty.className = 'macro-empty-inline';
                empty.textContent = '대기 중인 분화 스텝 없음 — 새로운 외부 개념·인과 연결이 발견되면 법칙 기반 분화 스텝이 자동 생성됩니다.';
                diffQueueHost.appendChild(empty);
            } else {
                rotorState.differentiationQueue.forEach((q, idx) => {
                    const chip = document.createElement('button');
                    chip.type = 'button';
                    chip.className = 'epi-axis-badge emergent';
                    chip.style.cursor = 'pointer';
                    chip.textContent = `#${idx + 1} ${q.lawTitle} → ★[${q.candidateLabel}] 분화 실행`;
                    chip.addEventListener('click', () => {
                        executeQueuedDifferentiationStep();
                    });
                    diffQueueHost.appendChild(chip);
                });
            }
        }

        // 3) World Tree Growth Rings Ledger (세계수 나이테 자동 기록 원장)
        const ringsHost = document.getElementById('epi-rings-ledger');
        if (ringsHost) {
            ringsHost.textContent = '';
            if (rotorState.worldTreeRings.length === 0) {
                const empty = document.createElement('div');
                empty.className = 'chain-step-line';
                empty.textContent = '아직 기록된 나이테가 없습니다. 개념을 탐색하거나 자동 학습 루프를 실행하면 새 인과 연결마다 나이테가 자동 추가됩니다.';
                ringsHost.appendChild(empty);
            } else {
                [...rotorState.worldTreeRings].reverse().slice(0, 12).forEach((ring) => {
                    const row = document.createElement('button');
                    row.type = 'button';
                    row.className = ring.spawnedAxisLabel ? 'epi-ring-row spawned' : 'epi-ring-row';
                    const bridgeLabel = ring.bridgeTargets && ring.bridgeTargets.length
                        ? `연결: ${ring.bridgeTargets.join(', ')}`
                        : '초기 기원 뿌리';
                    const lawTag = ring.lawTitle ? ` · ${ring.lawTitle}` : '';
                    const axisTag = ring.spawnedAxisLabel ? ` ★신경축 [${ring.spawnedAxisLabel}] 분화` : '';
                    row.textContent = `나이테 #${ring.ringNumber} (t${ring.tStep}) · [${ring.title}] · ${bridgeLabel}${lawTag}${axisTag}`;
                    row.addEventListener('click', () => {
                        rotorState.selectedIceTitle = ring.title;
                        rotorState.uiDirty = true;
                    });
                    ringsHost.appendChild(row);
                });
            }
        }

        // 4) Growth & Reflection Log
        const logHost = document.getElementById('epi-growth-log');
        if (logHost) {
            logHost.textContent = '';
            if (rotorState.growthLog.length === 0) {
                const empty = document.createElement('div');
                empty.className = 'chain-step-line';
                empty.textContent = '아직 외부 사유 기록이 없습니다. 첫 외부 지식을 탐색하거나 실시간 지구 기상 대조를 실행해 보세요.';
                logHost.appendChild(empty);
            } else {
                rotorState.growthLog.slice(0, 14).forEach((entry) => {
                    const row = document.createElement('div');
                    row.className = 'chain-step-line';
                    row.textContent = `[${entry.ts}] [${entry.tag}] ${entry.text}`;
                    logHost.appendChild(row);
                });
            }
        }

        // 5) Parallel Inclusion/Exclusion Causal Constraint Verifier Card
        const constraintHost = document.getElementById('epi-constraint-result');
        if (constraintHost) {
            constraintHost.textContent = '';
            const latest = rotorState.constraintChecks[0] || null;
            if (!latest) {
                const empty = document.createElement('div');
                empty.className = 'macro-empty';
                empty.textContent = '조합이나 반사실 조건을 입력해 보세요 (예: "빨간 사과" vs "파란 사과", "기압차 없는 바람"). 실재 외부 문서와 누적 인과망을 대조해 수용 인력과 배제 척력을 병렬로 산출합니다.';
                constraintHost.appendChild(empty);
            } else {
                const head = document.createElement('div');
                head.className = 'epi-duality-head';
                head.textContent = `[${latest.query}] → ${latest.verdictLabel}  │  ● 수용 인력 ${latest.attractionScore}%  ·  ◆ 배제 척력 ${latest.repulsionScore}%`;
                constraintHost.appendChild(head);

                // Dual attraction vs repulsion bar
                const barWrap = document.createElement('div');
                barWrap.style.display = 'flex';
                barWrap.style.height = '6px';
                barWrap.style.margin = '5px 0 7px';
                barWrap.style.background = 'rgba(255,255,255,0.08)';
                barWrap.style.overflow = 'hidden';
                const attBar = document.createElement('div');
                attBar.style.width = `${Math.max(2, Math.min(98, latest.attractionScore))}%`;
                attBar.style.background = '#10b981';
                const repBar = document.createElement('div');
                repBar.style.width = `${Math.max(2, Math.min(98, latest.repulsionScore))}%`;
                repBar.style.background = '#fb7185';
                barWrap.appendChild(attBar);
                barWrap.appendChild(repBar);
                constraintHost.appendChild(barWrap);

                (latest.includedEvidence || []).forEach((line) => {
                    const div = document.createElement('div');
                    div.className = 'epi-duality-line';
                    div.textContent = `● 수용 인력(포함): ${line}`;
                    constraintHost.appendChild(div);
                });
                (latest.excludedEvidence || []).forEach((line) => {
                    const div = document.createElement('div');
                    div.className = 'epi-duality-line diff';
                    div.textContent = `◆ 배제 척력(배척): ${line}`;
                    constraintHost.appendChild(div);
                });
                (latest.boundaryCrossingConditions || []).forEach((line) => {
                    const div = document.createElement('div');
                    div.className = 'epi-duality-line';
                    div.style.color = '#fcd34d';
                    div.textContent = `◌ 경계 전환 조건: ${line}`;
                    constraintHost.appendChild(div);
                });

                if (latest.subjectArticle && latest.subjectArticle.sourceUrl && latest.subjectArticle.sourceUrl.startsWith('https://')) {
                    const foot = document.createElement('div');
                    foot.style.marginTop = '5px';
                    foot.style.fontSize = '0.72rem';
                    foot.style.color = 'var(--muted)';
                    const meta = document.createElement('span');
                    meta.textContent = `실재 대조: 기준 [${latest.subjectArticle.title}] 본문 직접 일치 ${latest.coOccurrence ? latest.coOccurrence.directSubjectMentions : 0}문장 · 백과 공출현 ${latest.coOccurrence ? latest.coOccurrence.combinedSearchHits : 0}건  `;
                    foot.appendChild(meta);
                    const a = document.createElement('a');
                    a.href = latest.subjectArticle.sourceUrl;
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                    a.className = 'epi-ext-link';
                    a.textContent = '기준 원문 확인 ↗';
                    foot.appendChild(a);
                    constraintHost.appendChild(foot);
                }
            }
        }

        // 6) Cross-Modal Sensory-Hierarchy Boundary Mapper Card (100% safe DOM)
        const sensoryHost = document.getElementById('epi-sensory-result');
        if (sensoryHost) {
            sensoryHost.textContent = '';
            const latestS = rotorState.sensoryHierarchyChecks[0] || null;
            if (!latestS || !latestS.layers) {
                const empty = document.createElement('div');
                empty.className = 'macro-empty';
                empty.textContent = '대상을 입력해 보세요 (예: "사과", "바람", "불", "소금"). 단일 속성이 아니라 [물리·생물 기원 ↔ 6감각 채널 교차 ↔ 언어 경계]로 분해하고, 소프트웨어가 직접 체화하지 못하는 감각 공백을 함께 표시합니다.';
                sensoryHost.appendChild(empty);
            } else {
                const { physicalOrigin, sensoryChannels, linguisticBoundary, softwareGap } = latestS.layers;

                const head = document.createElement('div');
                head.className = 'epi-duality-head';
                head.textContent = `[${latestS.topic}] 통합 감각·계층 분해  │  텍스트 감각 교차 ${linguisticBoundary.convergedCount}/${linguisticBoundary.totalChannels}채널 (${softwareGap.textCoveragePct}%)  ·  직접 감각 체화 ${softwareGap.directEmbodimentPct}%`;
                sensoryHost.appendChild(head);

                // Layer 1: Physical / Biological Origin
                const l1 = document.createElement('div');
                l1.className = 'epi-duality-line';
                const catStr = (physicalOrigin.categories && physicalOrigin.categories.length)
                    ? ` [${physicalOrigin.categories.slice(0, 3).join(' · ')}]`
                    : '';
                const originSample = (physicalOrigin.evidenceSentences && physicalOrigin.evidenceSentences[0]) || '';
                l1.textContent = `L1 물리·생물 기원${catStr}: ${originSample}`;
                sensoryHost.appendChild(l1);

                // Layer 2: 6 Sensory Channels Grid
                const chGrid = document.createElement('div');
                chGrid.style.display = 'grid';
                chGrid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(220px, 1fr))';
                chGrid.style.gap = '6px';
                chGrid.style.margin = '7px 0';

                (sensoryChannels || []).forEach((ch) => {
                    const card = document.createElement('div');
                    card.style.padding = '6px 8px';
                    card.style.background = ch.textEvidenceCount > 0 ? 'rgba(30,41,59,0.72)' : 'rgba(15,23,42,0.42)';
                    card.style.border = `1px solid ${ch.textEvidenceCount > 0 ? ch.color : 'rgba(148,163,184,0.2)'}`;
                    card.style.display = 'flex';
                    card.style.flexDirection = 'column';
                    card.style.gap = '3px';

                    const top = document.createElement('div');
                    top.style.display = 'flex';
                    top.style.justifyContent = 'space-between';
                    top.style.fontFamily = 'var(--font-mono)';
                    top.style.fontSize = '0.71rem';
                    top.style.fontWeight = '700';
                    top.style.color = ch.textEvidenceCount > 0 ? ch.color : '#94a3b8';

                    const nameEl = document.createElement('span');
                    nameEl.textContent = ch.label;
                    const statEl = document.createElement('span');
                    statEl.textContent = ch.textEvidenceCount > 0 ? `텍스트 ${ch.textEvidenceCount}문장 (${ch.coverageScore}%)` : '문서 미관측 (0%)';
                    top.appendChild(nameEl);
                    top.appendChild(statEl);
                    card.appendChild(top);

                    const barBg = document.createElement('div');
                    barBg.style.height = '4px';
                    barBg.style.background = 'rgba(255,255,255,0.08)';
                    const barFill = document.createElement('div');
                    barFill.style.height = '100%';
                    barFill.style.width = `${Math.max(0, Math.min(100, ch.coverageScore))}%`;
                    barFill.style.background = ch.color;
                    barBg.appendChild(barFill);
                    card.appendChild(barBg);

                    const organEl = document.createElement('div');
                    organEl.style.fontSize = '0.69rem';
                    organEl.style.color = '#cbd5e1';
                    const cueStr = (ch.matchedCues && ch.matchedCues.length)
                        ? `단서: ${ch.matchedCues.join(', ')}`
                        : '직접 단서 없음';
                    organEl.textContent = `${ch.organ} · ${cueStr}`;
                    card.appendChild(organEl);

                    const sensorNote = document.createElement('div');
                    sensorNote.style.fontSize = '0.67rem';
                    sensorNote.style.color = ch.indirectApiProxy ? '#5eead4' : '#fca5a5';
                    sensorNote.textContent = ch.indirectApiProxy
                        ? `◌ 생체 감각기 부재 · ${ch.indirectApiProxy}`
                        : `◌ 직접 감각 부재 (필요 계측: ${ch.sensorNeeded})`;
                    card.appendChild(sensorNote);

                    chGrid.appendChild(card);
                });
                sensoryHost.appendChild(chGrid);

                // Layer 3: Linguistic Boundary Synthesis
                const l3 = document.createElement('div');
                l3.className = 'epi-duality-line';
                l3.style.color = '#7dd3fc';
                l3.textContent = `L3 통합 언어 경계: ${linguisticBoundary.boundarySummary}`;
                sensoryHost.appendChild(l3);

                // Layer 4: Honest Software Sensory Gap
                (softwareGap.gapLines || []).forEach((gLine) => {
                    const gDiv = document.createElement('div');
                    gDiv.className = 'epi-duality-line';
                    gDiv.style.color = '#fcd34d';
                    gDiv.textContent = `L4 시스템 감각 공백: ${gLine}`;
                    sensoryHost.appendChild(gDiv);
                });

                if (latestS.sourceUrl && latestS.sourceUrl.startsWith('https://')) {
                    const foot = document.createElement('div');
                    foot.style.marginTop = '5px';
                    foot.style.fontSize = '0.72rem';
                    foot.style.color = 'var(--muted)';
                    const meta = document.createElement('span');
                    meta.textContent = `실재 문서 ${latestS.totalSentences}문장 기준 다중 감각 교차 추출  `;
                    foot.appendChild(meta);
                    const a = document.createElement('a');
                    a.href = latestS.sourceUrl;
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                    a.className = 'epi-ext-link';
                    a.textContent = '기준 원문 확인 ↗';
                    foot.appendChild(a);
                    sensoryHost.appendChild(foot);
                }
            }
        }

        // 7) Autonomous Active Intervention & Unlabeled Cross-Situational Word Discovery Card (100% safe DOM)
        const streamHost = document.getElementById('epi-stream-grounding-result');
        if (streamHost) {
            streamHost.textContent = '';
            const latestEp = rotorState.streamEpisodes[0] || null;
            const totalEp = rotorState.streamGlobalStats ? rotorState.streamGlobalStats.totalEpisodes : 0;
            const allVocab = Object.values(rotorState.groundedLexicon || {});
            const specThr = rotorState.selfPolicy ? rotorState.selfPolicy.specificityThreshold : 14;
            const discovered = allVocab
                .filter((e) => e && e.count >= 1 && (e.specificityPct >= specThr || e.origin === 'novel_probe'))
                .sort((a, b) => (b.specificityPct * Math.min(3, b.count)) - (a.specificityPct * Math.min(3, a.count)));
            const rejectedNoiseCount = allVocab.filter((e) => e && e.count >= 2 && e.specificityPct < specThr).length;

            if (!latestEp) {
                const empty = document.createElement('div');
                empty.className = 'macro-empty';
                empty.textContent = '고정 어휘 라벨 없이, 엘리시아가 스스로 개입(행동)과 비개입(기준선)을 대조하며 원시 발화·상황 텍스트에서 어떤 단어가 어느 물리 채널(운동·충격·음향·위기·교역·물가)과 인과적으로 묶이는지 자율 발견합니다.';
                streamHost.appendChild(empty);
            } else {
                const d = latestEp.delta || {};
                const head = document.createElement('div');
                head.className = 'epi-duality-head';
                const errLabel = latestEp.prediction && latestEp.prediction.hadPrior
                    ? `사전 예측 오차 ${latestEp.prediction.errorPct}% (${latestEp.prediction.errorPct <= 20 ? '인과 수렴' : '자율 보정'})`
                    : '최초 자율 개입 · 기준선 대비 순수 인과차 계측';
                head.textContent = `자율 실험 #${totalEp} · [${latestEp.actionLabel}] (${latestEp.autonomous ? '자율 선택' : '수동 노출'})  │  ${errLabel}`;
                streamHost.appendChild(head);

                const liftLine = document.createElement('div');
                liftLine.className = 'epi-duality-line';
                liftLine.textContent = `● 개입 vs 비개입 인과 변화량(ΔLift): 주도 변화 [${latestEp.topCausalChannel || '균형'}] · 운동 ${d.peakMotion} · 충격 ${d.peakShake} · 음향 ${d.peakAudioHz}Hz · 위기 Δ${d.dCrisis >= 0 ? '+' : ''}${d.dCrisis}% · 교역 Δ${d.dTrade >= 0 ? '+' : ''}${d.dTrade}`;
                streamHost.appendChild(liftLine);

                if (latestEp.spokenUtterances && latestEp.spokenUtterances.length > 0) {
                    const spLine = document.createElement('div');
                    spLine.className = 'epi-duality-line';
                    spLine.style.color = '#7dd3fc';
                    spLine.textContent = `● 원시 관측 발화(무라벨 입력): ${latestEp.spokenUtterances.join('  /  ')}${latestEp.novelWord ? `  +  [미지 단어: ${latestEp.novelWord}]` : ''}`;
                    streamHost.appendChild(spLine);
                }

                if (latestEp.videoBridgeSummary) {
                    const vLine = document.createElement('div');
                    vLine.className = 'epi-duality-line';
                    vLine.style.color = '#c4b5fd';
                    vLine.textContent = `● 연동 영상 로터: ${latestEp.videoBridgeSummary}`;
                    streamHost.appendChild(vLine);
                }

                if (discovered.length > 0) {
                    const sub = document.createElement('div');
                    sub.style.fontSize = '0.71rem';
                    sub.style.color = '#6ee7b7';
                    sub.style.marginTop = '5px';
                    sub.style.fontFamily = 'var(--font-mono)';
                    sub.textContent = `★ 교차상황 자율 분별 어휘 (${discovered.length}건 수용 · 공통 배경어 ${rejectedNoiseCount}건 척력 자동 배제):`;
                    streamHost.appendChild(sub);

                    const lexWrap = document.createElement('div');
                    lexWrap.style.display = 'flex';
                    lexWrap.style.flexWrap = 'wrap';
                    lexWrap.style.gap = '5px';
                    lexWrap.style.marginTop = '4px';
                    discovered.slice(0, 12).forEach((entry) => {
                        const badge = document.createElement('span');
                        badge.className = 'epi-axis-badge';
                        badge.style.borderColor = entry.origin === 'novel_probe'
                            ? '#f472b6'
                            : (entry.specificityPct >= 30 ? '#10b981' : '#38bdf8');
                        badge.textContent = `${entry.origin === 'novel_probe' ? '★' : ''}[${entry.word}] → ${entry.dominantLabel} (특이도 ${entry.specificityPct}% · ${entry.count}회)`;
                        lexWrap.appendChild(badge);
                    });
                    streamHost.appendChild(lexWrap);
                }

                const honesty = document.createElement('div');
                honesty.className = 'epi-duality-line';
                honesty.style.color = '#fcd34d';
                honesty.style.marginTop = '5px';
                honesty.textContent = `◌ 무개입 원리: 개발자 지정 단어표 없이 [출현 장면 평균 − 미출현 장면 평균] 대조만으로 물리 채널에 특이적으로 반응하는 단어만 남기고 공통 잡음어를 자동 배제합니다.`;
                streamHost.appendChild(honesty);
            }
        }

        // 8) Self-Model Audit & Structural Parameter Auto-Calibration Card (100% safe DOM)
        const selfAuditHost = document.getElementById('epi-self-audit-result');
        if (selfAuditHost) {
            selfAuditHost.textContent = '';
            const sp = rotorState.selfPolicy;
            const tel = computeSelfTelemetry();
            const latestAudit = rotorState.selfAuditHistory[0] || null;

            const polStrip = document.createElement('div');
            polStrip.style.display = 'flex';
            polStrip.style.flexWrap = 'wrap';
            polStrip.style.gap = '5px';
            polStrip.style.marginBottom = '6px';
            const polBadges = [
                `특이도 임계 ${sp.specificityThreshold}%`,
                `재실험 오차기준 ${sp.interventionErrorTrigger}%`,
                `학습률 하한 ${sp.learningAlphaFloor}`,
                `사각지대 민감도 ${sp.blindSpotQueueThreshold}%`,
                `자기수정 ${sp.revisionsCount}회 · 롤백 ${sp.rollbacksCount}회`,
            ];
            polBadges.forEach((txt) => {
                const b = document.createElement('span');
                b.className = 'epi-axis-badge';
                b.style.borderColor = '#c084fc';
                b.textContent = txt;
                polStrip.appendChild(b);
            });
            selfAuditHost.appendChild(polStrip);

            const telLine = document.createElement('div');
            telLine.className = 'epi-duality-line';
            telLine.textContent = `● 현재 자기 작동 지표: 행동 예측오차 ${tel.meanErrorPct}% (추세 ${tel.errorTrendDelta >= 0 ? '+' : ''}${tel.errorTrendDelta}%) · 어휘 신호비 ${Math.round(tel.signalNoiseRatio * 100)}% (${tel.discoveredCount}/${tel.totalVocabCount}) · 프리즘 사각지대 평균 ${tel.avgBlindSpotPct}% · 행동 탐색률 ${tel.actionCoveragePct}%`;
            selfAuditHost.appendChild(telLine);

            if (!latestAudit) {
                const empty = document.createElement('div');
                empty.className = 'epi-duality-line';
                empty.style.color = 'var(--muted)';
                empty.textContent = '아직 자기구조 진단 이력이 없습니다. 자율 루프가 누적되거나 [자기구조 진단·수정 1회]를 누르면 자신의 오차·잡음·사각지대를 측정해 내부 임계값을 스스로 조정하고 다음 주기에 그 효과를 검증합니다.';
                selfAuditHost.appendChild(empty);
            } else {
                const diag = document.createElement('div');
                diag.className = 'epi-duality-line';
                diag.style.color = '#d8b4fe';
                diag.textContent = `● 최근 자기진단 (#${latestAudit.id} · ${latestAudit.trigger}): ${latestAudit.diagnosis}`;
                selfAuditHost.appendChild(diag);

                const act = document.createElement('div');
                act.className = 'epi-duality-line';
                act.style.color = '#6ee7b7';
                act.textContent = `● 구조 파라미터 변경: ${latestAudit.changeSummary}`;
                selfAuditHost.appendChild(act);

                if (latestAudit.priorEffectVerdict) {
                    const ver = document.createElement('div');
                    ver.className = 'epi-duality-line';
                    ver.style.color = latestAudit.rolledBack ? '#fda4af' : '#fcd34d';
                    ver.textContent = `◌ 직전 수정 사후 검증: ${latestAudit.priorEffectVerdict}`;
                    selfAuditHost.appendChild(ver);
                }
            }
        }

        syncPhaseSchedulerDOM();
    }

    function handleCanvasClick(x, y) {
        if (rotorState.busy) return;
        for (const t of rotorState.hitTargets) {
            const dx = x - t.x;
            const dy = y - t.y;
            if (dx * dx + dy * dy <= t.r * t.r) {
                if (t.kind === 'uncaptured') {
                    exploreTopic(t.title, { sourceTitle: t.sourceTitle });
                } else if (t.kind === 'ice') {
                    rotorState.selectedIceTitle = t.title;
                    rotorState.uiDirty = true;
                }
                return;
            }
        }
    }

    function step({ legacyCtx, rotorCtx, thumbS4Ctx, thumbS2Ctx, thumbS0Ctx }) {
        const t0 = performance.now();
        rotorState.rotAngle += 0.012;
        if (rotorState.ringPulseTimer > 0) {
            rotorState.ringPulseTimer = Math.max(0, rotorState.ringPulseTimer - 0.025);
        }

        tickPhaseScheduler();

        drawLeftCanvas(legacyCtx);
        drawRightCanvas(rotorCtx);

        const activeIce = rotorState.ice.find((n) => n.title === rotorState.selectedIceTitle)
            || rotorState.ice[rotorState.ice.length - 1]
            || null;
        const clarity = activeIce && activeIce.metrics ? activeIce.metrics.clarity : 20;
        const saturation = activeIce && activeIce.metrics ? activeIce.metrics.saturation : 15;
        const friction = activeIce && activeIce.metrics ? activeIce.metrics.friction : 50;

        drawThumbMini(thumbS4Ctx, `L2 거시 ${Math.round(rotorState.phaseScheduler.macroPressure)}%`, Math.min(1, rotorState.phaseScheduler.macroPressure / 100), '#2dd4bf');
        drawThumbMini(thumbS2Ctx, `L1 분화 ${Math.round(rotorState.phaseScheduler.midTension)}%`, Math.min(1, rotorState.phaseScheduler.midTension / 100), '#f472b6');
        drawThumbMini(thumbS0Ctx, `L0 마찰 ${Math.round(rotorState.phaseScheduler.fastPhase)}%`, Math.max(0.08, rotorState.phaseScheduler.fastPhase / 100), '#f59e0b');

        if (rotorState.uiDirty) {
            rotorState.uiDirty = false;
            syncInspectorDOM();
        }

        const dt = Math.max(0.2, performance.now() - t0);
        return {
            s4Same: Math.min(100, Math.round(clarity)),
            s2Same: Math.min(100, Math.round(saturation)),
            s0Same: Math.min(100, Math.round(100 - friction)),
            origin: activeIce ? `t${rotorState.tStepCount} [${activeIce.title}] · ${getAllAxes().length}축` : '열린 외부 사유 대기',
            activeRatio: Math.max(0.08, Math.min(1, friction / 100)),
            leftOps: Math.max(120, rotorState.ice.length * 420 + getAllAxes().length * 140),
            rS4Ops: Math.max(24, rotorState.ice.length * 18),
            rS2Ops: Math.max(16, rotorState.emergentAxes.length * 22 + rotorState.uncaptured.length * 10),
            rS0Ops: Math.max(12, Math.round(friction * 1.4)),
            leftMs: dt * 1.8,
            rightMs: dt,
        };
    }

    function onEnterTab() {
        rotorState.uiDirty = true;
        // Start autonomous closed-loop automatically on tab entry unless the user explicitly paused it
        if (!rotorState.userPaused && !rotorState.autoMode) {
            setAutoMode(true, { silent: true });
        }
    }

    function onLeaveTab() {
        // Suspend smoothly when leaving Tab 6 (preserve userPaused preference so re-entering auto-resumes)
        if (rotorState.autoMode) setAutoMode(false, { silent: true });
    }

    function bindUIOnce() {
        const formInput = document.getElementById('epi-topic-input');
        const btnExplore = document.getElementById('btn-epi-explore');
        const btnStep = document.getElementById('btn-epi-step');
        const btnAuto = document.getElementById('btn-epi-auto');
        const btnReality = document.getElementById('btn-epi-reality');
        const btnReset = document.getElementById('btn-epi-reset');
        const stimInput = document.getElementById('epi-stimulus-input');
        const btnStim = document.getElementById('btn-epi-stimulus');

        if (btnExplore && formInput) {
            const doExplore = () => {
                const val = formInput.value.trim();
                if (!val) return;
                exploreTopic(val, { autonomous: false });
                formInput.value = '';
            };
            btnExplore.addEventListener('click', doExplore);
            formInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') doExplore();
            });
        }
        if (btnStim && stimInput) {
            const doStim = () => {
                const val = stimInput.value.trim();
                if (!val) return;
                injectReflectiveStimulus(val);
                stimInput.value = '';
            };
            btnStim.addEventListener('click', doStim);
            stimInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') doStim();
            });
        }
        if (btnStep) btnStep.addEventListener('click', () => runAutonomousStep());
        if (btnAuto) btnAuto.addEventListener('click', () => setAutoMode(!rotorState.autoMode, { userInitiated: true }));
        if (btnReality) btnReality.addEventListener('click', () => runRealityProbe());
        if (btnReset) btnReset.addEventListener('click', () => resetMemory());
        const btnExport = document.getElementById('btn-epi-export');
        if (btnExport) btnExport.addEventListener('click', () => exportGrowthLedgerJson());
        const btnRunDiff = document.getElementById('btn-epi-run-diff');
        if (btnRunDiff) btnRunDiff.addEventListener('click', () => {
            rotorState.phaseScheduler.midTension = Math.max(0, rotorState.phaseScheduler.midTension - 100);
            rotorState.phaseScheduler.midFires += 1;
            executeQueuedDifferentiationStep();
        });
        const btnMacro = document.getElementById('btn-epi-macro');
        if (btnMacro) btnMacro.addEventListener('click', () => runMacroConsolidation(true));

        const constraintInput = document.getElementById('epi-constraint-input');
        const btnConstraint = document.getElementById('btn-epi-constraint');
        if (btnConstraint && constraintInput) {
            const doCheck = () => {
                const val = constraintInput.value.trim();
                if (!val) return;
                runConstraintCheck(val);
            };
            btnConstraint.addEventListener('click', doCheck);
            constraintInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') doCheck();
            });
        }
        document.querySelectorAll('[data-epi-constraint]').forEach((b) => {
            b.addEventListener('click', () => {
                const q = String(b.dataset.epiConstraint || '').trim();
                if (constraintInput) constraintInput.value = q;
                if (q) runConstraintCheck(q);
            });
        });

        const sensoryInput = document.getElementById('epi-sensory-input');
        const btnSensory = document.getElementById('btn-epi-sensory');
        if (btnSensory && sensoryInput) {
            const doSensory = () => {
                const val = sensoryInput.value.trim();
                if (!val) return;
                runSensoryHierarchyAnalysis(val);
            };
            btnSensory.addEventListener('click', doSensory);
            sensoryInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') doSensory();
            });
        }
        document.querySelectorAll('[data-epi-sensory]').forEach((b) => {
            b.addEventListener('click', () => {
                const q = String(b.dataset.epiSensory || '').trim();
                if (sensoryInput) sensoryInput.value = q;
                if (q) runSensoryHierarchyAnalysis(q);
            });
        });

        const btnAutoIntervene = document.getElementById('btn-epi-auto-intervene');
        if (btnAutoIntervene) {
            btnAutoIntervene.addEventListener('click', () => observeContinuousStreamEpisode(null));
        }
        const btnSelfAudit = document.getElementById('btn-epi-self-audit');
        if (btnSelfAudit) {
            btnSelfAudit.addEventListener('click', () => runMetaSelfObservation('manual'));
        }
        const novelInput = document.getElementById('epi-novel-word-input');
        const btnNovel = document.getElementById('btn-epi-novel-probe');
        if (btnNovel && novelInput) {
            const doNovel = () => {
                const w = novelInput.value.trim();
                if (!w) return;
                observeContinuousStreamEpisode(null, w);
                novelInput.value = '';
            };
            btnNovel.addEventListener('click', doNovel);
            novelInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') doNovel();
            });
        }
        document.querySelectorAll('[data-epi-stream]').forEach((b) => {
            b.addEventListener('click', () => {
                const actionId = String(b.dataset.epiStream || '').trim();
                const novelW = novelInput ? novelInput.value.trim() : '';
                if (actionId) observeContinuousStreamEpisode(actionId, novelW || null);
            });
        });

        document.querySelectorAll('#epi-frame-tabs button').forEach((b) => {
            b.addEventListener('click', () => setPhaseFrame(b.dataset.epiFrame));
        });
        document.querySelectorAll('[data-epi-seed]').forEach((b) => {
            b.addEventListener('click', () => exploreTopic(b.dataset.epiSeed, { autonomous: false }));
        });
        document.querySelectorAll('[data-epi-duality]').forEach((b) => {
            b.addEventListener('click', () => {
                const parts = String(b.dataset.epiDuality || '').split('|');
                if (parts.length === 2) observeBoundaryDuality(parts[0], parts[1]);
            });
        });
    }

    async function runConstraintCheck(queryText) {
        const query = String(queryText || '').trim();
        if (!query || rotorState.busy) return null;
        rotorState.busy = true;
        rotorState.lastStatus = `병렬 수용·배제 제약 검증 중: "${query}" (외부 실재 인과 경로 대조)...`;
        rotorState.uiDirty = true;

        try {
            const res = await fetch('/api/epistemic/constraint-check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    lang: 'ko',
                    priorNodes: buildPriorNodesPayload(),
                }),
            });
            const data = await res.json();
            if (!res.ok || data.status !== 'ok') {
                throw new Error(data.message || `인과 제약 검증 오류 (${res.status})`);
            }

            rotorState.constraintChecks.unshift(data);
            if (rotorState.constraintChecks.length > 8) rotorState.constraintChecks.length = 8;

            const friction = data.verdict === 'EXCLUDED' ? data.repulsionScore : Math.max(16, 100 - data.attractionScore);
            recordThoughtPhase(
                'constraint',
                `제약검증: ${query.slice(0, 14)}`,
                friction,
                data.verdict === 'INCLUDED' ? '#10b981' : (data.verdict === 'EXCLUDED' ? '#fb7185' : '#fbbf24')
            );
            pushLog(
                `수용·배제 검증 t${rotorState.tStepCount}`,
                `[${data.query}] → ${data.verdictLabel} (인력 ${data.attractionScore}% / 척력 ${data.repulsionScore}%)`
            );
            rotorState.lastStatus = `[${data.query}] ${data.verdictLabel} (수용 인력 ${data.attractionScore}% · 배제 척력 ${data.repulsionScore}%)`;

            // Feed result back into Causal Need Queue if the base subject isn't in Elysia's Ice memory yet
            const subjTitle = data.subjectArticle && data.subjectArticle.title ? data.subjectArticle.title : null;
            if (subjTitle && !rotorState.ice.some((n) => n.title.toLowerCase() === subjTitle.toLowerCase())) {
                enqueueCausalNeed({
                    dedupKey: `explore:${subjTitle.toLowerCase()}`,
                    action: 'explore',
                    priority: 92,
                    originEvent: `결과: [${data.query}] 제약 검증(${data.verdictLabel})에서 기준 대상 [${subjTitle}] 확인`,
                    internalLimit: `내부 한계: [${subjTitle}]의 전체 인과 구조가 아직 세계수 얼음 기억에 편입되지 않음`,
                    targetSummary: `기준 대상 [${subjTitle}] 전체 인과망 편입 탐색`,
                    payload: { topic: subjTitle, sourceTitle: null },
                });
            }

            rotorState.phaseScheduler.lastFriction = friction;
            rotorState.phaseScheduler.midTension = Math.min(130, rotorState.phaseScheduler.midTension + Math.round(friction * 0.4));
            persistState();
            rotorState.uiDirty = true;
            return data;
        } catch (err) {
            const msg = err instanceof Error ? err.message : '인과 제약 검증 실패';
            rotorState.lastStatus = `제약 검증 한계: ${msg}`;
            pushLog('제약 검증 오류', `"${query}" → ${msg}`);
            rotorState.uiDirty = true;
            return null;
        } finally {
            rotorState.busy = false;
        }
    }

    async function runSensoryHierarchyAnalysis(topicText) {
        const topic = String(topicText || '').trim();
        if (!topic || rotorState.busy) return null;
        rotorState.busy = true;
        rotorState.lastStatus = `통합 감각·계층 경계 분해 중: "${topic}" (물리 기원 ↔ 6감각 채널 ↔ 언어 경계 ↔ 감각 공백)...`;
        rotorState.uiDirty = true;

        try {
            const res = await fetch('/api/epistemic/sensory-hierarchy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, lang: 'ko' }),
            });
            const data = await res.json();
            if (!res.ok || data.status !== 'ok') {
                throw new Error(data.message || `감각·계층 분석 오류 (${res.status})`);
            }

            rotorState.sensoryHierarchyChecks.unshift(data);
            if (rotorState.sensoryHierarchyChecks.length > 6) rotorState.sensoryHierarchyChecks.length = 6;

            const lb = data.layers.linguisticBoundary;
            const sg = data.layers.softwareGap;
            const gapFriction = Math.max(20, 100 - sg.textCoveragePct);
            recordThoughtPhase('sensory_hierarchy', `감각계층: ${data.topic.slice(0, 12)}`, gapFriction, '#38bdf8');
            pushLog(
                `통합 감각·계층 t${rotorState.tStepCount}`,
                `[${data.topic}] 텍스트 감각 교차 ${lb.convergedCount}/${lb.totalChannels}채널(${sg.textCoveragePct}%) · 직접 체화 ${sg.directEmbodimentPct}%`
            );
            rotorState.lastStatus = `[${data.topic}] 통합 감각·계층 분해 완료: ${lb.convergedCount}/${lb.totalChannels}채널 교차 확인 · 직접 체화 0% 공백 명시`;

            // Feed back into Causal Need Queue if not yet in Ice memory
            if (data.topic && !rotorState.ice.some((n) => n.title.toLowerCase() === data.topic.toLowerCase())) {
                enqueueCausalNeed({
                    dedupKey: `explore:${data.topic.toLowerCase()}`,
                    action: 'explore',
                    priority: 90,
                    originEvent: `결과: [${data.topic}] 감각·계층 분해에서 ${lb.convergedCount}/${lb.totalChannels}채널 교차 확인`,
                    internalLimit: `내부 한계: [${data.topic}]의 감각·물리 경계가 아직 세계수 얼음 인과망에 연결되지 않음`,
                    targetSummary: `[${data.topic}] 외부 인과망 편입 탐색`,
                    payload: { topic: data.topic, sourceTitle: null },
                });
            }

            rotorState.phaseScheduler.lastFriction = gapFriction;
            rotorState.phaseScheduler.midTension = Math.min(130, rotorState.phaseScheduler.midTension + Math.round(gapFriction * 0.35));
            persistState();
            rotorState.uiDirty = true;
            return data;
        } catch (err) {
            const msg = err instanceof Error ? err.message : '감각·계층 분석 실패';
            rotorState.lastStatus = `감각·계층 분해 한계: ${msg}`;
            pushLog('감각·계층 오류', `"${topic}" → ${msg}`);
            rotorState.uiDirty = true;
            return null;
        } finally {
            rotorState.busy = false;
        }
    }

    function readUnifiedVideoBridgeSummary() {
        try {
            const raw = localStorage.getItem(BRIDGE_KEY);
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            const u = parsed && parsed.unifiedScaleRotor;
            if (!u || !u.nodes) return null;
            return `영상 스펙트럼 ${u.nodes}노드 · 차량 ${u.extractedVehicles || 0} · 인물 ${u.extractedPersons || 0} · 회상률 ${u.recallHitRatePct || 0}%`;
        } catch {
            return null;
        }
    }

    const STREAM_CHANNEL_LABELS = ['운동(속도)', '충격(진동)', '음향(Hz)', '위기(긴장)', '교역(흐름)', '물가(결핍)'];
    const RAW_TOKEN_STOP = new Set(['있는', '하는', '되는', '하고', '으로', '에서', '까지', '부터', '지금', '여기', '저기', '모든', '그냥', '다시', '계속', '상태', '유지', '진행', '판독', '살피는', '사건', '단계']);

    function extractUnlabeledStreamTokens(rawText) {
        const cleaned = String(rawText || '')
            .replace(/[^가-힣a-zA-Z0-9\s]/g, ' ')
            .split(/\s+/)
            .map((w) => w.replace(/(에서|으로|으로의|까지|부터|하는|하고|이다|입니다|했다|한다|중|은|는|이|가|을|를|의|에|도|만|로|와|과)$/, '').trim())
            .filter((w) => w.length >= 2 && w.length <= 12 && !RAW_TOKEN_STOP.has(w) && !/^\d+$/.test(w));
        return Array.from(new Set(cleaned)).slice(0, 14);
    }

    function pickNextAutonomousAction() {
        const actions = (window.ElysiaDigitalTwinRPG && window.ElysiaDigitalTwinRPG.getAvailableActionIds)
            ? window.ElysiaDigitalTwinRPG.getAvailableActionIds().filter((a) => a !== 'observe_tick')
            : ['skill_q', 'skill_w', 'skill_e', 'monster_raid', 'mana_vein', 'famine_hoard'];
        // Pure epistemic uncertainty selection: untested actions first, else highest prediction error, else least tested
        const untested = actions.find((a) => !rotorState.actionExpStats[a] || rotorState.actionExpStats[a].count === 0);
        if (untested) return untested;
        return [...actions].sort((a, b) => {
            const sa = rotorState.actionExpStats[a];
            const sb = rotorState.actionExpStats[b];
            const scoreA = (sa.avgErrorPct || 0) - sa.count * 6;
            const scoreB = (sb.avgErrorPct || 0) - sb.count * 6;
            return scoreB - scoreA;
        })[0];
    }

    function recomputeCrossSituationalVocabStats() {
        const gs = rotorState.streamGlobalStats;
        const total = Math.max(1, gs.totalEpisodes);
        Object.values(rotorState.groundedLexicon || {}).forEach((entry) => {
            if (!entry || !Array.isArray(entry.sumVec) || entry.count <= 0) return;
            const c = entry.count;
            const absentCount = total - c;
            let bestIdx = 0;
            let bestLift = -999;
            for (let i = 0; i < 6; i++) {
                const presentMean = entry.sumVec[i] / c;
                const absentMean = absentCount > 0 ? Math.max(0, (gs.globalSumVec[i] - entry.sumVec[i]) / absentCount) : 0;
                // Contrastive lift: presentMean - absentMean (words appearing everywhere drop to ~0!)
                const lift = absentCount > 0 ? (presentMean - absentMean) : presentMean * 0.55;
                if (lift > bestLift) {
                    bestLift = lift;
                    bestIdx = i;
                }
            }
            entry.dominantIdx = bestIdx;
            entry.dominantLabel = STREAM_CHANNEL_LABELS[bestIdx];
            entry.lift = Number(bestLift.toFixed(3));
            entry.specificityPct = Math.max(0, Math.min(99, Math.round(bestLift * 140)));
        });
    }

    function observeContinuousStreamEpisode(forcedActionId, optionalNovelWord) {
        if (!window.ElysiaDigitalTwinRPG || typeof window.ElysiaDigitalTwinRPG.runLiveCausalEpisode !== 'function') {
            rotorState.lastStatus = '디지털 트윈 시뮬레이션 브리지가 아직 초기화되지 않았습니다.';
            rotorState.uiDirty = true;
            return null;
        }

        const autonomous = !forcedActionId;
        const actionId = forcedActionId || pickNextAutonomousAction();

        // 1) Pre-intervention prediction strictly from past experiential vector of this action
        const prevAct = rotorState.actionExpStats[actionId];
        const hadPrior = Boolean(prevAct && prevAct.count > 0 && Array.isArray(prevAct.avgVec));
        const predVec = hadPrior ? prevAct.avgVec : [0, 0, 0, 0, 0, 0];

        // 2) Controlled Experiment: Passive Baseline (8 ticks) vs Active Intervention (14 ticks)
        const baseEp = window.ElysiaDigitalTwinRPG.runLiveCausalEpisode('observe_tick', 8);
        const ep = window.ElysiaDigitalTwinRPG.runLiveCausalEpisode(actionId, 14);
        const obsVec = Array.isArray(ep.channelVector) ? ep.channelVector : [0, 0, 0, 0, 0, 0];
        const baseVec = Array.isArray(baseEp.channelVector) ? baseEp.channelVector : [0, 0, 0, 0, 0, 0];

        // Causal lift vector (what actually changed because of intervention vs passive baseline)
        let topCausalIdx = 0;
        let topCausalVal = -1;
        const liftVec = obsVec.map((v, idx) => {
            const lift = Math.max(0, Number((v - baseVec[idx] * 0.65).toFixed(3)));
            if (lift > topCausalVal) {
                topCausalVal = lift;
                topCausalIdx = idx;
            }
            return lift;
        });

        // 3) Measure true prediction error across all 6 continuous physical channels
        let errorPct = 100;
        if (hadPrior) {
            let errSum = 0;
            for (let i = 0; i < 6; i++) {
                errSum += Math.abs(obsVec[i] - predVec[i]);
            }
            errorPct = Math.max(2, Math.min(99, Math.round((errSum / 6) * 240)));
        }

        // Update action uncertainty stats using live selfPolicy.learningAlphaFloor
        const alphaFloor = rotorState.selfPolicy ? rotorState.selfPolicy.learningAlphaFloor : 0.25;
        if (!prevAct) {
            rotorState.actionExpStats[actionId] = { count: 1, avgErrorPct: 75, avgVec: [...obsVec] };
        } else {
            const n = prevAct.count + 1;
            const alpha = Math.max(alphaFloor, 1 / n);
            prevAct.count = n;
            prevAct.avgErrorPct = Math.round(prevAct.avgErrorPct * (1 - alpha) + errorPct * alpha);
            prevAct.avgVec = prevAct.avgVec.map((v, i) => Number((v * (1 - alpha) + obsVec[i] * alpha).toFixed(3)));
        }

        // 4) Unlabeled Cross-Situational Word Discovery from raw speech + environment stream (+ optional novel word)
        const rawTokens = extractUnlabeledStreamTokens(ep.rawTextStream);
        const novelClean = optionalNovelWord ? String(optionalNovelWord).trim().slice(0, 16) : '';
        if (novelClean && !rawTokens.includes(novelClean)) rawTokens.push(novelClean);

        const gs = rotorState.streamGlobalStats;
        gs.totalEpisodes += 1;
        for (let i = 0; i < 6; i++) {
            gs.globalSumVec[i] = Number(((gs.globalSumVec[i] || 0) + obsVec[i]).toFixed(4));
        }

        rawTokens.forEach((w) => {
            const prev = rotorState.groundedLexicon[w];
            if (!prev || !Array.isArray(prev.sumVec)) {
                rotorState.groundedLexicon[w] = {
                    word: w,
                    count: 1,
                    sumVec: [...obsVec],
                    dominantIdx: topCausalIdx,
                    dominantLabel: STREAM_CHANNEL_LABELS[topCausalIdx],
                    lift: 0,
                    specificityPct: 0,
                    origin: w === novelClean ? 'novel_probe' : 'autonomous',
                };
            } else {
                prev.count += 1;
                for (let i = 0; i < 6; i++) {
                    prev.sumVec[i] = Number((prev.sumVec[i] + obsVec[i]).toFixed(4));
                }
                if (w === novelClean) prev.origin = 'novel_probe';
            }
        });
        recomputeCrossSituationalVocabStats();

        const enriched = {
            ...ep,
            autonomous,
            novelWord: novelClean || null,
            topCausalChannel: STREAM_CHANNEL_LABELS[topCausalIdx],
            liftVec,
            discoveredTokenSample: rawTokens.slice(0, 6),
            videoBridgeSummary: readUnifiedVideoBridgeSummary(),
            prediction: { hadPrior, predVec, errorPct },
        };
        rotorState.streamEpisodes.unshift(enriched);
        if (rotorState.streamEpisodes.length > 10) rotorState.streamEpisodes.length = 10;

        const friction = hadPrior ? Math.max(12, errorPct) : 68;
        recordThoughtPhase('active_intervention', `자율개입: ${ep.actionLabel.slice(0, 10)}`, friction, '#10b981');
        pushLog(
            `자율 능동실험 #${gs.totalEpisodes}`,
            `[${ep.actionLabel}] 주도변화 [${STREAM_CHANNEL_LABELS[topCausalIdx]}] · 원시토큰 ${rawTokens.length}개 교차대조 · ${hadPrior ? `예측오차 ${errorPct}%` : '최초 기준선 대조'}`
        );
        rotorState.lastStatus = `자율 능동실험 #${gs.totalEpisodes}: [${ep.actionLabel}] → 주도 인과채널 [${STREAM_CHANNEL_LABELS[topCausalIdx]}] (${hadPrior ? `예측오차 ${errorPct}%` : '초기 관측'})`;

        // Effect -> Cause: if an autonomously discovered word reaches high cross-situational specificity and isn't in external Ice memory yet, queue Wikipedia verification!
        const queueSpecMin = Math.max(18, (rotorState.selfPolicy ? rotorState.selfPolicy.specificityThreshold : 14) + 10);
        const topNewConcept = rawTokens
            .map((w) => rotorState.groundedLexicon[w])
            .filter((e) => e && e.count >= 2 && e.specificityPct >= queueSpecMin && e.origin !== 'novel_probe')
            .sort((a, b) => b.specificityPct - a.specificityPct)
            .find((e) => !rotorState.ice.some((n) => n.title.toLowerCase() === e.word.toLowerCase()));

        if (topNewConcept) {
            enqueueCausalNeed({
                dedupKey: `explore:${topNewConcept.word.toLowerCase()}`,
                action: 'explore',
                priority: 87,
                originEvent: `결과: 무라벨 교차상황 실험에서 [${topNewConcept.word}] → [${topNewConcept.dominantLabel}] 특이도 ${topNewConcept.specificityPct}% 자율 발견`,
                internalLimit: `내부 한계: 시뮬레이션 내부에서 자율 분별한 어휘 [${topNewConcept.word}]의 외부 현실 정의가 미대조 상태`,
                targetSummary: `자율 발견 어휘 [${topNewConcept.word}] 외부 현실 교차 탐색`,
                payload: { topic: topNewConcept.word, sourceTitle: null },
            });
        }

        rotorState.phaseScheduler.lastFriction = friction;
        rotorState.phaseScheduler.midTension = Math.min(130, rotorState.phaseScheduler.midTension + Math.round(friction * 0.32));
        persistState();
        rotorState.uiDirty = true;
        return enriched;
    }

    function computeSelfTelemetry() {
        const sp = rotorState.selfPolicy;
        const actEntries = Object.values(rotorState.actionExpStats || {}).filter((s) => s && s.count > 0);
        const meanErrorPct = actEntries.length > 0
            ? Math.round(actEntries.reduce((sum, s) => sum + (Number(s.avgErrorPct) || 0), 0) / actEntries.length)
            : 0;
        const recentEps = (rotorState.streamEpisodes || []).filter((e) => e && e.prediction && e.prediction.hadPrior);
        const recentErr = recentEps.slice(0, 3);
        const olderErr = recentEps.slice(3, 6);
        const avgOf = (arr) => (arr.length ? arr.reduce((s, e) => s + (e.prediction.errorPct || 0), 0) / arr.length : meanErrorPct);
        const errorTrendDelta = olderErr.length > 0 ? Math.round(avgOf(recentErr) - avgOf(olderErr)) : 0;

        const allVocab = Object.values(rotorState.groundedLexicon || {}).filter((e) => e && e.count > 0);
        const discoveredCount = allVocab.filter((e) => e.specificityPct >= sp.specificityThreshold).length;
        const signalNoiseRatio = allVocab.length > 0 ? Number((discoveredCount / allVocab.length).toFixed(2)) : 0;

        const bsNodes = rotorState.ice.filter((n) => n && n.contrastiveField && Number.isFinite(Number(n.contrastiveField.blindSpotPct)));
        const avgBlindSpotPct = bsNodes.length > 0
            ? Math.round(bsNodes.reduce((s, n) => s + Number(n.contrastiveField.blindSpotPct), 0) / bsNodes.length)
            : 0;
        const actionCoveragePct = Math.min(100, Math.round((actEntries.length / 6) * 100));

        return {
            meanErrorPct,
            errorTrendDelta,
            discoveredCount,
            totalVocabCount: allVocab.length,
            signalNoiseRatio,
            avgBlindSpotPct,
            actionCoveragePct,
            totalEpisodes: rotorState.streamGlobalStats ? rotorState.streamGlobalStats.totalEpisodes : 0,
        };
    }

    function runMetaSelfObservation(triggerSource) {
        const sp = rotorState.selfPolicy;
        const tel = computeSelfTelemetry();
        const prevAudit = rotorState.selfAuditHistory[0] || null;

        let priorEffectVerdict = null;
        let rolledBack = false;

        // 1) Verify whether the previous self-modification actually improved or worsened Elysia's own telemetry
        if (prevAudit && prevAudit.paramKey && prevAudit.metricsSnapshot) {
            const pm = prevAudit.metricsSnapshot;
            if (prevAudit.paramKey === 'learningAlphaFloor' || prevAudit.paramKey === 'interventionErrorTrigger') {
                const diff = tel.meanErrorPct - pm.meanErrorPct;
                if (diff > 6 && prevAudit.beforeVal !== undefined) {
                    sp[prevAudit.paramKey] = prevAudit.beforeVal;
                    sp.rollbacksCount += 1;
                    rolledBack = true;
                    priorEffectVerdict = `악화 감지 (예측오차 ${pm.meanErrorPct}% → ${tel.meanErrorPct}%) → [${prevAudit.paramKey}] 이전 값(${prevAudit.beforeVal})으로 자동 롤백`;
                } else if (diff < -2) {
                    priorEffectVerdict = `개선 확인 (예측오차 ${pm.meanErrorPct}% → ${tel.meanErrorPct}%) → 수정 정책 유지`;
                } else {
                    priorEffectVerdict = `유지 관측 (예측오차 ${pm.meanErrorPct}% → ${tel.meanErrorPct}%)`;
                }
            } else if (prevAudit.paramKey === 'specificityThreshold') {
                const snrOk = tel.signalNoiseRatio >= 0.22 && tel.signalNoiseRatio <= 0.68;
                priorEffectVerdict = snrOk
                    ? `어휘 신호비 안정화 (${Math.round(pm.signalNoiseRatio * 100)}% → ${Math.round(tel.signalNoiseRatio * 100)}%)`
                    : `어휘 신호비 편차 지속 (${Math.round(pm.signalNoiseRatio * 100)}% → ${Math.round(tel.signalNoiseRatio * 100)}%)`;
            } else if (prevAudit.paramKey === 'blindSpotQueueThreshold') {
                const bsDiff = tel.avgBlindSpotPct - pm.avgBlindSpotPct;
                priorEffectVerdict = bsDiff <= 0
                    ? `사각지대 감소 확인 (${pm.avgBlindSpotPct}% → ${tel.avgBlindSpotPct}%)`
                    : `사각지대 확장 관측 (${pm.avgBlindSpotPct}% → ${tel.avgBlindSpotPct}%) — 탐색 민감도 유지`;
            }
        }

        // 2) Diagnose the single largest live operational bottleneck and revise the actual runtime parameter
        let diagnosis = '';
        let paramKey = null;
        let beforeVal = null;
        let afterVal = null;
        let changeSummary = '현재 내부 정책 균형 범위 내 — 관측 유지';

        if (!rolledBack) {
            if (tel.totalEpisodes >= 2 && tel.totalVocabCount >= 4 && tel.signalNoiseRatio < 0.22 && sp.specificityThreshold > 8) {
                paramKey = 'specificityThreshold';
                beforeVal = sp.specificityThreshold;
                afterVal = Math.max(8, sp.specificityThreshold - 2);
                sp.specificityThreshold = afterVal;
                diagnosis = `어휘 신호비(${Math.round(tel.signalNoiseRatio * 100)}%)가 과도하게 낮아 유효 단어가 과배제됨`;
                changeSummary = `특이도 임계값 ${beforeVal}% → ${afterVal}% 완화 (유효 어휘 수용폭 확대)`;
            } else if (tel.totalEpisodes >= 3 && tel.totalVocabCount >= 10 && tel.signalNoiseRatio > 0.70 && sp.specificityThreshold < 34) {
                paramKey = 'specificityThreshold';
                beforeVal = sp.specificityThreshold;
                afterVal = Math.min(34, sp.specificityThreshold + 3);
                sp.specificityThreshold = afterVal;
                diagnosis = `어휘 신호비(${Math.round(tel.signalNoiseRatio * 100)}%)가 과도하게 높아 잡음어가 유입됨`;
                changeSummary = `특이도 임계값 ${beforeVal}% → ${afterVal}% 강화 (잡음어 척력 상향)`;
            } else if (tel.totalEpisodes >= 2 && tel.meanErrorPct >= 34 && tel.errorTrendDelta >= 0 && sp.learningAlphaFloor < 0.42) {
                paramKey = 'learningAlphaFloor';
                beforeVal = sp.learningAlphaFloor;
                afterVal = Number(Math.min(0.45, sp.learningAlphaFloor + 0.04).toFixed(2));
                sp.learningAlphaFloor = afterVal;
                sp.interventionErrorTrigger = Math.max(18, sp.interventionErrorTrigger - 3);
                diagnosis = `행동 예측오차(${tel.meanErrorPct}%)가 수렴하지 않고 정체됨 (추세 +${tel.errorTrendDelta}%)`;
                changeSummary = `학습률 하한 ${beforeVal} → ${afterVal} 상향 · 재실험 기준 ${sp.interventionErrorTrigger}%로 민감화`;
            } else if (tel.avgBlindSpotPct >= sp.blindSpotQueueThreshold && sp.blindSpotQueueThreshold > 18) {
                paramKey = 'blindSpotQueueThreshold';
                beforeVal = sp.blindSpotQueueThreshold;
                afterVal = Math.max(18, sp.blindSpotQueueThreshold - 3);
                sp.blindSpotQueueThreshold = afterVal;
                diagnosis = `외부 개념 평균 프리즘 사각지대(${tel.avgBlindSpotPct}%)가 기준(${beforeVal}%)을 초과함`;
                changeSummary = `사각지대 탐색 민감도 ${beforeVal}% → ${afterVal}%로 상향 (미포집 잔차 조기 포착)`;
            } else if (tel.totalEpisodes >= 4 && tel.errorTrendDelta <= -5 && sp.learningAlphaFloor > 0.14) {
                paramKey = 'learningAlphaFloor';
                beforeVal = sp.learningAlphaFloor;
                afterVal = Number(Math.max(0.12, sp.learningAlphaFloor - 0.02).toFixed(2));
                sp.learningAlphaFloor = afterVal;
                diagnosis = `행동 예측오차가 실제로 감소(${tel.errorTrendDelta}%)하며 안정 수렴 중`;
                changeSummary = `학습률 하한 ${beforeVal} → ${afterVal} 소폭 안정화 (과진동 억제)`;
            } else if (tel.actionCoveragePct < 100) {
                diagnosis = `자율 능동실험 탐색률 ${tel.actionCoveragePct}% — 미탐구 행동이 남아 있어 경험 표본 확대 필요`;
                changeSummary = `미탐구 행동 우선 실험 대기열 활성화 (현재 재실험 기준 ${sp.interventionErrorTrigger}%)`;
                enqueueCausalNeed({
                    dedupKey: `active_intervention:audit_${tel.totalEpisodes}`,
                    action: 'active_intervention',
                    priority: 86,
                    originEvent: `자기구조 진단: 행동 탐색률 ${tel.actionCoveragePct}%로 자기모델 표본 부족`,
                    internalLimit: '내부 한계: 경험하지 않은 행동의 인과 변화량을 모른 채 정책을 확정할 수 없음',
                    targetSummary: '미탐구 행동 자율 개입 실험으로 자기모델 보강',
                    payload: { actionId: null },
                });
            } else {
                diagnosis = `오차(${tel.meanErrorPct}%)·신호비(${Math.round(tel.signalNoiseRatio * 100)}%)·사각지대(${tel.avgBlindSpotPct}%)가 모두 허용 경계 내 안정`;
            }
        } else {
            diagnosis = `직전 정책 변경이 지표를 악화시켜 자동 롤백 실행`;
            changeSummary = `롤백 완료 (총 롤백 ${sp.rollbacksCount}회)`;
        }

        if (paramKey && !rolledBack) sp.revisionsCount += 1;

        const auditEntry = {
            id: (prevAudit ? prevAudit.id : 0) + 1,
            tStep: rotorState.tStepCount,
            trigger: triggerSource || 'auto',
            diagnosis,
            paramKey,
            beforeVal,
            afterVal,
            changeSummary,
            rolledBack,
            priorEffectVerdict,
            metricsSnapshot: tel,
            timestamp: new Date().toISOString(),
        };
        rotorState.selfAuditHistory.unshift(auditEntry);
        if (rotorState.selfAuditHistory.length > 10) rotorState.selfAuditHistory.length = 10;

        pushLog(`자기구조 진단 #${auditEntry.id}`, `${diagnosis} → ${changeSummary}`);
        if (triggerSource === 'manual') {
            recordThoughtPhase('self_audit', `자기진단 #${auditEntry.id}`, Math.max(18, tel.meanErrorPct), '#c084fc');
            rotorState.lastStatus = `자기구조 진단 #${auditEntry.id}: ${changeSummary}`;
        }
        persistState();
        rotorState.uiDirty = true;
        return auditEntry;
    }

    function resolveDualityPair() {
        if (rotorState.ice.length < 2) return null;
        let a = null;
        let b = null;
        if (rotorState.boundaryPair) {
            a = rotorState.ice.find((n) => n.title.toLowerCase() === rotorState.boundaryPair.aTitle.toLowerCase()) || null;
            b = rotorState.ice.find((n) => n.title.toLowerCase() === rotorState.boundaryPair.bTitle.toLowerCase()) || null;
        }
        if (!a || !b || a.title === b.title) {
            a = rotorState.ice.find((n) => n.title === rotorState.selectedIceTitle) || rotorState.ice[rotorState.ice.length - 1];
            b = rotorState.ice.find((n) => n.title !== a.title) || null;
        }
        if (!a || !b) return null;

        const tokB = new Set((b.tokens || []).map((t) => String(t).toLowerCase()));
        const sharedTokens = (a.tokens || []).filter((t) => tokB.has(String(t).toLowerCase())).slice(0, 6);
        const allAxes = getAllAxes();
        let minDiff = 999;
        let maxDiff = -1;
        let sameAxis = '인과구조';
        let diffAxis = '변화원리';
        let simSum = 0;

        allAxes.forEach((ax) => {
            const va = a.axes && a.axes[ax.key] ? a.axes[ax.key].score : 24;
            const vb = b.axes && b.axes[ax.key] ? b.axes[ax.key].score : 24;
            const d = Math.abs(va - vb);
            simSum += (100 - d);
            if (d < minDiff) {
                minDiff = d;
                sameAxis = ax.label;
            }
            if (d > maxDiff) {
                maxDiff = d;
                diffAxis = ax.label;
            }
        });
        const blurScore = Math.max(12, Math.min(92, Math.round((simSum / Math.max(1, allAxes.length)) * 0.68 + sharedTokens.length * 9)));
        return { a, b, sharedTokens, sameAxis, diffAxis, diffGap: Math.round(maxDiff), blurScore };
    }

    async function observeBoundaryDuality(topicA, topicB) {
        if (rotorState.busy) return;
        rotorState.activePurpose = `경계 통합·분화 관측: "${topicA}"와 "${topicB}"가 어디서 같아지고 동시에 어디서 달라지는지 실재 외부 지식으로 대조한다.`;
        rotorState.activeMotive = '기계와 인간, 무생물과 생물처럼 경계가 통합되면서도 다름으로 공존하는 관측구조의 원리를 확인한다.';
        rotorState.uiDirty = true;

        let nodeA = rotorState.ice.find((n) => n.title.toLowerCase() === topicA.toLowerCase()) || null;
        if (!nodeA) nodeA = await exploreTopic(topicA, { autonomous: false });
        let nodeB = rotorState.ice.find((n) => n.title.toLowerCase() === topicB.toLowerCase()) || null;
        if (!nodeB) nodeB = await exploreTopic(topicB, { autonomous: false, sourceTitle: nodeA ? nodeA.title : null });

        if (nodeA && nodeB) {
            rotorState.boundaryPair = { aTitle: nodeA.title, bTitle: nodeB.title };
            recordThoughtPhase('duality', `경계 대조: ${nodeA.title}⇄${nodeB.title}`, 48, '#2dd4bf');
            pushLog(`경계 관측 t${rotorState.tStepCount}`, `[${nodeA.title}] ⇄ [${nodeB.title}] 동일성·차이성 경계 관측 활성화`);
            persistState();
            rotorState.uiDirty = true;
        }
    }

    loadPersistedState();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bindUIOnce);
    } else {
        bindUIOnce();
    }

    window.ElysiaOutwardEpistemic = {
        step,
        exploreTopic,
        runAutonomousStep,
        runRealityProbe,
        runConstraintCheck,
        runSensoryHierarchyAnalysis,
        observeContinuousStreamEpisode,
        runMetaSelfObservation,
        runMacroConsolidation,
        injectReflectiveStimulus,
        observeBoundaryDuality,
        setAutoMode,
        setPhaseFrame,
        handleCanvasClick,
        onEnterTab,
        onLeaveTab,
        getState: () => ({
            iceCount: rotorState.ice.length,
            emergentAxisCount: rotorState.emergentAxes.length,
            tStepCount: rotorState.tStepCount,
            currentDt: rotorState.currentDt,
            uncapturedCount: rotorState.uncaptured.length,
            realityProbesCount: rotorState.realityProbes.length,
            constraintChecksCount: rotorState.constraintChecks.length,
            sensoryHierarchyChecksCount: rotorState.sensoryHierarchyChecks.length,
            groundedLexiconCount: Object.keys(rotorState.groundedLexicon || {}).length,
            streamEpisodesCount: rotorState.streamEpisodes.length,
            selfPolicy: { ...rotorState.selfPolicy },
            selfAuditCount: rotorState.selfAuditHistory.length,
            phaseFrame: rotorState.phaseFrame,
            phaseScheduler: {
                fastPhase: Math.round(rotorState.phaseScheduler.fastPhase),
                midTension: Math.round(rotorState.phaseScheduler.midTension),
                macroPressure: Math.round(rotorState.phaseScheduler.macroPressure),
                fastFires: rotorState.phaseScheduler.fastFires,
                midFires: rotorState.phaseScheduler.midFires,
                macroFires: rotorState.phaseScheduler.macroFires,
                idleSkippedTicks: rotorState.phaseScheduler.idleSkippedTicks,
            },
        }),
    };
})();
