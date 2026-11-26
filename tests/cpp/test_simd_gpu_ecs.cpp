#include "causal_engine/simd_gpu_ecs/simd_torque_transmission_system.hpp"

#include <cassert>
#include <chrono>
#include <cmath>
#include <iostream>
#include <vector>

int main() {
    // Non-multiple of 8 to exercise BOTH AVX2 8-wide path AND scalar tail path
    const size_t N = 100003;
    const float dt = 0.016f;

    FFixedGearComponentBuffer fixed_buf;
    FVariableGearComponentBuffer var_buf;
    FFlywheelComponentBuffer fly_buf;

    fixed_buf.Resize(N);
    var_buf.Resize(N);
    fly_buf.Resize(N);

    // Reference scalar arrays
    std::vector<float> ref_cur(N), ref_omega(N), ref_out(N);

    for (size_t i = 0; i < N; ++i) {
        float fi = static_cast<float>(i % 97) * 0.03f;
        fixed_buf.FixedRatio[i] = 1.0f + fi;
        fixed_buf.SystemInertia[i] = 2.0f + 0.5f * fi;

        var_buf.CurrentRatio[i] = 0.5f + 0.1f * (i % 11);
        var_buf.TargetRatio[i] = (i % 5 == 0) ? 0.0f : 2.5f;
        var_buf.ShiftSpeed[i] = 3.0f;
        var_buf.Friction[i] = (i % 5 == 0) ? 100.0f : 0.2f; // Trigger clamping to 0 on i%5==0

        fly_buf.AngularVelocity[i] = 10.0f + fi;
        fly_buf.DampingFactor[i] = 0.15f;
        fly_buf.InputTorque[i] = 5.0f + 0.2f * fi;
        fly_buf.BrakingTorque[i] = (i % 7 == 0) ? 5000.0f : 1.0f; // Trigger omega clamp to 0

        // Compute scalar reference
        float dR = var_buf.ShiftSpeed[i] * (var_buf.TargetRatio[i] - var_buf.CurrentRatio[i])
                 - var_buf.Friction[i] * var_buf.CurrentRatio[i];
        ref_cur[i] = std::max(0.0f, var_buf.CurrentRatio[i] + dR * dt);

        float out_t = fly_buf.InputTorque[i] * fixed_buf.FixedRatio[i] * ref_cur[i];
        ref_out[i] = out_t;
        float net_t = out_t - fly_buf.BrakingTorque[i] - fly_buf.DampingFactor[i] * fly_buf.AngularVelocity[i];
        float tot_i = fixed_buf.SystemInertia[i] * fixed_buf.FixedRatio[i];
        ref_omega[i] = std::max(0.0f, fly_buf.AngularVelocity[i] + (net_t / tot_i) * dt);
    }

    auto t0 = std::chrono::high_resolution_clock::now();
    FSIMDTorqueTransmissionSystem::BatchStepTransmission(var_buf, dt, N);
    FSIMDTorqueTransmissionSystem::BatchIntegrateTorque(fixed_buf, var_buf, fly_buf, dt, N);
    auto t1 = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    float max_err_cur = 0.0f, max_err_omega = 0.0f, max_err_out = 0.0f;
    for (size_t i = 0; i < N; ++i) {
        max_err_cur = std::max(max_err_cur, std::abs(var_buf.CurrentRatio[i] - ref_cur[i]));
        max_err_omega = std::max(max_err_omega, std::abs(fly_buf.AngularVelocity[i] - ref_omega[i]));
        max_err_out = std::max(max_err_out, std::abs(fly_buf.DerivedOutput[i] - ref_out[i]));
        assert(fly_buf.BrakingTorque[i] == 0.0f); // Impulse reset verified
        assert(var_buf.CurrentRatio[i] >= 0.0f);
        assert(fly_buf.AngularVelocity[i] >= 0.0f);
    }

    assert(max_err_cur < 1e-4f);
    assert(max_err_omega < 1e-4f);
    assert(max_err_out < 1e-4f);

    std::cout << "[PASS] AVX2 SIMD Torque ECS (" << N << " entities in " << ms << " ms): "
              << "max_err_cur=" << max_err_cur << ", max_err_omega=" << max_err_omega << "\n";
    std::cout << "ALL test_simd_gpu_ecs CHECKS PASSED.\n";
    return 0;
}
