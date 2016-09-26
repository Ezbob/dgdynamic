import sympy as sp
import functools as ft


class AbstractOdeSystem:

    def __init__(self, deviation_graph):
        self.graph = deviation_graph
        self.symbols = {vertex.id: sp.Symbol(vertex.graph.name) for vertex in deviation_graph.vertices}

        self.reaction_count = sum(1 for _ in self.graph.edges)
        self.parameters = (sp.Symbol("k{}".format(i)) for i in range(self.reaction_count))
        self.left_hands = tuple()

        for edge in self.graph.edges:
            # create a generator for the sympy Symbols in
            reduceMe = (self.symbols[vertex.id] for vertex in edge.sources)
            self.left_hands += (ft.reduce(lambda a, b: a * b, reduceMe),)


def as_lists(hyperedges):
    return [[[c.id for c in a.sources], [b.id for b in a.targets]] for a in hyperedges]
