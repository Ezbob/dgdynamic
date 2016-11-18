from dgDynamic.utils.project_utils import LogMixin
from dgDynamic.converters.reaction_parser import abstract_mod_parser, abstract_parser
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


class HyperEdge:
    def __init__(self, targets=None, sources=None, mod_edges=None, has_inverse=False, representation=None):
        self.mod_edges = mod_edges
        self.targets = targets
        self.sources = sources
        self.has_inverse = has_inverse
        self.representation = representation

    @property
    def has_mod_edges(self):
        return self.mod_edges is not None

    @property
    def has_vertex_sets(self):
        return self.sources is not None and self.sources is not None

    @property
    def is_empty(self):
        return self.mod_edges is None and self.sources is None and self.targets is None

    def __str__(self):
        if self.representation is not None:
            return self.representation
        else:
            if self.has_inverse:
                return "<HyperEdge ({}) <=> ({})>".format(", ".join(self.sources), ", ".join(self.targets))
            else:
                return "<HyperEdge ({}) -> ({})>".format(", ".join(self.sources), ", ".join(self.targets))

    def __iter__(self):
        if self.sources is not None and self.targets is not None:
            yield from zip(self.sources, self.targets)
        elif self.mod_edges is not None:
            yield from self.mod_edges
        else:
            raise StopIteration

    def __repr__(self):
        return self.__str__()


class AbstractReaction(HyperEdge):
    def __init__(self, reaction):
        parsed_results = abstract_parser(reaction)
        super().__init__(targets=parsed_results.targets, sources=parsed_results.sources, mod_edges=None,
                         has_inverse=parsed_results.has_inverse, representation=parsed_results.representation)


class AbstractModReaction(HyperEdge):
    def __init__(self, mod_dg, reaction):
        parsed_results = abstract_mod_parser(mod_dg, reaction)
        super().__init__(None, None, parsed_results.mod_edges,
                         parsed_results.has_inverse, parsed_results.representation)