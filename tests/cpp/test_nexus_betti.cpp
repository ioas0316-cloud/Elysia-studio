#include "nexus_betti.h"

#include <cassert>
#include <chrono>
#include <cmath>
#include <iostream>
#include <vector>

using namespace CausalNexus;

static void test_empty_and_single() {
    auto b_empty = CalculateBetti2D({}, 0, 0);
    assert(b_empty.betti_0 == 0 && b_empty.betti_1 == 0);

    std::vector<uint8_t> single(9, 0);
    single[4] = 1;
    auto b_single = CalculateBetti2D(single, 3, 3);
    assert(b_single.betti_0 == 1 && b_single.betti_1 == 0);
}

static void test_two_disjoint_squares() {
    // 5x5 grid with two separated 2x2 filled squares -> beta_0 = 2, beta_1 = 0
    int H = 5, W = 5;
    std::vector<uint8_t> grid(H * W, 0);
    for (int r = 0; r < 2; ++r)
        for (int c = 0; c < 2; ++c)
            grid[r * W + c] = 1;
    for (int r = 3; r < 5; ++r)
        for (int c = 3; c < 5; ++c)
            grid[r * W + c] = 1;

    auto b = CalculateBetti2D(grid, H, W);
    assert(b.betti_0 == 2);
    assert(b.betti_1 == 0);
}

static void test_hollow_ring_single_hole() {
    // 5x5 border ring -> 1 connected component, 1 hole (beta_0 = 1, beta_1 = 1)
    int H = 5, W = 5;
    std::vector<uint8_t> grid(H * W, 0);
    for (int r = 0; r < H; ++r) {
        for (int c = 0; c < W; ++c) {
            if (r == 0 || r == H - 1 || c == 0 || c == W - 1) {
                grid[r * W + c] = 1;
            }
        }
    }
    auto b = CalculateBetti2D(grid, H, W);
    assert(b.betti_0 == 1);
    assert(b.betti_1 == 1);
}

static void test_figure_eight_two_holes() {
    // 5x9 grid with two adjacent hollow boxes sharing a middle wall -> beta_0 = 1, beta_1 = 2
    int H = 5, W = 9;
    std::vector<uint8_t> grid(H * W, 0);
    for (int r = 0; r < H; ++r) {
        for (int c = 0; c < W; ++c) {
            if (r == 0 || r == H - 1 || c == 0 || c == 4 || c == W - 1) {
                grid[r * W + c] = 1;
            }
        }
    }
    auto b = CalculateBetti2D(grid, H, W);
    assert(b.betti_0 == 1);
    assert(b.betti_1 == 2);
}

static void benchmark_large_grid() {
    // 512x512 grid with 4x4 = 16 disjoint hollow rings -> beta_0 = 16, beta_1 = 16
    const int H = 512, W = 512;
    std::vector<uint8_t> grid(H * W, 0);
    const int tile = 128;
    for (int br = 0; br < 4; ++br) {
        for (int bc = 0; bc < 4; ++bc) {
            int r0 = br * tile + 16, r1 = br * tile + 112;
            int c0 = bc * tile + 16, c1 = bc * tile + 112;
            for (int r = r0; r <= r1; ++r) {
                for (int c = c0; c <= c1; ++c) {
                    if (r == r0 || r == r1 || c == c0 || c == c1) {
                        grid[r * W + c] = 1;
                    }
                }
            }
        }
    }

    auto t0 = std::chrono::high_resolution_clock::now();
    auto b = CalculateBetti2D(grid, H, W);
    auto t1 = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    assert(b.betti_0 == 16);
    assert(b.betti_1 == 16);
    std::cout << "[PASS] 512x512 Betti2D: beta_0=" << b.betti_0
              << ", beta_1=" << b.betti_1 << " (" << ms << " ms)\n";
}

int main() {
    test_empty_and_single();
    test_two_disjoint_squares();
    test_hollow_ring_single_hole();
    test_figure_eight_two_holes();
    benchmark_large_grid();
    std::cout << "ALL test_nexus_betti CHECKS PASSED.\n";
    return 0;
}
