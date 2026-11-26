#include "causal_engine/3dgs_sh_eval.h"

#include <cassert>
#include <chrono>
#include <cmath>
#include <iostream>
#include <vector>

using namespace elysia::gaussian3d;

static float eval_collision_energy(
    int P,
    const std::vector<Float3>& means,
    const std::vector<float>& inv_cov,
    const std::vector<float>& opacity,
    Float3 pA,
    Float3 pB
) {
    Float3 ab(pB.x - pA.x, pB.y - pA.y, pB.z - pA.z);
    float total = 0.0f;
    for (int i = 0; i < P; ++i) {
        Float3 mu = means[i];
        const float* ic = inv_cov.data() + i * 6;
        Float3 ic_ab(
            ic[0] * ab.x + ic[1] * ab.y + ic[2] * ab.z,
            ic[1] * ab.x + ic[3] * ab.y + ic[4] * ab.z,
            ic[2] * ab.x + ic[4] * ab.y + ic[5] * ab.z
        );
        float denom = ab.x * ic_ab.x + ab.y * ic_ab.y + ab.z * ic_ab.z;
        float t = 0.5f;
        if (denom > 1e-8f) {
            Float3 a_mu(mu.x - pA.x, mu.y - pA.y, mu.z - pA.z);
            t = std::max(0.0f, std::min(1.0f, (a_mu.x * ic_ab.x + a_mu.y * ic_ab.y + a_mu.z * ic_ab.z) / denom));
        }
        Float3 x_star(pA.x + t * ab.x, pA.y + t * ab.y, pA.z + t * ab.z);
        Float3 diff(x_star.x - mu.x, x_star.y - mu.y, x_star.z - mu.z);
        float m_sq =
            diff.x * (ic[0] * diff.x + ic[1] * diff.y + ic[2] * diff.z) +
            diff.y * (ic[1] * diff.x + ic[3] * diff.y + ic[4] * diff.z) +
            diff.z * (ic[2] * diff.x + ic[4] * diff.y + ic[5] * diff.z);
        total += opacity[i] * std::exp(-0.5f * m_sq);
    }
    return total;
}

static void test_sh_forward_and_backward_gradcheck() {
    const int P = 1;
    const int deg = 3;
    const int max_coeffs = 16;

    std::vector<Float3> means = {Float3(1.3f, -0.7f, 2.1f)};
    Float3 cam(0.2f, 0.4f, -0.5f);

    std::vector<float> shs(P * max_coeffs * 3, 0.0f);
    for (size_t i = 0; i < shs.size(); ++i) {
        shs[i] = 0.15f * std::sin(static_cast<float>(i + 1) * 0.73f);
    }
    shs[0] = 0.8f; shs[1] = 0.6f; shs[2] = 0.7f; // Ensure positive clamped RGB

    std::vector<Float3> rgb(P);
    computeColorFromSH(P, deg, max_coeffs, means.data(), cam, shs.data(), rgb.data());
    assert(rgb[0].x > 0.0f && rgb[0].y > 0.0f && rgb[0].z > 0.0f);

    std::vector<Float3> dL_drgb = {Float3(0.7f, -0.4f, 1.2f)};
    std::vector<float> dL_dsh(shs.size(), 0.0f);
    std::vector<Float3> dL_dmeans(P);

    computeColorFromSHBackward(
        P, deg, max_coeffs, means.data(), cam, shs.data(),
        rgb.data(), dL_drgb.data(), dL_dsh.data(), dL_dmeans.data()
    );

    auto loss_fn = [&](const std::vector<Float3>& m, const std::vector<float>& s) -> float {
        std::vector<Float3> out(P);
        computeColorFromSH(P, deg, max_coeffs, m.data(), cam, s.data(), out.data());
        return dL_drgb[0].x * out[0].x + dL_drgb[0].y * out[0].y + dL_drgb[0].z * out[0].z;
    };

    const float eps = 1e-3f;
    float max_sh_err = 0.0f;
    for (size_t i = 0; i < shs.size(); ++i) {
        auto s_plus = shs, s_minus = shs;
        s_plus[i] += eps;
        s_minus[i] -= eps;
        float num_grad = (loss_fn(means, s_plus) - loss_fn(means, s_minus)) / (2.0f * eps);
        max_sh_err = std::max(max_sh_err, std::abs(num_grad - dL_dsh[i]));
    }

    float max_mean_err = 0.0f;
    for (int axis = 0; axis < 3; ++axis) {
        auto m_plus = means, m_minus = means;
        if (axis == 0) { m_plus[0].x += eps; m_minus[0].x -= eps; }
        if (axis == 1) { m_plus[0].y += eps; m_minus[0].y -= eps; }
        if (axis == 2) { m_plus[0].z += eps; m_minus[0].z -= eps; }
        float num_grad = (loss_fn(m_plus, shs) - loss_fn(m_minus, shs)) / (2.0f * eps);
        float ana_grad = (axis == 0) ? dL_dmeans[0].x : (axis == 1 ? dL_dmeans[0].y : dL_dmeans[0].z);
        max_mean_err = std::max(max_mean_err, std::abs(num_grad - ana_grad));
    }

    assert(max_sh_err < 1e-3f);
    assert(max_mean_err < 1e-3f);
    std::cout << "[PASS] 3DGS SH Deg-3 GradCheck: max_sh_err=" << max_sh_err
              << ", max_means3D_err=" << max_mean_err << "\n";
}

