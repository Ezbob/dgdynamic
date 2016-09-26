import sympy as sp
import functools as ft
from mod import dgAbstract


class AbstractOdeSystem:

    def __init__(self, specification):
        self.graph = dgAbstract(specification) if type(specification) is str else specification
        self.symbols = {vertex.id: sp.Symbol(vertex.graph.name) for vertex in self.graph.vertices}

        self.reaction_count = sum(1 for _ in self.graph.edges)
        self.parameters = tuple(sp.Symbol("k{}".format(i + 1)) for i in range(self.reaction_count))
        self.left_hands = tuple()

        for index, edge in enumerate(self.graph.edges):
            # create a generator for the sympy Symbols in
            reduce_me = (self.symbols[vertex.id] for vertex in edge.sources)
            self.left_hands += (self.parameters[index] * ft.reduce(lambda a, b: a * b, reduce_me),)


def as_lists(hyper_edges):
    return [[[c.id for c in a.sources], [b.id for b in a.targets]] for a in hyperedges]
