from dgdynamic.utils.project_utils import LogMixin
from dgdynamic.base_converters.reaction_parser import hyper_edge_to_string
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

    @staticmethod
    def abstract(hyper_graph):
        yield from (hyper_edge_to_string(edge, add_newline=False) for edge in hyper_graph.edges)

    @staticmethod
    def union(hyper_graph_a, hyper_graph_b):
        new_abstract = tuple(HyperGraph.abstract(hyper_graph_a)) + tuple(HyperGraph.abstract(hyper_graph_b))
        print("\n".join(new_abstract))
        return mod.dgAbstract("\n".join(new_abstract))