static void test_phys3dgs_collision_gradient() {
    // 2-DOF planar articulated arm: pA = (cos q0, sin q0, 0), pB = pA + (cos(q0+q1), sin(q0+q1), 0)
    const float q0 = 0.4f, q1 = 0.6f;
    auto fk = [](float a, float b, Float3& pA, Float3& pB) {
        pA = Float3(std::cos(a), std::sin(a), 0.1f);
        pB = Float3(pA.x + std::cos(a + b), pA.y + std::sin(a + b), 0.3f);
    };

    Float3 pA, pB;
    fk(q0, q1, pA, pB);

    // Analytical Jacobians (3 x 2 row-major)
    float jacA[6] = {
        -std::sin(q0), 0.0f,
         std::cos(q0), 0.0f,
         0.0f,         0.0f
    };
    float jacB[6] = {
        -std::sin(q0) - std::sin(q0 + q1), -std::sin(q0 + q1),
         std::cos(q0) + std::cos(q0 + q1),  std::cos(q0 + q1),
         0.0f,                              0.0f
    };

    const int P = 3;
    std::vector<Float3> means = {
        Float3(1.1f, 0.8f, 0.2f),
        Float3(1.4f, 1.1f, 0.25f),
        Float3(0.6f, 0.5f, 0.15f)
    };
    // Symmetric positive definite inverse covariances (xx, xy, xz, yy, yz, zz)
    std::vector<float> inv_cov = {
        2.0f, 0.2f, 0.0f, 1.5f, 0.1f, 2.5f,
        1.8f, -0.1f, 0.05f, 2.2f, 0.0f, 1.9f,
        3.0f, 0.0f, 0.0f, 3.0f, 0.0f, 3.0f
    };
    std::vector<float> opacity = {0.9f, 0.7f, 0.85f};

    CapsuleLink link{pA, pB, 2, jacA, jacB};
    float dC_dq[2] = {0.0f, 0.0f};
    computePhys3DGSCollisionGradient(P, means.data(), inv_cov.data(), opacity.data(), link, dC_dq);

    const float eps = 1e-4f;
    float num_grad[2] = {0.0f, 0.0f};
    for (int k = 0; k < 2; ++k) {
        Float3 pA_p, pB_p, pA_m, pB_m;
        fk(q0 + (k == 0 ? eps : 0.0f), q1 + (k == 1 ? eps : 0.0f), pA_p, pB_p);
        fk(q0 - (k == 0 ? eps : 0.0f), q1 - (k == 1 ? eps : 0.0f), pA_m, pB_m);
        float e_p = eval_collision_energy(P, means, inv_cov, opacity, pA_p, pB_p);
        float e_m = eval_collision_energy(P, means, inv_cov, opacity, pA_m, pB_m);
        num_grad[k] = (e_p - e_m) / (2.0f * eps);
    }

    float max_err = std::max(std::abs(num_grad[0] - dC_dq[0]), std::abs(num_grad[1] - dC_dq[1]));
    assert(max_err < 1e-3f);
    std::cout << "[PASS] Phys3DGS Capsule Collision GradCheck: dC/dq=(" << dC_dq[0] << ", " << dC_dq[1]
              << "), max_err=" << max_err << "\n";
}

int main() {
    test_sh_forward_and_backward_gradcheck();
    test_phys3dgs_collision_gradient();
    std::cout << "ALL test_3dgs_sh_eval CHECKS PASSED.\n";
    return 0;
}
