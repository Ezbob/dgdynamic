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
    def __init__(self, educts, products, has_inverse=False):
        self.educts = tuple(educts) if not isinstance(educts, (tuple, list, set)) else educts
        self.products = tuple(products) if not isinstance(products, (tuple, list, set)) else products
        self.has_inverse = has_inverse

    def __str__(self):
        if self.has_inverse:
            return "{} <=> {}".format(" + ".join(self.educts), " + ".join(self.products))
        else:
            return "{} -> {}".format(" + ".join(self.educts), " + ".join(self.products))

    def __repr__(self):
        return self.__str__()

