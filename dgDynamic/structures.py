from dgDynamic.utils.project_utils import LogMixin


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
        self.edge_finder = graph.findEdge if hasattr(graph, "findEdge") else None

    def find_edge(self, vertices, edges):
        if self.edge_finder is not None:
            return self.edge_finder(vertices, edges)


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

