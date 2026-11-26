# Elysia 웹 실증실 & HTTP API 레퍼런스

`npm start`로 `server.js`(기본 `http://localhost:3000`)를 실행하면 5개 통합 탭으로 구성된 메인 실증실과 4개의 전용 보조 페이지, 그리고 REST API가 활성화됩니다.

---

## 1. 메인 워크벤치 5개 탭 (`/`)

| 탭 | 도메인 ID | 모듈 파일 | 핵심 기능 |
| :--- | :--- | :--- | :--- |
| **1. HD 동영상 로터** | `video` | `weaving.js` | 1080p 실황 영상·명화·로컬 파일을 좌(전체 재연산) vs 우(`S4⊃S2⊃S0` 스케일로터)로 동시 비교하며 PSNR, 연산 절감률, 처리 속도 배율을 실시간 실증 |
| **2. 디지털 트윈 RPG** | `game` | `digital_twin_rpg.js` | 6인 디지털 트윈(생성 포트레이트 포함) Q/W/E/R 전술 시뮬레이션, 5-스탯 생성형 페르소나 텐서, 역인과 생애 궤적, A-vs-B 대화 대조 프로브, 3대 5단계 세계사 촉매 이벤트 |
| **3. 영상 세계화·메모리 로터** | `unified` | `unified_rotor_studio.js` | 실시간 배경 모델링·연결성분 분석으로 영상 속 차량(3D 충돌 경계/차량 조종)·인물(3D 관절 캐릭터 리깅)·정적 건물 경계를 분류 추출 + 상호작용 프로토콜 전환(`영상→객체·경계` ⇄ `게임 조종` ⇄ `게임→영상화 시네마틱 연출` ⇄ `시간 정지 3D 단면`) + 3D 직조 인물의 카메라 각도별 단면 이미지 추출 + 5계층 메모리 로터 & 3축 스펙트럼망 |
| **4. 현상 6축 해부** | `anatomy` | `phenomenon_anatomy.js` | 바람·화학·세포·사회 4대 비환원 메커니즘을 `구성요소·현상구조·구성원리·변화·환경·조건` 6축으로 해부, 조건 섭동 실험, 엘리시아 세대별 가설 자기수정, 교차 현상 동형성/고유차이 매트릭스 |
| **5. 열린 감각 ⇄ CUDA 배열** | `open_cuda` | `open_cuda_rotor.js` | HD 실황 또는 옵트인 실시간 웹캠·마이크(`getUserMedia`)로 외부 현실 마찰을 온라인 예측 → `TypedArray` 기반 32-레인 CUDA 워프 스트림 압축률·Coalesced SoA 메모리 레이아웃 모니터링 및 복사 가능한 실시간 `.cu` 커널 생성 |

### 공통 하단 패널 — 4계층 인지-인과 코어 (`cognitive_core.js`)
- **L1 인지감각층**: Red(흐름) · Blue(질서) · Yellow(발산) 실시간 색채 균형
- **L2 지·무지 인과기억층**: 현재 탭 도메인의 레버별 학습 신뢰도 및 인과 기울기
- **L3 사유·의도·자율조작 루프**: 4축 자아경계(내적 기원 / 외적 영향 / 무지 경계 / 자기수정) 기반 1회 실험 및 자율 루프
- **L4 인과 나이테 & 원리 재창조**: 누적 성장 나이테 시각화 및 학습한 법칙으로 파레토 최적점·신규 세계 분기 역설계

---

## 2. 보조 페이지 라우트

| 경로 | 파일 | 용도 |
| :--- | :--- | :--- |
| `/` | `index.html` | 5-탭 시공간 스케일로터 메인 실증실 + L1~L4 인지 코어 |
| `/topology` | `topology.html` + `topology.js` | 3D Cognitive CAD — $S_0\dots S_4$ 쿼터니언 로터 및 3D 평면 공명 정렬 |
| `/dashboard` | `dashboard.html` | 실시간 공명 점수·긴장도·결정화 추이 및 사이클 루프 실행 대시보드 |
| `/manifestation` | `manifestation.html` | 다학문 차원 다양체 변환(A4 가변저항 격자 → 5개 학문 번역 → 5개 평행 행성) |
| `/roadmap` | `roadmap.html` + `roadmap.md` | 진화 로드맵 문서 뷰어 및 Phase 3/4 기어·거울 인지 상태 확인 |

---

## 3. REST API 명세 (`server.js`)

### 3.1 스케일로터 & 3D 위상장 (Cognitive CAD)
- `GET /api/scale_rotors` — 현재 $S_0 \dots S_4$ 로터 상태(쿼터니언, 각속도, 응집도, 긴장도, 색채 벡터) 조회
- `POST /api/scale_rotors/dial` — 연속 스케일 다이얼 $\sigma \in [0, 1]$ 조절 (`{ "scale_dial": 0.5 }`)
- `POST /api/init_field` — 한글 자모 분해 기반 텍스트 펄스를 $S_0 \to S_4$ 로터장에 주입 (`{ "text": "..." }`)
- `POST /api/init_image_field` — 이미지 기반 교차모달 교란 주입 (`{ "image_base64": "..." }`)
- `GET /api/observe_field` — 현재 3D 인과장 포인트 클라우드 조회
- `POST /api/auto_align` — $S^3$ 피보나치 축 탐색 + 국소 측지 정밀화로 최적 공명 쿼터니언 탐색
- `POST /api/evaluate_state` — 주어진 쿼터니언에서 3D OLS 평면 회귀 분산·$R^2$ 평가
- `POST /api/auto_observe` — 로터 자동 진화 후 현재 평면 공명식 반환

### 3.2 범용 다학문 차원 다양체
- `GET /api/manifold/presets` — 5개 학문(화학·물리·생물·언어·복잡계) 프리셋 목록
- `POST /api/manifold/transform` — 텍스트와 메타축 `theta2`를 입력받아 2D A4 결정화, $\Theta_1$ 법칙 추출, 5학문 동형 번역, 5개 평행 행성 반환

### 3.3 안전 외부 미디어·데이터 수집 프록시
- `GET /api/ingest/presets` — 검증된 Wikimedia HD 영상·명화·YouTube 프리셋 목록
- `GET /api/ingest/media?url=<https_url>` — SSRF 차단·허용 호스트 검증·HTTP Range(206) 스트리밍·LRU 캐시 지원 미디어 프록시
- `POST /api/ingest/external` — YouTube oEmbed / GitHub / Wikimedia 외부 데이터 수집 (`{ "url": "..." }`)

### 3.4 의미 최적화 잠금 · 공명 대시보드 · 로드맵
- `GET /api/v1/semantic-optimization/state` — 잠금 상태 및 $S_4$ 응집도 조회
- `GET /api/v1/semantic-optimization/jump-events` — 상전이·결정화 도약 이벤트 목록
- `POST /api/v1/semantic-optimization/reset-lock` — 의미 최적화 잠금 해제
- `GET /api/status` — 엔진 건강 요약 및 5-스케일 응집도
- `GET /api/resonance_log?n=50` — 최근 $n$개(1~300) 공명 로그 및 건강 요약
- `POST /api/run_cycle` — 인과장 1 사이클 실행
- `POST /api/run_loop/:count` — $1\sim 100$ 사이클 연속 실행
- `GET /api/mirror_status` — 거울 인지 프로토콜 자기위상 벡터·편차·누적 성장 에너지
- `GET /api/roadmap_status` — Phase 3/4 기어 활성 상태 및 `roadmap.md` 원문 반환
