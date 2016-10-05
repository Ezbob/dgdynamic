import functools as ft
from ..utils.project_utils import ProjectTypeHints as Types, LogMixin
import sympy as sp
from typing import Union, Iterable, Tuple
from collections import OrderedDict
import mod


class dgODESystem(LogMixin):
    """
    This class is meant to create ODEs in SymPys abstract symbolic mathematical syntax, using deviation graphs
    from the MØD framework.
    """
    def __init__(self, graph):
        """
        The initialisation phase consist of creating Sympy Symbols for the vertices of the deviation graph,
        and creating the rate laws for each reaction.
        :param graph: if this is parsed as a string the init function will try and parse the string argument to
        dgAbstract, else it just gets stored.
        """

        self.graph = graph
        self.ignored = tuple()

        # every vertex in the deviation graph gets a mapping from it's id to the corresponding SymPy Symbol
        self.symbols = OrderedDict(((vertex.id, sp.Symbol(vertex.graph.name)) for vertex in self.graph.vertices))

        # the best 'complicated' way of counting, this is needed because we can't take the length of the edges (yet?)
        self.reaction_count = sum(1 for _ in self.graph.edges)

        self.species_count = self.graph.numVertices # e.g. species count

        # the mass action law parameters. For mathematical reasons the symbol indices start at 1
        self.parameters = OrderedDict((edge.id, sp.Symbol("k{}".format(index + 1)))
                                      for index, edge in enumerate(self.graph.edges))

    def generate_rate_laws(self):
        for index, edge in enumerate(self.graph.edges):
            reduce_me = (self.symbols[vertex.id] for vertex in edge.sources)
            reduced = ft.reduce(lambda a, b: a * b, reduce_me)
            yield self.parameters[edge.id] * reduced

    def generate_equations(self):
        """
        This function will attempt to create the symbolic ODEs using the rate laws.
        :return: a tuple of tuples, wherein each nested tuple is a two-tuple consisting of the vertex id, of which the
        change over time is subjective to, and the symbolic ODE.
        """
        left_hand_sides = tuple(self.generate_rate_laws())
        ignore_dict = dict(self.ignored)
        for vertex_id, vertex in enumerate(self.graph.vertices):
            if sp.Symbol(vertex.graph.name) in ignore_dict:
                yield vertex.graph.name, 0
            else:
                # Since we use numpy, we can use the left hand expresses as mathematical expressions
                sub_result = 0
                for reaction_index, reaction_edge in enumerate(self.graph.edges):
                    for source_vertex in reaction_edge.sources:
                        if vertex.id == source_vertex.id:
                            sub_result -= left_hand_sides[reaction_index]

                    for target_vertex in reaction_edge.targets:
                        if vertex.id == target_vertex.id:
                            sub_result += left_hand_sides[reaction_index]
                yield vertex.graph.name, sub_result

    def unchanging_species(self, *species: Union[str, sp.Symbol, Types.Countable_Sequence]):
        """
        Specify the list of species you don't want to see ODEs for
        :param species: list of strings symbol
        :return:
        """
        if len(self.ignored) < self.species_count:
            if type(species) is str:
                self.ignored = tuple((item, index) for index, item in enumerate(self.symbols.values())
                                     if sp.Symbol(species) == item)
            elif type(species) is sp.Symbol:
                self.ignored = tuple((item, index) for index, item in enumerate(self.symbols.values())
                                     if species == item)
            else:
                self.ignored = tuple((item, index) for index, item in enumerate(self.symbols.values())
                                     for element in species if sp.Symbol(element) == item)
        else:
            self.logger.warn("ignored species count exceeds the count of actual species")
        return self

    def parse_abstract_reaction(self, reaction: str) -> Union[object, Tuple[object,object]]:

        def parse_sides(side):
            skip_next = False
            the_splitting = side.split()
            for index, char in enumerate(the_splitting):
                if not skip_next:
                    if str.isdigit(char):
                        skip_next = True
                        multiplier = int(char)
                        try:
                            species = the_splitting[index + 1]
                        except IndexError:
                            raise IndexError("Index error in\
                              specification parsing; tried index {} but length is {} ".format(index + 1,
                                                                                              len(the_splitting)))
                        for i in range(multiplier):
                            yield species
                    elif '+' == char:
                        continue
                    if str.isalpha(char):
                        yield char
                else:
                    skip_next = False
                    continue

        def get_side_vertices(side):
            for sym in parse_sides(side):
                for vertex in self.graph.vertices:
                    if vertex.graph.name == sym:
                        yield vertex

        def break_two_way_deviations(two_way: str) -> Iterable[str]:
            yield " -> ".join(two_way.split(" <=> "))
            yield " -> ".join(reversed(two_way.split(" <=> ")))

        def parse_reaction(derivation: str):
            sources, _, targets = derivation.partition(" -> ")
            return self.graph.findEdge(get_side_vertices(sources), get_side_vertices(targets))

        if reaction.find(" <=> ") != -1:
            first_reaction, second_reaction = break_two_way_deviations(reaction)
            return parse_reaction(first_reaction), parse_reaction(second_reaction)

        elif reaction.find(' -> ') != -1:
            return parse_reaction(reaction)

    def __repr__(self):
        return "<Abstract Ode System {}>".format(self.left_hand_sides)

