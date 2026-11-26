# Elysia 프로젝트 맵 & 검증 카탈로그 (Project Map)

이 문서는 저장소 전체 디렉토리 구조, 주요 파일의 책임, 그리고 재현 가능한 검증·벤치마크 명령을 한눈에 정리합니다.

---

## 1. 최상위 디렉토리 맵

```text
/
├── README.md                  # 마스터 개요, 5대 패러다임, 빠른 시작 및 정량 벤치마크
├── AGENTS.md                  # Continuous Causal Intelligence 개발 헌법
├── server.js                  # Node.js 웹 실증실 & 5-스케일 로터 / 다양체 / 안전 프록시 서버
├── package.json               # Node.js 실행·구문 검증 스크립트 (start, dev, build, lint, verify)
├── metadata.json              # 앱 메타데이터 및 카메라·마이크 권한 선언
├── CMakeLists.txt             # C++17 네이티브 빌드 설정
├── pyproject.toml             # Python 패키지 및 연구 코어 메타데이터
│
├── docs/                      # 체계화된 아키텍처·원리·API·맵 문서 모음
│   ├── UNIFIED_ARCHITECTURE_SYNTHESIS.md # 통합 기준서 (인지적 확장구조 · 실증 성찰 · 앱 스케일로터화 설계)
│   ├── PRINCIPLES.md          # 핵심 철학 및 6대 구조 원리
│   ├── ARCHITECTURE.md        # 3단 계층 아키텍처, 모듈 통신 브리지, 영속화 규약
│   ├── WORKBENCH_AND_API.md   # 웹 실증실 5개 탭 + 4개 보조 페이지 + 전체 REST API 명세
│   └── PROJECT_MAP.md         # 본 문서 (전체 디렉토리 및 검증 카탈로그)
│
├── L0_substrate/              # Layer 0: 네이티브 물리·GPU·RTL 기판 및 MVA 웹 UI
│   ├── engine_native/         # C++/CUDA FOC 커널, 스케줄러, VRAM 모니터
│   ├── include/               # C++17 / CUDA 핵심 헤더 (CausalPhaseTensor, TopIR, Betti 등)
│   ├── src/                   # C++17/OpenMP, AVX2 SIMD ECS, CUDA 커널 구현체
│   ├── kernels/               # 독립 CUDA 커널 (Cl(3,1), Raymarcher, Homeostasis, Multisensory)
│   ├── shaders/               # HLSL & WGSL GPU 컴퓨트·레이마칭 셰이더
│   ├── isa_compiler/          # TopIR 기하 ISA 컴파일러 및 코드젠
│   ├── rtl_hardware/          # Verilog RTL (PIM/NVM DMA, Rotor Alignment, SRAM-R)
│   └── mva/                   # Minimum Viable Architecture 웹 앱
│       ├── api/               # Python MVA API 참조 구현
│       └── static/            # 인터랙티브 5-탭 웹 UI + 4개 보조 페이지 + JS 엔진 8종
│
├── L1_causal_field/           # Layer 1: Python 정본 연속 인과장 코어 & 응용 모듈
│   ├── core/                  # physics, sensory, memory, topology, lens, sovereignty,
│   │                          # consciousness, evolution, layer_0~3, Hangul Kronecker
│   ├── modules/               # active_inference, causal_game_engine, causal_topology, asura_nexus
│   └── benchmarks/            # C++/CUDA/Python 벤치마크 및 프로파일러
│
├── spinoffs/                  # 독립 패키징·벤치마크 가능한 3대 핵심 원석
│   ├── phys3dgs_betti_native/ # Phys3DGS 7-DOF 충돌 미분 + 2D Betti 수 추출 (C++17/OpenMP)
│   ├── rotor_kuramoto/        # Clifford Rotor 직교 불변성 + Dual-Timescale Kuramoto
│   └── hangul_kronecker/      # 한글 자모 64-D 크로네커 토크나이저 (11,172음절 전수 검증)
│
├── src/
│   └── assets/images/         # 디지털 트윈 RPG 캐릭터 고화질 포트레이트 자산 6종
│
├── tests/
│   ├── cpp/                   # C++17 네이티브 단위 테스트 (3DGS, Betti, SIMD ECS, TopIR)
│   └── python/                # Python 코어 파이프라인 통합 테스트
│
├── tools/
│   ├── run_native_tests.sh    # CMake 없이 g++로 C++17 테스트 일괄 실행
│   ├── audit_python_integrity.py # 전체 활성 Python 파일 AST 구문·임포트 무결성 감사
│   └── archive_orphans.py     # Zero-Delete 정책 기반 고립 실험 모듈 격리 도구
│
└── archive/                   # Zero-Delete 정책으로 안전 보관된 실험 이력
    ├── ARCHIVE_INDEX.md       # 아카이브 색인
    └── L1_causal_field/       # 격리된 과거 실험 모듈
```

---

## 2. 검증·테스트·벤치마크 명령 카탈로그

| 검증 대상 | 실행 명령 | 기대 결과 |
| :--- | :--- | :--- |
| **웹 서버 & 8개 JS 엔진 구문 검사** | `npm run verify` | 구문 오류 0건 (`server.js` + `static/*.js` 8종) |
| **웹 실증실 실행** | `npm start` | `http://0.0.0.0:3000` 리스닝, 5개 탭 + 4개 보조 페이지 HTTP 200 |
| **C++17 네이티브 단위 테스트** | `bash tools/run_native_tests.sh` | 3DGS, Betti2D, SIMD ECS, TopIR 전체 통과 |
| **CMake 전체 빌드 & CTest** | `cmake -B build && cmake --build build && ctest --test-dir build --output-on-failure` | 전체 네이티브 타깃 통과 |
| **Python 코어 파이프라인 테스트** | `python3 tests/python/test_core_pipeline.py` | 인과장 파이프라인 정상 통과 |
| **Python 정적 무결성 감사** | `python3 tools/audit_python_integrity.py` | 524개 활성 파일 구문 오류 0건, 깨진 내부 임포트 0건 |
| **Spin-off #2 (Clifford + Kuramoto)** | `python3 spinoffs/rotor_kuramoto/benchmark_rotor_kuramoto.py` | 노름 오차 `≤ 7.1e-15`, 동기화 $R \to 0.998+$ |
| **Spin-off #3 (Hangul 64-D)** | `python3 spinoffs/hangul_kronecker/benchmark_hangul_kronecker.py` | 11,172음절 전수 검증, 오타 분리 마진 `+1.1509` |

---

## 3. 저장소 유지관리 원칙 (Zero-Delete Policy)

1. **Zero-Delete 보존**: 과거 실험 코드나 레거시 연구 파일은 삭제하지 않고 `archive/`로 격리하며 `archive/ARCHIVE_INDEX.md`에 기록합니다.
2. **계층 경계 준수**: 고속 네이티브·커널·웹 UI는 `L0_substrate/`, 정본 인과장 이론 및 Python 연구 코어는 `L1_causal_field/`, 독립 배포·벤치마크 자산은 `spinoffs/`, 체계화된 문서는 `docs/`에 배치합니다.
3. **실측 기반 문서화**: 모든 벤치마크 수치와 API 계약은 실제 코드와 실행 결과로 검증된 값만 기록합니다.
