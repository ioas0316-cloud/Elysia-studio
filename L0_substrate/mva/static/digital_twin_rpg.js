/**
 * Elysia Deep Causal Digital-Twin Engine
 * ----------------------------------------------------------------------------
 * Unifies TWO deeply coupled causal architectures on a single Spatiotemporal Scale-Rotor:
 *
 *  1. 5-STAT GENERATIVE PERSONA TENSOR (STR · AGI · INT · WIS · VIT):
 *     Stats are NOT shallow RPG numbers. Every character's Personality, Value Orientation,
 *     Sensory Sensitivity, Impatience Threshold, Quirk/Hobby, Facial Expression, Speech Tone,
 *     Combat Kinematics, and Political/Economic Reaction are ALL continuously derived from
 *     their 5-Stat Tensor:
 *       - STR (힘)   : 우직한 돌파 · 무력/권위/세력 지향 · 방어적 벽 또는 폭력적 제압 · 취미(대장간·힘겨루기)
 *       - AGI (민첩) : 성급·현실적 즉결형 · 지체되면 답답함 표출 · 극도로 예민한 감각 · 취미(지름길 정찰·단검 손장난)
 *       - INT (지식) : 인과·이권 구조 분석 · 마나/경제/정치 판세 계산 · 전략/음모 설계 · 취미(마나광석 감정·장부 해독)
 *       - WIS (지혜) : 장기 통찰·균형 중재 · 시대/생태/신뢰 흐름 관조 · 취미(고문서 관조·약초 채집·차 우려내기)
 *       - VIT (체력) : 불굴의 버팀목 · 흉년·장기전 속 공동체 수호 끈기 · 취미(성벽 보수·구호 식량 비축)
 *     Drag ANY 5-stat slider for World B and watch Personality, Hobby, Speed, Expression,
 *     Dialogue & Macro Choices diverge organically from Baseline World A!
 *
 *  2. REAL MULTI-STAGE WORLD CAUSAL CHAIN ENGINE (S0 Incident -> S1 Economy -> S2 Guild -> S3 Politics -> S4 Era):
 *     - Catalyst ① 몬스터 창발 : 마을 교역로 몬스터 출현 → 상인 마차 피해 → 상행 위축·물가 폭등 → 길드 토벌령 공고 → 군수 상단 이권 팽창
 *     - Catalyst ② 마나광석 발견 : 벚꽃 성역 지하 광맥 노출 → 상단·공방 몰림 → 귀족/심연 첩보·정치 음모 → 채굴권 견제·국지전
 *     - Catalyst ③ 흉년·투기 매점 : 이상 기후 수확 급감 → 투기 세력 매점매석 이득 → 민심 폭발 → 성향별(AGI 직결/STR 응징/WIS 중재/INT 대안) 분기
 *
 *  3. 2,400-PETAL CHERRY BLOSSOM FRAME-ROTOR + LOCAL INTERVENTION DEFORMATION + ψ QUANTUM UNOBSERVED LOCK + PARALLEL ENDINGS.
 */

