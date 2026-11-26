# Elysia 시스템 아키텍처 (System Architecture)

이 문서는 Elysia 저장소의 계층 구조(L0 → L1 → MVA Web Runtime)와 브라우저·서버 간 실시간 데이터 흐름을 정리합니다.

---

## 1. 3단 계층 구조

### Layer 0 — 네이티브 물리·하드웨어 기판 (`L0_substrate/`)
고속 연속 물리 연산, 위상 추출, GPU 커널 및 하드웨어 RTL 설계를 담당합니다.
- **C++17 / OpenMP / AVX2 SIMD ECS (`src/`, `include/`, `engine_native/`)**: 3DGS 구면조화·7-DOF 충돌 미분(`3dgs_sh_eval.cpp`), 2D Betti 수 추출(`nexus_betti.cpp`), 위상 잠금 엔진(`phase_lock_engine.cpp`), 감각 위상 코어(`sensory_phase_core.cpp`), 인과 메모리 캐시(`causal_memory_cache_manager.cpp`).
- **CUDA 커널 (`kernels/`, `src/*.cu`)**: Clifford $Cl(3,1)$ 로터, FOC 스케줄러, 이중 시간척도 RK4, 부교감 통합·유사분열 분기 커널, 비동기 고정 메모리 스트림.
- **GPU 셰이더 (`shaders/`)**: HLSL(`ComputeGravitySoA`, `ElysiaFusedKernel`, `RaymarchShader`, `attractor_terrain`) 및 WGSL(`elysia_resonant_field`).
- **기하 ISA 컴파일러 (`isa_compiler/`)**: TopIR 파서·코드젠·런타임(`topir_compiler.py`, `topir_runtime_engine.cpp`).
- **Verilog RTL (`rtl_hardware/`)**: `rotor_alignment_engine.v`, `pim_nvm_dma_pipeline.v`, `sram_r_register.v`.

### Layer 1 — 정본 인과장 코어 (`L1_causal_field/`)
Python 기반 정본 연속 인과장 연구 코드와 도메인별 응용 모듈을 포함합니다.
- **`core/`**: `physics`(CausalField), `sensory`, `memory`, `topology`, `lens`, `sovereignty`, `consciousness`, `evolution`, `ingestion`, `orchestration`, `elysia_hangul_kronecker_tokenizer.py` 등 4개 계층(`layer_0_substrate` ~ `layer_3_macro`) 구성.
- **`modules/`**: `active_inference`, `causal_game_engine`, `causal_topology`, `asura_nexus`, `asset_generator`.
- **`benchmarks/`**: C++/CUDA/Python 성능·위상 프로파일러.

### Layer 2 — 인터랙티브 웹 실증실 & MVA 서버 (`server.js` + `L0_substrate/mva/static/`)
별도 빌드 번들러 없이 Node.js 표준 HTTP 서버(`0.0.0.0:3000`)와 순수 ES/Canvas/WebGL 모듈로 즉시 구동되는 실시간 실증 환경입니다.

---

## 2. Node.js 서버 엔진 (`server.js`) 내부 구성

`server.js`는 정적 UI 서빙과 함께 4개의 서버-사이드 엔진을 내장합니다.

1. **`ElysiaLiveEngine` (5-스케일 쿼터니언 로터 엔진)**
   - $S_0 \dots S_4$ 중첩 로터의 상향 토크 전달(Upward Ascent)과 하향 가소성 분화(Downward Plastic Differentiation)를 $S^3$ 단위 쿼터니언 지수 사상으로 적분합니다.
   - 3D 최소자승법(OLS) 평면 회귀(`fitSymbolicPlane`) 및 피보나치 구면 탐색 기반 공명 정렬(`findResonanceAngle`)을 수행합니다.
   - Semantic Optimization Lock과 거울 인지 프로토콜(`mirror`) 상태를 유지합니다.
2. **범용 다학문 차원 다양체 엔진 (`runUniversalManifoldTransform`)**
   - 입력 텍스트를 2D A4 가변저항 격자(`8×8` 매크로 셀) 위에서 병렬 결정화하고, 4개 핵심 법칙 벡터 $\Theta_1$(보존·구배·결합·경계)과 메타축 $\Theta_2$를 추출해 물리·화학·생물·언어·복잡계 5개 학문으로 동시 번역하고 5개 평행 행성 세계선을 생성합니다.
