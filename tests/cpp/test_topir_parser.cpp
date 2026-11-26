#include "topir/eol_parser.hpp"

#include <cassert>
#include <cmath>
#include <iostream>

using namespace elysia::topir;

int main() {
    const std::string eol = R"(
        // Custom 4-stage pipeline with non-default constants
        vort = Diff::curl(V)
        sync = PhaseLock(K_0=24.5)(Q, neighbors(Q))
        comp = ScaleCompress(gamma=0.85)(sync)
        q_next = Q.integrate_langevin(vort, comp, dt=0.0025)
        phi = q_next.local_coherence()
        stress = BlendByOrder(phi, solid_th=0.8, gas_th=0.2)
    )";

    auto graph = EOLParser::parse_to_topir(eol);
    assert(graph.get_node_order().size() == 6);

    const auto* sync_node = graph.get_node("node_sync");
    assert(sync_node != nullptr);
    assert(sync_node->opcode == OperatorOpcode::PHASE_LOCK);
    assert(std::abs(sync_node->float_params.at("K_0") - 24.5f) < 1e-5f);

    const auto* comp_node = graph.get_node("node_comp");
    assert(comp_node != nullptr);
    assert(comp_node->opcode == OperatorOpcode::SCALE_COMPRESS);
    assert(std::abs(comp_node->float_params.at("gamma") - 0.85f) < 1e-5f);

    const auto* blend_node = graph.get_node("node_stress");
    assert(blend_node != nullptr);
    assert(blend_node->blend_order_param_id == "node_phi");
    assert(std::abs(blend_node->float_params.at("solid_th") - 0.8f) < 1e-5f);

    // Check data-flow edges were extracted dynamically (sync->comp, vort->q_next, comp->q_next, q_next->phi, phi->stress)
    assert(graph.get_edges().size() == 5);

    auto isa_insts = EOLParser::lower_topir_to_isa(graph);
    assert(isa_insts.size() == 3);
    assert(std::abs(isa_insts[0].immediate_param - 24.5f) < 1e-5f);

    std::cout << "[PASS] TopIR EOLParser dynamically parsed " << graph.get_node_order().size()
              << " nodes, " << graph.get_edges().size() << " edges, and lowered "
              << isa_insts.size() << " geometric ISA instructions.\n";
    return 0;
}
