from dgDynamic.utils.project_utils import LogMixin
import mod


class HyperGraph(LogMixin):
    def __new__(cls, derivation_graph):
        if hasattr(derivation_graph, "findEdge") and hasattr(derivation_graph, "vertices") \
                and hasattr(derivation_graph, "edges"):
            return derivation_graph
        else:
            raise TypeError("Unsupported type for derivation graph. "
                            "Derivation graph must have attributes:"
                            "vertices, edges and findEdge")

    @staticmethod
    def from_flow_solution(solution):
        if isinstance(solution, mod.DGFlowSolution):
            original_graph = solution.dgFlow.dg
            sub_hypergraph_edges = (e for e in original_graph.edges if solution.eval(mod.edge(e)) != 0.0)
            new_graph = mod.dgDerivations([mod.DerivationRef(edge).derivation for edge in sub_hypergraph_edges])
            return HyperGraph(new_graph)

    @staticmethod
    def from_abstract(*abstract_reactions):
        if len(abstract_reactions) > 0:
            map(str.strip, abstract_reactions)
            whole_network = "\n".join(abstract_reactions)
            dg = mod.dgAbstract(whole_network)
            return HyperGraph(dg)