3. **안전 외부 데이터 수집 프록시 (`ingestExternalData`, `fetchCachedSafeMedia`)**
   - 허용된 공개 호스트(Wikimedia Commons, YouTube, GitHub)만 HTTPS로 수집하며, DNS 해석 후 사설/루프백 IP 차단(SSRF 방어), 10MB 상한, HTTP Range 스트리밍(206 Partial Content), 3클립 LRU 캐시를 적용합니다.
4. **정적 자산 라우터**
   - `/static/*` (`L0_substrate/mva/static/`, `Cache-Control: no-cache`)
   - `/src/assets/images/*` (생성된 디지털 트윈 캐릭터 포트레이트 6종)

---

## 3. 프론트엔드 모듈 아키텍처 (`L0_substrate/mva/static/`)

```text
index.html (5-Tab Workspace + L1~L4 Cognitive Core)
 ├── weaving.js                  ── Tab 1: HD 동영상 시공간 스케일로터 + 전역 ElysiaEngineBridge
 ├── digital_twin_rpg.js         ── Tab 2: 디지털 트윈 전술 RPG (Q/W/E/R · 5-스탯 페르소나 텐서 · A/B 대화)
 ├── unified_rotor_studio.js     ── Tab 3: 영상→3D 시차 세계화 카메라 로터 + 5계층 메모리 로터 + 3축 스펙트럼망
 ├── phenomenon_anatomy.js       ── Tab 4: 6축 현상 해부 & 비환원적 인과 검증실 (바람·화학·세포·사회)
 ├── open_cuda_rotor.js          ── Tab 5: 열린 현실 감각(HD/웹캠·마이크) ⇄ CUDA 32-레인 워프 압축 / SoA
 ├── cognitive_core.js           ── 하단 L1~L4 4계층 인지-인과 코어 (5개 탭 공통 폐루프 학습·재창조)
 └── elysia_self_reclamation.js  ── 자율 주권·자기회수 보조 프로토콜
```

### 모듈 간 통신 브리지 (`window.ElysiaEngineBridge`)
`weaving.js`가 노출하는 `ElysiaEngineBridge`는 5개 탭의 공통 상태 스냅샷(`domain`, `s4SamePct`, `s2SamePct`, `s0SamePct`, `psnr`, `savedPct`, `speedRatio`, `controls`)을 `cognitive_core.js`에 제공합니다.
- `cognitive_core.js`는 5개 도메인(`video`, `game`, `unified`, `anatomy`, `open_cuda`) 모두에 대한 `LEVER_SPECS`와 `ensureDomainKnowledge()` 자동 보정 로직을 보유하여, 어떤 탭으로 전환하더라도 `L1~L4` 자율 실험 루프가 끊김 없이 동작합니다.

---

## 4. 브라우저 영속 상태 (`localStorage` 키 규약)

| Storage Key | 소유 모듈 | 저장 내용 |
| :--- | :--- | :--- |
| `elysia_cognitive_memory_v1` | `cognitive_core.js` | 5개 도메인별 학습된 인과 기울기·신뢰도, 인과 나이테(`rings`), 실험 이력(`traces`), 재창조 횟수 |
| `elysia_cognitive_voxel_bridge_v1` | `cognitive_core.js` | 인지 실험 결과를 `/topology` 3D 공간 보셀 브리지로 전달하기 위한 스냅샷 |
| `elysia_unified_spectrum_ssd_v1` | `unified_rotor_studio.js` | **S4 SSD 영속 계층** — 3축(관계성·연결성·연속성) 직조 스펙트럼 신경망 노드·간선 및 히트 통계 |

---

## 5. 보안 및 UI 설계 원칙

- **안전한 DOM 렌더링**: 동적 문자열에 `innerHTML`을 사용하지 않고 `document.createElement` + `textContent`로 렌더링합니다.
- **안전한 API 파싱**: 대시보드 및 프론트엔드 fetch 호출은 `res.ok`와 `content-type: application/json`을 검증한 뒤 파싱합니다.
- **최소 권한 감각 개구부**: 웹캠·마이크(`getUserMedia`)는 사용자가 Tab 5에서 명시적으로 활성화할 때만 요청하며, 기본값은 즉시 실행 가능한 HD 실황 영상 모드입니다.
