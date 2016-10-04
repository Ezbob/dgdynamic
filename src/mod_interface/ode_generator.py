import functools as ft
from typing import Union
from ..utils.project_utils import ProjectTypeHints as Types, LogMixin
import sympy as sp
from collections import OrderedDict
import mod


class AbstractOdeSystem(LogMixin):
    """
    This class is meant to create ODEs in SymPys abstract symbolic mathematical syntax, using deviation graphs
    from the MØD framework.
    """
    def __init__(self, specification: Union[str, mod.dgAbstract]):
        """
        The initialisation phase consist of creating Sympy Symbols for the vertices of the deviation graph,
        and creating the rate laws for each reaction.
        :param specification: if this is parsed as a string the init function will try and parse the string argument to
        dgAbstract, else it just gets stored.
        """
        self.graph = mod.dgAbstract(specification)
        self.reaction_mapping = {reaction: index for index, reaction in enumerate(specification.strip().splitlines())}
        self._ignored = tuple()

        # every vertex in the deviation graph gets a mapping from it's id to the corresponding SymPy Symbol
        self.symbols = OrderedDict(((vertex.id, sp.Symbol(vertex.graph.name)) for vertex in self.graph.vertices))
        # the best 'complicated' way of counting, this is needed because we can't take the length of the edges (yet?)
        self.reaction_count = sum(1 for _ in self.graph.edges)
        self.species_count = self.graph.numVertices # e.g. species count
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
        for vertex_id, vertex in enumerate(self.graph.vertices):
            if sp.Symbol(vertex.graph.name) in (ignore_tuple[0] for ignore_tuple in self._ignored):
                results += ((vertex.graph.name, 0),)
            else:
                subres = 0
                for edge_index, edge in enumerate(self.graph.edges):
                    for source_vertex in edge.sources:
                        if vertex.id == source_vertex.id:
                            subres -= self.left_hands[edge_index]

                    for target_vertex in edge.targets:
                        if vertex.id == target_vertex.id:
                            subres += self.left_hands[edge_index]
                results += ((vertex.graph.name, subres),)
        return results

    def unchanging_species(self, *species: Union[str, sp.Symbol, Types.Countable_Sequence]):
        """
        Specify the list of species you don't want to see ODEs for
        :param species: list of strings symbol
        :return:
        """
        if len(self._ignored) < self.species_count:
            if type(species) is str:
                self._ignored = tuple((item, index) for index, item in enumerate(self.symbols.values())
                                      if sp.Symbol(species) == item)
            elif type(species) is sp.Symbol:
                self._ignored = tuple((item, index) for index, item in enumerate(self.symbols.values())
                                      if species == item)
            else:
                self._ignored = tuple((item, index) for index, item in enumerate(self.symbols.values())
                                      for element in species if sp.Symbol(element) == item)
        else:
            self.logger.warn("ignored species count exceeds the count of actual species")
        return self

    def __repr__(self):
        return "<Abstract Ode System {}>".format(self.left_hands)
