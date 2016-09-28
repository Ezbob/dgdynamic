import functools as ft
from enum import Enum

import sympy as sp
from mod import dgAbstract


class AbstractOdeSystem:
    """
    This class is meant to create ODEs in SymPys abstract symbolic mathematical syntax, using deviation graphs
    from the MØD framework.
    """
    def __init__(self, specification):
        """
        The initialisation phase consist of creating Sympy Symbols for the vertices of the deviation graph,
        and creating the rate laws for each reaction.
        :param specification: if this is parsed as a string the init function will try and parse the string argument to
        dgAbstract, else it just gets stored.
        """
        self.graph = dgAbstract(specification) if type(specification) is str else specification

        # every vertex in the deviation graph gets a mapping from it's id to the corresponding SymPy Symbol
        self.symbols = {vertex.id: sp.Symbol(vertex.graph.name) for vertex in self.graph.vertices}
        # the best 'complicated' way of counting, this is needed because we can't take the length of the edges (yet?)
        self.reaction_count = sum(1 for _ in self.graph.edges)

        # the mass action law parameters. For mathematical reasons the symbol indices start at 1
        self.parameters = tuple(sp.Symbol("k{}".format(i + 1)) for i in range(self.reaction_count))
        self.left_hands = tuple()

        # Now we create the left hand equation according to the law of mass action
        for index, edge in enumerate(self.graph.edges):
            reduce_me = (self.symbols[vertex.id] for vertex in edge.sources)
            reduced = ft.reduce(lambda a, b: a * b, reduce_me)
            self.left_hands += (self.parameters[index] * reduced,)

    def generate_equations(self):
        """
        This function will attempt to create the symbolic ODEs using the rate laws.
        :return: a tuple of tuples, wherein each nested tuple is a two-tuple consisting of the vertex id, of which the
        change over time is subjective to, and the symbolic ODE.
        """
        results = tuple()
        for vertex in self.graph.vertices:
            subres = 0
            for edge_index, edge in enumerate(self.graph.edges):
                for source_vertex in edge.sources:
                    if vertex.id == source_vertex.id:
                        subres -= self.left_hands[edge_index]

                for target_vertex in edge.targets:
                    if vertex.id == target_vertex.id:
                        subres += self.left_hands[edge_index]
            results += ((vertex.id, subres),)
        return results

    def __repr__(self):
        return "<Abstract Ode System {}>".format(self.left_hands)
