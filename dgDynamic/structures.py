from dgDynamic.utils.project_utils import LogMixin
from dgDynamic.converters.reaction_parser import abstract_reaction_parser
import mod


class HyperGraph(LogMixin):
    def __init__(self, graph):
        if isinstance(graph, (tuple, list, set)):
            self.vertices, self.edges = graph[0], graph[1]
        elif isinstance(graph, dict):
            self.vertices, self.edges = graph['vertices'], graph['edges']
        elif hasattr(graph, "vertices") and hasattr(graph, "edges"):
            self.vertices, self.edges = graph.vertices, graph.edges
        else:
            raise TypeError('Object "{}" does not have any vertices or edges'.format(graph))

    @staticmethod
    def from_flow_solution(solution):
        if isinstance(solution, mod.DGFlowSolution):
            original_graph = solution.dgFlow.dg
            return HyperGraph({'vertices': tuple(v for v in original_graph.vertices
                                                 if solution.eval(mod.vertex(v.graph)) != 0.0),
                               'edges': tuple(e for e in original_graph.edges
                                              if solution.eval(mod.edge(e)) != 0.0)})


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
    def __init__(self, mod_dg, reaction):
        parsed_results = abstract_reaction_parser(mod_dg, reaction)
        super().__init__(None, None, parsed_results.mod_edges,
                         parsed_results.has_inverse, parsed_results.representation)