#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build_native_tests"
mkdir -p "${BUILD_DIR}"

CXX="${CXX:-g++}"
CXXFLAGS="-std=c++17 -O3 -Wall -Wextra -fopenmp"
INCLUDES="-I${ROOT_DIR}/L0_substrate/include -I${ROOT_DIR}/L0_substrate/isa_compiler"

echo "=== [1/3] Compiling & Running test_nexus_betti ==="
${CXX} ${CXXFLAGS} ${INCLUDES} \
    "${ROOT_DIR}/tests/cpp/test_nexus_betti.cpp" \
    "${ROOT_DIR}/L0_substrate/src/nexus_betti.cpp" \
    -o "${BUILD_DIR}/test_nexus_betti"
"${BUILD_DIR}/test_nexus_betti"

echo "=== [2/3] Compiling & Running test_3dgs_sh_eval ==="
${CXX} ${CXXFLAGS} ${INCLUDES} \
    "${ROOT_DIR}/tests/cpp/test_3dgs_sh_eval.cpp" \
    "${ROOT_DIR}/L0_substrate/src/3dgs_sh_eval.cpp" \
    -o "${BUILD_DIR}/test_3dgs_sh_eval"
"${BUILD_DIR}/test_3dgs_sh_eval"

echo "=== [3/3] Compiling & Running test_simd_gpu_ecs (AVX2/FMA) ==="
SIMD_FLAGS=""
if grep -q "avx2" /proc/cpuinfo 2>/dev/null; then
    SIMD_FLAGS="-mavx2 -mfma"
fi
${CXX} ${CXXFLAGS} ${SIMD_FLAGS} ${INCLUDES} \
    "${ROOT_DIR}/tests/cpp/test_simd_gpu_ecs.cpp" \
    "${ROOT_DIR}/L0_substrate/src/simd_gpu_ecs/simd_torque_transmission_system.cpp" \
    -o "${BUILD_DIR}/test_simd_gpu_ecs"
"${BUILD_DIR}/test_simd_gpu_ecs"

if [ -f "${ROOT_DIR}/tests/cpp/test_topir_parser.cpp" ]; then
    echo "=== [4/4] Compiling & Running test_topir_parser ==="
    ${CXX} ${CXXFLAGS} ${INCLUDES} \
        "${ROOT_DIR}/tests/cpp/test_topir_parser.cpp" \
        "${ROOT_DIR}/L0_substrate/src/topir_runtime_engine.cpp" \
        -o "${BUILD_DIR}/test_topir_parser"
    "${BUILD_DIR}/test_topir_parser"
fi

echo "=== ALL NATIVE C++ TESTS PASSED ==="
