#ifndef EOL_PARSER_HPP
#define EOL_PARSER_HPP

#include "topir_graph.hpp"
#include "../geometric_isa.hpp"
#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <iostream>
#include <regex>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

namespace elysia::topir {

/// Elysia Operator Language (EOL) Real Lexer & Graph Parser
class EOLParser {
public:
    EOLParser() = default;

    static TopologicalGraphIR parse_to_topir(const std::string& eol_source) {
        TopologicalGraphIR graph;
        std::unordered_map<std::string, std::string> var_to_node;
        int edge_counter = 0;
        int node_counter = 0;

        auto trim = [](std::string s) {
            auto not_space = [](unsigned char c) { return !std::isspace(c); };
            s.erase(s.begin(), std::find_if(s.begin(), s.end(), not_space));
            s.erase(std::find_if(s.rbegin(), s.rend(), not_space).base(), s.end());
            return s;
        };

        auto parse_float_param = [](const std::string& expr, const std::string& key, float default_val) -> float {
            std::regex re(key + R"(\s*=\s*([-+]?[0-9]*\.?[0-9]+))");
            std::smatch m;
            if (std::regex_search(expr, m, re)) {
                return std::stof(m[1].str());
            }
            return default_val;
        };

        std::istringstream iss(eol_source);
        std::string raw_line;
        while (std::getline(iss, raw_line)) {
            // Strip comments
            auto comment_pos = raw_line.find("//");
            if (comment_pos != std::string::npos) {
                raw_line = raw_line.substr(0, comment_pos);
            }
            std::string line = trim(raw_line);
            if (line.empty() || line[0] == '#') continue;
            if (!line.empty() && line.back() == ';') line.pop_back();
            line = trim(line);
            if (line.empty()) continue;

            // Optional assignment: lhs = rhs
            std::string lhs;
            std::string rhs = line;
            auto eq_pos = line.find('=');
            // Ignore '=' inside parentheses like PhaseLock(K_0=10.0)
            auto paren_pos = line.find('(');
            if (eq_pos != std::string::npos && (paren_pos == std::string::npos || eq_pos < paren_pos)) {
                lhs = trim(line.substr(0, eq_pos));
                rhs = trim(line.substr(eq_pos + 1));
            }

            TopIRNode node{};
            node.op_name = rhs;
            node.node_id = lhs.empty() ? ("node_" + std::to_string(node_counter)) : ("node_" + lhs);
            node_counter++;

            if (rhs.find("Diff::curl") != std::string::npos) {
                node.opcode = OperatorOpcode::DIFF_CURL;
                node.output_type = TopIRType{TypeKind::VectorField3D, 1, 3};
            } else if (rhs.find("Diff::div") != std::string::npos) {
                node.opcode = OperatorOpcode::DIFF_DIV;
                node.output_type = TopIRType{TypeKind::ScalarField, 0, 1};
            } else if (rhs.find("Diff::grad") != std::string::npos) {
                node.opcode = OperatorOpcode::DIFF_GRAD;
                node.output_type = TopIRType{TypeKind::VectorField3D, 1, 3};
            } else if (rhs.find("PhaseLock") != std::string::npos) {
                node.opcode = OperatorOpcode::PHASE_LOCK;
                node.output_type = TopIRType{TypeKind::VectorField3D, 1, 3};
                node.float_params["K_0"] = parse_float_param(rhs, "K_0", 10.0f);
            } else if (rhs.find("ScaleCompress") != std::string::npos) {
                node.opcode = OperatorOpcode::SCALE_COMPRESS;
                node.output_type = TopIRType{TypeKind::VectorField3D, 1, 3};
                node.float_params["gamma"] = parse_float_param(rhs, "gamma", 0.5f);
            } else if (rhs.find("Noise::rotational_brownian") != std::string::npos) {
                node.opcode = OperatorOpcode::NOISE_ROTATIONAL;
                node.output_type = TopIRType{TypeKind::VectorField3D, 1, 3};
                node.float_params["Temp"] = parse_float_param(rhs, "Temp", 0.1f);
            } else if (rhs.find("integrate_langevin") != std::string::npos) {
                node.opcode = OperatorOpcode::LANGEVIN_INTEGRATE;
                node.output_type = TopIRType{TypeKind::S3Field, 0, 4};
                node.float_params["dt"] = parse_float_param(rhs, "dt", 0.005f);
            } else if (rhs.find("local_coherence") != std::string::npos) {
                node.opcode = OperatorOpcode::LOCAL_COHERENCE;
                node.output_type = TopIRType{TypeKind::OrderField, 0, 1};
            } else if (rhs.find("BlendByOrder") != std::string::npos) {
                node.opcode = OperatorOpcode::BLEND_BY_ORDER;
                node.output_type = TopIRType{TypeKind::TensorField, 2, 3};
                node.is_blended_branch = true;
                node.blended_branches = {"Solid", "Liquid", "Gas"};
                node.float_params["solid_th"] = parse_float_param(rhs, "solid_th", 0.7f);
                node.float_params["gas_th"] = parse_float_param(rhs, "gas_th", 0.3f);
            } else {
                node.opcode = OperatorOpcode::CUSTOM_OPERATOR;
                node.output_type = TopIRType{TypeKind::ScalarField, 0, 1};
            }

            // Connect edges from previously defined variables referenced in rhs
            for (const auto& kv : var_to_node) {
                const std::string& var_name = kv.first;
                const std::string& src_node_id = kv.second;
                std::regex var_re("\\b" + var_name + "\\b");
                if (std::regex_search(rhs, var_re)) {
                    const auto* src_node = graph.get_node(src_node_id);
                    TopIRType edge_type = src_node ? src_node->output_type : TopIRType{TypeKind::VectorField3D, 1, 3};
                    FiberBundleEdge edge{
                        "edge_" + std::to_string(edge_counter++),
                        edge_type,
                        src_node_id,
                        node.node_id,
                        0,
                        static_cast<int>(node.input_edge_ids.size()),
                        true,
                        true
                    };
                    if (node.opcode == OperatorOpcode::BLEND_BY_ORDER && edge_type.kind == TypeKind::OrderField) {
                        node.blend_order_param_id = src_node_id;
                    }
                    node.input_edge_ids.push_back(edge.edge_id);
                    graph.add_edge(edge);
                }
            }

            graph.add_node(node);
            if (!lhs.empty()) {
                var_to_node[lhs] = node.node_id;
            }
        }

        // If input source was empty, emit minimal canonical default pipeline
        if (graph.get_node_order().empty()) {
            return parse_to_topir(
                "vorticity = Diff::curl(V)\n"
                "sync_torque = PhaseLock(K_0=10.0)(Q, neighbors(Q))\n"
                "thermal_noise = Noise::rotational_brownian(Temp=0.1)\n"
                "q_update = Q.integrate_langevin(vorticity, sync_torque, thermal_noise, dt=0.005)\n"
                "phi = q_update.local_coherence()\n"
                "blend_stress = BlendByOrder(phi, solid_th=0.7, gas_th=0.3)\n"
            );
        }

        return graph;
    }

