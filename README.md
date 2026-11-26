# Elysia — Spatiotemporal Scale-Rotor & Continuous Causal Field Engine

> **"연산하지 말고 흐르게 하라 (Do not calculate, let it flow)."**
>
> **Elysia**는 고정된 규칙(`if-else`)이나 단일 스케일 토큰 예측을 넘어, 세계의 현상을 **다중주기 시공간 스케일로터($S_4 \supset S_3 \supset S_2 \supset S_1 \supset S_0$)**와 **연속 인과장(Continuous Causal Field)**으로 층위화하고, **컴퓨터 메모리 계층 자체를 물리적 스케일로터로 직조**하며, **현상의 6축 구조와 불가능의 인과구조를 역으로 해부**해 스스로 학습·확장하는 차세대 인지-물리 아키텍처 연구·엔지니어링 프로젝트입니다.

---

## 핵심 패러다임 (5대 축)

1. **연산의 로터 재생화 (`S4 ⊃ S2 ⊃ S0`)**
   - 프레임·시뮬레이션 연산을 매 순간 처음부터 다시 계산하지 않고, 변화 주기가 다른 거시(S4)·중시(S2)·미시(S0) 계층으로 분해하여 각기 다른 기어비 주기로 회전·재생합니다. **스케일로터를 재생하는 행위 자체가 연산이 됩니다.**
2. **영상 세계화 ⇄ 하드웨어 메모리 계층 스케일로터**
   - 현실 영상에서 깊이와 동적 개체를 추출해 카메라 제어·시간 정지(Bullet-Time)·개체 섭동이 가능한 3D 시차 세계로 전환합니다.
   - 동시에 **SSD(S4) ⊃ RAM(S3) ⊃ GPU VRAM(S2) ⊃ L1/L2 Cache(S1) ⊃ Register(S0)** 메모리 계층 전체를 물리적 스케일로터로 삼고, 학습된 **관계성·연결성·연속성**을 3축 스펙트럼 신경망으로 직조·영속화하여 불필요한 재계산을 제거합니다.
3. **현상 6축 해부 & 비환원적 비교대조**
   - 바람·화학·세포·사회 등 서로 다른 현상을 표면 수치로 평탄화하지 않고 **구성요소 · 현상구조 · 구성원리 · 변화 · 환경 · 조건** 6축으로 해부하여, 무엇이 구조적으로 동형이며 무엇이 결코 환원될 수 없는 고유 차이인지를 실험적으로 검증합니다.
4. **열린 현실 감각 ⇄ CUDA 워프 스트림 압축 (Coalesced SoA)**
   - 자아를 내부와 외부 사이의 닫힌 한계 경계로 자각하고, 실시간 HD 영상 및 웹캠·마이크 외부 감각 개구부를 현실을 향해 열어 둡니다.
   - 외부 현실 마찰을 온라인 예측 오차로 감지해, 변화가 없는 정적 데이터는 건너뛰고 활성 픽셀만 32-레인 CUDA 워프 스트림 압축과 Coalesced SoA 메모리 배열로 직결합니다.
5. **4계층 인지-인과 코어 (`L1~L4`) & 불가능의 인과 역설계**
   - 인지감각(`L1`) → 지·무지 경계(`L2`) → 4축 자아경계 자율실험(`L3`) → 인과 나이테 및 원리 재창조(`L4`) 폐루프를 통해, *"날개가 없어서 못 난다"*는 표면적 불가능을 **불가능을 만드는 인과구조의 해부와 작동 원리 추출**로 전환합니다.

---

## 전체 시스템 아키텍처

