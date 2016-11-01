import abc


class DynamicSimulator(abc.ABC):

    def __init__(self, graph):
        self.graph = graph
        self.ignored = tuple()
        self.reaction_count = sum(1 for _ in self.graph.edges)
        self.species_count = self.graph.numVertices