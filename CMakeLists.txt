cmake_minimum_required(VERSION 3.18)
project(causal_engine_core LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(L0_DIR "${CMAKE_CURRENT_SOURCE_DIR}/L0_substrate")
set(L1_DIR "${CMAKE_CURRENT_SOURCE_DIR}/L1_causal_field")

# Optional CUDA compiler
include(CheckLanguage)
check_language(CUDA)

if(CMAKE_CUDA_COMPILER)
    enable_language(CUDA)
    set(CMAKE_CUDA_STANDARD 17)
    set(CMAKE_CUDA_STANDARD_REQUIRED ON)

    if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
        set(CMAKE_CUDA_ARCHITECTURES 61 75 86)
    endif()
endif()

option(BUILD_D3D12_RENDERER "Build Direct3D12 Volume Raymarcher GUI Engine (Windows only)" OFF)
option(ELYSIA_BUILD_TESTS "Build Elysia C++ verification test suite" ON)

find_package(OpenMP REQUIRED)
find_package(Eigen3 3.3 QUIET)

include_directories(
    ${L0_DIR}/include
    ${L0_DIR}/isa_compiler
    ${L1_DIR}/modules/causal_topology
    ${CMAKE_CURRENT_SOURCE_DIR}
)

if(EIGEN3_FOUND)
    include_directories(${EIGEN3_INCLUDE_DIR})
endif()

# -----------------------------------------------------------------------------
# Core C++ Libraries (L0_substrate)
# -----------------------------------------------------------------------------
add_library(nexus_core STATIC
    ${L0_DIR}/src/nexus_betti.cpp
    ${L0_DIR}/src/3dgs_sh_eval.cpp
    ${L0_DIR}/src/topir_runtime_engine.cpp
)
target_include_directories(nexus_core PUBLIC ${L0_DIR}/include)
target_link_libraries(nexus_core PRIVATE OpenMP::OpenMP_CXX)

add_library(topir_runtime SHARED
    ${L0_DIR}/src/topir_runtime_engine.cpp
)
target_include_directories(topir_runtime PUBLIC ${L0_DIR}/include)
target_link_libraries(topir_runtime PRIVATE OpenMP::OpenMP_CXX)

add_library(simd_gpu_ecs STATIC
    ${L0_DIR}/src/simd_gpu_ecs/simd_torque_transmission_system.cpp
    ${L0_DIR}/src/simd_gpu_ecs/gpu_particle_frame_pipeline.cpp
    ${L0_DIR}/src/simd_gpu_ecs/indirect_dispatch_pipeline.cpp
)
target_include_directories(simd_gpu_ecs PUBLIC ${L0_DIR}/include)
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    target_compile_options(simd_gpu_ecs PRIVATE -mavx2 -mfma)
endif()

# Shared memory benchmark (if source exists)
if(EXISTS "${L0_DIR}/src/nexus_shared_memory_bench.cpp")
    add_executable(nexus_shared_memory_bench ${L0_DIR}/src/nexus_shared_memory_bench.cpp)
    target_link_libraries(nexus_shared_memory_bench PRIVATE OpenMP::OpenMP_CXX)
endif()

# Optional HLSL DXC Offline Compilation
find_program(DXC_EXECUTABLE dxc PATHS "$ENV{WindowsSDKDir}/bin/$ENV{WindowsSDKLibVersion}/x64" "/usr/bin" "/usr/local/bin")
if(DXC_EXECUTABLE AND EXISTS "${L0_DIR}/shaders/ElysiaFusedKernel.hlsl")
    add_custom_target(
        Compile_ElysiaFusedKernel ALL
        COMMAND ${DXC_EXECUTABLE} -E CS_EvolveSystem -T cs_6_5 -Fo "${CMAKE_CURRENT_BINARY_DIR}/ElysiaFusedKernel.cso" "${L0_DIR}/shaders/ElysiaFusedKernel.hlsl"
        COMMENT "Compiling Shader: ElysiaFusedKernel.hlsl"
    )
endif()

# -----------------------------------------------------------------------------
# Elysia Dual Pillars Hardware Pipeline Library (Host Fallback / C++)
# -----------------------------------------------------------------------------
set(ELYSIA_HARDWARE_CU_SOURCES
    ${L0_DIR}/src/phase_lock_evaluator.cu
    ${L0_DIR}/src/sensory_tensor_encoder.cu
    ${L0_DIR}/src/sensory_quantizer.cu
    ${L0_DIR}/src/codebook_online_trainer.cu
    ${L0_DIR}/src/multi_gpu_nvlink_router.cu
)
set_source_files_properties(${ELYSIA_HARDWARE_CU_SOURCES} PROPERTIES LANGUAGE CXX COMPILE_FLAGS "-x c++")

add_library(elysia_hardware STATIC
    ${L0_DIR}/src/d3d12_causal_page_allocator.cpp
    ${L0_DIR}/src/d3d12_cuda_interop.cpp
    ${L0_DIR}/src/d3d12_cuda_semaphore.cpp
    ${L0_DIR}/src/causal_memory_cache_manager.cpp
    ${L0_DIR}/src/elysian_engine_main_loop.cpp
    ${ELYSIA_HARDWARE_CU_SOURCES}
)
target_include_directories(elysia_hardware PUBLIC ${L0_DIR}/include)

# Autonomic Causal Architecture Sources (Host Fallback)
set(AUTONOMIC_CU_SOURCES
    ${L0_DIR}/src/k_parasympathetic_consolidation.cu
    ${L0_DIR}/src/k_singularity_rotor_bypass.cu
    ${L0_DIR}/src/k_mitotic_tensor_branching.cu
    ${L0_DIR}/src/k_parasympathetic_node_fusion.cu
    ${L0_DIR}/src/k_mitotic_branching_fast.cu
)
set_source_files_properties(${AUTONOMIC_CU_SOURCES} PROPERTIES LANGUAGE CXX COMPILE_FLAGS "-x c++ -include elysia/cuda_host_stub.h")

if(EXISTS "${L1_DIR}/benchmarks/benchmark_parasympathetic.cu")
    set_source_files_properties(${L1_DIR}/benchmarks/benchmark_parasympathetic.cu PROPERTIES LANGUAGE CXX COMPILE_FLAGS "-x c++ -include elysia/cuda_host_stub.h")
    add_executable(benchmark_parasympathetic
        ${L1_DIR}/benchmarks/benchmark_parasympathetic.cu
        ${AUTONOMIC_CU_SOURCES}
    )
    target_include_directories(benchmark_parasympathetic PUBLIC ${L0_DIR}/include)
    target_link_libraries(benchmark_parasympathetic PRIVATE OpenMP::OpenMP_CXX)
endif()

# Elysia FOC & Clifford Wave Computing (Host Fallback)
set_source_files_properties(${L0_DIR}/src/elysia_foc_kernel.cu PROPERTIES LANGUAGE CXX COMPILE_FLAGS "-x c++ -include elysia/cuda_host_stub.h")
if(EXISTS "${L0_DIR}/src/elysia_foc_main.cpp")
    add_executable(elysia_foc_main
        ${L0_DIR}/src/elysia_foc_main.cpp
        ${L0_DIR}/src/elysia_foc_kernel.cu
        ${L0_DIR}/src/elysia_scheduler.cpp
    )
    target_include_directories(elysia_foc_main PUBLIC ${L0_DIR}/include)
    target_link_libraries(elysia_foc_main PRIVATE OpenMP::OpenMP_CXX)
endif()

# -----------------------------------------------------------------------------
# CUDA / Host Fallback Core Benchmarks
# -----------------------------------------------------------------------------
set(ELYSIA_CORE_CU_TARGETS
    "elysia_core_bench;${L0_DIR}/src/elysia_core_loop.cu"
    "elysia_pinned_async_stream;${L0_DIR}/src/elysia_pinned_async_stream.cu"
    "elysia_integrated_bench;${L0_DIR}/src/elysia_integrated_bench.cu"
    "elysia_unified_hologram_engine;${L0_DIR}/src/elysia_unified_hologram_engine.cu"
)

foreach(pair IN LISTS ELYSIA_CORE_CU_TARGETS)
    list(GET pair 0 tgt_name)
    list(GET pair 1 src_path)
    if(EXISTS "${src_path}")
        if(CMAKE_CUDA_COMPILER)
            add_executable(${tgt_name} ${src_path})
            target_include_directories(${tgt_name} PUBLIC ${L0_DIR}/include)
            target_compile_options(${tgt_name} PRIVATE
                $<$<COMPILE_LANGUAGE:CUDA>:-O3 --use_fast_math --expt-relaxed-constexpr -Xcompiler -O3,-Wall>
                $<$<COMPILE_LANGUAGE:CXX>:-O3 -Wall>
            )
        else()
            set_source_files_properties(${src_path} PROPERTIES LANGUAGE CXX COMPILE_FLAGS "-x c++ -include elysia/cuda_host_stub.h")
            add_executable(${tgt_name} ${src_path})
            target_include_directories(${tgt_name} PUBLIC ${L0_DIR}/include)
        endif()
        if(TARGET Eigen3::Eigen)
            target_link_libraries(${tgt_name} PRIVATE Eigen3::Eigen)
        endif()
    endif()
endforeach()

# Optional Direct3D12 Renderer Target (Windows only)
if(WIN32 AND BUILD_D3D12_RENDERER AND EXISTS "${L0_DIR}/src/elysia_d3d12_raymarcher.cpp")
    add_executable(ElysiaVolumeRaymarcher ${L0_DIR}/src/elysia_d3d12_raymarcher.cpp)
    target_link_libraries(ElysiaVolumeRaymarcher PRIVATE d3d12.lib dxgi.lib d3dcompiler.lib nexus_core)
endif()

# -----------------------------------------------------------------------------
# pybind11 Python Extension Module
# -----------------------------------------------------------------------------
find_package(pybind11 CONFIG QUIET)
if(NOT pybind11_FOUND)
    execute_process(
        COMMAND python3 -m pybind11 --cmake
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )
    if(pybind11_DIR)
        find_package(pybind11 CONFIG HINTS ${pybind11_DIR})
    endif()
endif()

if(pybind11_FOUND AND EXISTS "${L0_DIR}/src/bindings/python_bindings.cpp")
    pybind11_add_module(causal_engine_py ${L0_DIR}/src/bindings/python_bindings.cpp)
    target_include_directories(causal_engine_py PRIVATE ${L0_DIR}/include)
    target_link_libraries(causal_engine_py PRIVATE OpenMP::OpenMP_CXX)
    set_target_properties(causal_engine_py PROPERTIES OUTPUT_NAME "causal_engine")
endif()

# -----------------------------------------------------------------------------
# Verified C++ Test Suite (tests/cpp)
# -----------------------------------------------------------------------------
if(ELYSIA_BUILD_TESTS)
    enable_testing()

    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/test_nexus_betti.cpp")
        add_executable(test_nexus_betti tests/cpp/test_nexus_betti.cpp)
        target_link_libraries(test_nexus_betti PRIVATE nexus_core OpenMP::OpenMP_CXX)
        add_test(NAME test_nexus_betti COMMAND test_nexus_betti)
    endif()

    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/test_3dgs_sh_eval.cpp")
        add_executable(test_3dgs_sh_eval tests/cpp/test_3dgs_sh_eval.cpp)
        target_link_libraries(test_3dgs_sh_eval PRIVATE nexus_core OpenMP::OpenMP_CXX)
        add_test(NAME test_3dgs_sh_eval COMMAND test_3dgs_sh_eval)
    endif()

    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/test_simd_gpu_ecs.cpp")
        add_executable(test_simd_gpu_ecs tests/cpp/test_simd_gpu_ecs.cpp)
        target_link_libraries(test_simd_gpu_ecs PRIVATE simd_gpu_ecs)
        if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
            target_compile_options(test_simd_gpu_ecs PRIVATE -mavx2 -mfma)
        endif()
        add_test(NAME test_simd_gpu_ecs COMMAND test_simd_gpu_ecs)
    endif()

    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/test_topir_parser.cpp")
        add_executable(test_topir_parser tests/cpp/test_topir_parser.cpp)
        target_include_directories(test_topir_parser PRIVATE ${L0_DIR}/isa_compiler ${L0_DIR}/include)
        target_link_libraries(test_topir_parser PRIVATE nexus_core OpenMP::OpenMP_CXX)
        add_test(NAME test_topir_parser COMMAND test_topir_parser)
    endif()
endif()
