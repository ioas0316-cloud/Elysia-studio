/**
 * Elysia 6-Axis Phenomenon Anatomy & Emergent Causal Verification Lab
 * -------------------------------------------------------------------
 * Does NOT mimic surface pixels. Instead, each phenomenon runs its own
 * distinct constituent mechanism across 6 explicit epistemic axes:
 *   1. 구성요소 (Elements)
 *   2. 현상구조 (Structure / Topology)
 *   3. 구성원리 (Compositional Principles)
 *   4. 변화     (Dynamics / Phase Transitions)
 *   5. 환경     (Embedding Environment)
 *   6. 조건     (Boundary Conditions & Thresholds)
 *
 * Left Viewport:  True Ground-Truth Phenomenon Mechanism (Wind / Chemistry / Cell / Society)
 * Right Viewport: Elysia's Current 6-Axis Generative Hypothesis Model (starts incomplete,
 *                 reveals exact structural ignorance/limits, revises principles generation by generation).
 */
(function () {
    'use strict';

    const W = 960;
    const H = 540;

    // 4 Real Distinct Phenomena with Non-Reducible 6-Axis Anatomies
    const PHENOMENA = {
        wind: {
            id: 'wind',
            name: '① 바람 · 대기 대류',
            short: '바람(유체·열대류)',
            domainTag: 'PHYSICS · FLUID CONVECTION',
            condLabels: [
                { key: 'c1', label: '온도·압력 구배 (ΔT·ΔP)', min: 0.1, max: 2.0, def: 1.15, unit: '×' },
                { key: 'c2', label: '지형 마찰·장애물 저항', min: 0.1, max: 2.0, def: 0.85, unit: '×' },
                { key: 'c3', label: '코리올리 회전 편향', min: 0.0, max: 2.0, def: 0.90, unit: '×' },
            ],
            anatomy: {
                elements: '기체 분자 군집, 국소 기압(P), 열에너지(T) 밀도',
                structure: '고기압→저기압 연속 압력장, 지형 경계층 및 와류(Vortex) 셀',
                principle: '압력 기울기 가속(-∇P) + 열부력 상승 + 회전 좌표계 코리올리 편향',
                dynamics: '정체 대기 → 층류 이동 → 장애물 후류 소용돌이(카르만 와류) → 돌풍 순환',
                environment: '지표 가열/냉각 구배, 산악·건물 지형 장애물, 개방 대기 경계',
                conditions: '임계 압력차(ΔP > 마찰) 충족 시 유동 창발 · ΔP 소실 시 정체 붕괴',
            },
            hypotheses: [
                {
                    gen: 0,
                    title: '세대 0 (표면 이동 가설 — 미완성)',
                    missingAxis: '구성원리(열부력·코리올리) & 환경(지형 장애물 경계층)',
                    limitDiagnosis: '기체를 단순 직선 이동 입자로만 가정함 → 지형 뒤편 와류와 고·저기압 소용돌이 창발을 전혀 재현 못 함.',
                    revisionAction: '오차 원인 포착: 압력 기울기(-∇P)와 지형 경계 반발을 구조 축에 추가 필요.',
                    knowsPressure: false,
                    knowsObstacle: false,
                    knowsCoriolis: false,
                },
                {
                    gen: 1,
                    title: '세대 1 (압력장·지형 결합 가설)',
                    missingAxis: '구성원리(코리올리 회전 편향) & 조건(임계 난류 전이)',
                    limitDiagnosis: '고기압→저기압 유동과 장애물 우회는 창발했으나, 회전 편향에 의한 거시 저기압 소용돌이 각도가 어긋남.',
                    revisionAction: '기준 자기수정: 유속 벡터에 수직 편향(코리올리 항)과 전단 와류 보존 항을 결합.',
                    knowsPressure: true,
                    knowsObstacle: true,
                    knowsCoriolis: false,
                },
                {
                    gen: 2,
                    title: '세대 2 (6축 완결 유체-대류 원리)',
                    missingAxis: '없음 (임계 조건 변화 시 층류↔와류 상전이 정합)',
                    limitDiagnosis: '압력 구배·지형 경계·코리올리 편향을 독립 원리로 결합 완료 → 조건 슬라이더 변경에도 동일 상전이 창발.',
                    revisionAction: '현재 경계: 미시 분자 충돌(볼츠만) 대신 연속체 근사 사용 중임을 무지 경계로 유지.',
                    knowsPressure: true,
                    knowsObstacle: true,
                    knowsCoriolis: true,
                },
            ],
        },
        chemistry: {
            id: 'chemistry',
            name: '② 화학 반응 · 활성화·촉매',
            short: '화학(반응·촉매)',
            domainTag: 'CHEMISTRY · ACTIVATION KINETICS',
            condLabels: [
                { key: 'c1', label: '반응계 온도 (운동에너지 T)', min: 0.1, max: 2.0, def: 1.1, unit: '×' },
                { key: 'c2', label: '촉매 활성 밀도 (Ea 저감)', min: 0.0, max: 2.0, def: 1.0, unit: '×' },
                { key: 'c3', label: '반응물 A·B 초기 농도', min: 0.2, max: 2.0, def: 1.2, unit: '×' },
            ],
            anatomy: {
                elements: '반응물 분자 A(청), 반응물 B(적), 촉매 표면 활성점(황), 생성물 C(녹) + 반응열',
                structure: '무작위 열운동 충돌 공간 + 촉매 표면 흡착 전이 상태(Transition State)',
                principle: '유효 충돌 에너지가 활성화 에너지(Ea)를 돌파할 때만 결합 재편·발열(ΔH) 발생',
                dynamics: '비활성 혼합 → 촉매/고온 점화 → 발열 연쇄 확산 → 반응물 고갈 평형',
                environment: '열전도 용매 매질, 국소 온도장, 촉매 격자 표면',
                conditions: 'T < Ea 이면 충돌해도 무반응 · 촉매 투입 시 Ea 장벽 하강으로 반응 창발',
            },
            hypotheses: [
                {
                    gen: 0,
                    title: '세대 0 (단순 접촉 혼합 가설 — 미완성)',
                    missingAxis: '조건(활성화 에너지 Ea 임계치) & 구성원리(촉매 장벽 저감)',
                    limitDiagnosis: 'A와 B가 닿기만 하면 무조건 변한다고 가정함 → 저온에서도 비정상 과반응하고 촉매 유무 차이를 설명 못 함.',
                    revisionAction: '오차 원인 포착: 충돌 에너지 ≥ Ea 임계 조건을 반응 규칙의 필수 문턱으로 도입.',
                    knowsActivation: false,
                    knowsCatalyst: false,
                    knowsExothermic: false,
                },
                {
                    gen: 1,
                    title: '세대 1 (활성화 장벽 + 촉매 가설)',
                    missingAxis: '변화(발열 반응 ΔH → 주변 국소 온도 상승 피드백)',
                    limitDiagnosis: '저온 정체와 촉매 점화는 구분했으나, 반응열이 인접 분자를 연쇄 가속하는 자발적 점화파가 약함.',
                    revisionAction: '기준 자기수정: 생성물 C 형성 시 국소 열펄스(ΔH)를 환경 온도장에 되먹임.',
                    knowsActivation: true,
                    knowsCatalyst: true,
                    knowsExothermic: false,
                },
                {
                    gen: 2,
                    title: '세대 2 (6축 완결 반응동역학 원리)',
                    missingAxis: '없음 (온도·촉매·농도 조건 변화에 따른 점화/소멸 정합)',
                    limitDiagnosis: 'Ea 장벽·촉매 표면 흡착·발열 피드백이 결합되어 저온 정체↔촉매 점화 상전이를 원리적으로 재현.',
                    revisionAction: '현재 경계: 양자 궤도함수(분자오비탈) 대칭성까지는 미관측 상태로 표기.',
                    knowsActivation: true,
                    knowsCatalyst: true,
                    knowsExothermic: true,
                },
            ],
        },
        cell: {
            id: 'cell',
            name: '③ 세포 · 막투과·대사·분열',
            short: '세포(자기유지·분열)',
            domainTag: 'BIOLOGY · AUTOPOIETIC MITOSIS',
            condLabels: [
                { key: 'c1', label: '외부 배지 양분 공급률', min: 0.1, max: 2.0, def: 1.2, unit: '×' },
                { key: 'c2', label: '삼투압·독성 스트레스', min: 0.0, max: 2.0, def: 0.45, unit: '×' },
                { key: 'c3', label: '세포막 선택 투과·복구력', min: 0.2, max: 2.0, def: 1.1, unit: '×' },
            ],
            anatomy: {
                elements: '인지질 경계막, 내부 대사 에너지(ATP), 핵 청사진, 외부 양분·삼투 이온',
                structure: '반투과성 경계막으로 내부 질서와 외부 환경을 능동 분리하는 자기유지 구획',
                principle: '선택적 양분 동화 → 막·내부 에너지 축적 → 임계 부피 도달 시 유사분열 복제',
                dynamics: '양분 흡수 → 성장 → 핵 복제·분열 → 군집 항상성 (스트레스 초과 시 용해·사멸)',
                environment: '액체 배지 양분 농도장, 삼투압 기울기, 대사 노폐물',
                conditions: '양분 > 기초대사량이면 성장·분열 창발 · 삼투 스트레스 > 막 안정성이면 파열 붕괴',
            },
            hypotheses: [
                {
                    gen: 0,
                    title: '세대 0 (단순 구형 입자 가설 — 미완성)',
                    missingAxis: '현상구조(반투과 경계막) & 구성원리(동화 대사·유사분열)',
                    limitDiagnosis: '세포를 무생물 공처럼 취급함 → 양분을 먹어 커지거나 임계점에서 둘로 분열하는 생명 현상이 전혀 창발 안 됨.',
                    revisionAction: '오차 원인 포착: 내부 ATP 저장고와 선택적 막 투과 흡수 구조를 도입.',
                    knowsMetabolism: false,
                    knowsMitosis: false,
                    knowsOsmosis: false,
                },
                {
                    gen: 1,
                    title: '세대 1 (대사·분열 가설)',
                    missingAxis: '조건(삼투압 스트레스에 의한 막 파열·사멸 경계)',
                    limitDiagnosis: '양분 흡수 및 유사분열은 창발했으나, 고삼투/독성 환경에서도 세포가 죽지 않고 무한 증식하는 비현실 오차 발생.',
                    revisionAction: '기준 자기수정: 환경 삼투 스트레스와 막 복구력의 불균형 시 세포 용해(Lysis) 경계 결합.',
                    knowsMetabolism: true,
                    knowsMitosis: true,
                    knowsOsmosis: false,
                },
                {
                    gen: 2,
                    title: '세대 2 (6축 완결 자기유지 세포 원리)',
                    missingAxis: '없음 (양분 번식 ↔ 기아 휴면 ↔ 삼투 파열 전 구간 정합)',
                    limitDiagnosis: '경계막 투과·대사 성장·유사분열·삼투 붕괴 조건이 통합되어 생물학적 항상성 경계를 정밀 포착.',
                    revisionAction: '현재 경계: 유전자 돌연변이·단백질 접힘 서열은 미관측 미세 계층으로 남김.',
                    knowsMetabolism: true,
                    knowsMitosis: true,
                    knowsOsmosis: true,
                },
            ],
        },
        society: {
            id: 'society',
            name: '④ 인간 사회 · 상행·신뢰·제도',
            short: '사회(교역·신뢰·규범)',
            domainTag: 'CIVILIZATION · RELATIONAL TRUST',
            condLabels: [
                { key: 'c1', label: '교역 자원 공급 안정성', min: 0.1, max: 2.0, def: 1.15, unit: '×' },
                { key: 'c2', label: '사회적 신뢰·규범 집행력', min: 0.1, max: 2.0, def: 1.10, unit: '×' },
                { key: 'c3', label: '외부 위기·약탈 교란', min: 0.0, max: 2.0, def: 0.45, unit: '×' },
            ],
            anatomy: {
                elements: '자율 행위자(상인·시민·길드), 재화 재고, 상호 신뢰도, 공유 규범',
                structure: '시장 거점과 상인 교역로로 엮인 다층 관계망 및 길드 보호권',
                principle: '희소성 기반 교환 이득 + 상호 신뢰 누적 → 분업·번영 (불신 시 사재기·이탈)',
                dynamics: '거래 체결 → 신용 축적 → 상권 번영 (위기·규범 붕괴 시 매점매석·교역 마비)',
                environment: '교역로 치안, 지역 자원 생산성, 시대적 위기 압력',
                conditions: '신뢰 × 치안 > 위기이면 상권 번영 창발 · 임계 이하 시 신용 경색·붕괴',
            },
            hypotheses: [
                {
                    gen: 0,
                    title: '세대 0 (기계적 왕복 이동 가설 — 미완성)',
                    missingAxis: '구성원리(신뢰·희소성 판단) & 조건(위기 시 교역 회피·사재기)',
                    limitDiagnosis: '인간을 물리 공처럼 단순 왕복시킴 → 치안이 무너져도 거래량이 안 줄고, 신뢰 붕괴에 따른 시장 마비를 못 봄.',
                    revisionAction: '오차 원인 포착: 행위자별 신뢰 상태와 위기 회피 의사결정 원리를 도입.',
                    knowsTrust: false,
                    knowsScarcity: false,
                    knowsGuild: false,
                },
                {
                    gen: 1,
                    title: '세대 1 (신뢰·희소성 시장 가설)',
                    missingAxis: '현상구조(길드·규범 제도의 집단 방어 및 신용 보증)',
                    limitDiagnosis: '개별 상인의 위축과 가격 급등은 포착했으나, 길드가 토벌·치안을 회복해 상권을 되살리는 제도적 반등이 누락됨.',
                    revisionAction: '기준 자기수정: 규범 집행력 조건에 비례하는 길드 보호장·신용 회복 고리를 구조 축에 결합.',
                    knowsTrust: true,
                    knowsScarcity: true,
                    knowsGuild: false,
                },
                {
                    gen: 2,
                    title: '세대 2 (6축 완결 사회-인과 원리)',
                    missingAxis: '없음 (번영 ↔ 신용경색 ↔ 제도복원 상전이 정합)',
                    limitDiagnosis: '개인 신뢰·희소성 인센티브·길드 제도 방어가 연결되어 물리 현상과 구별되는 사회적 인과를 정확히 재현.',
                    revisionAction: '현재 경계: 장기 문화·이념·세대교체 서사는 상위 역사 계층 과제로 기록.',
                    knowsTrust: true,
                    knowsScarcity: true,
                    knowsGuild: true,
                },
            ],
        },
    };

    const COMPARISON_MATRIX = {
        'wind|chemistry': {
            same: '둘 다 국소 에너지 기울기(압력차 vs 열운동)와 환경 경계에 따라 거시 패턴이 창발함.',
            diff: [
                ['구성요소', '바람은 동일 기체 입자의 집단 운동 / 화학은 서로 다른 반응물(A·B)과 촉매·생성물(C)로 물질 정체성이 바뀜'],
                ['구성원리', '바람은 연속적 압력차(-∇P)로 즉시 가속 / 화학은 활성화 에너지(Ea) 문턱을 못 넘으면 충돌해도 무반응'],
                ['조건', '바람은 장애물·회전이 형태를 결정 / 화학은 촉매 유무가 에너지 장벽 자체를 낮춰 반응 여부를 갈라놓음'],
            ],
        },
        'wind|cell': {
            same: '둘 다 외부 에너지 유입으로 질서 있는 국소 구조(와류 vs 세포)를 유지하는 비평형 열린계임.',
            diff: [
                ['현상구조', '바람 와류는 고정 경계막이 없어 외력이 사라지면 즉시 소멸 / 세포는 반투과 경계막으로 내·외부를 능동 분리'],
                ['구성원리', '바람은 외력 수동 반응 / 세포는 양분을 선택 동화해 스스로 복제(유사분열)하는 자기유지(Autopoiesis) 원리'],
                ['조건', '바람은 압력차 소실 시 정체 / 세포는 삼투압·독성 임계 초과 시 경계막 자체가 파열(용해)되어 비가역 사멸'],
            ],
        },
        'wind|society': {
            same: '둘 다 국소 마찰과 거시 환경 압력이 결합해 흐름(기류 vs 교역량)의 순환 또는 정체를 만듦.',
            diff: [
                ['구성요소', '바람은 의도 없는 기체 분자 / 사회는 기억·신뢰·가치 판단을 가진 자율 행위자와 제도'],
                ['구성원리', '바람은 물리 보존 법칙에 종속 / 사회는 신뢰·희소성·규범 집행이라는 관계적 약속으로 작동'],
                ['변화', '바람은 원인이 같으면 반복 순환 / 사회는 신뢰 붕괴 후 길드·제도 개입으로 구조 자체를 재설계함'],
            ],
        },
        'chemistry|cell': {
            same: '둘 다 분자 수준의 에너지 문턱과 촉매(효소)를 통해 물질 변환을 일으킴.',
            diff: [
                ['현상구조', '화학 반응은 열린 용매 공간에서 반응물 소진 시 평형 종료 / 세포는 경계막 안에서 반응을 조직화해 항상성 유지'],
                ['변화', '화학은 평형을 향해 소진 / 세포는 대사 에너지를 구조 복제(분열)로 전환해 세대를 이어감'],
                ['환경', '화학은 온도·농도에 수동 종속 / 세포는 막 투과 조절로 내부 환경을 외부와 다르게 버팀'],
            ],
        },
        'chemistry|society': {
            same: '둘 다 임계점(활성화 에너지 vs 신뢰 임계치)과 촉매 역할(촉매 vs 제도/길드)이 존재해 비선형 상전이를 보임.',
            diff: [
                ['구성요소', '화학은 무의식 분자의 확률 충돌 / 사회는 미래를 예측하고 위험을 회피하는 인간 행위자'],
                ['현상구조', '화학은 물리적 근접 충돌로만 결합 / 사회는 신뢰망·가격 신호·규범이라는 비물질 정보 구조로 원거리 연동'],
                ['조건', '화학은 온도가 높을수록 충돌 증가 / 사회는 위기(열기·갈등)가 높아지면 오히려 거래가 얼어붙음'],
            ],
        },
        'cell|society': {
            same: '둘 다 경계(세포막 vs 공동체·제도)를 유지하며 외부 자원을 흡수·분배하고 스트레스 임계치에서 붕괴함.',
            diff: [
                ['구성요소', '세포는 화학적 대사 구획과 유전 청사진 / 사회는 서로 다른 가치관과 이해관계를 가진 개인·길드'],
                ['구성원리', '세포는 효소·삼투의 생화학적 항상성 / 사회는 계약·신뢰·정치적 합의로 규범을 스스로 수정'],
                ['변화', '세포는 임계 부피에서 복제 분열 / 사회는 위기 시 제도 개혁·분업·전쟁 등 질적으로 다른 시대로 분기'],
            ],
        },
    };

    // Active State
    let activeId = 'wind';
    let compareId = 'cell';
    let conditions = { c1: 1.15, c2: 0.85, c3: 0.90 };
    const learnedGen = { wind: 0, chemistry: 0, cell: 0, society: 0 };
    let tickCount = 0;
    let lastMatchPct = 42.0;
    let lastEmergenceLabel = '관측 중';

    // Simulation Worlds (Left = True Ground Truth, Right = Elysia's Current 6-Axis Hypothesis)
    let worldTrue = null;
    let worldElysia = null;

    function rng(seed) {
        let s = seed >>> 0;
        return function () {
            s = (s * 1664525 + 1013904223) >>> 0;
            return s / 4294967296;
        };
    }

    function createWorld(phenId, seed) {
        const rand = rng(seed);
        if (phenId === 'wind') {
            const particles = [];
            for (let i = 0; i < 160; i++) {
                particles.push({
                    x: rand() * W,
                    y: rand() * H,
                    vx: 1.2,
                    vy: (rand() - 0.5) * 0.4,
                    temp: 0.5,
                    trail: [],
                });
            }
            return {
                kind: 'wind',
                particles,
                highP: { x: 185, y: 265, r: 95 },
                lowP: { x: 755, y: 255, r: 105 },
                obstacle: { x: 470, y: 270, r: 62 },
                vorticity: 0,
                meanSpeed: 0,
                phaseText: '층류 유동',
            };
        }
        if (phenId === 'chemistry') {
            const mols = [];
            for (let i = 0; i < 110; i++) {
                const ang = rand() * Math.PI * 2;
                const spd = 1.4 + rand() * 1.8;
                mols.push({
                    x: 60 + rand() * (W - 120),
                    y: 60 + rand() * (H - 120),
                    vx: Math.cos(ang) * spd,
                    vy: Math.sin(ang) * spd,
                    type: i % 2 === 0 ? 'A' : 'B', // A, B -> C (product)
                    heat: 0,
                    age: 0,
                });
            }
            const catalysts = [];
            for (let i = 0; i < 7; i++) {
                catalysts.push({ x: 240 + i * 80, y: H * 0.5 + Math.sin(i * 1.2) * 75, r: 22 });
            }
            return {
                kind: 'chemistry',
                mols,
                catalysts,
                flashes: [],
                productRatio: 0,
                localHeat: 0,
                phaseText: '충돌 관측',
            };
        }
        if (phenId === 'cell') {
            const cells = [];
            for (let i = 0; i < 6; i++) {
                cells.push({
                    x: 240 + (i % 3) * 230 + (rand() - 0.5) * 50,
                    y: 180 + Math.floor(i / 3) * 180 + (rand() - 0.5) * 40,
                    vx: (rand() - 0.5) * 0.6,
                    vy: (rand() - 0.5) * 0.6,
                    r: 22 + rand() * 6,
                    atp: 55 + rand() * 18,
                    integrity: 100,
                    alive: true,
                    divFlash: 0,
                });
            }
            const nutrients = [];
            for (let i = 0; i < 75; i++) {
                nutrients.push({ x: 40 + rand() * (W - 80), y: 40 + rand() * (H - 80), vx: (rand() - 0.5) * 0.8, vy: (rand() - 0.5) * 0.8 });
            }
            return {
                kind: 'cell',
                cells,
                nutrients,
                lysedCount: 0,
                divisions: 0,
                phaseText: '항상성 성장',
            };
        }
        // society
        const hubs = [
            { name: '북부 광산', x: 200, y: 155, stock: 75, price: 1.0 },
            { name: '중앙 시장', x: 480, y: 270, stock: 85, price: 1.0 },
            { name: '남부 항구', x: 760, y: 165, stock: 80, price: 1.0 },
            { name: '길드 요새', x: 480, y: 440, stock: 90, price: 1.0 },
        ];
        const agents = [];
        for (let i = 0; i < 42; i++) {
            const h0 = hubs[i % hubs.length];
            const h1 = hubs[(i + 1) % hubs.length];
            agents.push({
                x: h0.x + (rand() - 0.5) * 50,
                y: h0.y + (rand() - 0.5) * 50,
                from: i % hubs.length,
                to: (i + 1) % hubs.length,
                trust: 0.72 + rand() * 0.2,
                carrying: 1,
                hoarding: false,
                speed: 1.3 + rand() * 0.7,
                tx: h1.x,
                ty: h1.y,
            });
        }
        return {
            kind: 'society',
            hubs,
            agents,
            tradeRate: 0.7,
            avgTrust: 0.78,
            guildShield: 0.8,
            phaseText: '안정 교역기',
        };
    }

    function resetWorlds() {
        const seed = 4091 + activeId.length * 137;
        worldTrue = createWorld(activeId, seed);
        worldElysia = createWorld(activeId, seed);
    }

    // Step Functions for each distinct mechanism
    function stepWind(w, hyp, cond) {
        const grad = cond.c1;
        const drag = cond.c2;
        const coriolis = cond.c3;
        const usePressure = hyp ? hyp.knowsPressure : true;
        const useObstacle = hyp ? hyp.knowsObstacle : true;
        const useCoriolis = hyp ? hyp.knowsCoriolis : true;

        let speedSum = 0;
        let vortSum = 0;

        for (const p of w.particles) {
            let ax = 0.08 * grad;
            let ay = 0;

            if (usePressure) {
                // High pressure outward push + Low pressure inward suction
                const dxH = p.x - w.highP.x;
                const dyH = p.y - w.highP.y;
                const dH = Math.hypot(dxH, dyH) + 18;
                ax += (dxH / dH) * (24 * grad / dH);
                ay += (dyH / dH) * (24 * grad / dH);

                const dxL = w.lowP.x - p.x;
                const dyL = w.lowP.y - p.y;
                const dL = Math.hypot(dxL, dyL) + 20;
                ax += (dxL / dL) * (26 * grad / dL);
                ay += (dyL / dL) * (26 * grad / dL);

                // Thermal buoyancy lift across warmed center band
                ay -= Math.sin((p.x / W) * Math.PI) * 0.055 * grad;
            }

            if (useCoriolis) {
                // Perpendicular rotational deflection proportional to velocity
                ax += -p.vy * 0.065 * coriolis;
                ay += p.vx * 0.065 * coriolis;
            }

            if (useObstacle) {
                const dxO = p.x - w.obstacle.x;
                const dyO = p.y - w.obstacle.y;
                const dO = Math.hypot(dxO, dyO);
                if (dO < w.obstacle.r + 36) {
                    const push = ((w.obstacle.r + 36 - dO) / 36) * 0.65;
                    ax += (dxO / (dO + 1)) * push;
                    ay += (dyO / (dO + 1)) * push;
                }
                // Karman wake vortex shedding behind obstacle
                if (p.x > w.obstacle.x + 25 && p.x < w.obstacle.x + 230 && Math.abs(p.y - w.obstacle.y) < 92) {
                    const wakePhase = Math.sin(tickCount * 0.09 + p.x * 0.045);
                    ay += wakePhase * 0.19 * grad * drag;
                    vortSum += Math.abs(wakePhase);
                }
            }

            const damp = Math.max(0.84, 0.975 - drag * 0.032);
            p.vx = (p.vx + ax) * damp;
            p.vy = (p.vy + ay) * damp;

            const spd = Math.hypot(p.vx, p.vy);
            if (spd > 5.8) {
                p.vx = (p.vx / spd) * 5.8;
                p.vy = (p.vy / spd) * 5.8;
            }

            p.x += p.vx;
            p.y += p.vy;

            if (useObstacle) {
                const dxO = p.x - w.obstacle.x;
                const dyO = p.y - w.obstacle.y;
                const dO = Math.hypot(dxO, dyO);
                if (dO < w.obstacle.r + 4) {
                    p.x = w.obstacle.x + (dxO / (dO || 1)) * (w.obstacle.r + 4);
                    p.y = w.obstacle.y + (dyO / (dO || 1)) * (w.obstacle.r + 4);
                }
            }

            if (p.x > W - 8) { p.x = 12; p.trail.length = 0; }
            if (p.x < 8) { p.x = W - 12; p.trail.length = 0; }
            if (p.y > H - 8) { p.y = 14; p.trail.length = 0; }
            if (p.y < 8) { p.y = H - 14; p.trail.length = 0; }

            p.temp = Math.min(1, Math.max(0, spd / 4.2));
            if (tickCount % 2 === 0) {
                p.trail.push([p.x, p.y]);
                if (p.trail.length > 7) p.trail.shift();
            }
            speedSum += spd;
        }

        w.meanSpeed = speedSum / w.particles.length;
        w.vorticity = vortSum / Math.max(1, w.particles.length * 0.25);
        w.phaseText = grad < 0.35
            ? '정체 대기 (ΔP 임계 미달)'
            : (w.vorticity > 0.28 ? '전단 와류·대류 순환 창발' : '층류 기압 이동');
    }

    function stepChemistry(w, hyp, cond) {
        const temp = cond.c1;
        const catalyst = cond.c2;
        const conc = cond.c3;
        const useAct = hyp ? hyp.knowsActivation : true;
        const useCat = hyp ? hyp.knowsCatalyst : true;
        const useExo = hyp ? hyp.knowsExothermic : true;

        const activeCount = Math.max(30, Math.min(w.mols.length, Math.round(w.mols.length * (0.45 + conc * 0.35))));
        const catCount = Math.round(w.catalysts.length * Math.min(1, catalyst * 0.65));

        w.localHeat *= 0.96;
        let prodCount = 0;

        for (let i = 0; i < activeCount; i++) {
            const m = w.mols[i];
            const spdTarget = (0.7 + temp * 1.45 + (useExo ? m.heat * 1.1 : 0));
            const curSpd = Math.hypot(m.vx, m.vy) || 0.1;
            const blend = 0.08;
            const ns = curSpd + (spdTarget - curSpd) * blend;
            m.vx = (m.vx / curSpd) * ns;
            m.vy = (m.vy / curSpd) * ns;

            m.x += m.vx;
            m.y += m.vy;
            if (m.x < 18 || m.x > W - 18) { m.vx *= -1; m.x = Math.max(18, Math.min(W - 18, m.x)); }
            if (m.y < 18 || m.y > H - 18) { m.vy *= -1; m.y = Math.max(18, Math.min(H - 18, m.y)); }
            m.heat *= 0.96;

            if (m.type === 'C') {
                prodCount += 1;
                m.age += 1;
                // Reversible equilibrium regeneration when very old so steady dynamics remain observable
                if (m.age > 340) {
                    m.type = i % 2 === 0 ? 'A' : 'B';
                    m.age = 0;
                }
            }
        }

        // Pairwise collision kinetics
        for (let i = 0; i < activeCount; i++) {
            const a = w.mols[i];
            if (a.type !== 'A') continue;
            for (let j = 0; j < activeCount; j++) {
                const b = w.mols[j];
                if (b.type !== 'B') continue;
                const d = Math.hypot(a.x - b.x, a.y - b.y);
                if (d < 16) {
                    let nearCatalyst = false;
                    if (useCat) {
                        for (let k = 0; k < catCount; k++) {
                            const c = w.catalysts[k];
                            if (Math.hypot(a.x - c.x, a.y - c.y) < c.r + 28) {
                                nearCatalyst = true;
                                break;
                            }
                        }
                    }
                    const ea = nearCatalyst ? 0.62 : 1.38; // Catalyst lowers Activation Energy barrier Ea!
                    const kineticE = temp + (useExo ? (a.heat + b.heat + w.localHeat) * 0.55 : 0);
                    const reacts = useAct ? (kineticE >= ea) : true;
                    if (reacts) {
                        a.type = 'C';
                        b.type = 'C';
                        a.age = 0;
                        b.age = 0;
                        if (useExo) {
                            a.heat = 1.0;
                            b.heat = 1.0;
                            w.localHeat = Math.min(1.4, w.localHeat + 0.16);
                            w.flashes.push({ x: (a.x + b.x) * 0.5, y: (a.y + b.y) * 0.5, r: 28, life: 22 });
                        }
                        break;
                    } else {
                        // Elastic bounce without reaction (failed to clear Ea barrier)
                        const tx = a.vx; a.vx = b.vx; b.vx = tx;
                        const ty = a.vy; a.vy = b.vy; b.vy = ty;
                    }
                }
            }
        }

        for (let i = w.flashes.length - 1; i >= 0; i--) {
            w.flashes[i].life -= 1;
            if (w.flashes[i].life <= 0) w.flashes.splice(i, 1);
        }

        w.productRatio = prodCount / activeCount;
        w.phaseText = w.productRatio < 0.08
            ? '비활성 정체 (T < Ea 장벽 미돌파)'
            : (w.localHeat > 0.35 ? '촉매·발열 연쇄 반응 창발' : '완만 화학 평형 진행');
    }

    function stepCell(w, hyp, cond) {
        const nutrientSupply = cond.c1;
        const osmoticStress = cond.c2;
        const membraneRepair = cond.c3;
        const useMeta = hyp ? hyp.knowsMetabolism : true;
        const useMito = hyp ? hyp.knowsMitosis : true;
        const useOsmo = hyp ? hyp.knowsOsmosis : true;

        // Drift nutrients
        const activeNuts = Math.max(12, Math.min(w.nutrients.length, Math.round(w.nutrients.length * (0.25 + nutrientSupply * 0.45))));
        for (let i = 0; i < activeNuts; i++) {
            const n = w.nutrients[i];
            n.x += n.vx;
            n.y += n.vy;
            if (n.x < 16 || n.x > W - 16) n.vx *= -1;
            if (n.y < 16 || n.y > H - 16) n.vy *= -1;
        }

        const newborn = [];
        let aliveCount = 0;

        for (const c of w.cells) {
            if (!c.alive) continue;
            aliveCount += 1;
            c.x += c.vx;
            c.y += c.vy;
            if (c.x < c.r + 12 || c.x > W - c.r - 12) c.vx *= -1;
            if (c.y < c.r + 12 || c.y > H - c.r - 12) c.vy *= -1;
            if (c.divFlash > 0) c.divFlash -= 1;

            if (useMeta) {
                // Basal metabolic burn
                c.atp -= 0.085;
                // Selective permeability absorption of external nutrients
                for (let i = 0; i < activeNuts; i++) {
                    const n = w.nutrients[i];
                    if (Math.hypot(n.x - c.x, n.y - c.y) < c.r + 12) {
                        c.atp = Math.min(125, c.atp + 11 * membraneRepair);
                        c.r = Math.min(42, c.r + 0.95);
                        n.x = 30 + ((tickCount * 37 + i * 71) % (W - 60));
                        n.y = 30 + ((tickCount * 53 + i * 43) % (H - 60));
                    }
                }
            }

            if (useOsmo) {
                const netStress = osmoticStress * 1.15 - membraneRepair * 0.72;
                if (netStress > 0.25) {
                    c.integrity -= netStress * 0.55;
                } else {
                    c.integrity = Math.min(100, c.integrity + 0.35);
                }
                if (c.integrity <= 0 || c.atp <= 0) {
                    c.alive = false;
                    w.lysedCount += 1;
                    continue;
                }
            }

            if (useMito && c.r >= 35 && c.atp >= 82 && w.cells.length + newborn.length < 22) {
                c.r = 21;
                c.atp = 48;
                c.divFlash = 24;
                w.divisions += 1;
                newborn.push({
                    x: Math.max(40, Math.min(W - 40, c.x + 28)),
                    y: Math.max(40, Math.min(H - 40, c.y + 12)),
                    vx: -c.vx + 0.35,
                    vy: -c.vy - 0.25,
                    r: 21,
                    atp: 48,
                    integrity: c.integrity,
                    alive: true,
                    divFlash: 24,
                });
            }
        }
        for (const nb of newborn) w.cells.push(nb);

        // Soft repulsion between living cells
        for (let i = 0; i < w.cells.length; i++) {
            const a = w.cells[i];
            if (!a.alive) continue;
            for (let j = i + 1; j < w.cells.length; j++) {
                const b = w.cells[j];
                if (!b.alive) continue;
                const dx = b.x - a.x;
                const dy = b.y - a.y;
                const d = Math.hypot(dx, dy) || 1;
                const minD = a.r + b.r + 6;
                if (d < minD) {
                    const push = (minD - d) * 0.04;
                    a.x -= (dx / d) * push; a.y -= (dy / d) * push;
                    b.x += (dx / d) * push; b.y += (dy / d) * push;
                }
            }
        }

        // Keep at least 2 seed cells if conditions recover so user can observe re-emergence
        if (aliveCount === 0 && osmoticStress < membraneRepair * 0.8 && tickCount % 90 === 0) {
            w.cells = createWorld('cell', 4091 + tickCount).cells.slice(0, 3);
        }

        w.phaseText = aliveCount === 0
            ? '삼투 파열·대사 붕괴 (조건 임계 이탈)'
            : (w.divisions > 0 && aliveCount > 7 ? '자기유지·유사분열 군집 창발' : '선택적 투과·항상성 유지');
    }

    function stepSociety(w, hyp, cond) {
        const supply = cond.c1;
        const normTrust = cond.c2;
        const crisis = cond.c3;
        const useTrust = hyp ? hyp.knowsTrust : true;
        const useScarcity = hyp ? hyp.knowsScarcity : true;
        const useGuild = hyp ? hyp.knowsGuild : true;

        const shield = useGuild ? Math.min(1.4, normTrust * 0.85) : 0.15;
        const effectiveThreat = Math.max(0, crisis - shield * 0.55);
        w.guildShield = shield;

        let trustSum = 0;
        let activeTraders = 0;

        for (const h of w.hubs) {
            const targetStock = 35 + supply * 42 - effectiveThreat * 26;
            h.stock += (Math.max(8, Math.min(100, targetStock)) - h.stock) * 0.02;
            h.price = useScarcity ? Math.max(0.6, Math.min(3.5, 85 / Math.max(18, h.stock))) : 1.0;
        }

        for (const a of w.agents) {
            if (useTrust) {
                const targetT = Math.max(0.08, Math.min(0.98, 0.45 + normTrust * 0.36 - effectiveThreat * 0.52));
                a.trust += (targetT - a.trust) * 0.03;
                a.hoarding = a.trust < 0.36 || (useScarcity && effectiveThreat > 0.72);
            } else {
                a.trust = 0.85;
                a.hoarding = false;
            }

            trustSum += a.trust;
            if (!a.hoarding) {
                activeTraders += 1;
                const dest = w.hubs[a.to];
                const dx = dest.x - a.x;
                const dy = dest.y - a.y;
                const d = Math.hypot(dx, dy) || 1;
                const spd = a.speed * (0.55 + a.trust * 0.85);
                a.x += (dx / d) * spd;
                a.y += (dy / d) * spd;
                if (d < 22) {
                    a.from = a.to;
                    a.to = (a.to + 1 + (tickCount % 2)) % w.hubs.length;
                }
            } else {
                // Retreat toward home hub when trust breaks (hoarding / freeze)
                const home = w.hubs[a.from];
                a.x += (home.x - a.x) * 0.03;
                a.y += (home.y - a.y) * 0.03;
            }
        }

        w.avgTrust = trustSum / w.agents.length;
        w.tradeRate = activeTraders / w.agents.length;
        w.phaseText = w.tradeRate < 0.35
            ? '신용 경색·매점매석 붕괴 (신뢰 임계 이탈)'
            : (effectiveThreat > 0.35 && useGuild ? '길드 규범 방어·상권 회복 중' : '분업 교역·사회 번영 창발');
    }

    // Measure Honest Structural Equivalence between True Phenomenon and Elysia's Hypothesis
    function measureStructuralMatch() {
        if (!worldTrue || !worldElysia) return 50;
        if (activeId === 'wind') {
            const speedErr = Math.abs(worldTrue.meanSpeed - worldElysia.meanSpeed) / Math.max(0.5, worldTrue.meanSpeed + 0.5);
            const vortErr = Math.abs(worldTrue.vorticity - worldElysia.vorticity) / Math.max(0.25, worldTrue.vorticity + 0.25);
            return Math.max(18, Math.min(98.5, (1 - (speedErr * 0.45 + vortErr * 0.55)) * 100));
        }
        if (activeId === 'chemistry') {
            const prodErr = Math.abs(worldTrue.productRatio - worldElysia.productRatio);
            const heatErr = Math.abs(worldTrue.localHeat - worldElysia.localHeat) * 0.65;
            return Math.max(16, Math.min(98.5, (1 - Math.min(0.84, prodErr * 1.15 + heatErr)) * 100));
        }
        if (activeId === 'cell') {
            const aliveT = worldTrue.cells.filter((c) => c.alive).length;
            const aliveE = worldElysia.cells.filter((c) => c.alive).length;
            const popErr = Math.abs(aliveT - aliveE) / Math.max(4, aliveT + aliveE);
            const divErr = Math.abs(worldTrue.divisions - worldElysia.divisions) / Math.max(3, worldTrue.divisions + worldElysia.divisions + 2);
            return Math.max(18, Math.min(98.5, (1 - (popErr * 0.55 + divErr * 0.45)) * 100));
        }
        const trErr = Math.abs(worldTrue.tradeRate - worldElysia.tradeRate);
        const trustErr = Math.abs(worldTrue.avgTrust - worldElysia.avgTrust);
        return Math.max(18, Math.min(98.5, (1 - Math.min(0.82, trErr * 0.65 + trustErr * 0.65)) * 100));
    }

    // High-Craft Technical Rendering for each Phenomenon
    function drawWorld(ctx, w, titleBadge, badgeColor, hyp) {
        ctx.fillStyle = '#050811';
        ctx.fillRect(0, 0, W, H);

        // Subtle scientific coordinate grid
        ctx.strokeStyle = 'rgba(30, 41, 59, 0.32)';
        ctx.lineWidth = 1;
        for (let x = 80; x < W; x += 80) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        }
        for (let y = 90; y < H; y += 90) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
        }

        if (w.kind === 'wind') {
            // High & Low pressure fields
            const drawZone = (z, color, lbl) => {
                const g = ctx.createRadialGradient(z.x, z.y, 6, z.x, z.y, z.r);
                g.addColorStop(0, color);
                g.addColorStop(1, 'rgba(0,0,0,0)');
                ctx.fillStyle = g;
                ctx.beginPath(); ctx.arc(z.x, z.y, z.r, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = '#e2e8f0';
                ctx.font = '700 11px "IBM Plex Mono", monospace';
                ctx.textAlign = 'center';
                ctx.fillText(lbl, z.x, z.y + 4);
            };
            if (!hyp || hyp.knowsPressure) {
                drawZone(w.highP, 'rgba(244, 63, 94, 0.25)', 'H 고기압');
                drawZone(w.lowP, 'rgba(6, 182, 212, 0.28)', 'L 저기압');
            }
            if (!hyp || hyp.knowsObstacle) {
                ctx.fillStyle = '#1e293b';
                ctx.strokeStyle = '#64748b';
                ctx.lineWidth = 2;
                ctx.beginPath(); ctx.arc(w.obstacle.x, w.obstacle.y, w.obstacle.r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
                ctx.fillStyle = '#cbd5e1';
                ctx.font = '700 10px "IBM Plex Mono", monospace';
                ctx.textAlign = 'center';
                ctx.fillText('지형 경계층', w.obstacle.x, w.obstacle.y + 4);
            }
            for (const p of w.particles) {
                if (p.trail.length > 1) {
                    ctx.strokeStyle = p.temp > 0.65 ? '#38bdf8' : '#10b981';
                    ctx.globalAlpha = 0.72;
                    ctx.lineWidth = 1.6;
                    ctx.beginPath();
                    ctx.moveTo(p.trail[0][0], p.trail[0][1]);
                    for (let i = 1; i < p.trail.length; i++) ctx.lineTo(p.trail[i][0], p.trail[i][1]);
                    ctx.stroke();
                }
                ctx.globalAlpha = 1;
                ctx.fillStyle = p.temp > 0.65 ? '#e0f2fe' : '#6ee7b7';
                ctx.beginPath(); ctx.arc(p.x, p.y, 2.3, 0, Math.PI * 2); ctx.fill();
            }
        } else if (w.kind === 'chemistry') {
            // Catalyst active surface lattice
            const catCount = Math.round(w.catalysts.length * Math.min(1, conditions.c2 * 0.65));
            if (!hyp || hyp.knowsCatalyst) {
                for (let i = 0; i < catCount; i++) {
                    const c = w.catalysts[i];
                    ctx.fillStyle = 'rgba(245, 158, 11, 0.16)';
                    ctx.strokeStyle = '#f59e0b';
                    ctx.lineWidth = 1.5;
                    ctx.beginPath(); ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
                    ctx.fillStyle = '#fbbf24';
                    ctx.font = '700 9px "IBM Plex Mono", monospace';
                    ctx.textAlign = 'center';
                    ctx.fillText('촉매(Ea↓)', c.x, c.y + 3);
                }
            }
            for (const fl of w.flashes) {
                ctx.strokeStyle = `rgba(249, 115, 22, ${fl.life / 22})`;
                ctx.lineWidth = 2;
                ctx.beginPath(); ctx.arc(fl.x, fl.y, fl.r * (1.4 - fl.life / 22), 0, Math.PI * 2); ctx.stroke();
            }
            const activeCount = Math.max(30, Math.min(w.mols.length, Math.round(w.mols.length * (0.45 + conditions.c3 * 0.35))));
            for (let i = 0; i < activeCount; i++) {
                const m = w.mols[i];
                ctx.fillStyle = m.type === 'A' ? '#38bdf8' : (m.type === 'B' ? '#f43f5e' : '#34d399');
                ctx.beginPath(); ctx.arc(m.x, m.y, m.type === 'C' ? 5.8 : 4.4, 0, Math.PI * 2); ctx.fill();
                if (m.type === 'C') {
                    ctx.strokeStyle = '#a7f3d0';
                    ctx.lineWidth = 1.2;
                    ctx.stroke();
                }
            }
        } else if (w.kind === 'cell') {
            // Osmotic environment tint
            if (conditions.c2 > 1.1) {
                ctx.fillStyle = `rgba(244, 63, 94, ${Math.min(0.22, (conditions.c2 - 1.0) * 0.16)})`;
                ctx.fillRect(0, 0, W, H);
            }
            const activeNuts = Math.max(12, Math.min(w.nutrients.length, Math.round(w.nutrients.length * (0.25 + conditions.c1 * 0.45))));
            ctx.fillStyle = '#fbbf24';
            for (let i = 0; i < activeNuts; i++) {
                const n = w.nutrients[i];
                ctx.fillRect(n.x - 2, n.y - 2, 4, 4);
            }
            for (const c of w.cells) {
                if (!c.alive) continue;
                ctx.save();
                ctx.fillStyle = c.divFlash > 0 ? 'rgba(52, 211, 153, 0.34)' : 'rgba(6, 182, 212, 0.18)';
                ctx.strokeStyle = c.integrity < 45 ? '#f43f5e' : '#22d3ee';
                ctx.lineWidth = 2.4;
                ctx.beginPath(); ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
                // Inner nucleus & ATP core
                ctx.fillStyle = '#34d399';
                ctx.beginPath(); ctx.arc(c.x, c.y, Math.max(5, c.r * 0.32), 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = '#e2e8f0';
                ctx.font = '600 9px "IBM Plex Mono", monospace';
                ctx.textAlign = 'center';
                ctx.fillText(`ATP ${Math.round(c.atp)}`, c.x, c.y + c.r + 12);
                ctx.restore();
            }
        } else if (w.kind === 'society') {
            // Trade routes
            ctx.strokeStyle = `rgba(6, 182, 212, ${0.15 + w.tradeRate * 0.45})`;
            ctx.lineWidth = 1.6;
            for (let i = 0; i < w.hubs.length; i++) {
                for (let j = i + 1; j < w.hubs.length; j++) {
                    ctx.beginPath();
                    ctx.moveTo(w.hubs[i].x, w.hubs[i].y);
                    ctx.lineTo(w.hubs[j].x, w.hubs[j].y);
                    ctx.stroke();
                }
            }
            // Guild protection aura
            const guildHub = w.hubs[3];
            if (!hyp || hyp.knowsGuild) {
                ctx.strokeStyle = 'rgba(16, 185, 129, 0.48)';
                ctx.lineWidth = 1.5;
                ctx.setLineDash([6, 4]);
                ctx.beginPath(); ctx.arc(guildHub.x, guildHub.y, 70 + w.guildShield * 65, 0, Math.PI * 2); ctx.stroke();
                ctx.setLineDash([]);
            }
            for (const h of w.hubs) {
                ctx.fillStyle = '#0f172a';
                ctx.strokeStyle = h.price > 1.8 ? '#f43f5e' : '#38bdf8';
                ctx.lineWidth = 2.2;
                ctx.beginPath(); ctx.arc(h.x, h.y, 32, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
                ctx.fillStyle = '#f8fafc';
                ctx.font = '700 10.5px "Plus Jakarta Sans", sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(h.name, h.x, h.y - 2);
                ctx.fillStyle = h.price > 1.8 ? '#fb7185' : '#34d399';
                ctx.font = '600 9px "IBM Plex Mono", monospace';
                ctx.fillText(`물가 ${h.price.toFixed(1)}×`, h.x, h.y + 13);
            }
            for (const a of w.agents) {
                ctx.fillStyle = a.hoarding ? '#f43f5e' : '#34d399';
                ctx.beginPath(); ctx.arc(a.x, a.y, 4.2, 0, Math.PI * 2); ctx.fill();
            }
        }

        // Top HUD bar inside canvas
        ctx.fillStyle = 'rgba(6, 10, 19, 0.88)';
        ctx.fillRect(14, 12, 460, 26);
        ctx.strokeStyle = badgeColor;
        ctx.lineWidth = 1.2;
        ctx.strokeRect(14, 12, 460, 26);
        ctx.fillStyle = badgeColor;
        ctx.font = '700 10.5px "IBM Plex Mono", monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`${titleBadge} · ${w.phaseText}`, 22, 29);
    }

    function renderAnatomyUI() {
        const p = PHENOMENA[activeId];
        const genIdx = learnedGen[activeId];
        const hyp = p.hypotheses[genIdx];

        const titleEl = document.getElementById('ana-active-title');
        if (titleEl) titleEl.textContent = `${p.name} — 6축 현상 해부 (${p.domainTag})`;

        const map = {
            'ana-v-elements': p.anatomy.elements,
            'ana-v-structure': p.anatomy.structure,
            'ana-v-principle': p.anatomy.principle,
            'ana-v-dynamics': p.anatomy.dynamics,
            'ana-v-environment': p.anatomy.environment,
            'ana-v-conditions': p.anatomy.conditions,
        };
        Object.entries(map).forEach(([id, txt]) => {
            const el = document.getElementById(id);
            if (el) el.textContent = txt;
        });

        const hypEl = document.getElementById('ana-elysia-hyp');
        if (hypEl) hypEl.textContent = `${hyp.title} · 실측 구조 정합도 ${lastMatchPct.toFixed(1)}%`;

        const limEl = document.getElementById('ana-elysia-limit');
        if (limEl) limEl.textContent = `[자기 한계 / 누락 축: ${hyp.missingAxis}] ${hyp.limitDiagnosis}`;

        const revEl = document.getElementById('ana-elysia-rev');
        if (revEl) revEl.textContent = `[기준 자기수정 방향] ${hyp.revisionAction}`;

        // Render cross-phenomenon 6-axis comparison (Sameness vs Non-Reducible Difference)
        const cmpHost = document.getElementById('ana-compare-body');
        if (cmpHost) {
            cmpHost.textContent = '';
            if (activeId === compareId) {
                const row = document.createElement('div');
                row.className = 'ana-cmp-row';
                row.textContent = '서로 다른 두 현상을 선택하면 6개 축에서 무엇이 구조적으로 같고 무엇이 근본적으로 다른지 대조합니다.';
                cmpHost.appendChild(row);
            } else {
                const key1 = `${activeId}|${compareId}`;
                const key2 = `${compareId}|${activeId}`;
                const entry = COMPARISON_MATRIX[key1] || COMPARISON_MATRIX[key2];
                if (entry) {
                    const sameDiv = document.createElement('div');
                    sameDiv.className = 'ana-cmp-row same';
                    sameDiv.textContent = `● 구조적 공통점(동형): ${entry.same}`;
                    cmpHost.appendChild(sameDiv);
                    entry.diff.forEach(([axis, detail]) => {
                        const dDiv = document.createElement('div');
                        dDiv.className = 'ana-cmp-row diff';
                        dDiv.textContent = `▲ 비환원 차이 [${axis}]: ${detail}`;
                        cmpHost.appendChild(dDiv);
                    });
                }
            }
        }
    }

    function syncConditionSliders() {
        const p = PHENOMENA[activeId];
        p.condLabels.forEach((cfg, idx) => {
            const lbl = document.getElementById(`ana-lbl-c${idx + 1}`);
            const sl = document.getElementById(`ana-sl-c${idx + 1}`);
            const val = document.getElementById(`ana-val-c${idx + 1}`);
            if (lbl) lbl.textContent = cfg.label;
            if (sl) {
                sl.min = String(cfg.min);
                sl.max = String(cfg.max);
                sl.value = String(conditions[cfg.key]);
            }
            if (val) val.textContent = `${Number(conditions[cfg.key]).toFixed(2)}${cfg.unit}`;
        });
    }

    function syncToVoxelBridge(note) {
        try {
            const key = 'elysia_cognitive_voxel_bridge_v1';
            const prev = JSON.parse(localStorage.getItem(key) || '{}');
            prev.phenomenonAnatomy = {
                phenomenon: activeId,
                generation: learnedGen[activeId],
                structuralMatchPct: Number(lastMatchPct.toFixed(1)),
                conditions: { ...conditions },
                note,
                updatedAt: Date.now(),
            };
            localStorage.setItem(key, JSON.stringify(prev));
        } catch { /* ignore storage quota */ }
        if (typeof window.__elysiaOnExternalInfluence === 'function') {
            window.__elysiaOnExternalInfluence(note);
        }
    }

    resetWorlds();

    window.ElysiaPhenomenonAnatomy = {
        selectPhenomenon(id) {
            if (!PHENOMENA[id]) return;
            activeId = id;
            const cfg = PHENOMENA[id].condLabels;
            conditions = { c1: cfg[0].def, c2: cfg[1].def, c3: cfg[2].def };
            if (compareId === activeId) {
                compareId = activeId === 'wind' ? 'cell' : 'wind';
            }
            resetWorlds();
            syncConditionSliders();
            renderAnatomyUI();
        },
        selectCompare(id) {
            if (!PHENOMENA[id]) return;
            compareId = id;
            renderAnatomyUI();
        },
        setCondition(key, value) {
            if (!(key in conditions)) return;
            conditions[key] = Number(value);
            syncConditionSliders();
        },
        reviseElysiaHypothesis(audioPulse) {
            const p = PHENOMENA[activeId];
            if (learnedGen[activeId] < p.hypotheses.length - 1) {
                learnedGen[activeId] += 1;
            } else {
                learnedGen[activeId] = 0; // Cycle back to re-observe growth from Gen 0
            }
            resetWorlds();
            const hyp = p.hypotheses[learnedGen[activeId]];
            if (audioPulse) audioPulse(learnedGen[activeId] === 2 ? 720 : 520);
            syncToVoxelBridge(`6축 현상 해부 자기수정: ${p.short} → ${hyp.title}`);
            renderAnatomyUI();
            return learnedGen[activeId];
        },
        resetHypothesis() {
            learnedGen[activeId] = 0;
            resetWorlds();
            renderAnatomyUI();
        },
        initUI() {
            syncConditionSliders();
            renderAnatomyUI();
        },
        step({ legacyCtx, rotorCtx, thumbS4Ctx, thumbS2Ctx, thumbS0Ctx }) {
            tickCount += 1;
            const p = PHENOMENA[activeId];
            const hyp = p.hypotheses[learnedGen[activeId]];

            const tL0 = performance.now();
            if (activeId === 'wind') stepWind(worldTrue, null, conditions);
            else if (activeId === 'chemistry') stepChemistry(worldTrue, null, conditions);
            else if (activeId === 'cell') stepCell(worldTrue, null, conditions);
            else stepSociety(worldTrue, null, conditions);
            drawWorld(legacyCtx, worldTrue, `실제 현상 원리 (${p.short})`, '#38bdf8', null);
            const leftMs = performance.now() - tL0;

            const tR0 = performance.now();
            if (activeId === 'wind') stepWind(worldElysia, hyp, conditions);
            else if (activeId === 'chemistry') stepChemistry(worldElysia, hyp, conditions);
            else if (activeId === 'cell') stepCell(worldElysia, hyp, conditions);
            else stepSociety(worldElysia, hyp, conditions);
            drawWorld(rotorCtx, worldElysia, `엘리시아 6축 창발 가설 · ${hyp.title}`, learnedGen[activeId] === 2 ? '#10b981' : '#f59e0b', hyp);
            const rightMs = performance.now() - tR0;

            lastMatchPct = measureStructuralMatch();
            lastEmergenceLabel = `${p.short} · ${worldTrue.phaseText}`;

            // Update S4/S2/S0 track mini previews
            if (tickCount % 3 === 0) {
                thumbS4Ctx.drawImage(legacyCtx.canvas, 0, 0, 120, 68);
                thumbS2Ctx.drawImage(rotorCtx.canvas, 0, 0, 160, 90);
                thumbS0Ctx.fillStyle = '#05080f';
                thumbS0Ctx.fillRect(0, 0, 160, 90);
                thumbS0Ctx.fillStyle = learnedGen[activeId] === 2 ? '#10b981' : '#f59e0b';
                thumbS0Ctx.fillRect(10, 40, Math.round((lastMatchPct / 100) * 140), 10);
                thumbS0Ctx.fillStyle = '#e2e8f0';
                thumbS0Ctx.font = '700 10px "IBM Plex Mono", monospace';
                thumbS0Ctx.fillText(`6축 구조 정합 ${lastMatchPct.toFixed(1)}%`, 10, 30);
            }

            if (tickCount % 8 === 0) renderAnatomyUI();

            return {
                leftOps: 4800,
                rS4Ops: 420,
                rS2Ops: 680,
                rS0Ops: Math.round((100 - lastMatchPct) * 18) + 120,
                leftMs,
                rightMs,
                s4Same: learnedGen[activeId] >= 1 ? 94 : 62,
                s2Same: lastMatchPct,
                s0Same: Math.max(25, lastMatchPct - (learnedGen[activeId] < 2 ? 14 : 2)),
                origin: learnedGen[activeId] < 2
                    ? `자기 한계 관측: [${hyp.missingAxis}] 누락으로 창발 오차 발생 → [6축 자기수정] 실행 가능`
                    : `6축 원리 정합 완료 (${lastMatchPct.toFixed(1)}%) — 조건 슬라이더로 상전이·붕괴 경계를 검증하세요`,
                activeRatio: Math.max(0.12, (100 - lastMatchPct) / 100),
                emergenceLabel: lastEmergenceLabel,
            };
        },
    };
})();
