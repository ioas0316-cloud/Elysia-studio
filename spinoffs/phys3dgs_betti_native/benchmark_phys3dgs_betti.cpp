#include "causal_engine/3dgs_sh_eval.h"
#include "nexus_betti.h"

#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

using namespace elysia::gaussian3d;
using namespace CausalNexus;

int main() {
    std::cout << "=================================================================\n";
    std::cout << "  Elysia Spin-off #1 Benchmark: Phys3DGS Collision & Betti2D TDA\n";
    std::cout << "=================================================================\n";

    // 1. Phys3DGS 7-DOF Articulated Robot Capsule vs Anisotropic 3D Gaussians
    const int dof = 7;
    std::vector<float> jacA(3 * dof, 0.0f), jacB(3 * dof, 0.0f);
    for (int k = 0; k < dof; ++k) {
        jacA[0 * dof + k] = std::cos(0.3f * (k + 1));
        jacA[1 * dof + k] = std::sin(0.3f * (k + 1));
        jacB[0 * dof + k] = std::cos(0.5f * (k + 1));
        jacB[1 * dof + k] = std::sin(0.5f * (k + 1));
        jacB[2 * dof + k] = 0.25f;
    }
    CapsuleLink link{Float3(0.0f, 0.0f, 0.0f), Float3(0.8f, 0.6f, 0.4f), dof, jacA.data(), jacB.data()};

    for (int P : {10000, 100000}) {
        std::vector<Float3> means(P);
        std::vector<float> inv_cov(P * 6);
        std::vector<float> opacity(P);
        for (int i = 0; i < P; ++i) {
            float a = static_cast<float>(i % 360) * 0.01745f;
            means[i] = Float3(0.4f + 0.5f * std::cos(a), 0.3f + 0.5f * std::sin(a), 0.2f + 0.001f * (i % 200));
            inv_cov[i * 6 + 0] = 4.0f; inv_cov[i * 6 + 1] = 0.2f; inv_cov[i * 6 + 2] = 0.0f;
            inv_cov[i * 6 + 3] = 3.5f; inv_cov[i * 6 + 4] = 0.1f; inv_cov[i * 6 + 5] = 5.0f;
            opacity[i] = 0.85f;
        }
        std::vector<float> dC_dq(dof, 0.0f);

        // Warmup
        computePhys3DGSCollisionGradient(P, means.data(), inv_cov.data(), opacity.data(), link, dC_dq.data());

        const int runs = 10;
        auto t0 = std::chrono::high_resolution_clock::now();
        for (int r = 0; r < runs; ++r) {
            computePhys3DGSCollisionGradient(P, means.data(), inv_cov.data(), opacity.data(), link, dC_dq.data());
        }
        auto t1 = std::chrono::high_resolution_clock::now();
        double avg_ms = std::chrono::duration<double, std::milli>(t1 - t0).count() / runs;
        double m_per_sec = (P / (avg_ms / 1000.0)) / 1e6;

        std::cout << std::fixed << std::setprecision(3)
                  << "[Phys3DGS] P=" << std::setw(6) << P << " Gaussians (7-DOF) | "
                  << std::setw(6) << avg_ms << " ms/step | "
                  << std::setw(6) << m_per_sec << " M Gaussians/s | ||dC/dq||="
                  << std::sqrt(dC_dq[0]*dC_dq[0] + dC_dq[1]*dC_dq[1]) << "\n";
    }

    // 2. 2D Betti Number Topological Extraction Throughput
    for (int side : {256, 512, 1024}) {
        std::vector<uint8_t> grid(side * side, 0);
        const int blocks = 8;
        const int tile = side / blocks;
        for (int br = 0; br < blocks; ++br) {
            for (int bc = 0; bc < blocks; ++bc) {
                int r0 = br * tile + 4, r1 = (br + 1) * tile - 5;
                int c0 = bc * tile + 4, c1 = (bc + 1) * tile - 5;
                for (int r = r0; r <= r1; ++r) {
                    for (int c = c0; c <= c1; ++c) {
                        if (r == r0 || r == r1 || c == c0 || c == c1) {
                            grid[r * side + c] = 1;
                        }
                    }
                }
            }
        }
        auto t0 = std::chrono::high_resolution_clock::now();
        auto b = CalculateBetti2D(grid, side, side);
        auto t1 = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
        double mpix_s = (side * side / 1e6) / (ms / 1000.0);
        std::cout << "[Betti2D ] " << std::setw(4) << side << "x" << std::setw(4) << side
                  << " | beta_0=" << b.betti_0 << ", beta_1=" << b.betti_1
                  << " | " << std::setw(6) << ms << " ms | " << std::setw(6) << mpix_s << " MPix/s\n";
    }

    return 0;
}
