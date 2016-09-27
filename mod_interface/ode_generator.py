import sympy as sp
import functools as ft
from mod import dgAbstract
from plugins.ode_plugin import LogMixin


class AbstractOdeSystem:

    def __init__(self, specification):
        self.graph = dgAbstract(specification) if type(specification) is str else specification

        # every vertex in the deviation graph gets a mapping from it's id to the corresponding SymPy Symbol
        self.symbols = {vertex.id: sp.Symbol(vertex.graph.name) for vertex in self.graph.vertices}
        # the best 'complicated' way of counting, this is needed because we can't take the length of the edges (yet?)
        self.reaction_count = sum(1 for _ in self.graph.edges)

        # the mass action law parameters
        self.parameters = tuple(sp.Symbol("k{}".format(i + 1)) for i in range(self.reaction_count))
        self.left_hands = tuple()

        for index, edge in enumerate(self.graph.edges):
            # create a generator for the sympy Symbols in
            reduce_me = (self.symbols[vertex.id] for vertex in edge.sources)
            reduced = ft.reduce(lambda a, b: a * b, reduce_me)
            self.left_hands += (self.parameters[index] * reduced,)

    def generate_equations(self):
        results = tuple()
        for vertex in self.graph.vertices:
            print(vertex.graph.name)
            subres = 0
            for edge in self.graph.edges:
                for source_index, source_vertex in enumerate(edge.sources):
                    if vertex.id == source_vertex.id:
                        subres -= self.left_hands[source_index]

                for target_index, target_vertex in enumerate(edge.targets):
                    if vertex.id == target_vertex.id:
                        subres += self.left_hands[target_index]
            results += (subres,)
            print(results)
        return results


def as_lists(hyper_edges):
    return [[[c.id for c in a.sources], [b.id for b in a.targets]] for a in hyper_edges]