    /// Map TopIR nodes to geometric ISA instructions in `isa_compiler/geometric_isa.hpp`
    static std::vector<isa::Instruction> lower_topir_to_isa(const TopologicalGraphIR& graph) {
        std::vector<isa::Instruction> instructions;
        uint32_t addr = 0x1000;

        for (const auto& node_id : graph.get_node_order()) {
            const auto* node = graph.get_node(node_id);
            if (!node) continue;

            if (node->opcode == OperatorOpcode::PHASE_LOCK) {
                isa::Instruction inst{};
                inst.opcode = isa::Opcode::PLOCK;
                inst.dst_reg = 1;
                inst.memory_address = addr;
                inst.immediate_param = node->float_params.count("K_0") ? node->float_params.at("K_0") : 10.0f;
                instructions.push_back(inst);
                addr += 0x400;
            } else if (node->opcode == OperatorOpcode::LANGEVIN_INTEGRATE) {
                isa::Instruction inst{};
                inst.opcode = isa::Opcode::ROTOR_PIN;
                inst.src_reg = 1;
                inst.memory_address = addr;
                inst.immediate_param = node->float_params.count("dt") ? node->float_params.at("dt") : 0.005f;
                instructions.push_back(inst);
                addr += 0x400;
            } else if (node->opcode == OperatorOpcode::BLEND_BY_ORDER) {
                isa::Instruction inst{};
                inst.opcode = isa::Opcode::METRIC_MOD;
                inst.dst_reg = 2;
                inst.memory_address = addr;
                inst.immediate_param = node->float_params.count("solid_th") ? node->float_params.at("solid_th") : 0.7f;
                instructions.push_back(inst);
                addr += 0x400;
            }
        }

        return instructions;
    }
};

} // namespace elysia::topir

#endif // EOL_PARSER_HPP