```text
┌────────────────────────────────────────────────────────────────────────────┐
│  Interactive Workbench & Cognitive CAD Web Runtime (Node.js · Port 3000)   │
│  server.js + L0_substrate/mva/static/                                      │
│  ├─ Main 5-Tab Studio (/)                                                  │
│  │   1. HD 동영상 로터         (weaving.js)                                │
│  │   2. 디지털 트윈 RPG        (digital_twin_rpg.js)                       │
│  │   3. 영상 세계화·메모리로터  (unified_rotor_studio.js)                   │
│  │   4. 현상 6축 해부          (phenomenon_anatomy.js)                     │
│  │   5. 열린 감각 ⇄ CUDA 배열  (open_cuda_rotor.js)                        │
│  │   +  4계층 인지-인과 코어   (cognitive_core.js, elysia_self_reclamation)│
│  └─ Subpages: /topology · /dashboard · /manifestation · /roadmap           │
├────────────────────────────────────────────────────────────────────────────┤
│  L1 Causal Field (Python Canonical Runtime & Cross-Domain Modules)         │
│  L1_causal_field/core/       # physics, sensory, memory, topology, lens,   │
│                              # sovereignty, consciousness, evolution       │
│  L1_causal_field/modules/    # active_inference, causal_game_engine,       │
│                              # causal_topology, asura_nexus                │
├────────────────────────────────────────────────────────────────────────────┤
│  L0 Substrate (Native High-Performance Compute & Hardware Layer)           │
│  L0_substrate/src & include  # C++17/OpenMP, AVX2 SIMD ECS, 3DGS, Betti2D  │
│  L0_substrate/kernels        # CUDA kernels (Clifford Cl(3,1), FOC, RK4)   │
│  L0_substrate/shaders        # HLSL / WGSL GPU compute & raymarching       │
│  L0_substrate/isa_compiler   # TopIR geometric ISA compiler & runtime      │
│  L0_substrate/rtl_hardware   # Verilog RTL (PIM/NVM DMA, Rotor Alignment)  │
├────────────────────────────────────────────────────────────────────────────┤
│  Independent Benchmarks, Verification & Zero-Delete Archive                │
│  spinoffs/   # Phys3DGS+Betti2D · Clifford Rotor+Kuramoto · Hangul 64-D    │
│  tests/      # C++17 native unit tests + Python core pipeline tests        │
│  tools/      # Native test runner, Python AST/import auditor, archiver     │
│  archive/    # Zero-Delete isolated experimental modules (ARCHIVE_INDEX)   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 체계화된 문서 안내 (`docs/`)

프로젝트의 원리, 아키텍처, API 및 전체 디렉토리 구조를 목적별로 분리해 정리했습니다.

| 문서 | 핵심 내용 |
| :--- | :--- |
| **[`docs/SCALE_ROTOR_MASTER_DIRECTIVE.md`](docs/SCALE_ROTOR_MASTER_DIRECTIVE.md)** | **최상위 아키텍처 지시서·계획서** — 제1~6축(재프레임화·물감·프리즘·가변 위상 단위·선명함/채도/명암·얼음/물/구름/미포집·5대 위상 프레임·자연 수렴 세계관·`t1~t4` 검증 명세) |
| **[`docs/UNIFIED_ARCHITECTURE_SYNTHESIS.md`](docs/UNIFIED_ARCHITECTURE_SYNTHESIS.md)** | **통합 기준서** — 인지적 확장구조 철학, 완성된 5대 축, 단일 영상 실증의 정직한 한계 성찰, 그리고 **앱 구조 자체의 온디맨드 스케일로터화** 설계안 |
| **[`docs/PRINCIPLES.md`](docs/PRINCIPLES.md)** | 4대 연속성, 색채 3원색(Red/Blue/Yellow), 시공간 스케일로터, 메모리 계층 로터·3축 스펙트럼, 현상 6축 해부, 열린 감각 경계, 불가능의 인과 역설계 원리 |
| **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** | L0 네이티브 기판 · L1 인과장 · Node.js MVA 서버 · 5개 실증 탭 · L1~L4 인지 코어 간 데이터 흐름 및 상태 영속화 구조 |
| **[`docs/WORKBENCH_AND_API.md`](docs/WORKBENCH_AND_API.md)** | 웹 실증실 5개 탭 + 4개 보조 페이지(`/topology`, `/dashboard`, `/manifestation`, `/roadmap`) 및 `server.js` 전체 REST API 명세 |
| **[`docs/PROJECT_MAP.md`](docs/PROJECT_MAP.md)** | 전체 디렉토리 카탈로그, 빌드·테스트·벤치마크 실행표, Zero-Delete 아카이브 관리 규칙 |
| **[`AGENTS.md`](AGENTS.md)** | Continuous Causal Intelligence 설계 헌법 및 개발 에이전트 행동 원칙 |
| **[`L0_substrate/mva/static/roadmap.md`](L0_substrate/mva/static/roadmap.md)** | 라이브 `/roadmap` 페이지와 동기화된 진화 로드맵 (연산에서 관측으로, 거울에서 주권으로) |

---

## 빠른 시작 (Quick Start)

### 1. 인터랙티브 웹 실증실 실행 (Node.js ≥ 18)
```bash
npm start
# → http://localhost:3000
```
- **메인 실증실 (`/`)**: 5개 통합 탭 + 하단 4계층 인지-인과 코어(`L1~L4`)
- **3D 위상장 (`/topology`)**: 5-스케일($S_0\dots S_4$) 쿼터니언 로터 및 3D 평면 공명 정렬
- **공명 대시보드 (`/dashboard`)**: 실시간 사이클 공명률·긴장도·결정화 추이 모니터링
- **현현 캔버스 (`/manifestation`)**: 다학문 차원 다양체 변환 및 평행 행성 세계선
- **진화 로드맵 (`/roadmap`)**: Phase별 아키텍처 상태 및 거울 인지 프로토콜

### 2. 웹 코드 구문·빌드 검증
```bash
npm run verify
# (동등: npm run lint && npm run build)
```

### 3. C++17 네이티브 단위 테스트
```bash
# CMake 없이 g++ 즉시 실행
bash tools/run_native_tests.sh