(function initElysiaDigitalTwinRPG() {
    const W = 960;
    const H = 540;
    const TREE_X = W * 0.5;
    const TREE_Y = H * 0.40;
    const VEIN_X = W * 0.5;
    const VEIN_Y = 74;
    const ROAD_Y = H - 56;
    const BLOSSOM_COUNT = 420;
    const BLOSSOM_ROTOR_PHASES = 8;
    const BLOSSOM_CANVAS_SIZE = 270;
    const OBSERVER_RADIUS = 260;

    function makeCanvas(w, h) {
        const c = document.createElement('canvas');
        c.width = w;
        c.height = h;
        return c;
    }

    const s4Cache = makeCanvas(W, H);
    const s4Ctx = s4Cache.getContext('2d', { alpha: false });

    // Preload High-Craft Character Portrait Artworks (Eternal Return Tactical MOBA Style)
    const PORTRAIT_URLS = {
        aria: '/src/assets/images/portrait_aria_knight_1795632351917.jpg',
        kael: '/src/assets/images/portrait_kael_mage_1795632353296.jpg',
        volk: '/src/assets/images/portrait_volk_brawler_1795632355315.jpg',
        orion: '/src/assets/images/portrait_orion_commander_1795632356209.jpg',
        sera: '/src/assets/images/portrait_sera_assassin_1795632357108.jpg',
        lina: '/src/assets/images/portrait_lina_alchemist_1795632357109.jpg',
    };
    const portraitImages = {};
    Object.entries(PORTRAIT_URLS).forEach(([id, url]) => {
        const img = new Image();
        img.decoding = 'async';
        img.src = url;
        portraitImages[id] = img;
    });

    const QWER_SKILLS = {
        q: { key: 'Q', name: '서리 창격', elem: 'frost', cdTicks: 145, spCost: 14, color: '#38bdf8', desc: '직선 관통 서리창' },
        w: { key: 'W', name: '전술 도약', elem: 'fire', cdTicks: 270, spCost: 20, color: '#fb923c', desc: '돌진·보호막·충격파' },
        e: { key: 'E', name: '뇌전 속박진', elem: 'volt', cdTicks: 390, spCost: 26, color: '#facc15', desc: '원형 장판·속박(CC)' },
        r: { key: 'R', name: '성역 절대영도', elem: 'aether', cdTicks: 810, spCost: 40, color: '#34d399', desc: '궁극기·광역 심판+치유' },
        space: { key: 'SP', name: '전술 회피', elem: 'frost', cdTicks: 180, spCost: 0, color: '#94a3b8', desc: '긴급 구르기 회피' },
    };

    function detRand(seed) {
        const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
        return x - Math.floor(x);
    }

    // ========================================================================
    // 1. 2,400-Petal Cherry Blossom Tree & 8-Phase O(1) Frame-Rotor
    // ========================================================================
    const blossomPetals = [];
    for (let i = 0; i < BLOSSOM_COUNT; i++) {
        const ang = detRand(i * 3.1 + 1) * Math.PI * 2;
        const rad = Math.sqrt(detRand(i * 5.7 + 2)) * 90;
        const shade = detRand(i * 9.3 + 4);
        blossomPetals.push({
            rx: Math.cos(ang) * rad * 1.15,
            ry: Math.sin(ang) * rad * 0.72 - 40,
            size: 2.6 + detRand(i * 4.3 + 3) * 2.8,
            phase: detRand(i * 7.1 + 5) * Math.PI * 2,
            sway: 1.4 + detRand(i * 2.9 + 6) * 2.3,
            color: shade > 0.65 ? '#fbcfe8' : shade > 0.28 ? '#f472b6' : '#f9a8d4',
        });
    }

    function drawCherryTreeDirect(ctx, cx, cy, windPhase) {
        ctx.strokeStyle = '#4a3531';
        ctx.lineCap = 'round';
        ctx.lineWidth = 10;
        ctx.beginPath();
        ctx.moveTo(cx, cy + 52);
        ctx.quadraticCurveTo(cx - 4, cy + 14, cx + 2, cy - 12);
        ctx.stroke();

        const branches = [[-58, -46], [-34, -70], [-8, -78], [26, -72], [60, -44], [-72, -20], [70, -18]];
        ctx.lineWidth = 4;
        for (let b = 0; b < branches.length; b++) {
            const [bx, by] = branches[b];
            const sway = Math.sin(windPhase + b * 0.8) * 2.1;
            ctx.beginPath();
            ctx.moveTo(cx, cy - 6);
            ctx.quadraticCurveTo(cx + bx * 0.5, cy + by * 0.45, cx + bx + sway, cy + by);
            ctx.stroke();
        }
        for (let i = 0; i < BLOSSOM_COUNT; i++) {
            const p = blossomPetals[i];
            const wx = Math.sin(windPhase + p.phase) * p.sway;
            const wy = Math.cos(windPhase * 0.8 + p.phase) * (p.sway * 0.55);
            ctx.fillStyle = p.color;
            ctx.fillRect(cx + p.rx + wx, cy + p.ry + wy, p.size, p.size * 0.82);
        }
    }

    // Lazy-build blossom rotor canvases ONLY when Tab 2 is actually rendered (zero idle RAM/VRAM on other tabs!)
    const blossomRotorFrames = [];
    function ensureBlossomRotorFrames() {
        if (blossomRotorFrames.length > 0) return;
        for (let f = 0; f < BLOSSOM_ROTOR_PHASES; f++) {
            const fc = makeCanvas(BLOSSOM_CANVAS_SIZE, BLOSSOM_CANVAS_SIZE);
            const fctx = fc.getContext('2d');
            drawCherryTreeDirect(fctx, BLOSSOM_CANVAS_SIZE * 0.5, BLOSSOM_CANVAS_SIZE * 0.62, (f / BLOSSOM_ROTOR_PHASES) * Math.PI * 2);
            blossomRotorFrames.push(fc);
        }
    }

    // ========================================================================
    // 2. 5-STAT GENERATIVE PERSONA ENGINE (STR · AGI · INT · WIS · VIT -> ALL TRAITS)
    // ========================================================================
    const STAT_ARCHETYPES = {
        str: {
            code: 'STR', name: '힘',
            temperament: '우직한 정면 돌파 · 무력·권위 지향',
            sensory: '위협을 정면 압도로 해결하려 하며 세력·방어선 유지에 집착',
            hobby: '대장간 무기 단련 · 전선 순찰 · 힘겨루기',
            valueAxis: '권위·무력 방어',
        },
        agi: {
            code: 'AGI', name: '민첩',
            temperament: '성격이 급한 현실 즉결형 · 속도 중시',
            sensory: '반응·감각 극예민 — 상황이 지체되면 곧바로 답답함과 초조함 표출',
            hobby: '지름길 정찰 · 단검 손장난 · 속독 첩보',
            valueAxis: '신속·실리 즉결',
        },
        int: {
            code: 'INT', name: '지식',
            temperament: '인과·이권 구조 분석형 · 냉철한 설계자',
            sensory: '감정보다 손익·자원·정치적 역학 구조를 먼저 분해해 포착',
            hobby: '마나광석 순도 감정 · 상단 장부 해독 · 원소 배합 기록',
            valueAxis: '구조·이권 설계',
        },
        wis: {
            code: 'WIS', name: '지혜',
            temperament: '장기 통찰·균형 중재형 · 공감적 관조',
            sensory: '개인의 갈등 너머 마을·생태·시대의 연쇄 파장을 읽어냄',
            hobby: '고문서 관조 · 약초 채집 · 차 우려내며 경청',
            valueAxis: '조화·장기 균형',
        },
        vit: {
            code: 'VIT', name: '체력',
            temperament: '불굴의 버팀목 · 공동체 지구력 수호',
            sensory: '위기와 흉년 속에서도 공황에 빠지지 않고 버티며 타인을 감쌈',
            hobby: '성벽 보수 · 구호 식량 비축 · 야영지 관리',
            valueAxis: '생존·공동체 수호',
        },
    };

    function derivePersonaFrom5Stats(stats, valueBias = 1.0, empathyConn = 1.0) {
        const s = stats;
        const pairs = [
            ['str', s.str], ['agi', s.agi], ['int', s.int], ['wis', s.wis], ['vit', s.vit],
        ].sort((a, b) => b[1] - a[1]);

        const domKey = pairs[0][0];
        const secKey = pairs[1][0];
        const dom = STAT_ARCHETYPES[domKey];
        const sec = STAT_ARCHETYPES[secKey];

        // ValueBias shifts Dominance vs Protection smoothly across World B
        const domShift = (valueBias - 1.0) * 0.42;
        const dominance = Math.max(0.05, Math.min(0.98, (s.str * 0.55 + s.int * 0.25 + s.agi * 0.20) / 100 + domShift));
        const protect = Math.max(0.05, Math.min(0.98, (s.vit * 0.52 + s.wis * 0.48) / 100 - domShift * 0.75));
        const urgency = Math.max(0.1, Math.min(0.99, (s.agi * 0.78 + s.str * 0.22) / 100)); // High AGI = impatient/urgent!
        const analytical = Math.max(0.1, Math.min(0.99, (s.int * 0.70 + s.wis * 0.30) / 100));
        const trustBase = Math.max(0.1, Math.min(0.99, ((s.wis * 0.55 + s.vit * 0.45) / 100) * empathyConn));

        // Derived concrete gameplay kinematics directly from 5 stats!
        const moveSpeed = 0.16 + (s.agi / 100) * 0.22;
        const cooldownScale = Math.max(0.55, 1.32 - (s.agi / 100) * 0.65);
        const dmgScale = 0.72 + (s.str * 0.45 + s.int * 0.35) / 100;
        const maxHp = Math.round(75 + s.vit * 0.65);
        const patienceTicks = Math.round(135 - urgency * 80); // High AGI snaps faster when stagnant!

        return {
            domKey,
            secKey,
            temperament: `${dom.temperament} (+${sec.name} 보조)`,
            sensory: dom.sensory,
            hobby: `${dom.hobby.split('·')[0].trim()} · ${sec.hobby.split('·')[1] ? sec.hobby.split('·')[1].trim() : sec.hobby.split('·')[0].trim()}`,
            valueAxis: `${dom.valueAxis} / ${sec.valueAxis}`,
            dominance,
            protect,
            urgency,
            analytical,
            trustBase,
            moveSpeed,
            cooldownScale,
            dmgScale,
            maxHp,
            patienceTicks,
        };
    }

    // Inverse Mechanism Generation: Reconstruct Past -> Present Life/Routine -> Relational Web -> Future Becoming
    const PAST_ORIGIN_MAP = {
        str: {
            base: '변경 수비대 대장간과 거친 최전선에서 자라며 "힘과 권위가 무너지면 질서도 무너진다"는 현실을 몸으로 배움',
            agi: '수비대 시절 한 박자 늦은 지원 때문에 동료를 잃은 뒤, 압도적인 힘으로 가장 먼저 돌파해야 살아남는다고 각인됨',
            int: '무력만으로는 세력을 지킬 수 없음을 깨닫고, 무인의 힘 위에 전략과 권력 구조를 얹어 자랐음',
            wis: '수많은 전투의 폐허를 목격하며 힘은 약탈이 아니라 방어선을 세우는 방패로 써야 한다는 규율을 세움',
            vit: '폭풍우와 야습 속에서도 무너지지 않는 성벽 옆에서 단련하며 우직하게 끝까지 버티는 기질을 형성함',
        },
        agi: {
            base: '난세의 교역로와 뒷골목에서 자라며 "망설이는 순간 전부 빼앗긴다"는 극도로 예민한 즉결 감각이 각인됨',
            str: '약탈당하던 어린 시절의 무력감을 씻기 위해, 누구보다 빠르게 움직여 힘으로 상황을 단숨에 정리하는 습관이 붙음',
            int: '복잡한 첩보전과 밀거래 사이에서 살아남으며 눈치·반응속도·실리 계산이 동시에 극대화됨',
            wis: '성급함 때문에 큰 실수를 겪은 뒤에도 본능은 빠르지만, 가끔은 큰 판을 돌아보려는 균형 감각이 남음',
            vit: '장거리 파발과 척후 임무를 밤새 뛰며 빠른 기동력과 질긴 현장 생존력을 함께 몸에 익힘',
        },
        int: {
            base: '상단 장부와 고대 마나 문헌 속에서 자라며 감정보다 이권·자원·인과의 법칙이 세상을 움직인다는 걸 체득함',
            str: '단순한 학자는 권력자에게 이용당한다는 걸 깨달아, 자신의 설계를 직접 관철할 무력과 결단력을 키움',
            agi: '시세와 전황이 분 단위로 뒤집히는 현장에서 즉각 판세를 해독하고 선수를 치는 현실적 계산력을 얻음',
            wis: '기록 속 수많은 왕조의 흥망을 읽으며 단기 이익 너머 생태와 시대의 장기 구조를 해석하게 됨',
            vit: '수년간 밤새 연구와 현장 측량을 병행하며 흔들리지 않는 집중력과 지구력을 쌓음',
        },
        wis: {
            base: '대흉년과 전란의 여파를 겪은 마을에서 서로를 살려낸 기억이 남아, 개인보다 관계와 시대의 균형을 중시하게 됨',
            str: '선한 의지만으로는 마을을 지킬 수 없음을 겪고, 평화를 지키기 위한 단호한 결단과 힘을 겸비함',
            agi: '위기가 번지기 전에 미세한 조짐을 눈치채고 먼저 움직여 갈등을 진화하는 감각을 기름',
            int: '약초·기후·교역의 연결 고리를 체계적으로 공부해 통찰을 실제 제도 설계로 옮길 줄 알게 됨',
            vit: '흉년과 역병 속에서도 끝까지 마을 곁을 지킨 어른들의 등을 보고 묵묵한 인내를 물려받음',
        },
        vit: {
            base: '변방 성벽과 구호 창고를 지키며 살아온 경험 덕분에, 어떤 재난이 와도 공황에 빠지지 않고 자리를 버티는 기질이 뿌리내림',
            str: '성벽을 두드리는 몬스터와 약탈자를 맨몸으로 막아내며 묵직한 방어 무력과 책임감을 키움',
            agi: '위급할 때 구호 물자와 다친 사람을 누구보다 빠르게 옮기며 현장 대응 감각을 익힘',
            int: '식량 비축량과 보급선을 꼼꼼히 관리하며 생존을 위한 현실적인 자원 배분 감각을 터득함',
            wis: '오랜 시간 마을 사람들과 동고동락하며 공동체의 마음을 다독이고 묶어내는 포용력을 얻음',
        },
    };

    function deriveLifeTrajectory(c, world) {
        const p = c.persona;
        const s = c.stats;
        const dom = p.domKey;
        const sec = p.secKey;
        const stress = Math.max(0, Math.min(1, 1 - c.hp / Math.max(1, c.maxHp)));

        // 1. Inverse-derived Past Origin
        const pastOrigin = (PAST_ORIGIN_MAP[dom] && PAST_ORIGIN_MAP[dom][sec]) || PAST_ORIGIN_MAP[dom].base;

        // 2. Present Occupation, After-Work Routine (drinking / workout / research / tea & relief), & Core Meaning
        let occupation = '';
        let afterWork = '';
        let meaning = '';
        if (dom === 'str') {
            occupation = sec === 'int' ? '세력 전략 사령관 · 무장 규율 감독' : '최전선 중장 돌파대장 · 성채 경비 총괄';
            afterWork = stress > 0.42
                ? '임무 직후 갑옷 땀도 식히지 않은 채 선술집에서 독한 맥주를 들이키며 힘겨루기로 울분을 푼다'
                : '퇴근 후 연병장에서 쇠추와 대검을 휘두르며 근력 운동을 마친 뒤, 동료들과 투박하게 술잔을 기울인다';
            meaning = '확실한 힘과 규율로 내 사람과 세력의 방어선을 끝까지 지켜내는 것';
        } else if (dom === 'agi') {
            occupation = sec === 'int' ? '고속 첩보 해결사 · 상단 긴급 정찰관' : '변경 쾌속 척후병 · 전술 기동 타격수';
            afterWork = stress > 0.35
                ? '답답한 회의가 끝나자마자 선술집 바에 앉아 독한 술을 한 번에 털어 넣고 단검을 돌리며 다음 의뢰를 재촉한다'
                : '일과가 끝나면 지름길 지붕을 타고 야간 러닝·민첩 훈련을 한 뒤, 선술집 구석에서 시장 소문을 수집하며 한 잔 한다';
            meaning = '지체와 탁상공론을 끊어내고 지금 당장 눈앞의 문제를 내 손으로 해결하는 쾌감';
        } else if (dom === 'int') {
            occupation = sec === 'str' ? '길드 권력·군수 설계관 · 마도 전략가' : '마나광석 감정사 · 상단 경제·인과 분석가';
            afterWork = world.manaVein.discovered
                ? '퇴근 후에도 서재 등불 아래서 마나광맥 순도와 귀족 세력 장부를 대조하며 진한 커피를 마신다'
                : '일과를 마치면 조용한 공방에서 원소 배합 노트를 정리하고 독서·체스로 다음 판의 수를 계산한다';
            meaning = '혼돈처럼 보이는 세계의 숨은 인과와 이권 구조를 해독해 판 전체를 설계하는 것';
        } else if (dom === 'wis') {
            occupation = sec === 'int' ? '성역 협약 중재자 · 생태·제도 연구관' : '치유 약초사 · 길드·마을 원로 상담역';
            afterWork = world.famine.active
                ? '해 질 녘 구호소에서 약초를 달이고 따뜻한 차를 나누며, 불안한 주민들의 이야기를 늦게까지 경청한다'
                : '퇴근 후 벚꽃나무 아래서 차를 우려내고 고문서를 읽으며, 동료들의 갈등을 부드럽게 조율한다';
            meaning = '승패와 탐욕의 소용돌이 속에서도 사람과 자연, 시대가 함께 숨 쉴 균형을 잇는 것';
        } else {
            occupation = sec === 'str' ? '성벽 방어 공병대장 · 구호 호송 지휘관' : '마을 구호 창고 총괄 · 야영지 생존 관리자';
            afterWork = '해가 져도 성벽 균열과 비상 식량을 한 번 더 점검한 뒤, 숙소에서 땀을 씻고 동료들과 묵직한 스튜를 나눠 먹는다';
            meaning = '누군가 화려하게 빛나지 않아도 모두가 내일 아침 무사히 눈뜰 수 있는 토대를 버텨내는 것';
        }

        // 3. Relational & Co-Movement Web (Who they resonate with & who they clash with right now)
        let bestPartner = null;
        let bestScore = -999;
        let worstRival = null;
        let worstScore = 999;
        for (const other of world.chars) {
            if (other.id === c.id) continue;
            const sameTeamBonus = other.team === c.team ? 32 : -18;
            const statDist = (
                Math.abs(other.stats.str - s.str) +
                Math.abs(other.stats.agi - s.agi) +
                Math.abs(other.stats.int - s.int) +
                Math.abs(other.stats.wis - s.wis) +
                Math.abs(other.stats.vit - s.vit)
            ) / 5;
            const paceClash = Math.abs(other.stats.agi - s.agi) > 35 ? -22 : 8;
            const score = sameTeamBonus + (55 - statDist * 0.7) + paceClash;
            if (score > bestScore) { bestScore = score; bestPartner = other; }
            if (score < worstScore) { worstScore = score; worstRival = other; }
        }
        const partnerPct = Math.max(38, Math.min(97, Math.round(52 + bestScore * 0.52)));
        const partnerAct = dom === 'str' || dom === 'vit'
            ? '방어선 합동 훈련·퇴근 후 식사 동행'
            : dom === 'agi'
                ? '선술집 정보 교환·즉결 기동 협공'
                : dom === 'int'
                    ? '장부·전술 공동 설계'
                    : '마을 중재·차담 동행';
        const clashReason = worstRival
            ? (Math.abs(worstRival.stats.agi - s.agi) > 30
                ? '속도·성급함 템포 충돌'
                : worstRival.persona.dominance > 0.65 !== p.dominance > 0.65
                    ? '권위·지배 vs 보호 가치 충돌'
                    : '이권·전술 노선 마찰')
            : '균형 유지';
        const relationalWeb = bestPartner && worstRival
            ? `동행 공명: ${bestPartner.name}(${partnerPct}% · ${partnerAct}) │ 긴장·마찰: ${worstRival.name}(${clashReason})`
            : '주변 인물과 위상 정렬 중';

        // 4. Future Becoming (Coupled with Active World B Events + Era!)
        let futureBecoming = '';
        if (world.monsters.length > 0) {
            if (dom === 'str') futureBecoming = '교역로 토벌령의 영웅으로 군사적 권위를 쥐어 변경 군벌 사령관으로 각성 예정';
            else if (dom === 'agi') futureBecoming = '느린 길드 행정을 떠나 독자적인 고속 토벌 해결사 길드를 창설할 예정';
            else if (dom === 'int') futureBecoming = '토벌 군수 보급과 상단 호위 보험 제도를 설계해 도시 경제를 좌우할 예정';
            else if (dom === 'wis') futureBecoming = '몬스터 창발의 생태 원인을 규명해 인간과 성역의 공존 경계를 새로 그릴 예정';
            else futureBecoming = '피해 상인과 난민을 품는 변경 요새 수호 단장으로 추대될 예정';
        } else if (world.manaVein.discovered) {
            if (dom === 'int') futureBecoming = '북부 마나광맥 특허와 대륙 상단 동맹을 쥔 그림자 재상으로 도약 예정';
            else if (dom === 'str') futureBecoming = '광맥 채굴권을 무력으로 장악하는 철권 영주 혹은 전쟁 사령관이 될 예정';
            else if (dom === 'agi') futureBecoming = '첩보전과 광석 밀수망 한복판에서 가장 비싼 값을 부르는 자유 청부업자가 될 예정';
            else if (dom === 'wis') futureBecoming = '마나 전쟁을 막는 대륙 중립 공명 조약의 대표 중재자로 역사에 남을 예정';
            else futureBecoming = '광산 노동자와 마을 안전을 지키는 자치 조합 위원장으로 성장 예정';
        } else if (world.famine.active) {
            if (dom === 'agi') futureBecoming = '매점매석 창고를 직접 털어 분배하는 현실주의 의적·혁명 선봉으로 기울 예정';
            else if (dom === 'str') futureBecoming = '비상 계엄으로 투기꾼을 응징하고 식량을 강제 배급하는 철혈 집정관이 될 예정';
            else if (dom === 'int') futureBecoming = '마나 온실과 대체 교역로를 구축해 기근 경제 구조를 근본 개혁할 설계자가 될 예정';
            else if (dom === 'wis') futureBecoming = '계층 갈등을 봉합하고 상호부조 공동체 시대를 여는 현자 지도자가 될 예정';
            else futureBecoming = '끝까지 구호소를 지켜내 마을 사람들이 가장 신뢰하는 촌장·수호자가 될 예정';
        } else {
            if (dom === 'str') futureBecoming = `${world.society.eraName} 속에서 최정예 수호 기사단을 이끄는 무력 중심축으로 성장 예정`;
            else if (dom === 'agi') futureBecoming = '대륙 각지의 난제를 가장 먼저 해결하는 전설적 기동 해결사로 이름날 예정';
            else if (dom === 'int') futureBecoming = '마나 공학과 상단 정치를 결합한 차세대 학술원장·전략가로 도약 예정';
            else if (dom === 'wis') futureBecoming = '세력 간 불신을 녹이는 성역 대현자·외교 중재자로 자리매김 예정';
            else futureBecoming = '어떤 시대가 와도 도시의 일상을 지탱하는 든든한 길드 총괄로 남을 예정';
        }

        return { pastOrigin, occupation, afterWork, meaning, relationalWeb, futureBecoming };
    }

    function composeProbeReply(c, world, questionText) {
        const q = String(questionText || '').trim();
        const life = deriveLifeTrajectory(c, world);
        const dom = c.persona.domKey;
        const tonePrefix = dom === 'agi'
            ? '아, 결론부터 짧게 말할게.'
            : dom === 'str'
                ? '복잡하게 돌릴 필요 없어.'
                : dom === 'int'
                    ? '인과 구조로 정리해 주지.'
                    : dom === 'wis'
                        ? '잠시 숨을 고르고 얘기해 볼까.'
                        : '천천히 들려줄게, 걱정 마.';

        let answer = '';
        let causeTag = '';
        if (/과거|어째서|왜|이유|어릴|배경/.test(q)) {
            answer = `${tonePrefix} ${life.pastOrigin}. 그래서 지금도 ${c.persona.valueAxis} 쪽으로 몸이 먼저 움직여.`;
            causeTag = `역인과 도출 (${STAT_ARCHETYPES[dom].code} ${c.stats[dom]} + ${STAT_ARCHETYPES[c.persona.secKey].code} ${c.stats[c.persona.secKey]})`;
        } else if (/끝나고|퇴근|술|운동|취미|일상|생활|직업|뭐\s*해/.test(q)) {
            answer = `${tonePrefix} 지금은 ${life.occupation} 일을 맡고 있고, ${life.afterWork}. 결국 내가 버티는 의미는 '${life.meaning}'이야.`;
            causeTag = `생활·루틴 도출 (피로도 ${Math.round((1 - c.hp / Math.max(1, c.maxHp)) * 100)}% · 취미: ${c.persona.hobby})`;
        } else if (/관계|동료|사람|친구|적|마찰|누구/.test(q)) {
            answer = `${tonePrefix} 요즘 주변 관계는 이래 — ${life.relationalWeb}. 서로 성향과 속도가 다르니 부딪힐 때도 있지만, 결국 다 연결돼 함께 움직이더군.`;
            causeTag = `관계망 공명·마찰 계산 (신뢰축 ${Math.round(c.persona.trustBase * 100)}%)`;
        } else if (/미래|앞으로|꿈|될|예정|엔딩/.test(q)) {
            answer = `${tonePrefix} 이 흐름대로라면 나는 '${life.futureBecoming}'. 지금 시대(${world.society.eraName})가 나를 그쪽으로 밀고 있거든.`;
            causeTag = `미래 궤적 예측 (${world.society.eraName} × ${STAT_ARCHETYPES[dom].code})`;
        } else if (/세상|마을|사건|몬스터|광석|흉년|물가|정치/.test(q)) {
            answer = `${tonePrefix} 지금 현장(${c.situation}) 보이지? 상행은 ${Math.round(world.society.tradeVolume)}%, 물가는 ${Math.round(world.society.priceIndex)}야. ${c.speech}`;
            causeTag = `거시-미시 연쇄 반응 (${world.society.politicsState})`;
        } else {
            answer = `${tonePrefix} 나는 ${c.persona.temperament} 쪽이야. ${life.afterWork}. 지금 상황에서 내가 보는 핵심은 '${life.meaning}'이고, 앞으로는 ${life.futureBecoming}.`;
            causeTag = `통합 페르소나 응답 (${STAT_ARCHETYPES[dom].code} 주도 · ${world.society.eraName})`;
        }
        return { answer, causeTag, life };
    }

    const ELEMENTS = {
        fire: { id: 'fire', name: '화염', color: '#f97316', glow: 'rgba(249,115,22,0.45)', skillName: '화염 쇄도' },
        frost: { id: 'frost', name: '빙결', color: '#38bdf8', glow: 'rgba(56,189,248,0.45)', skillName: '빙결 결계' },
        volt: { id: 'volt', name: '뇌전', color: '#facc15', glow: 'rgba(250,204,21,0.45)', skillName: '뇌전 연쇄' },
        aether: { id: 'aether', name: '공명', color: '#10b981', glow: 'rgba(16,185,129,0.45)', skillName: '공명 치유' },
    };

    const COMBO_REACTIONS = {
        'fire+frost': { name: '열충격 융해', color: '#fb7185', dmg: 26, radius: 112, shake: 10, hitstop: 4 },
        'frost+fire': { name: '열충격 융해', color: '#fb7185', dmg: 26, radius: 112, shake: 10, hitstop: 4 },
        'frost+volt': { name: '초전도 과부하', color: '#a78bfa', dmg: 24, radius: 128, shake: 9, hitstop: 4 },
        'volt+frost': { name: '초전도 과부하', color: '#a78bfa', dmg: 24, radius: 128, shake: 9, hitstop: 4 },
        'fire+volt': { name: '플라즈마 폭풍', color: '#f59e0b', dmg: 28, radius: 118, shake: 12, hitstop: 5 },
        'volt+fire': { name: '플라즈마 폭풍', color: '#f59e0b', dmg: 28, radius: 118, shake: 12, hitstop: 5 },
        'aether+any': { name: '성역 공명 증폭', color: '#34d399', dmg: 16, radius: 142, shake: 7, hitstop: 3 },
    };

    const CHARACTER_ARCHETYPES = [
        {
            id: 'aria', name: '아리아', role: '수호 기사', team: 0, isPlayer: true,
            x: 245, y: 260, hair: '#38bdf8', accent: '#06b6d4', skin: '#f5d7c4',
            primaryElem: 'frost', secondaryElem: 'aether',
            stats: { str: 62, agi: 58, int: 54, wis: 84, vit: 88 },
        },
        {
            id: 'kael', name: '카엘', role: '전술 마도사', team: 0, isPlayer: false,
            x: 170, y: 155, hair: '#818cf8', accent: '#6366f1', skin: '#f1d5c2',
            primaryElem: 'volt', secondaryElem: 'frost',
            stats: { str: 36, agi: 64, int: 92, wis: 76, vit: 48 },
        },
        {
            id: 'volk', name: '볼크', role: '열혈 격투가', team: 0, isPlayer: false,
            x: 210, y: 365, hair: '#fb923c', accent: '#f97316', skin: '#ecc6aa',
            primaryElem: 'fire', secondaryElem: 'volt',
            stats: { str: 92, agi: 78, int: 34, wis: 40, vit: 74 },
        },
        {
            id: 'orion', name: '오리온', role: '심연 지휘관', team: 1, isPlayer: false,
            x: 720, y: 260, hair: '#f43f5e', accent: '#e11d48', skin: '#e8c9ba',
            primaryElem: 'fire', secondaryElem: 'volt',
            stats: { str: 88, agi: 56, int: 82, wis: 42, vit: 78 },
        },
        {
            id: 'sera', name: '세라', role: '그림자 암살자', team: 1, isPlayer: false,
            x: 775, y: 155, hair: '#c084fc', accent: '#a855f7', skin: '#f3d9cb',
            primaryElem: 'volt', secondaryElem: 'fire',
            stats: { str: 52, agi: 95, int: 68, wis: 38, vit: 44 },
        },
        {
            id: 'lina', name: '리나', role: '변이 공명사', team: 1, isPlayer: false,
            x: 755, y: 365, hair: '#34d399', accent: '#10b981', skin: '#f4d9c6',
            primaryElem: 'frost', secondaryElem: 'aether',
            stats: { str: 38, agi: 62, int: 86, wis: 80, vit: 58 },
        },
    ];

    function createWorld() {
        const chars = CHARACTER_ARCHETYPES.map((arch) => {
            const st = { ...arch.stats };
            const p = derivePersonaFrom5Stats(st, 1.0, 1.0);
            return {
                ...arch,
                stats: st,
                persona: p,
                vx: 0,
                vy: 0,
                facing: arch.team === 0 ? 0 : Math.PI,
                hp: p.maxHp,
                maxHp: p.maxHp,
                sp: 100,
                maxSp: 100,
                shield: 14,
                cooldown: 16,
                skillCd: { q: 0, w: 0, e: 0, r: 0, space: 0 },
                rootTimer: 0,
                castFlash: 0,
                moveTarget: null,
                elementTag: null,
                elementTimer: 0,
                stagnationTicks: 0,
                emotion: 'calm',
                browTilt: 0,
                mouthCurve: 0.1,
                mouthOpen: 0.0,
                eyeOpen: 1.0,
                speech: '주변 교역로와 기류를 살피는 중.',
                speechTimer: 80,
                thought: `[${p.temperament}] 성향으로 현장 상황을 판독 중`,
                situation: '평시 교역 유지',
                lastSkill: '대기',
                lastCombo: '없음',
                observed: true,
            };
        });

        return {
            tick: 0,
            climatePhase: 0.35,
            crisisLevel: 0.14,
            hitstop: 0,
            shake: 0,
            bannerText: '',
            bannerColor: '#06b6d4',
            bannerTimer: 0,
            score: 0,
            comboCount: 0,
            caravan: { x: 140, dir: 1, hp: 100, halted: false, tradeValue: 100 },
            monsters: [],
            manaVein: { discovered: false, richness: 0, intrigueHeat: 0 },
            famine: { active: false, foodReserve: 84, profiteerWealth: 15, riotHeat: 0 },
            society: {
                tradeVolume: 88,
                priceIndex: 100,
                guildBounty: '평시 순찰',
                politicsState: '균형 외교',
                eraName: '벚꽃 교역 · 평온 균형기',
                eraTone: 'calm',
                endingPreview: '「균형 유지 · 사건 분기 대기」',
                activeChainTitle: '평시 교역로 순환 (사건 미발생)',
                chainSteps: [
                    'S0 현장: 상인 마차가 벚꽃 성역 교역로를 정상 왕래 중',
                    'S1 경제: 교역량 88% · 물가 100 안정 유지',
                    'S2 길드: 수호단·모험가 길드 평시 순찰 상태',
                    'S3 정치: 마나·식량 이권 충돌 없음 (균형 외교)',
                    'S4 시대: 평온 균형기 — 촉발 사건이나 5대 스탯 분기로 역사 전개',
                ],
            },
            dynamicPetals: [],
            treeDeformHeat: 0,
            chars,
            projectiles: [],
            zones: [],
            afterimages: [],
            floatTexts: [],
            moveMarker: null,
            effects: [],
            links: [],
        };
    }

    let worldA = createWorld();
    let worldB = createWorld();
    let s4Init = false;
    let selectedCharIdx = 0;
    let lastUserMoveTick = -999;
    let queuedQwerKey = null;
    let queuedDash = false;
    let queuedMoveOrder = null;
    let lastAimPos = { x: W * 0.56, y: H * 0.48 };
    let quantumLockEnabled = true;
    let videoTransduceEnabled = false;
    let latestVideoMood = { warmth: 0, flux: 0.25, chaos: 0.2, title: 'HD 영상 대기' };

    const historyRing = [];
    let historyHead = 0;
    const RING_CAP = 16;
    const savedBranches = [];
    let lastPredictions = [];

    function deepCopyWorld(w) {
        return {
            tick: w.tick,
            climatePhase: w.climatePhase,
            crisisLevel: w.crisisLevel,
            hitstop: 0,
            shake: 0,
            bannerText: w.bannerText,
            bannerColor: w.bannerColor,
            bannerTimer: w.bannerTimer,
            score: w.score,
            comboCount: w.comboCount,
            caravan: { ...w.caravan },
            monsters: w.monsters.map((m) => ({ ...m })),
            manaVein: { ...w.manaVein },
            famine: { ...w.famine },
            society: { ...w.society, chainSteps: [...w.society.chainSteps] },
            dynamicPetals: w.dynamicPetals.slice(0, 60).map((p) => ({ ...p })),
            treeDeformHeat: w.treeDeformHeat,
            chars: w.chars.map((c) => ({
                ...c,
                stats: { ...c.stats },
                persona: { ...c.persona },
                skillCd: { ...c.skillCd },
                moveTarget: c.moveTarget ? { ...c.moveTarget } : null,
            })),
            projectiles: w.projectiles.map((p) => ({ ...p })),
            zones: (w.zones || []).map((z) => ({ ...z })),
            afterimages: [],
            floatTexts: [],
            moveMarker: null,
            effects: w.effects.map((e) => ({ ...e })),
            links: [],
        };
    }

    function spawnTreeInterventionPetals(world, ix, iy, colorOverride = null, count = 24) {
        if (Math.hypot(ix - TREE_X, iy - (TREE_Y - 15)) > 165) return;
        world.treeDeformHeat = Math.min(1.0, world.treeDeformHeat + 0.45);
        for (let i = 0; i < count; i++) {
            const ang = Math.atan2(iy - TREE_Y, ix - TREE_X) + (detRand(world.tick + i * 13) - 0.5) * 2.6;
            const spd = 1.6 + detRand(world.tick + i * 7) * 4.0;
            world.dynamicPetals.push({
                x: TREE_X + (detRand(i * 19 + world.tick) - 0.5) * 115,
                y: TREE_Y - 32 + (detRand(i * 23 + world.tick) - 0.5) * 80,
                vx: Math.cos(ang) * spd,
                vy: Math.sin(ang) * spd - 0.5,
                size: 2.1 + detRand(i * 11) * 2.1,
                color: colorOverride || (i % 2 === 0 ? '#fbcfe8' : '#f472b6'),
                life: 46 + Math.round(detRand(i * 5) * 32),
                maxLife: 78,
            });
        }
        if (world.dynamicPetals.length > 160) world.dynamicPetals.splice(0, world.dynamicPetals.length - 160);
    }

    // ========================================================================
    // 3. REAL MULTI-STEP EVENT CATALYSTS (Monster / Mana Vein / Famine)
    // ========================================================================
    function triggerCausalCatalystOnWorld(w, kind) {
        if (kind === 'monster_raid') {
            w.crisisLevel = Math.max(w.crisisLevel, 0.72);
            w.monsters = [];
            for (let m = 0; m < 4; m++) {
                w.monsters.push({
                    id: `mon_${w.tick}_${m}`,
                    x: 340 + m * 85,
                    y: ROAD_Y - 18 + (m % 2) * 18,
                    vx: 0,
                    vy: 0,
                    hp: 58,
                    maxHp: 58,
                });
            }
            w.caravan.halted = true;
            w.caravan.hp = Math.max(35, w.caravan.hp - 34);
            w.society.tradeVolume = Math.max(18, w.society.tradeVolume - 46);
            w.society.priceIndex = Math.min(220, w.society.priceIndex + 44);
            w.society.guildBounty = '긴급 몬스터 토벌령 (현상금 ×2.5)';
            w.society.politicsState = '군수 상단 무기 독점 이득 · 길드 영향력 급증';
            w.society.activeChainTitle = '① 몬스터 창발 → 상인 피해 → 상행 위축 → 길드 토벌령 → 군수 이권';
            w.bannerText = '▲ 인과 촉발 ①: 마을 외곽 몬스터 창발! 상인 마차 습격 → 상행 급감 → 길드 긴급 토벌령 발령';
            w.bannerColor = '#f97316';
            w.bannerTimer = 135;
            w.chars.forEach((c) => reactCharacterToCatalyst(c, 'monster_raid'));
        } else if (kind === 'mana_vein') {
            w.crisisLevel = Math.max(w.crisisLevel, 0.65);
            w.manaVein.discovered = true;
            w.manaVein.richness = 100;
            w.manaVein.intrigueHeat = 68;
            w.society.tradeVolume = Math.min(130, w.society.tradeVolume + 28);
            w.society.guildBounty = '광맥 채굴권 호위·감시령';
            w.society.politicsState = '귀족·심연 첩보전 & 채굴권 정치 음모 (전쟁 임박)';
            w.society.activeChainTitle = '② 마나광석 발견 → 상단 집중 → 첩보·정치 음모 → 세력 견제·국지전';
            w.bannerText = '▲ 인과 촉발 ②: 고순도 마나광석 광맥 발견! 정치 음모·첩보 견제 폭발 → 자원 쟁탈 국지전 임박';
            w.bannerColor = '#a855f7';
            w.bannerTimer = 135;
            w.effects.push({ type: 'combo', x: VEIN_X, y: VEIN_Y, r: 16, maxR: 150, color: '#a855f7', life: 36, maxLife: 36, label: '고순도 마나 광맥' });
            w.chars.forEach((c) => reactCharacterToCatalyst(c, 'mana_vein'));
        } else if (kind === 'famine_hoard') {
            w.crisisLevel = Math.max(w.crisisLevel, 0.78);
            w.famine.active = true;
            w.famine.foodReserve = 24;
            w.famine.profiteerWealth = 86;
            w.famine.riotHeat = 72;
            w.society.tradeVolume = Math.max(20, w.society.tradeVolume - 35);
            w.society.priceIndex = Math.min(260, w.society.priceIndex + 78);
            w.society.guildBounty = '구호 식량 호송 & 투기 단속령';
            w.society.politicsState = '투기 상단 매점매석 폭리 → 민심 폭발·봉기 위기';
            w.society.activeChainTitle = '③ 대흉년·기근 → 투기 상단 매점매석 → 물가 폭등 → 민심 봉기 vs 구호 개혁';
            w.bannerText = '▲ 인과 촉발 ③: 대흉년 발생! 일부 투기 상단의 매점매석 폭리 → 5대 스탯 성향별 대응 분기 개시';
            w.bannerColor = '#f59e0b';
            w.bannerTimer = 135;
            spawnTreeInterventionPetals(w, TREE_X, TREE_Y, '#f59e0b', 45);
            w.chars.forEach((c) => reactCharacterToCatalyst(c, 'famine_hoard'));
        }
    }

    // Characters react DIFFERENTLY to the EXACT SAME world event based on their dominant 5-Stat Persona!
    function reactCharacterToCatalyst(c, kind) {
        const d = c.persona.domKey;
        if (kind === 'monster_raid') {
            if (d === 'agi') {
                c.emotion = 'fierce'; c.browTilt = 0.85; c.mouthCurve = -0.3; c.mouthOpen = 0.7;
                c.speech = '토벌령 공고 기다릴 틈이 없어! 당장 달려가 베어버린다!';
                c.thought = '[고-AGI 성급·현실] 길드 절차가 답답함 — 상행이 더 끊기기 전에 직접 즉결 토벌 돌입';
            } else if (d === 'str') {
                c.emotion = 'determined'; c.browTilt = 0.7; c.mouthCurve = 0.2; c.mouthOpen = 0.6;
                c.speech = '마차 앞을 내가 힘으로 막아선다! 덤벼라 괴물들아!';
                c.thought = '[고-STR 우직한 돌파] 무력으로 정면 제압해 세력 위신과 방어선을 동시에 세움';
            } else if (d === 'int') {
                c.emotion = 'calm'; c.browTilt = 0.25; c.mouthCurve = 0.35; c.mouthOpen = 0.35;
                c.speech = '군수 상단이 폭리를 노리겠군… 토벌 계약 조건부터 다시 짜야 해.';
                c.thought = '[고-INT 구조 분석] 몬스터 습격 → 물가 상승 → 군수 이권 독점의 정치경제 구조를 계산 중';
            } else if (d === 'wis') {
                c.emotion = 'empathetic'; c.browTilt = -0.5; c.mouthCurve = 0.1; c.mouthOpen = 0.45;
                c.speech = '몬스터가 갑자기 내려온 원인이 있어… 상인부터 대피시키자.';
                c.thought = '[고-WIS 장기 통찰] 생태계 교란 원인과 마을 민심 이탈을 동시에 우려하며 인명 보호 우선';
            } else {
                c.emotion = 'determined'; c.browTilt = 0.3; c.mouthCurve = 0.1; c.mouthOpen = 0.5;
                c.speech = '상인들은 내 뒤로! 성역 방어선은 절대 무너지지 않아.';
                c.thought = '[고-VIT 공동체 버팀목] 장기 교전과 호위를 버텨내며 마을 교역로 복구 결의';
            }
        } else if (kind === 'mana_vein') {
            if (d === 'int') {
                c.emotion = 'triumph'; c.browTilt = 0.2; c.mouthCurve = 0.75; c.mouthOpen = 0.5;
                c.speech = '순도 94% 마나광석… 이걸 쥐는 쪽이 다음 시대의 패권을 쥔다!';
                c.thought = '[고-INT 이권 설계] 광맥 소유권과 마도 기술 독점 시 발생하는 정치적 파급을 즉시 시뮬레이션';
            } else if (d === 'agi') {
                c.emotion = 'anxious'; c.browTilt = 0.65; c.mouthCurve = -0.25; c.mouthOpen = 0.65;
                c.speech = '첩자들이 벌써 기어들어왔어! 냄새가 나, 지금 잡아야 해!';
                c.thought = '[고-AGI 예민한 감각] 정치적 암살자·첩보 기척을 남들보다 먼저 감지하고 즉각 추격';
            } else if (d === 'str') {
                c.emotion = 'fierce'; c.browTilt = 0.9; c.mouthCurve = -0.15; c.mouthOpen = 0.65;
                c.speech = '말뿐인 외교는 끝났다! 강한 세력이 광맥을 점령하는 게 법칙이다!';
                c.thought = '[고-STR 무력·세력주의] 협상보다 무력 점거로 주도권을 강제하려는 충동 강화';
            } else if (d === 'wis') {
                c.emotion = 'anxious'; c.browTilt = -0.65; c.mouthCurve = -0.35; c.mouthOpen = 0.45;
                c.speech = '이 광석이 축복이 아니라 전쟁의 불씨가 될 거야… 공동 협정이 필요해.';
                c.thought = '[고-WIS 균형 중재] 자원 발견이 음모와 전면전으로 번지는 역사적 인과를 경고';
            } else {
                c.emotion = 'determined'; c.browTilt = 0.25; c.mouthCurve = 0.0; c.mouthOpen = 0.45;
                c.speech = '전쟁이 터져도 마을 주민은 지켜야 해. 대피소와 방벽을 보강하자.';
                c.thought = '[고-VIT 생존 수호] 정치 싸움보다 전란 대비 마을 생존선 구축에 집중';
            }
        } else if (kind === 'famine_hoard') {
            if (d === 'agi') {
                c.emotion = 'fierce'; c.browTilt = 0.88; c.mouthCurve = -0.5; c.mouthOpen = 0.75;
                c.speech = '굶어 죽어가는데 회의만 해?! 투기꾼 창고부터 당장 열어버려!';
                c.thought = '[고-AGI 성급·현실] 탁상공론에 극심한 답답함 — 즉각적 물리 해법으로 직행';
            } else if (d === 'str') {
                c.emotion = 'fierce'; c.browTilt = 0.82; c.mouthCurve = -0.3; c.mouthOpen = 0.65;
                c.speech = '매점매석한 놈들을 무력으로 끌어내 본보기를 보여주겠다!';
                c.thought = '[고-STR 권위·응징] 힘으로 질서를 강제해 투기 세력을 굴복시키려 함';
            } else if (d === 'int') {
                c.emotion = 'calm'; c.browTilt = 0.2; c.mouthCurve = 0.2; c.mouthOpen = 0.4;
                c.speech = '남부 항구와 마나 온실 재배를 연결하면 투기꾼 시세를 무너뜨릴 수 있어.';
                c.thought = '[고-INT 구조 해법] 단발 약탈 대신 공급망 재설계로 투기 이득 구조를 붕괴시킬 방안 도출';
            } else if (d === 'wis') {
                c.emotion = 'empathetic'; c.browTilt = -0.6; c.mouthCurve = 0.1; c.mouthOpen = 0.5;
                c.speech = '폭력이 번지면 내전이 돼… 길드 비축곡을 풀어 신뢰부터 되살리자.';
                c.thought = '[고-WIS 중재·공감] 흉년이 내전으로 비화하지 않도록 상호부조 협약 설득';
            } else {
                c.emotion = 'empathetic'; c.browTilt = -0.35; c.mouthCurve = 0.25; c.mouthOpen = 0.5;
                c.speech = '내 몫부터 나눌게. 우리가 버티면 겨울은 반드시 지나가.';
                c.thought = '[고-VIT 버팀목] 직접 구호소를 운영하며 공동체 붕괴를 몸으로 막아냄';
            }
        }
        c.speechTimer = 140;
    }

    // ========================================================================
    // 4. CONTINUOUS S4~S6 MACRO CAUSAL PROPAGATION (Caravan, Monsters, Vein, Famine -> Era)
    // ========================================================================
    function evolveMacroCausalWorld(world, valueBias, empathyConn) {
        const soc = world.society;

        // 1) Merchant Caravan on Trade Road
        const hasMonsters = world.monsters.length > 0;
        if (!hasMonsters) {
            world.caravan.halted = false;
            world.caravan.x += world.caravan.dir * 1.15;
            if (world.caravan.x > W - 110) world.caravan.dir = -1;
            if (world.caravan.x < 110) world.caravan.dir = 1;
            soc.tradeVolume = Math.min(115, soc.tradeVolume + 0.18);
            soc.priceIndex = Math.max(96, soc.priceIndex - 0.15);
            if (soc.guildBounty.includes('토벌령')) {
                soc.guildBounty = '토벌 완료 · 교역로 정상화';
            }
        } else {
            // Monsters actively harass the caravan and drain regional trade!
            world.caravan.halted = true;
            soc.tradeVolume = Math.max(12, soc.tradeVolume - 0.25);
            soc.priceIndex = Math.min(240, soc.priceIndex + 0.22);
        }

        // 2) Mana Vein Political Intrigue vs Mediation
        const avgWis = world.chars.slice(0, 3).reduce((s, c) => s + c.stats.wis, 0) / 3;
        const avgStr = world.chars.slice(0, 3).reduce((s, c) => s + c.stats.str, 0) / 3;
        const avgInt = world.chars.slice(0, 3).reduce((s, c) => s + c.stats.int, 0) / 3;
        const avgAgi = world.chars.slice(0, 3).reduce((s, c) => s + c.stats.agi, 0) / 3;

        if (world.manaVein.discovered) {
            const intrigueDelta = (valueBias - 0.95) * 0.45 + (avgStr - avgWis) * 0.008;
            world.manaVein.intrigueHeat = Math.max(5, Math.min(100, world.manaVein.intrigueHeat + intrigueDelta));
            if (world.manaVein.intrigueHeat > 72) {
                soc.politicsState = '마나 광맥 채굴권 전면전 · 정치 암살 격화';
            } else if (world.manaVein.intrigueHeat < 32) {
                soc.politicsState = '마나 공명 공동 협정 · 마도 공방 번영';
            } else {
                soc.politicsState = '귀족·심연 첩보 견제 · 외교 줄다리기';
            }
        }

        // 3) Famine Profiteering vs Relief Reform
        if (world.famine.active) {
            const reliefRate = (avgWis * 0.4 + avgInt * 0.35 + (empathyConn * 30)) * 0.004 - (valueBias - 1.0) * 0.28;
            world.famine.foodReserve = Math.max(5, Math.min(100, world.famine.foodReserve + reliefRate));
            world.famine.riotHeat = Math.max(0, Math.min(100, 100 - world.famine.foodReserve - empathyConn * 14));
            if (world.famine.foodReserve > 70) {
                world.famine.active = false;
                soc.politicsState = '구호·공급망 개혁 성공 (투기 상단 해체)';
            } else if (world.famine.riotHeat > 68) {
                soc.politicsState = '매점매석 폭리 → 민중 봉기·내전 확산';
            }
        }

        // 4) Derive Era & 5-Step Living Causal Chain Readout
        const instability =
            (100 - soc.tradeVolume) * 0.35 +
            Math.max(0, soc.priceIndex - 100) * 0.45 +
            world.manaVein.intrigueHeat * 0.4 +
            world.famine.riotHeat * 0.5;

        if (world.manaVein.discovered && world.manaVein.intrigueHeat > 68) {
            soc.eraName = '마나 패권 · 자원 쟁탈 전쟁기';
            soc.eraTone = 'iron';
            soc.endingPreview = '「마나 광맥 패권 전쟁 엔딩」';
        } else if (world.famine.active && world.famine.riotHeat > 60) {
            soc.eraName = '흉년 투기 · 민중 봉기 격변기';
            soc.eraTone = 'rift';
            soc.endingPreview = '「기근과 신뢰 붕괴 · 내전 엔딩」';
        } else if (hasMonsters && soc.tradeVolume < 45) {
            soc.eraName = '교역 단절 · 길드 토벌 비상체제';
            soc.eraTone = 'rift';
            soc.endingPreview = '「군수 독점 · 길드 계엄 엔딩」';
        } else if (instability < 38 && empathyConn >= 0.9 && avgWis >= 60) {
            soc.eraName = '벚꽃 교역 · 공명 르네상스기';
            soc.eraTone = 'harmony';
            soc.endingPreview = '「상호 신뢰 · 벚꽃 성역 번영 엔딩」';
        } else if (avgAgi > 76 || avgStr > 78 || valueBias > 1.35) {
            soc.eraName = '실리 즉결 · 강경 세력 재편기';
            soc.eraTone = 'iron';
            soc.endingPreview = '「속전속결 · 힘의 질서 재편 엔딩」';
        } else {
            soc.eraName = '균형 대치 · 전환 임계기';
            soc.eraTone = 'calm';
            soc.endingPreview = '「열린 분기 · 다음 선택 대기」';
        }

        soc.chainSteps = [
            `S0 현장: ${hasMonsters ? `교역로 몬스터 ${world.monsters.length}체 출현(마차 정지)` : world.manaVein.discovered ? `마나광맥 활성(긴장 ${Math.round(world.manaVein.intrigueHeat)}%)` : world.famine.active ? `흉년 식량 ${Math.round(world.famine.foodReserve)}%` : '상인 마차 정상 운행 중'}`,
            `S1 경제: 상행 교역 ${Math.round(soc.tradeVolume)}% · 물가지수 ${Math.round(soc.priceIndex)}${world.famine.active ? ` · 투기이득 ${Math.round(world.famine.profiteerWealth)}%` : ''}`,
            `S2 길드: ${soc.guildBounty}`,
            `S3 정치: ${soc.politicsState}`,
            `S4 시대: ${soc.eraName} → ${soc.endingPreview}`,
        ];
    }

    // ========================================================================
    // 5. MACRO ARENA RENDERER (Includes Trade Road, Caravan, Mana Vein & Drought)
    // ========================================================================
    function renderMacroWorld(ctx, world) {
        const era = world.society.eraTone;
        const drought = world.famine.active ? 1 : 0;

        const sky = ctx.createLinearGradient(0, 0, W, H);
        if (drought) {
            sky.addColorStop(0, '#1f1610');
            sky.addColorStop(0.55, '#2a1d14');
            sky.addColorStop(1, '#120d0a');
        } else if (era === 'harmony') {
            sky.addColorStop(0, '#0b1b2b');
            sky.addColorStop(0.55, '#12283a');
            sky.addColorStop(1, '#091420');
        } else if (era === 'iron') {
            sky.addColorStop(0, '#1e1018');
            sky.addColorStop(0.55, '#291523');
            sky.addColorStop(1, '#120a12');
        } else if (era === 'rift') {
            sky.addColorStop(0, '#191026');
            sky.addColorStop(0.55, '#231331');
            sky.addColorStop(1, '#0d0917');
        } else {
            sky.addColorStop(0, '#0c1322');
            sky.addColorStop(0.55, '#111b2e');
            sky.addColorStop(1, '#080c15');
        }
        ctx.fillStyle = sky;
        ctx.fillRect(0, 0, W, H);

        // Tactical Grid
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.07)';
        ctx.lineWidth = 1;
        for (let x = 60; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 26); ctx.lineTo(x, H - 26); ctx.stroke(); }
        for (let y = 45; y < H; y += 54) { ctx.beginPath(); ctx.moveTo(26, y); ctx.lineTo(W - 26, y); ctx.stroke(); }

        // Northern Mana Ore Ridge
        ctx.strokeStyle = world.manaVein.discovered ? 'rgba(168, 85, 247, 0.55)' : 'rgba(148, 163, 184, 0.16)';
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        ctx.ellipse(VEIN_X, VEIN_Y, 82, 24, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = world.manaVein.discovered ? '#d8b4fe' : '#64748b';
        ctx.font = '600 9.5px "IBM Plex Mono", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(world.manaVein.discovered ? `◆ 마나광맥 활성 (음모·쟁탈 ${Math.round(world.manaVein.intrigueHeat)}%)` : '◇ 북부 암반지대 (미발견)', VEIN_X, VEIN_Y + 4);

        // Southern Village Trade Road (상행 교역로!)
        ctx.fillStyle = 'rgba(245, 158, 11, 0.08)';
        ctx.fillRect(36, ROAD_Y - 16, W - 72, 32);
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.28)';
        ctx.setLineDash([8, 6]);
        ctx.beginPath();
        ctx.moveTo(36, ROAD_Y);
        ctx.lineTo(W - 36, ROAD_Y);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = '#94a3b8';
        ctx.textAlign = 'left';
        ctx.fillText(`마을 상행 교역로 (교역량 ${Math.round(world.society.tradeVolume)}% · 물가 ${Math.round(world.society.priceIndex)})`, 44, ROAD_Y + 26);

        // Central Cherry Sanctuary Circle
        ctx.strokeStyle = drought ? 'rgba(245, 158, 11, 0.28)' : 'rgba(244, 114, 182, 0.28)';
        ctx.beginPath();
        ctx.ellipse(TREE_X, TREE_Y + 32, 148, 82, 0, 0, Math.PI * 2);
        ctx.stroke();
    }

    // ========================================================================
    // 6. S3~S0 COMBAT, 5-STAT IMPATIENCE/BEHAVIOR, MONSTER RAID & SKILL COMBOS
    // ========================================================================
    function applyDamage(target, amount) {
        let rem = amount;
        if (target.shield > 0) {
            const ab = Math.min(target.shield, rem);
            target.shield -= ab;
            rem -= ab;
        }
        target.hp = Math.max(0, target.hp - rem);
        if (target.hp <= 0) {
            target.hp = target.maxHp;
            target.shield = 18;
            target.x = target.team === 0 ? 130 : W - 130;
            target.y = 145 + (target.id.charCodeAt(0) % 3) * 115;
            target.elementTag = null;
            target.speech = '위상 복원! 다시 전선으로!';
            target.speechTimer = 80;
        }
    }

    function triggerElementalCombo(world, caster, victim, key, audioPulse) {
        const rx = COMBO_REACTIONS[key] || COMBO_REACTIONS['aether+any'];
        victim.elementTag = null;
        victim.elementTimer = 0;
        world.comboCount += 1;
        world.score += 120;
        world.hitstop = Math.max(world.hitstop, rx.hitstop);
        world.shake = Math.max(world.shake, rx.shake);
        world.bannerText = `★ 스킬 조합: ${rx.name} (${caster.name} [${STAT_ARCHETYPES[caster.persona.domKey].name}특화] → ${victim.name})`;
        world.bannerColor = rx.color;
        world.bannerTimer = 85;
        caster.lastCombo = rx.name;
        caster.stagnationTicks = 0;

        world.effects.push({ type: 'combo', x: victim.x, y: victim.y, r: 18, maxR: rx.radius, color: rx.color, life: 30, maxLife: 30, label: rx.name });
        spawnTreeInterventionPetals(world, victim.x, victim.y, rx.color, 30);

        for (const other of world.chars) {
            if (other.team !== caster.team) {
                const d = Math.hypot(other.x - victim.x, other.y - victim.y) || 1;
                if (d < rx.radius) {
                    applyDamage(other, rx.dmg * caster.persona.dmgScale * (1 - d / (rx.radius * 1.6)));
                }
            }
        }
        // Also damage nearby road monsters if combo explodes near trade road!
        for (let m = world.monsters.length - 1; m >= 0; m--) {
            const mon = world.monsters[m];
            if (Math.hypot(mon.x - victim.x, mon.y - victim.y) < rx.radius + 45) {
                mon.hp -= rx.dmg * 1.1;
                if (mon.hp <= 0) { world.monsters.splice(m, 1); world.score += 90; }
            }
        }
        caster.emotion = caster.persona.domKey === 'str' || caster.persona.domKey === 'agi' ? 'fierce' : 'triumph';
        caster.browTilt = caster.persona.domKey === 'agi' ? 0.8 : 0.35;
        caster.mouthCurve = 0.85;
        caster.mouthOpen = 0.72;
        caster.speech = caster.persona.domKey === 'agi'
            ? `${rx.name}! 질질 끌지 말고 여기서 끝낸다!`
            : caster.persona.domKey === 'int'
                ? `계산대로 ${rx.name} 연쇄 성공!`
                : `${rx.name} 공명 발동!`;
        caster.speechTimer = 100;
        if (audioPulse) audioPulse(720);
    }

    function pushFloatText(world, x, y, text, color = '#f8fafc') {
        world.floatTexts.push({ x, y, vy: -1.1, text, color, life: 42, maxLife: 42 });
        if (world.floatTexts.length > 28) world.floatTexts.shift();
    }

    function castQwerSkill(world, caster, slot, tx, ty, audioPulse) {
        const def = QWER_SKILLS[slot];
        if (!def) return false;
        if ((caster.skillCd[slot] || 0) > 0) return false;
        if (caster.sp < def.spCost) {
            if (caster.isPlayer) pushFloatText(world, caster.x, caster.y - 26, 'SP 부족', '#94a3b8');
            return false;
        }
        const ang = Math.atan2(ty - caster.y, tx - caster.x);
        caster.facing = ang;
        caster.sp = Math.max(0, caster.sp - def.spCost);
        caster.skillCd[slot] = Math.max(24, Math.round(def.cdTicks * caster.persona.cooldownScale));
        caster.lastSkill = `[${def.key}] ${def.name}`;
        caster.castFlash = 14;
        caster.stagnationTicks = 0;

        if (slot === 'q') {
            // [Q] Frost Piercing Lance: Fast piercing linear skillshot!
            world.projectiles.push({
                ownerId: caster.id,
                team: caster.team,
                elemId: 'frost',
                kind: 'lance',
                piercing: true,
                hitSet: [],
                x: caster.x + Math.cos(ang) * 24,
                y: caster.y + Math.sin(ang) * 24,
                vx: Math.cos(ang) * 12.2,
                vy: Math.sin(ang) * 12.2,
                ang,
                r: 10,
                dmg: Math.round(18 * caster.persona.dmgScale),
                life: 36,
            });
            world.effects.push({ type: 'ring', x: caster.x + Math.cos(ang) * 18, y: caster.y + Math.sin(ang) * 18, r: 6, maxR: 34, color: '#38bdf8', life: 12, maxLife: 12 });
            spawnTreeInterventionPetals(world, caster.x, caster.y, '#7dd3fc', 14);
            if (audioPulse) audioPulse(540);
            return true;
        }

        if (slot === 'w') {
            // [W] Tactical Vault Dash + Shield + Landing Shockwave!
            const dashDist = Math.min(165, Math.max(70, Math.hypot(tx - caster.x, ty - caster.y)));
            const startX = caster.x;
            const startY = caster.y;
            const destX = Math.max(46, Math.min(W - 46, startX + Math.cos(ang) * dashDist));
            const destY = Math.max(48, Math.min(H - 70, startY + Math.sin(ang) * dashDist));
            for (let k = 0; k < 5; k++) {
                const t = k / 5;
                world.afterimages.push({
                    id: caster.id,
                    x: startX + (destX - startX) * t,
                    y: startY + (destY - startY) * t,
                    color: def.color,
                    life: 18 - k * 2,
                    maxLife: 18,
                });
            }
            caster.x = destX;
            caster.y = destY;
            caster.moveTarget = null;
            const shGain = Math.round(16 + caster.stats.vit * 0.18);
            caster.shield = Math.min(48, caster.shield + shGain);
            pushFloatText(world, caster.x, caster.y - 26, `+${shGain} 보호막`, '#34d399');
            world.effects.push({ type: 'combo', x: destX, y: destY, r: 14, maxR: 92, color: '#fb923c', life: 20, maxLife: 20, label: '[W] 전술 도약' });
            world.shake = Math.max(world.shake, 5);
            spawnTreeInterventionPetals(world, destX, destY, '#fb923c', 22);
            const slamDmg = Math.round(16 * caster.persona.dmgScale);
            for (const other of world.chars) {
                if (other.team !== caster.team && Math.hypot(other.x - destX, other.y - destY) < 92) {
                    applyDamage(other, slamDmg);
                    pushFloatText(world, other.x, other.y - 22, `-${slamDmg}`, '#fb923c');
                    if (other.elementTag && other.elementTag !== 'fire') {
                        triggerElementalCombo(world, caster, other, `${other.elementTag}+fire`, audioPulse);
                    } else {
                        other.elementTag = 'fire';
                        other.elementTimer = 175;
                    }
                }
            }
            for (let m = world.monsters.length - 1; m >= 0; m--) {
                const mon = world.monsters[m];
                if (Math.hypot(mon.x - destX, mon.y - destY) < 98) {
                    mon.hp -= slamDmg * 1.4;
                    pushFloatText(world, mon.x, mon.y - 18, `-${Math.round(slamDmg * 1.4)}`, '#fb923c');
                    if (mon.hp <= 0) { world.monsters.splice(m, 1); world.score += 80; }
                }
            }
            if (audioPulse) audioPulse(340);
            return true;
        }

        if (slot === 'e') {
            // [E] Voltaic Snare Field: Ground telegraph circle -> delayed lightning root burst!
            const range = Math.min(260, Math.hypot(tx - caster.x, ty - caster.y));
            const zx = Math.max(54, Math.min(W - 54, caster.x + Math.cos(ang) * range));
            const zy = Math.max(54, Math.min(H - 64, caster.y + Math.sin(ang) * range));
            world.zones.push({
                ownerId: caster.id,
                team: caster.team,
                kind: 'snare',
                elemId: 'volt',
                x: zx,
                y: zy,
                r: 86,
                timer: 24,
                maxTimer: 24,
                dmg: Math.round(21 * caster.persona.dmgScale),
                color: '#facc15',
                label: '[E] 뇌전 속박진',
            });
            if (audioPulse) audioPulse(660);
            return true;
        }

        if (slot === 'r') {
            // [R] Ultimate: Sanctuary Absolute Judgment — expanding rune circle telegraph -> huge AoE + Ally Heal!
            const range = Math.min(220, Math.hypot(tx - caster.x, ty - caster.y));
            const zx = Math.max(70, Math.min(W - 70, caster.x + Math.cos(ang) * range));
            const zy = Math.max(70, Math.min(H - 76, caster.y + Math.sin(ang) * range));
            world.zones.push({
                ownerId: caster.id,
                team: caster.team,
                kind: 'ultimate',
                elemId: 'aether',
                x: zx,
                y: zy,
                r: 158,
                timer: 34,
                maxTimer: 34,
                dmg: Math.round(34 * caster.persona.dmgScale),
                color: '#34d399',
                label: '[R] 성역 절대영도',
            });
            world.bannerText = `★ ${caster.name} 궁극기 발동 — [R] 성역 절대영도!`;
            world.bannerColor = '#34d399';
            world.bannerTimer = 85;
            caster.emotion = 'triumph';
            caster.speech = '성역의 위상을 고정한다 — 절대영도 심판!';
            caster.speechTimer = 110;
            spawnTreeInterventionPetals(world, zx, zy, '#fbcfe8', 42);
            if (audioPulse) audioPulse(820);
            return true;
        }

        if (slot === 'space') {
            const dashDist = 96;
            const startX = caster.x;
            const startY = caster.y;
            const destX = Math.max(44, Math.min(W - 44, startX + Math.cos(ang) * dashDist));
            const destY = Math.max(46, Math.min(H - 68, startY + Math.sin(ang) * dashDist));
            for (let k = 0; k < 3; k++) {
                const t = k / 3;
                world.afterimages.push({ id: caster.id, x: startX + (destX - startX) * t, y: startY + (destY - startY) * t, color: '#38bdf8', life: 14 - k * 3, maxLife: 14 });
            }
            caster.x = destX;
            caster.y = destY;
            world.effects.push({ type: 'ring', x: destX, y: destY, r: 8, maxR: 44, color: '#38bdf8', life: 12, maxLife: 12 });
            if (audioPulse) audioPulse(460);
            return true;
        }
        return false;
    }

    function fireSkill(world, caster, elemId, tx, ty, audioPulse) {
        const elem = ELEMENTS[elemId] || ELEMENTS.frost;
        const ang = Math.atan2(ty - caster.y, tx - caster.x);
        caster.facing = ang;
        caster.lastSkill = elem.skillName;
        caster.cooldown = Math.round((elemId === 'aether' ? 54 : 28) * caster.persona.cooldownScale);
        caster.castFlash = 8;
        caster.stagnationTicks = 0;

        spawnTreeInterventionPetals(world, caster.x, caster.y, elem.color, 10);

        if (elemId === 'aether') {
            world.effects.push({ type: 'ring', x: caster.x, y: caster.y, r: 16, maxR: 138, color: elem.color, life: 22, maxLife: 22, label: '공명 치유' });
            for (const other of world.chars) {
                if (other.team === caster.team && Math.hypot(other.x - caster.x, other.y - caster.y) < 175) {
                    other.hp = Math.min(other.maxHp, other.hp + 16);
                    other.shield = Math.min(44, other.shield + 14);
                    pushFloatText(world, other.x, other.y - 24, '+16 치유', '#34d399');
                }
            }
            if (audioPulse) audioPulse(440);
            return;
        }

        world.projectiles.push({
            ownerId: caster.id,
            team: caster.team,
            elemId,
            kind: 'bolt',
            piercing: false,
            hitSet: [],
            x: caster.x + Math.cos(ang) * 22,
            y: caster.y + Math.sin(ang) * 22,
            vx: Math.cos(ang) * (elemId === 'volt' ? 10.2 : 8.4),
            vy: Math.sin(ang) * (elemId === 'volt' ? 10.2 : 8.4),
            ang,
            r: elemId === 'fire' ? 8 : 6.5,
            dmg: Math.round((elemId === 'fire' ? 13 : 10) * caster.persona.dmgScale),
            life: 52,
        });
        if (audioPulse) audioPulse(elemId === 'fire' ? 280 : elemId === 'volt' ? 620 : 490);
    }

    function evaluateSocioTacticalLayer(world, dtScale, valueBias, empathyConn, applyQuantumLock, audioPulse) {
        let ops = 0;
        world.links = [];
        const chars = world.chars;
        const obsX = chars[0].x;
        const obsY = chars[0].y;

        for (let i = 0; i < chars.length; i++) {
            const c = chars[i];
            c.observed = !applyQuantumLock || i === 0 || Math.hypot(c.x - obsX, c.y - obsY) <= OBSERVER_RADIUS + 35;
            c.persona = derivePersonaFrom5Stats(c.stats, valueBias, empathyConn);
            c.maxHp = c.persona.maxHp;
            if (c.hp > c.maxHp) c.hp = c.maxHp;
            ops += c.observed ? 42 : 4;
        }

        for (let i = 0; i < chars.length; i++) {
            const c = chars[i];
            if (!c.observed) {
                const dx = W * 0.5 - c.x;
                const dy = H * 0.5 - c.y;
                const d = Math.hypot(dx, dy) || 1;
                c.vx = (c.vx + (dx / d) * 0.14 * dtScale) * 0.92;
                c.vy = (c.vy + (dy / d) * 0.14 * dtScale) * 0.92;
                c.situation = 'ψ 양자 미관측 잠금';
                ops += 16;
                continue;
            }

            ops += 720;
            c.stagnationTicks += dtScale;
            const allies = chars.filter((o) => o.team === c.team && o !== c);
            const enemies = chars.filter((o) => o.team !== c.team);

            for (const al of allies) {
                if (Math.hypot(al.x - c.x, al.y - c.y) < 285 && c.persona.trustBase > 0.35 && c.id < al.id) {
                    world.links.push({ x1: c.x, y1: c.y, x2: al.x, y2: al.y, strength: c.persona.trustBase, color: c.team === 0 ? '#06b6d4' : '#f43f5e' });
                }
            }

            // High-AGI characters visibly get impatient & snap if battle drags without resolution!
            if (c.stagnationTicks > c.persona.patienceTicks && c.persona.domKey === 'agi' && c.speechTimer <= 0) {
                c.emotion = 'fierce';
                c.browTilt = 0.82;
                c.mouthCurve = -0.35;
                c.mouthOpen = 0.55;
                c.speech = '너무 느려! 답답해 죽겠네, 내가 먼저 끝낸다!';
                c.thought = `[민첩 ${c.stats.agi} · 성급함 발현] 교착 상태를 못 견디고 즉각 돌진 결단`;
                c.speechTimer = 95;
                c.stagnationTicks = 0;
            }

            const woundedAlly = allies.reduce((best, a) => (!best || a.hp / a.maxHp < best.hp / best.maxHp ? a : best), null);
            const roadMonster = c.team === 0 && world.monsters.length > 0 ? world.monsters[0] : null;
            const taggedEnemy = enemies.find((e) => e.elementTag && e.elementTag !== c.primaryElem);
            const nearestEnemy = enemies.reduce((best, e) => {
                const d = Math.hypot(e.x - c.x, e.y - c.y);
                return !best || d < best.d ? { e, d } : best;
            }, null);

            if (roadMonster) c.situation = `길드 토벌령: 교역로 몬스터 ${world.monsters.length}체 대응`;
            else if (world.manaVein.discovered) c.situation = `마나광맥 쟁탈·첩보 (긴장 ${Math.round(world.manaVein.intrigueHeat)}%)`;
            else if (world.famine.active) c.situation = `대흉년·매점매석 위기 (식량 ${Math.round(world.famine.foodReserve)}%)`;
            else c.situation = world.society.eraName;

            const playerOverride = c.isPlayer && (world.tick - lastUserMoveTick < 110);
            if (!playerOverride && nearestEnemy) {
                let targetObj = nearestEnemy.e;
                let prefDist = c.persona.domKey === 'str' || c.persona.domKey === 'agi' ? 115 : 210;

                if (roadMonster && (c.persona.domKey === 'agi' || c.persona.domKey === 'str' || c.persona.domKey === 'vit')) {
                    targetObj = roadMonster;
                    prefDist = 90;
                } else if (world.manaVein.discovered && c.persona.domKey === 'int') {
                    targetObj = { x: VEIN_X, y: VEIN_Y + 34 };
                    prefDist = 70;
                } else if (woundedAlly && woundedAlly.hp / woundedAlly.maxHp < 0.56 && c.persona.protect > 0.52) {
                    targetObj = woundedAlly;
                    prefDist = 65;
                } else if (taggedEnemy && c.persona.trustBase > 0.44) {
                    targetObj = taggedEnemy;
                    prefDist = 165;
                }

                const dx = targetObj.x - c.x;
                const dy = targetObj.y - c.y;
                const dist = Math.hypot(dx, dy) || 1;
                const dirSign = dist > prefDist ? 1 : -0.58;
                const orbitSign = (i % 2 === 0 ? 1 : -1) * 0.42;
                const spd = c.persona.moveSpeed * dtScale;

                c.vx = (c.vx + ((dx / dist) * dirSign - (dy / dist) * orbitSign) * spd) * 0.9;
                c.vy = (c.vy + ((dy / dist) * dirSign + (dx / dist) * orbitSign) * spd) * 0.9;
                c.facing = Math.atan2(targetObj.y - c.y, targetObj.x - c.x);

                if (c.cooldown <= 0) {
                    if (woundedAlly && woundedAlly.hp / woundedAlly.maxHp < 0.62 && c.persona.protect > 0.56 && (c.primaryElem === 'aether' || c.secondaryElem === 'aether')) {
                        fireSkill(world, c, 'aether', woundedAlly.x, woundedAlly.y, audioPulse);
                    } else if (roadMonster) {
                        fireSkill(world, c, c.primaryElem, roadMonster.x, roadMonster.y, audioPulse);
                    } else if (taggedEnemy && c.persona.trustBase > 0.44) {
                        const comboElem = taggedEnemy.elementTag === c.primaryElem ? c.secondaryElem : c.primaryElem;
                        fireSkill(world, c, comboElem, taggedEnemy.x, taggedEnemy.y, audioPulse);
                    } else if (nearestEnemy.d < 360) {
                        const elem = detRand(world.tick + i * 17) > 0.3 ? c.primaryElem : c.secondaryElem;
                        fireSkill(world, c, elem, nearestEnemy.e.x, nearestEnemy.e.y, audioPulse);
                    }
                }
            }

            if (c.speechTimer <= 0) {
                const stress = 1 - c.hp / c.maxHp;
                c.emotion = stress > 0.55 ? 'anxious' : c.persona.domKey === 'str' || c.persona.domKey === 'agi' ? 'fierce' : c.persona.domKey === 'wis' ? 'empathetic' : 'calm';
                c.browTilt = stress > 0.55 ? -0.5 : c.persona.urgency > 0.72 ? 0.65 : 0.1;
                c.mouthCurve = stress > 0.55 ? -0.35 : c.persona.domKey === 'int' ? 0.25 : 0.15;
                c.mouthOpen = Math.max(0, c.mouthOpen - 0.08);
            }
        }
        return ops;
    }

    function stepMicroPhysics(world, keys, mouse, firedClick, audioPulse) {
        let microOps = 40;
        if (world.hitstop > 0) { world.hitstop -= 1; return microOps; }
        if (world.shake > 0) world.shake *= 0.84;
        if (world.shake < 0.25) world.shake = 0;
        if (world.bannerTimer > 0) world.bannerTimer -= 1;
        world.treeDeformHeat = Math.max(0, world.treeDeformHeat * 0.96);
        lastAimPos = { x: mouse.x, y: mouse.y };

        const player = world.chars[0];
        if (queuedMoveOrder) {
            lastUserMoveTick = world.tick;
            player.moveTarget = { x: Math.max(44, Math.min(W - 44, queuedMoveOrder.x)), y: Math.max(46, Math.min(H - 68, queuedMoveOrder.y)) };
            world.moveMarker = { x: player.moveTarget.x, y: player.moveTarget.y, life: 28, maxLife: 28 };
        }

        // Arrow keys move smoothly (Q/W/E/R stay dedicated to Eternal Return skills!)
        let ix = 0, iy = 0;
        if (keys.has('ArrowUp')) iy -= 1;
        if (keys.has('ArrowDown')) iy += 1;
        if (keys.has('ArrowLeft')) ix -= 1;
        if (keys.has('ArrowRight')) ix += 1;
        if ((ix !== 0 || iy !== 0) && player.rootTimer <= 0) {
            lastUserMoveTick = world.tick;
            player.moveTarget = null;
            const m = Math.hypot(ix, iy);
            const pSpd = 0.82 + (player.stats.agi / 100) * 0.58;
            player.vx = (player.vx + (ix / m) * pSpd) * 0.84;
            player.vy = (player.vy + (iy / m) * pSpd) * 0.84;
            player.facing = Math.atan2(mouse.y - player.y, mouse.x - player.x);
            if (Math.hypot(player.x - TREE_X, player.y - TREE_Y) < 120 && world.tick % 6 === 0) {
                spawnTreeInterventionPetals(world, player.x, player.y, null, 7);
            }
        } else if (player.moveTarget && player.rootTimer <= 0) {
            const dx = player.moveTarget.x - player.x;
            const dy = player.moveTarget.y - player.y;
            const dist = Math.hypot(dx, dy);
            if (dist < 10) {
                player.moveTarget = null;
            } else {
                const pSpd = 0.86 + (player.stats.agi / 100) * 0.62;
                player.vx = (player.vx + (dx / dist) * pSpd) * 0.84;
                player.vy = (player.vy + (dy / dist) * pSpd) * 0.84;
                player.facing = Math.atan2(dy, dx);
                if (Math.hypot(player.x - TREE_X, player.y - TREE_Y) < 120 && world.tick % 6 === 0) {
                    spawnTreeInterventionPetals(world, player.x, player.y, null, 6);
                }
            }
        }

        if (queuedDash) {
            lastUserMoveTick = world.tick;
            castQwerSkill(world, player, 'space', mouse.x, mouse.y, audioPulse);
        }
        if (queuedQwerKey) {
            lastUserMoveTick = world.tick;
            castQwerSkill(world, player, queuedQwerKey, mouse.x, mouse.y, audioPulse);
        } else if (firedClick && player.cooldown <= 0) {
            lastUserMoveTick = world.tick;
            fireSkill(world, player, player.primaryElem, mouse.x, mouse.y, audioPulse);
        }

        for (const c of world.chars) {
            if (c.cooldown > 0) c.cooldown -= 1;
            if (c.speechTimer > 0) c.speechTimer -= 1;
            if (c.rootTimer > 0) c.rootTimer -= 1;
            if (c.castFlash > 0) c.castFlash -= 1;
            for (const sk of ['q', 'w', 'e', 'r', 'space']) {
                if (c.skillCd[sk] > 0) c.skillCd[sk] -= 1;
            }
            c.sp = Math.min(c.maxSp, c.sp + 0.14 + (c.stats.wis / 100) * 0.14);
            if (c.elementTimer > 0) { c.elementTimer -= 1; if (c.elementTimer === 0) c.elementTag = null; }
            if (c.rootTimer > 0) {
                c.vx *= 0.65;
                c.vy *= 0.65;
            } else {
                c.x = Math.max(44, Math.min(W - 44, c.x + c.vx));
                c.y = Math.max(46, Math.min(H - 68, c.y + c.vy));
            }
            c.vx *= 0.93;
            c.vy *= 0.93;
            microOps += 8;
        }

        // Delayed Telegraphed Ground Zones ([E] Snare Field & [R] Sanctuary Ultimate)
        for (let i = world.zones.length - 1; i >= 0; i--) {
            const z = world.zones[i];
            z.timer -= 1;
            microOps += 5;
            if (z.timer <= 0) {
                const caster = world.chars.find((u) => u.id === z.ownerId) || world.chars[0];
                world.effects.push({ type: 'combo', x: z.x, y: z.y, r: 18, maxR: z.r * 1.08, color: z.color, life: 28, maxLife: 28, label: z.label });
                world.shake = Math.max(world.shake, z.kind === 'ultimate' ? 12 : 6);
                if (z.kind === 'ultimate') world.hitstop = Math.max(world.hitstop, 5);
                spawnTreeInterventionPetals(world, z.x, z.y, z.color, z.kind === 'ultimate' ? 38 : 18);

                for (const other of world.chars) {
                    const d = Math.hypot(other.x - z.x, other.y - z.y);
                    if (other.team !== z.team && d <= z.r) {
                        applyDamage(other, z.dmg);
                        pushFloatText(world, other.x, other.y - 24, `-${z.dmg}${z.kind === 'snare' ? ' 속박!' : '!'}`, z.color);
                        if (z.kind === 'snare') other.rootTimer = 72;
                        if (other.elementTag && other.elementTag !== z.elemId) {
                            triggerElementalCombo(world, caster, other, `${other.elementTag}+${z.elemId}`, audioPulse);
                        } else {
                            other.elementTag = z.elemId === 'aether' ? 'frost' : z.elemId;
                            other.elementTimer = 175;
                        }
                    } else if (z.kind === 'ultimate' && other.team === z.team && d <= z.r + 30) {
                        other.hp = Math.min(other.maxHp, other.hp + 26);
                        other.shield = Math.min(48, other.shield + 22);
                        pushFloatText(world, other.x, other.y - 26, '+26 공명 치유', '#34d399');
                    }
                }
                for (let m = world.monsters.length - 1; m >= 0; m--) {
                    const mon = world.monsters[m];
                    if (Math.hypot(mon.x - z.x, mon.y - z.y) <= z.r + 12) {
                        mon.hp -= z.dmg * 1.4;
                        pushFloatText(world, mon.x, mon.y - 18, `-${Math.round(z.dmg * 1.4)}`, z.color);
                        if (mon.hp <= 0) { world.monsters.splice(m, 1); world.score += 95; }
                    }
                }
                if (audioPulse) audioPulse(z.kind === 'ultimate' ? 760 : 580);
                world.zones.splice(i, 1);
            }
        }

        // Road Monsters pace around halted Merchant Caravan
        for (const mon of world.monsters) {
            const dx = world.caravan.x - mon.x;
            const dy = (ROAD_Y - 8) - mon.y;
            const d = Math.hypot(dx, dy) || 1;
            mon.x += (dx / d) * (d > 48 ? 0.9 : -0.3);
            mon.y += (dy / d) * 0.4;
            microOps += 4;
        }

        for (let i = world.projectiles.length - 1; i >= 0; i--) {
            const p = world.projectiles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.life -= 1;
            microOps += 8;
            if (Math.hypot(p.x - TREE_X, p.y - (TREE_Y - 25)) < 85 && world.tick % 4 === 0) {
                spawnTreeInterventionPetals(world, p.x, p.y, ELEMENTS[p.elemId].color, 5);
            }
            if (p.life <= 0 || p.x < 24 || p.x > W - 24 || p.y < 24 || p.y > H - 24) {
                world.projectiles.splice(i, 1);
                continue;
            }
            let consumed = false;
            if (p.team === 0) {
                for (let m = world.monsters.length - 1; m >= 0; m--) {
                    const mon = world.monsters[m];
                    if ((mon.x - p.x) ** 2 + (mon.y - p.y) ** 2 < 560 && !p.hitSet.includes(mon.id)) {
                        p.hitSet.push(mon.id);
                        const mdmg = Math.round(p.dmg * 1.4);
                        mon.hp -= mdmg;
                        pushFloatText(world, mon.x, mon.y - 18, `-${mdmg}`, ELEMENTS[p.elemId].color);
                        world.effects.push({ type: 'hit', x: p.x, y: p.y, r: 5, maxR: 30, color: ELEMENTS[p.elemId].color, life: 12, maxLife: 12 });
                        if (mon.hp <= 0) { world.monsters.splice(m, 1); world.score += 75; }
                        if (!p.piercing) { world.projectiles.splice(i, 1); consumed = true; break; }
                    }
                }
            }
            if (consumed) continue;

            for (const c of world.chars) {
                if (c.team === p.team || p.hitSet.includes(c.id)) continue;
                if ((c.x - p.x) ** 2 + (c.y - p.y) ** 2 < 625) {
                    p.hitSet.push(c.id);
                    const caster = world.chars.find((u) => u.id === p.ownerId) || world.chars[0];
                    applyDamage(c, p.dmg);
                    if (p.kind === 'bolt') caster.sp = Math.min(caster.maxSp, caster.sp + 7);
                    pushFloatText(world, c.x, c.y - 22, `-${p.dmg}`, ELEMENTS[p.elemId].color);
                    world.score += p.team === 0 ? 18 : 0;
                    if (c.elementTag && c.elementTag !== p.elemId) {
                        triggerElementalCombo(world, caster, c, `${c.elementTag}+${p.elemId}`, audioPulse);
                    } else {
                        c.elementTag = p.elemId;
                        c.elementTimer = 175;
                        world.effects.push({ type: 'hit', x: p.x, y: p.y, r: 5, maxR: 36, color: ELEMENTS[p.elemId].color, life: 14, maxLife: 14 });
                    }
                    if (!p.piercing) {
                        world.projectiles.splice(i, 1);
                        break;
                    }
                }
            }
        }

        if (world.moveMarker) {
            world.moveMarker.life -= 1;
            if (world.moveMarker.life <= 0) world.moveMarker = null;
        }
        for (let i = world.afterimages.length - 1; i >= 0; i--) {
            world.afterimages[i].life -= 1;
            if (world.afterimages[i].life <= 0) world.afterimages.splice(i, 1);
        }
        for (let i = world.floatTexts.length - 1; i >= 0; i--) {
            const ft = world.floatTexts[i];
            ft.y += ft.vy;
            ft.life -= 1;
            if (ft.life <= 0) world.floatTexts.splice(i, 1);
        }
        for (let i = world.effects.length - 1; i >= 0; i--) {
            const e = world.effects[i];
            e.life -= 1;
            e.r += (e.maxR - e.r) * 0.22;
            if (e.life <= 0) world.effects.splice(i, 1);
        }
        for (let i = world.dynamicPetals.length - 1; i >= 0; i--) {
            const dp = world.dynamicPetals[i];
            dp.x += dp.vx;
            dp.y += dp.vy;
            dp.vx *= 0.96;
            dp.vy = dp.vy * 0.95 + 0.05;
            dp.life -= 1;
            microOps += 2;
            if (dp.life <= 0) world.dynamicPetals.splice(i, 1);
        }
        return microOps;
    }

    // ========================================================================
    // 7. DRAWING: FACE RIG, CHERRY ROTOR, CARAVAN, MONSTERS & ENTITIES
    // ========================================================================
    function drawFacePortrait(ctx, c, w, h, tagLabel) {
        ctx.fillStyle = '#070b14';
        ctx.fillRect(0, 0, w, h);

        const emoBorder = {
            calm: '#06b6d4', determined: '#38bdf8', fierce: '#f43f5e',
            anxious: '#f59e0b', empathetic: '#10b981', triumph: '#facc15',
        };
        const tintColor = emoBorder[c.emotion] || '#06b6d4';
        const img = portraitImages[c.id];

        if (img && img.complete && img.naturalWidth > 0) {
            ctx.save();
            // Subtle emotional zoom/intensity framing
            const scale = c.emotion === 'fierce' || c.castFlash > 0 ? 1.12 : 1.04;
            const dw = w * scale;
            const dh = h * scale;
            const ox = (w - dw) * 0.5;
            const oy = (h - dh) * 0.36;
            ctx.drawImage(img, ox, oy, dw, dh);
            // Emotional vignette rim lighting
            const grad = ctx.createLinearGradient(0, 0, 0, h);
            grad.addColorStop(0, 'rgba(7, 11, 20, 0.42)');
            grad.addColorStop(0.55, 'rgba(7, 11, 20, 0)');
            grad.addColorStop(1, 'rgba(7, 11, 20, 0.85)');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, w, h);
            ctx.strokeStyle = tintColor;
            ctx.lineWidth = 2.5;
            ctx.strokeRect(1.25, 1.25, w - 2.5, h - 2.5);
            ctx.restore();
        } else {
            ctx.fillStyle = c.accent;
            ctx.fillRect(0, 0, w, h);
        }

        // Top tag & bottom emotion readout
        ctx.fillStyle = 'rgba(7, 11, 20, 0.82)';
        ctx.fillRect(0, 0, w, 17);
        ctx.fillStyle = tagLabel === 'A' ? '#38bdf8' : '#f59e0b';
        ctx.font = '700 9.5px "IBM Plex Mono", monospace';
        const emoKo = { calm: '평온', determined: '결의', fierce: '격앙', anxious: '긴장', empathetic: '수호', triumph: '환희' };
        ctx.fillText(`${tagLabel}·${STAT_ARCHETYPES[c.persona.domKey].code} ${emoKo[c.emotion] || ''}`, 4, 12);
    }

    function drawCherryTreeLayer(ctx, world, useRotorBlit) {
        if (useRotorBlit) {
            ensureBlossomRotorFrames();
            const phaseIdx = Math.floor((world.tick * 0.12) % BLOSSOM_ROTOR_PHASES);
            ctx.drawImage(blossomRotorFrames[phaseIdx], TREE_X - BLOSSOM_CANVAS_SIZE * 0.5, TREE_Y - BLOSSOM_CANVAS_SIZE * 0.62);
            ctx.fillStyle = world.treeDeformHeat > 0.08 ? 'rgba(244,114,182,0.88)' : 'rgba(16,185,129,0.78)';
            ctx.font = '600 9.5px "IBM Plex Mono", monospace';
            ctx.textAlign = 'center';
            ctx.fillText(
                world.treeDeformHeat > 0.08
                    ? `벚꽃 2,400꽃잎 · 개입구간 동적변형 (${world.dynamicPetals.length}개)`
                    : `벚꽃 2,400꽃잎 · 프레임로터 #${phaseIdx + 1}/8 (O(1))`,
                TREE_X, TREE_Y + 68
            );
            ctx.textAlign = 'left';
        } else {
            drawCherryTreeDirect(ctx, TREE_X, TREE_Y, world.tick * 0.08);
            ctx.fillStyle = 'rgba(245,158,11,0.85)';
            ctx.font = '600 9.5px "IBM Plex Mono", monospace';
            ctx.textAlign = 'center';
            ctx.fillText('기존 방식: 매 프레임 2,400꽃잎 전수 연산', TREE_X, TREE_Y + 68);
            ctx.textAlign = 'left';
        }
        for (const dp of world.dynamicPetals) {
            ctx.fillStyle = dp.color;
            ctx.globalAlpha = Math.max(0, dp.life / dp.maxLife);
            ctx.fillRect(dp.x, dp.y, dp.size, dp.size);
        }
        ctx.globalAlpha = 1;
    }

    function drawChampionToken(ctx, c, isSelected) {
        const r = c.isPlayer ? 22 : 20;
        const img = portraitImages[c.id];

        // 1) Ground shadow + directional aiming chevron (Eternal Return tactical ground ring)
        ctx.save();
        ctx.fillStyle = 'rgba(2, 6, 14, 0.52)';
        ctx.beginPath();
        ctx.ellipse(c.x, c.y + r * 0.85, r * 0.95, r * 0.42, 0, 0, Math.PI * 2);
        ctx.fill();

        // Directional aim wedge
        const aimX = c.x + Math.cos(c.facing) * (r + 12);
        const aimY = c.y + Math.sin(c.facing) * (r + 12);
        ctx.fillStyle = c.team === 0 ? 'rgba(56, 189, 248, 0.88)' : 'rgba(244, 63, 94, 0.88)';
        ctx.beginPath();
        ctx.moveTo(aimX, aimY);
        ctx.lineTo(c.x + Math.cos(c.facing + 0.34) * (r + 2), c.y + Math.sin(c.facing + 0.34) * (r + 2));
        ctx.lineTo(c.x + Math.cos(c.facing - 0.34) * (r + 2), c.y + Math.sin(c.facing - 0.34) * (r + 2));
        ctx.closePath();
        ctx.fill();

        if (isSelected) {
            ctx.strokeStyle = 'rgba(248, 250, 252, 0.82)';
            ctx.lineWidth = 1.6;
            ctx.setLineDash([5, 3]);
            ctx.beginPath();
            ctx.arc(c.x, c.y, r + 9, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Rooted CC indicator ring
        if (c.rootTimer > 0) {
            ctx.strokeStyle = '#facc15';
            ctx.lineWidth = 2.4;
            ctx.beginPath();
            ctx.arc(c.x, c.y, r + 5, 0, Math.PI * 2);
            ctx.stroke();
        }

        // 2) Circular-clipped High-Res Human Character Portrait Token!
        ctx.save();
        ctx.beginPath();
        ctx.arc(c.x, c.y, r, 0, Math.PI * 2);
        ctx.closePath();
        ctx.clip();
        if (img && img.complete && img.naturalWidth > 0) {
            ctx.drawImage(img, c.x - r * 1.15, c.y - r * 1.05, r * 2.3, r * 2.3);
        } else {
            ctx.fillStyle = c.accent;
            ctx.fillRect(c.x - r, c.y - r, r * 2, r * 2);
        }
        if (c.castFlash > 0) {
            ctx.fillStyle = `rgba(255, 255, 255, ${(c.castFlash / 14) * 0.35})`;
            ctx.fillRect(c.x - r, c.y - r, r * 2, r * 2);
        }
        ctx.restore();

        // 3) Metallic dual champion frame ring
        ctx.strokeStyle = c.isPlayer ? '#38bdf8' : c.team === 0 ? '#0ea5e9' : '#f43f5e';
        ctx.lineWidth = c.isPlayer ? 3.2 : 2.4;
        ctx.beginPath();
        ctx.arc(c.x, c.y, r, 0, Math.PI * 2);
        ctx.stroke();

        // Shield arc overlay
        if (c.shield > 1) {
            ctx.strokeStyle = '#34d399';
            ctx.lineWidth = 2.6;
            ctx.beginPath();
            ctx.arc(c.x, c.y, r + 3.5, -Math.PI * 0.5, -Math.PI * 0.5 + Math.PI * 2 * Math.min(1, c.shield / 48));
            ctx.stroke();
        }

        // Elemental mark badge
        if (c.elementTag) {
            const el = ELEMENTS[c.elementTag];
            ctx.fillStyle = el.color;
            ctx.beginPath();
            ctx.arc(c.x + r * 0.82, c.y - r * 0.78, 7.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#070b14';
            ctx.lineWidth = 1.4;
            ctx.stroke();
            ctx.fillStyle = '#041016';
            ctx.font = '700 8.5px "IBM Plex Mono", monospace';
            ctx.textAlign = 'center';
            ctx.fillText(el.name[0], c.x + r * 0.82, c.y - r * 0.78 + 3);
        }

        // 4) Authentic Eternal Return Top HP + Shield + SP Segmented Bar
        const barW = 54;
        const bx = c.x - barW * 0.5;
        const by = c.y - r - 18;
        ctx.fillStyle = 'rgba(5, 9, 17, 0.92)';
        ctx.fillRect(bx - 1, by - 1, barW + 2, 11);
        const hpRatio = Math.max(0, Math.min(1, c.hp / Math.max(1, c.maxHp)));
        ctx.fillStyle = c.isPlayer ? '#10b981' : c.team === 0 ? '#38bdf8' : '#f43f5e';
        ctx.fillRect(bx, by, barW * hpRatio, 6);
        if (c.shield > 1) {
            ctx.fillStyle = '#e2e8f0';
            ctx.fillRect(bx + barW * Math.max(0, hpRatio - 0.12), by, Math.min(barW * 0.28, (c.shield / 48) * barW * 0.3), 6);
        }
        // Subtle 4-segment HP ticks
        ctx.fillStyle = 'rgba(5, 9, 17, 0.65)';
        for (let seg = 1; seg < 4; seg++) ctx.fillRect(bx + (barW * seg) / 4, by, 1, 6);
        // SP (Mana) thin bar underneath HP
        ctx.fillStyle = '#2563eb';
        ctx.fillRect(bx, by + 7, barW * Math.max(0, Math.min(1, c.sp / c.maxSp)), 2.5);

        // Nameplate & Dominant 5-Stat Code
        ctx.fillStyle = '#f8fafc';
        ctx.font = '700 10px "Plus Jakarta Sans", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${c.name} · ${STAT_ARCHETYPES[c.persona.domKey].code}`, c.x, c.y + r + 14);
        ctx.restore();
    }

    function drawWorldEntities(ctx, world, showMeso, showMicro, isRotorSide) {
        if (isRotorSide && quantumLockEnabled && showMeso) {
            const obs = world.chars[0];
            ctx.save();
            ctx.strokeStyle = 'rgba(6, 182, 212, 0.34)';
            ctx.lineWidth = 1.4;
            ctx.setLineDash([6, 5]);
            ctx.beginPath();
            ctx.arc(obs.x, obs.y, OBSERVER_RADIUS, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.fillStyle = 'rgba(6, 182, 212, 0.72)';
            ctx.font = '600 9.5px "IBM Plex Mono", monospace';
            ctx.fillText('관측 반경 (외부 ψ 양자 잠금)', Math.max(34, obs.x - 85), Math.max(42, obs.y - OBSERVER_RADIUS - 6));
            ctx.restore();
        }

        // Right-Click MOBA Move Destination Marker
        if (showMicro && world.moveMarker) {
            const mm = world.moveMarker;
            const prog = 1 - mm.life / mm.maxLife;
            ctx.save();
            ctx.globalAlpha = 1 - prog;
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(mm.x, mm.y, 6 + prog * 18, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(mm.x - 5, mm.y); ctx.lineTo(mm.x + 5, mm.y);
            ctx.moveTo(mm.x, mm.y - 5); ctx.lineTo(mm.x, mm.y + 5);
            ctx.stroke();
            ctx.restore();
        }

        // Telegraphed Ground Skill Zones ([E] Snare Field & [R] Sanctuary Ultimate)
        if (showMicro && world.zones) {
            for (const z of world.zones) {
                const fillFrac = 1 - z.timer / z.maxTimer;
                ctx.save();
                ctx.fillStyle = z.kind === 'ultimate' ? 'rgba(52, 211, 153, 0.14)' : 'rgba(250, 204, 21, 0.15)';
                ctx.beginPath();
                ctx.arc(z.x, z.y, z.r, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = z.color;
                ctx.lineWidth = 2.2;
                ctx.beginPath();
                ctx.arc(z.x, z.y, z.r, 0, Math.PI * 2);
                ctx.stroke();
                // Expanding inner detonation timer circle
                ctx.fillStyle = z.kind === 'ultimate' ? 'rgba(52, 211, 153, 0.25)' : 'rgba(250, 204, 21, 0.26)';
                ctx.beginPath();
                ctx.arc(z.x, z.y, z.r * fillFrac, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = z.color;
                ctx.font = '700 10.5px "IBM Plex Mono", monospace';
                ctx.textAlign = 'center';
                ctx.fillText(z.label, z.x, z.y + 4);
                ctx.restore();
            }
        }

        if (showMeso) {
            // Covered Merchant Caravan Wagon on Trade Road
            const cv = world.caravan;
            ctx.save();
            ctx.fillStyle = 'rgba(0,0,0,0.45)';
            ctx.fillRect(cv.x - 20, ROAD_Y + 4, 40, 6);
            ctx.fillStyle = '#78350f';
            ctx.fillRect(cv.x - 19, ROAD_Y - 6, 38, 11);
            ctx.fillStyle = cv.halted ? '#be123c' : '#d97706';
            ctx.beginPath();
            ctx.arc(cv.x, ROAD_Y - 6, 17, Math.PI, 0);
            ctx.fill();
            ctx.strokeStyle = '#fef3c7';
            ctx.lineWidth = 1.2;
            ctx.stroke();
            ctx.fillStyle = '#1e293b';
            ctx.beginPath(); ctx.arc(cv.x - 12, ROAD_Y + 6, 4.5, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(cv.x + 12, ROAD_Y + 6, 4.5, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = cv.halted ? '#fda4af' : '#fde68a';
            ctx.font = '600 9px "IBM Plex Mono", monospace';
            ctx.textAlign = 'center';
            ctx.fillText(cv.halted ? '상인마차(피습!)' : '교역 상인마차', cv.x, ROAD_Y - 26);
            ctx.restore();

            // Horned Shadow Beast Road Monsters with HP bars
            for (const mon of world.monsters) {
                ctx.save();
                ctx.fillStyle = 'rgba(244, 63, 94, 0.25)';
                ctx.beginPath(); ctx.arc(mon.x, mon.y, 19, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = '#1f1024';
                ctx.strokeStyle = '#f97316';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(mon.x - 13, mon.y - 12);
                ctx.lineTo(mon.x - 6, mon.y - 4);
                ctx.lineTo(mon.x + 6, mon.y - 4);
                ctx.lineTo(mon.x + 13, mon.y - 12);
                ctx.lineTo(mon.x + 11, mon.y + 9);
                ctx.lineTo(mon.x - 11, mon.y + 9);
                ctx.closePath();
                ctx.fill(); ctx.stroke();
                ctx.fillStyle = '#fb923c';
                ctx.fillRect(mon.x - 6, mon.y - 2, 3, 3);
                ctx.fillRect(mon.x + 3, mon.y - 2, 3, 3);
                ctx.fillStyle = 'rgba(0,0,0,0.85)';
                ctx.fillRect(mon.x - 18, mon.y - 22, 36, 4);
                ctx.fillStyle = '#f97316';
                ctx.fillRect(mon.x - 18, mon.y - 22, 36 * Math.max(0, mon.hp / mon.maxHp), 4);
                ctx.restore();
            }

            // Relational Trust Beams
            for (const lk of world.links) {
                ctx.strokeStyle = lk.color;
                ctx.globalAlpha = 0.14 + lk.strength * 0.22;
                ctx.lineWidth = 1.2 + lk.strength * 1.4;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                ctx.moveTo(lk.x1, lk.y1);
                ctx.lineTo(lk.x2, lk.y2);
                ctx.stroke();
            }
            ctx.setLineDash([]);
            ctx.globalAlpha = 1;

            // Dash Afterimages
            if (world.afterimages) {
                for (const ai of world.afterimages) {
                    const img = portraitImages[ai.id];
                    ctx.save();
                    ctx.globalAlpha = (ai.life / ai.maxLife) * 0.45;
                    ctx.beginPath();
                    ctx.arc(ai.x, ai.y, 19, 0, Math.PI * 2);
                    ctx.clip();
                    if (img && img.complete && img.naturalWidth > 0) {
                        ctx.drawImage(img, ai.x - 21, ai.y - 20, 42, 42);
                    }
                    ctx.fillStyle = ai.color;
                    ctx.globalAlpha = (ai.life / ai.maxLife) * 0.28;
                    ctx.fillRect(ai.x - 22, ai.y - 22, 44, 44);
                    ctx.restore();
                }
            }

            // 6 Champions with Illustrated Portrait Tokens
            for (let i = 0; i < world.chars.length; i++) {
                const c = world.chars[i];
                if (isRotorSide && quantumLockEnabled && !c.observed) {
                    ctx.strokeStyle = 'rgba(148, 163, 184, 0.45)';
                    ctx.lineWidth = 1.2;
                    ctx.setLineDash([3, 3]);
                    ctx.beginPath();
                    ctx.arc(c.x, c.y, 18, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.setLineDash([]);
                    ctx.fillStyle = 'rgba(148, 163, 184, 0.78)';
                    ctx.font = '600 10px "IBM Plex Mono", monospace';
                    ctx.textAlign = 'center';
                    ctx.fillText(`ψ ${c.name} (잠금)`, c.x, c.y + 4);
                    ctx.textAlign = 'left';
                    continue;
                }

                drawChampionToken(ctx, c, i === selectedCharIdx);

                if (c.speechTimer > 0 && c.speech) {
                    ctx.save();
                    ctx.font = '500 10.5px "Plus Jakarta Sans", sans-serif';
                    const tw = Math.min(240, ctx.measureText(c.speech).width + 14);
                    const bx = Math.max(12, Math.min(W - tw - 12, c.x - tw * 0.5));
                    const by = Math.max(12, c.y - 62);
                    ctx.fillStyle = 'rgba(9, 14, 24, 0.94)';
                    ctx.fillRect(bx, by, tw, 20);
                    ctx.strokeStyle = c.accent;
                    ctx.lineWidth = 1;
                    ctx.strokeRect(bx, by, tw, 20);
                    ctx.fillStyle = '#e2e8f0';
                    ctx.textAlign = 'left';
                    ctx.fillText(c.speech, bx + 7, by + 13.5, tw - 14);
                    ctx.restore();
                }
            }
        }

        if (showMicro) {
            for (const p of world.projectiles) {
                const el = ELEMENTS[p.elemId] || ELEMENTS.frost;
                ctx.save();
                if (p.kind === 'lance') {
                    // Eternal Return style elongated glowing piercing spear!
                    ctx.translate(p.x, p.y);
                    ctx.rotate(p.ang || Math.atan2(p.vy, p.vx));
                    const grad = ctx.createLinearGradient(-34, 0, 14, 0);
                    grad.addColorStop(0, 'rgba(56, 189, 248, 0)');
                    grad.addColorStop(0.65, 'rgba(56, 189, 248, 0.85)');
                    grad.addColorStop(1, '#ffffff');
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.moveTo(16, 0);
                    ctx.lineTo(-4, -6);
                    ctx.lineTo(-34, 0);
                    ctx.lineTo(-4, 6);
                    ctx.closePath();
                    ctx.fill();
                } else {
                    ctx.fillStyle = el.glow;
                    ctx.beginPath(); ctx.arc(p.x, p.y, p.r * 2.1, 0, Math.PI * 2); ctx.fill();
                    ctx.fillStyle = el.color;
                    ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
                }
                ctx.restore();
            }
            for (const e of world.effects) {
                ctx.save();
                ctx.globalAlpha = e.life / e.maxLife;
                ctx.strokeStyle = e.color;
                ctx.lineWidth = e.type === 'combo' ? 3.4 : 2;
                ctx.beginPath();
                ctx.arc(e.x, e.y, e.r, 0, Math.PI * 2);
                ctx.stroke();
                if (e.label) {
                    ctx.fillStyle = e.color;
                    ctx.font = '700 11.5px "Plus Jakarta Sans", sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(e.label, e.x, e.y - e.r * 0.55);
                }
                ctx.restore();
            }
            if (world.floatTexts) {
                for (const ft of world.floatTexts) {
                    ctx.save();
                    ctx.globalAlpha = Math.max(0, ft.life / ft.maxLife);
                    ctx.font = '700 11.5px "IBM Plex Mono", monospace';
                    ctx.textAlign = 'center';
                    ctx.fillStyle = '#040812';
                    ctx.fillText(ft.text, ft.x + 1, ft.y + 1);
                    ctx.fillStyle = ft.color;
                    ctx.fillText(ft.text, ft.x, ft.y);
                    ctx.restore();
                }
            }
            if (world.bannerTimer > 0 && world.bannerText) {
                ctx.save();
                ctx.globalAlpha = Math.min(1, world.bannerTimer / 20);
                ctx.fillStyle = 'rgba(7, 10, 18, 0.90)';
                ctx.fillRect(W * 0.12, 10, W * 0.76, 26);
                ctx.strokeStyle = world.bannerColor;
                ctx.lineWidth = 1.4;
                ctx.strokeRect(W * 0.12, 10, W * 0.76, 26);
                ctx.fillStyle = world.bannerColor;
                ctx.font = '700 11px "Plus Jakarta Sans", sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(world.bannerText, W * 0.5, 27);
                ctx.restore();
            }
        }
    }

    function drawSuperpositionOverlay(ctx) {
        ctx.drawImage(s4Cache, 0, 0);
        drawCherryTreeLayer(ctx, worldB, true);
        ctx.fillStyle = 'rgba(7, 9, 14, 0.60)';
        ctx.fillRect(0, 0, W, H);

        for (let i = 0; i < worldA.chars.length; i++) {
            const a = worldA.chars[i];
            const b = worldB.chars[i];
            const dist = Math.hypot(b.x - a.x, b.y - a.y);
            const personaDiff = a.persona.domKey !== b.persona.domKey;
            const emoDiff = a.emotion !== b.emotion;
            const diverged = dist > 12 || personaDiff || emoDiff;

            if (diverged) {
                ctx.strokeStyle = personaDiff ? 'rgba(244, 63, 94, 0.90)' : 'rgba(245, 158, 11, 0.75)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(a.x, a.y);
                ctx.lineTo(b.x, b.y);
                ctx.stroke();

                ctx.strokeStyle = 'rgba(6, 182, 212, 0.65)';
                ctx.setLineDash([3, 3]);
                ctx.beginPath();
                ctx.arc(a.x, a.y, 17, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);

                ctx.fillStyle = personaDiff ? 'rgba(244, 63, 94, 0.28)' : 'rgba(245, 158, 11, 0.25)';
                ctx.beginPath();
                ctx.arc(b.x, b.y, 22, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = personaDiff ? '#f43f5e' : '#f59e0b';
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.fillStyle = '#fde68a';
                ctx.font = '600 10px "IBM Plex Mono", monospace';
                ctx.textAlign = 'center';
                const tag = personaDiff
                    ? `성향분기(${STAT_ARCHETYPES[a.persona.domKey].name}→${STAT_ARCHETYPES[b.persona.domKey].name})`
                    : emoDiff ? `표정분기(${a.emotion}→${b.emotion})` : `궤도 ${Math.round(dist)}px`;
                ctx.fillText(`${b.name}: ${tag}`, b.x, b.y - 27);
            } else {
                ctx.fillStyle = 'rgba(16, 185, 129, 0.25)';
                ctx.beginPath();
                ctx.arc(b.x, b.y, 17, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#10b981';
                ctx.lineWidth = 1.5;
                ctx.stroke();
                ctx.fillStyle = '#6ee7b7';
                ctx.font = '600 10px "IBM Plex Mono", monospace';
                ctx.textAlign = 'center';
                ctx.fillText(`${b.name} (동일 수렴)`, b.x, b.y - 22);
            }
        }
        ctx.textAlign = 'left';
    }

    // ========================================================================
    // 8. PARALLEL-UNIVERSE SAVE/LOAD & 3-BRANCH COUNTERFACTUAL ENDING PREDICTOR
    // ========================================================================
    function runParallelEndingPredictions(curValueBias, curEmpathy) {
        const specs = [
            { id: 'alpha', label: '우주 α · 현재 5스탯·사건 궤적', valBias: curValueBias, empathy: curEmpathy, accent: '#06b6d4' },
            { id: 'beta', label: '우주 β · 지혜(WIS)·신뢰 중재 분기', valBias: 0.35, empathy: 2.2, accent: '#10b981' },
            { id: 'gamma', label: '우주 γ · 무력(STR)·속전(AGI) 패권 분기', valBias: 2.0, empathy: 0.5, accent: '#f43f5e' },
        ];

        const results = specs.map((sp) => {
            const sim = deepCopyWorld(worldB);
            if (sp.id === 'beta') sim.chars.slice(0, 3).forEach((c) => { c.stats.wis = Math.min(98, c.stats.wis + 22); });
            if (sp.id === 'gamma') sim.chars.slice(0, 3).forEach((c) => { c.stats.str = Math.min(98, c.stats.str + 22); c.stats.agi = Math.min(98, c.stats.agi + 16); });
            for (let step = 0; step < 150; step++) {
                sim.tick += 2;
                evaluateSocioTacticalLayer(sim, 2.0, sp.valBias, sp.empathy, false, null);
                evolveMacroCausalWorld(sim, sp.valBias, sp.empathy);
            }
            return {
                ...sp,
                eraName: sim.society.eraName,
                ending: sim.society.endingPreview,
                trade: Math.round(sim.society.tradeVolume),
                price: Math.round(sim.society.priceIndex),
                politics: sim.society.politicsState,
            };
        });
        lastPredictions = results;
        renderParallelPredictionsUI();
        return results;
    }

    function renderParallelPredictionsUI() {
        const host = document.getElementById('parallel-endings-list');
        if (!host) return;
        host.textContent = '';
        if (!lastPredictions.length) {
            const hint = document.createElement('div');
            hint.className = 'macro-empty';
            hint.textContent = '[미래 엔딩 예측 실행]을 누르면 현재 사건·5대스탯 기준 3개 평행우주(α·β·γ)를 고속 롤아웃해 경제·정치·엔딩 분기를 비교합니다.';
            host.appendChild(hint);
            return;
        }
        for (const p of lastPredictions) {
            const card = document.createElement('button');
            card.type = 'button';
            card.className = 'parallel-card';
            card.style.borderLeftColor = p.accent;
            const top = document.createElement('div');
            top.className = 'parallel-top';
            top.textContent = `${p.label} → ${p.ending}`;
            const sub = document.createElement('div');
            sub.className = 'parallel-sub';
            sub.textContent = `상행 ${p.trade}% · 물가 ${p.price} │ 정치: ${p.politics} (클릭해 진입)`;
            card.appendChild(top);
            card.appendChild(sub);
            card.addEventListener('click', () => {
                if (window.ElysiaEngineBridge) {
                    window.ElysiaEngineBridge.applyControls({ envCoupling: p.valBias, objConnectivity: p.empathy });
                    window.ElysiaEngineBridge.setOutputView('overlay');
                }
                worldB.bannerText = `★ 평행우주 분기 진입: ${p.label} (${p.ending})`;
                worldB.bannerColor = p.accent;
                worldB.bannerTimer = 110;
            });
            host.appendChild(card);
        }
    }

    function renderSavedBranchesUI() {
        const host = document.getElementById('saved-branches-list');
        if (!host) return;
        host.textContent = '';
        if (!savedBranches.length) {
            const hint = document.createElement('span');
            hint.className = 'macro-empty-inline';
            hint.textContent = '저장된 세이브 분기 없음';
            host.appendChild(hint);
            return;
        }
        savedBranches.forEach((br, idx) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn branch-slot-btn';
            btn.textContent = `로드 #${idx + 1} (${br.eraShort} · ${br.time})`;
            btn.addEventListener('click', () => {
                worldA = deepCopyWorld(br.worldA);
                worldB = deepCopyWorld(br.worldB);
                s4Init = false;
                if (window.ElysiaEngineBridge) window.ElysiaEngineBridge.applyControls(br.controls);
                worldB.bannerText = `↺ 평행우주 세이브 #${idx + 1} 복원 완료 (${br.eraShort})`;
                worldB.bannerColor = '#06b6d4';
                worldB.bannerTimer = 95;
                syncStatSlidersToSelected();
                updateDigitalTwinInspectorUI();
            });
            host.appendChild(btn);
        });
    }

    function syncStatSlidersToSelected() {
        const cB = worldB.chars[selectedCharIdx];
        if (!cB) return;
        for (const k of ['str', 'agi', 'int', 'wis', 'vit']) {
            const sl = document.getElementById(`stat-b-${k}`);
            const vl = document.getElementById(`stat-b-val-${k}`);
            if (sl) sl.value = String(cB.stats[k]);
            if (vl) vl.textContent = String(cB.stats[k]);
        }
    }

    let activeProbeQuestion = '임무 끝나고 뭐 해? 왜 그렇게 살아?';

    function renderProbeReplyUI(cA, cB) {
        const elA = document.getElementById('probe-reply-a');
        const elB = document.getElementById('probe-reply-b');
        const elQ = document.getElementById('probe-active-q');
        if (!elA || !elB) return;
        const repA = composeProbeReply(cA, worldA, activeProbeQuestion);
        const repB = composeProbeReply(cB, worldB, activeProbeQuestion);
        if (elQ) elQ.textContent = `질문: "${activeProbeQuestion}"`;
        elA.textContent = `[원본 자아 A · ${STAT_ARCHETYPES[cA.persona.domKey].code}] "${repA.answer}"  (${repA.causeTag})`;
        elB.textContent = `[변형 자아 B · ${STAT_ARCHETYPES[cB.persona.domKey].code}] "${repB.answer}"  (${repB.causeTag})`;
    }

    function updateDigitalTwinInspectorUI() {
        const cA = worldA.chars[selectedCharIdx];
        const cB = worldB.chars[selectedCharIdx];
        if (!cA || !cB) return;

        const faceACanvas = document.getElementById('twin-face-a');
        const faceBCanvas = document.getElementById('twin-face-b');
        if (faceACanvas && faceBCanvas) {
            drawFacePortrait(faceACanvas.getContext('2d'), cA, faceACanvas.width, faceACanvas.height, 'A');
            drawFacePortrait(faceBCanvas.getContext('2d'), cB, faceBCanvas.width, faceBCanvas.height, 'B');
        }

        const elTitle = document.getElementById('twin-char-title');
        if (elTitle) {
            const diffPersona = cA.persona.domKey !== cB.persona.domKey;
            elTitle.textContent = `${cB.name} (${cB.role}) · ${diffPersona ? `5스탯 성향 분기! (${STAT_ARCHETYPES[cA.persona.domKey].name}→${STAT_ARCHETYPES[cB.persona.domKey].name})` : `주도 축: ${STAT_ARCHETYPES[cB.persona.domKey].name}(${STAT_ARCHETYPES[cB.persona.domKey].code})`}`;
        }
        const elCond = document.getElementById('twin-situation-text');
        if (elCond) {
            elCond.textContent = `성향(B): ${cB.persona.temperament} │ 취미·개성: ${cB.persona.hobby}`;
        }
        const elSens = document.getElementById('twin-sensory-text');
        if (elSens) {
            elSens.textContent = `감각·반응 특성: ${cB.persona.sensory} │ 상황: ${cB.situation}`;
        }
        const elSpeechA = document.getElementById('twin-speech-a');
        if (elSpeechA) elSpeechA.textContent = `[기준 A · ${STAT_ARCHETYPES[cA.persona.domKey].code}] "${cA.speech}"`;
        const elSpeechB = document.getElementById('twin-speech-b');
        if (elSpeechB) elSpeechB.textContent = `[분기 B · ${STAT_ARCHETYPES[cB.persona.domKey].code}] "${cB.speech}"`;
        const elThought = document.getElementById('twin-thought-b');
        if (elThought) elThought.textContent = `내면 사유(B): ${cB.thought}`;

        // Update Inverse-Causal Life-Arc (Past -> Present Occupation/After-Work -> Relational Web -> Future Becoming)
        const lifeB = deriveLifeTrajectory(cB, worldB);
        const elPast = document.getElementById('life-past-val');
        const elPres = document.getElementById('life-present-val');
        const elRel = document.getElementById('life-relation-val');
        const elFut = document.getElementById('life-future-val');
        if (elPast) elPast.textContent = lifeB.pastOrigin;
        if (elPres) elPres.textContent = `직업: ${lifeB.occupation} │ 퇴근·생활: ${lifeB.afterWork} │ 추구 의미: ${lifeB.meaning}`;
        if (elRel) elRel.textContent = lifeB.relationalWeb;
        if (elFut) elFut.textContent = lifeB.futureBecoming;

        // Keep Interactive Dialogue Probe A vs B live-synced with any stat or world change!
        renderProbeReplyUI(cA, cB);

        // Update Real 5-Step Macro Causal Chain Feed!
        const chainHost = document.getElementById('causal-chain-feed');
        if (chainHost) {
            chainHost.textContent = '';
            for (const stepTxt of worldB.society.chainSteps) {
                const line = document.createElement('div');
                line.className = 'chain-step-line';
                line.textContent = stepTxt;
                chainHost.appendChild(line);
            }
        }
    }

    function updateMobaHudUI() {
        const p = worldB.chars[0];
        if (!p) return;
        const hpFill = document.getElementById('moba-hp-fill');
        const hpTxt = document.getElementById('moba-hp-text');
        const spFill = document.getElementById('moba-sp-fill');
        const spTxt = document.getElementById('moba-sp-text');
        if (hpFill) hpFill.style.width = `${Math.max(0, Math.min(100, (p.hp / p.maxHp) * 100)).toFixed(1)}%`;
        if (hpTxt) hpTxt.textContent = `HP ${Math.round(p.hp)} / ${p.maxHp}${p.shield > 1 ? ` (+${Math.round(p.shield)})` : ''}`;
        if (spFill) spFill.style.width = `${Math.max(0, Math.min(100, (p.sp / p.maxSp) * 100)).toFixed(1)}%`;
        if (spTxt) spTxt.textContent = `SP ${Math.round(p.sp)} / ${p.maxSp}`;

        for (const sk of ['q', 'w', 'e', 'r', 'space']) {
            const btn = document.getElementById(`moba-slot-${sk}`);
            const cdMask = document.getElementById(`moba-cd-${sk}`);
            const cdTxt = document.getElementById(`moba-cdtxt-${sk}`);
            if (!btn) continue;
            const rem = p.skillCd[sk] || 0;
            const maxCd = Math.max(24, Math.round(QWER_SKILLS[sk].cdTicks * p.persona.cooldownScale));
            const noSp = p.sp < QWER_SKILLS[sk].spCost;
            btn.classList.toggle('on-cd', rem > 0);
            btn.classList.toggle('no-sp', rem <= 0 && noSp);
            if (cdMask) cdMask.style.height = rem > 0 ? `${Math.min(100, (rem / maxCd) * 100).toFixed(1)}%` : '0%';
            if (cdTxt) cdTxt.textContent = rem > 0 ? `${(rem / 60).toFixed(1)}s` : '';
        }
    }

    // ========================================================================
    // PUBLIC API
    // ========================================================================
    window.ElysiaDigitalTwinRPG = {
        reset() {
            worldA = createWorld();
            worldB = createWorld();
            s4Init = false;
            historyRing.length = 0;
            historyHead = 0;
            syncStatSlidersToSelected();
            updateDigitalTwinInspectorUI();
            updateMobaHudUI();
            renderParallelPredictionsUI();
            renderSavedBranchesUI();
        },
        syncBtoA() {
            worldB = deepCopyWorld(worldA);
            s4Init = false;
            syncStatSlidersToSelected();
            updateDigitalTwinInspectorUI();
            updateMobaHudUI();
        },
        queueQwerSkill(slot) {
            if (slot in QWER_SKILLS) queuedQwerKey = slot;
        },
        queueSkill(elemId) {
            const map = { frost: 'q', fire: 'w', volt: 'e', aether: 'r' };
            queuedQwerKey = map[elemId] || 'q';
        },
        issueMoveOrder(x, y) { queuedMoveOrder = { x, y }; },
        queueDash() { queuedDash = true; },
        selectCharacter(idx) {
            selectedCharIdx = Math.max(0, Math.min(worldA.chars.length - 1, idx));
            syncStatSlidersToSelected();
            updateDigitalTwinInspectorUI();
        },
        setSelectedCharStatB(statKey, val) {
            const cB = worldB.chars[selectedCharIdx];
            if (!cB || !(statKey in cB.stats)) return;
            cB.stats[statKey] = Math.max(10, Math.min(99, Number(val)));
            cB.persona = derivePersonaFrom5Stats(cB.stats, 1.0, 1.0);
            cB.maxHp = cB.persona.maxHp;
            const arch = STAT_ARCHETYPES[cB.persona.domKey];
            cB.speech = cB.persona.domKey === 'agi'
                ? '시간 끌지 마! 지금 당장 처리해야 속이 풀리겠어!'
                : cB.persona.domKey === 'str'
                    ? '복잡하게 굴지 말고 힘으로 정면 돌파한다!'
                    : cB.persona.domKey === 'int'
                        ? '이 판의 이권과 인과 구조가 전부 읽히기 시작했어.'
                        : cB.persona.domKey === 'wis'
                            ? '눈앞의 승패보다 마을과 시대의 균형을 봐야 해.'
                            : '무슨 일이 와도 내가 이 자리를 끝까지 버텨낸다.';
            cB.thought = `[${arch.code} ${cB.stats[cB.persona.domKey]} 주도] ${cB.persona.temperament} · 취미(${cB.persona.hobby})`;
            cB.speechTimer = 135;
            cB.emotion = cB.persona.domKey === 'agi' || cB.persona.domKey === 'str' ? 'fierce' : cB.persona.domKey === 'int' ? 'triumph' : 'empathetic';
            cB.browTilt = cB.persona.domKey === 'agi' || cB.persona.domKey === 'str' ? 0.8 : cB.persona.domKey === 'wis' ? -0.45 : 0.15;
            updateDigitalTwinInspectorUI();
        },
        triggerEventCatalyst(kind, audioPulse) {
            triggerCausalCatalystOnWorld(worldA, kind);
            triggerCausalCatalystOnWorld(worldB, kind);
            s4Init = false;
            updateDigitalTwinInspectorUI();
            if (audioPulse) audioPulse(kind === 'mana_vein' ? 580 : kind === 'famine_hoard' ? 240 : 320);
        },
        probeCharacterDialogue(questionText) {
            const q = String(questionText || '').trim();
            if (!q) return;
            activeProbeQuestion = q;
            const cA = worldA.chars[selectedCharIdx];
            const cB = worldB.chars[selectedCharIdx];
            if (!cA || !cB) return;
            const repB = composeProbeReply(cB, worldB, q);
            cB.speech = repB.answer.length > 52 ? `${repB.answer.slice(0, 50)}…` : repB.answer;
            cB.thought = `[대화 프로브] ${repB.causeTag}`;
            cB.speechTimer = 140;
            cB.mouthOpen = 0.62;
            cB.emotion = cB.persona.domKey === 'agi' || cB.persona.domKey === 'str' ? 'determined' : cB.persona.domKey === 'wis' ? 'empathetic' : 'calm';
            renderProbeReplyUI(cA, cB);
            updateDigitalTwinInspectorUI();
        },
        toggleQuantumLock() { quantumLockEnabled = !quantumLockEnabled; return quantumLockEnabled; },
        toggleVideoTransduction() {
            videoTransduceEnabled = !videoTransduceEnabled;
            if (videoTransduceEnabled) {
                worldB.bannerText = `★ HD 영상 인과 실시간 전이 ON · 소스: ${latestVideoMood.title}`;
                worldB.bannerColor = '#06b6d4';
                worldB.bannerTimer = 95;
            }
            return videoTransduceEnabled;
        },
        feedVideoMood(mood) { if (mood) latestVideoMood = { ...latestVideoMood, ...mood }; },
        saveParallelBranch(controls) {
            const entry = {
                time: new Date().toLocaleTimeString('ko-KR', { hour12: false }),
                eraShort: worldB.society.eraName.split('·')[0].trim(),
                worldA: deepCopyWorld(worldA),
                worldB: deepCopyWorld(worldB),
                controls: { ...controls },
            };
            savedBranches.push(entry);
            if (savedBranches.length > 4) savedBranches.shift();
            renderSavedBranchesUI();
            worldB.bannerText = `● 평행우주 스냅샷 #${savedBranches.length} 저장 완료 (${entry.eraShort})`;
            worldB.bannerColor = '#10b981';
            worldB.bannerTimer = 80;
        },
        predictEndings(valBias, empathy) { return runParallelEndingPredictions(valBias, empathy); },
        triggerCrisisEvent(audioPulse) { this.triggerEventCatalyst('monster_raid', audioPulse); },
        stageCreativeScene(patternId, audioPulse) {
            const kind = patternId === 'spiral_vortex' ? 'monster_raid' : patternId === 'twin_orbit' ? 'mana_vein' : 'famine_hoard';
            triggerCausalCatalystOnWorld(worldB, kind);
            s4Init = false;
            if (audioPulse) audioPulse(540);
        },
        getRingLength() { return historyRing.length; },

        step({ legacyCtx, rotorCtx, thumbS4Ctx, thumbS2Ctx, thumbS0Ctx, state, keys, mouse, firedClick, audioPulse }) {
            if (state.scrubbing && historyRing.length > 0) {
                const snap = historyRing[Math.min(historyRing.length - 1, Math.max(0, state.scrubIdx))];
                if (snap) {
                    renderMacroWorld(legacyCtx, snap);
                    drawCherryTreeLayer(legacyCtx, snap, false);
                    drawWorldEntities(legacyCtx, snap, true, true, false);
                    renderMacroWorld(rotorCtx, snap);
                    drawCherryTreeLayer(rotorCtx, snap, true);
                    drawWorldEntities(rotorCtx, snap, true, true, true);
                }
                return null;
            }

            let effValueBias = state.envCoupling;
            let effEmpathy = state.objConnectivity;
            if (videoTransduceEnabled) {
                effValueBias = Math.max(0.1, Math.min(2.2, 1.0 + latestVideoMood.warmth * 0.85 + (latestVideoMood.flux - 0.25) * 0.8));
                effEmpathy = Math.max(0.2, Math.min(2.4, 1.15 - latestVideoMood.chaos * 0.65));
            }

            // LEFT: Conventional 60Hz Brute Force
            const tL0 = performance.now();
            worldA.tick += 1;
            worldA.climatePhase += 0.012;
            worldA.crisisLevel = Math.max(0.14, worldA.crisisLevel * 0.996);
            evolveMacroCausalWorld(worldA, 1.0, 1.0);
            const leftSocioOps = evaluateSocioTacticalLayer(worldA, 1.0, 1.0, 1.0, false, null);
            const leftMicroOps = stepMicroPhysics(worldA, keys, mouse, firedClick, null);
            legacyCtx.save();
            if (worldA.shake > 0) legacyCtx.translate((Math.random() - 0.5) * worldA.shake, (Math.random() - 0.5) * worldA.shake);
            renderMacroWorld(legacyCtx, worldA);
            drawCherryTreeLayer(legacyCtx, worldA, false);
            drawWorldEntities(legacyCtx, worldA, true, true, false);
            legacyCtx.restore();
            const leftMs = performance.now() - tL0;
            const leftTotalOps = 6200 + BLOSSOM_COUNT + leftSocioOps + leftMicroOps;

            // RIGHT: Coupled Multi-Rate Scale-Rotor + O(1) Blossom Rotor + Quantum Lock
            const tR0 = performance.now();
            worldB.tick += 1;
            worldB.climatePhase += 0.012;
            worldB.crisisLevel = Math.max(0.14, worldB.crisisLevel * 0.996);

            let rS4Ops = 0, rS2Ops = 0, rS0Ops = 0;
            if (!s4Init || worldB.tick % state.s4Stride === 0) {
                evolveMacroCausalWorld(worldB, effValueBias, effEmpathy);
                renderMacroWorld(s4Ctx, worldB);
                s4Init = true;
                rS4Ops = 6200;
            }
            if (worldB.tick % state.s2Stride === 0) {
                rS2Ops = evaluateSocioTacticalLayer(worldB, state.s2Stride, effValueBias, effEmpathy, quantumLockEnabled, audioPulse);
            }
            rS0Ops = stepMicroPhysics(worldB, keys, mouse, firedClick, audioPulse) + 1 + worldB.dynamicPetals.length;

            queuedQwerKey = null;
            queuedDash = false;
            queuedMoveOrder = null;
            if (worldB.tick % 3 === 0) updateMobaHudUI();

            let posDiffSum = 0, emoSame = 0, personaSame = 0;
            for (let i = 0; i < worldA.chars.length; i++) {
                const a = worldA.chars[i];
                const b = worldB.chars[i];
                posDiffSum += Math.hypot(b.x - a.x, b.y - a.y);
                if (a.emotion === b.emotion) emoSame += 1;
                if (a.persona.domKey === b.persona.domKey) personaSame += 1;
            }
            const avgPosDiff = posDiffSum / worldA.chars.length;
            const s4Same = Math.max(0, Math.min(100, (1 - Math.abs(worldB.society.tradeVolume - worldA.society.tradeVolume) / 80) * 100));
            const s2Same = Math.max(0, Math.min(100, (1 - avgPosDiff / 190) * 60 + (personaSame / 6) * 40));
            const s0Same = Math.max(0, Math.min(100, (emoSame / 6) * 65 + (1 - Math.min(1, avgPosDiff / 240)) * 35));

            let origin = '전 계층 수렴 (5스탯·사건·시대 동일)';
            if (personaSame < 6) {
                origin = `분기 개시: 5대 스탯 성향 변이 → 대사·표정·사건 대응 연쇄 분기`;
            } else if (worldB.monsters.length > 0 || worldB.manaVein.discovered || worldB.famine.active) {
                origin = `인과 연쇄 진행 중: ${worldB.society.activeChainTitle}`;
            } else if (videoTransduceEnabled) {
                origin = `HD 영상 인과 전이 활성 → 시대 '${worldB.society.eraName}'`;
            }

            const view = state.outputView;
            rotorCtx.save();
            if (worldB.shake > 0 && view === 'composite') rotorCtx.translate((Math.random() - 0.5) * worldB.shake, (Math.random() - 0.5) * worldB.shake);
            if (view === 'composite') {
                rotorCtx.drawImage(s4Cache, 0, 0);
                drawCherryTreeLayer(rotorCtx, worldB, true);
                drawWorldEntities(rotorCtx, worldB, true, true, true);
            } else if (view === 'overlay') {
                drawSuperpositionOverlay(rotorCtx);
            } else if (view === 's4') {
                rotorCtx.drawImage(s4Cache, 0, 0);
                drawCherryTreeLayer(rotorCtx, worldB, true);
            } else if (view === 's2') {
                rotorCtx.fillStyle = '#05080f';
                rotorCtx.fillRect(0, 0, W, H);
                drawWorldEntities(rotorCtx, worldB, true, false, true);
            } else if (view === 's0') {
                rotorCtx.fillStyle = '#05080f';
                rotorCtx.fillRect(0, 0, W, H);
                drawWorldEntities(rotorCtx, worldB, false, true, true);
            }
            rotorCtx.restore();
            const rightMs = performance.now() - tR0;

            if (worldB.tick % 6 === 0) {
                thumbS4Ctx.drawImage(s4Cache, 0, 0, 120, 68);

                thumbS2Ctx.save();
                thumbS2Ctx.fillStyle = '#05080f';
                thumbS2Ctx.fillRect(0, 0, 160, 90);
                thumbS2Ctx.scale(160 / W, 90 / H);
                drawWorldEntities(thumbS2Ctx, worldB, true, false, true);
                thumbS2Ctx.restore();

                thumbS0Ctx.save();
                thumbS0Ctx.fillStyle = '#05080f';
                thumbS0Ctx.fillRect(0, 0, 160, 90);
                thumbS0Ctx.scale(160 / W, 90 / H);
                drawWorldEntities(thumbS0Ctx, worldB, false, true, true);
                thumbS0Ctx.restore();
            }

            if (worldB.tick % 14 === 0) updateDigitalTwinInspectorUI();
            if (worldB.tick % 8 === 0) {
                historyRing[historyHead] = deepCopyWorld(worldB);
                historyHead = (historyHead + 1) % RING_CAP;
            }

            return {
                tick: worldB.tick,
                sunAngle: worldB.climatePhase,
                score: worldB.score,
                comboCount: worldB.comboCount,
                leftTotalOps,
                rS4Ops,
                rS2Ops,
                rS0Ops,
                leftMs,
                rightMs,
                s4Same,
                s2Same,
                s0Same,
                origin,
                activeRatio: Math.min(1, 0.14 + worldB.projectiles.length * 0.09 + worldB.effects.length * 0.12),
            };
        },
    };
})();
