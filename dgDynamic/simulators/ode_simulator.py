import functools as ft
import sympy as sp
from collections import OrderedDict
from typing import Union
from dgDynamic.choices import SupportedOdePlugins
from .simulator import DynamicSimulator


class ODESystem(DynamicSimulator):
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
        super().__init__(graph=graph)

        # every vertex in the deviation graph gets a mapping from it's id to the corresponding SymPy Symbol
        self.symbols_mapping = OrderedDict(((vertex.id, sp.Symbol(vertex.graph.name))
                                            for vertex in self.graph.vertices))
        self.symbols = tuple(vertex.graph.name for vertex in self.graph.vertices)

        # the mass action law parameters. For mathematical reasons the symbol indices start at 1
        self.parameters = OrderedDict((edge.id, sp.Symbol("k{}".format(index + 1)))
                                      for index, edge in enumerate(self.graph.edges))

    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        if enum_variable == SupportedOdePlugins.Scipy:
            from dgDynamic.plugins.ode.scipy import ScipyOde
            return ScipyOde(self, *args, **kwargs)
        elif enum_variable == SupportedOdePlugins.Matlab:
            from dgDynamic.plugins.ode.matlab import MatlabOde
            return MatlabOde(self, *args, **kwargs)

    def get_plugin(self, plugin_name: Union[str, SupportedOdePlugins], *args, **kwargs):
        if isinstance(plugin_name, str):
            for plugin in SupportedOdePlugins:
                if plugin.value in plugin_name.lower():
                    return self.get_plugin_from_enum(plugin, *args, **kwargs)
            raise ValueError("plugin name not recognized")
        elif isinstance(plugin_name, SupportedOdePlugins):
            return self.get_plugin_from_enum(plugin_name, *args, **kwargs)

    def generate_rate_laws(self):
        for index, edge in enumerate(self.graph.edges):
            reduce_me = (sp.Symbol(vertex.graph.name) for vertex in edge.sources)
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
            if vertex.graph.name in ignore_dict:
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

    def __repr__(self):
        return "<Abstract Ode System>"