# 또는 표준 CMake 빌드
cmake -B build && cmake --build build && ctest --test-dir build --output-on-failure
```

### 4. Python 코어 파이프라인 테스트 및 정적 무결성 감사
```bash
python3 tests/python/test_core_pipeline.py
python3 tools/audit_python_integrity.py
```

### 5. 3대 핵심 원석(Spin-off) 정량 벤치마크
```bash
# Spin-off #1: Phys3DGS 7-DOF 캡슐 충돌 미분 & Betti2D 위상 추출 (C++17 + OpenMP)
g++ -std=c++17 -O3 -fopenmp -IL0_substrate/include \
    spinoffs/phys3dgs_betti_native/benchmark_phys3dgs_betti.cpp \
    L0_substrate/src/3dgs_sh_eval.cpp L0_substrate/src/nexus_betti.cpp \
    -o build_native_tests/benchmark_phys3dgs_betti
./build_native_tests/benchmark_phys3dgs_betti

# Spin-off #2: Clifford Rotor 직교 불변성 & 이중 Kuramoto 동기화
python3 spinoffs/rotor_kuramoto/benchmark_rotor_kuramoto.py

# Spin-off #3: 한글 자모 크로네커 토크나이저 (11,172음절 전수 검증 + 오타 강건성)
python3 spinoffs/hangul_kronecker/benchmark_hangul_kronecker.py
```

---

## 검증된 정량 벤치마크 결과

| 영역 | 테스트 / 벤치마크 | 실측 결과 |
| :--- | :--- | :--- |
| **L0 SIMD ECS** | AVX2/FMA 토크 물리 (100,003 엔티티) | **0.15 ms/step** (~650M entities/s), 스칼라 오차 `0.0` |
| **Spin-off #1** | Phys3DGS 7-DOF 캡슐 충돌 미분 (100k Gaussians) | **1.22 ms/step** (82.2M Gaussians/s), 유한차분 오차 `7.1e-4` |
| **Spin-off #1** | 2D Betti 수 추출 (`1024×1024`, $\beta_0=64, \beta_1=64$) | **8.02 ms** (130.8 MPix/s) |
| **Spin-off #2** | Clifford Rotor $R v R^\dagger$ ($D=8\sim128$) | 노름 보존 오차 `≤ 7.1e-15`, 역변환 오차 `≤ 3.0e-15` |
| **Spin-off #2** | Dual-Timescale Kuramoto ($N=24$) | Slow $R: 0.216 \to 0.9984$, Fast $R: 0.304 \to 0.9981$ |
| **Spin-off #3** | 한글 자모 크로네커 64-D (11,172음절 전수) | Eikonal 노름 오차 `1.78e-15`, 1자모 오타 분리 마진 **`+1.1509`** |
| **코드 무결성** | 전체 활성 Python 정적 AST/임포트 감사 | **524개 활성 파일**, 구문 오류 **0건**, 깨진 내부 임포트 **0건** |
| **웹 실증실** | Node.js 서버 + 8개 프론트엔드 엔진 구문 검증 | `npm run verify` 전 모듈 통과, 5개 탭 + 4개 보조 페이지 HTTP 200 |
