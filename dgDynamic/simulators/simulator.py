import abc
import sympy as sp
from typing import Union, Tuple
from ..converters.reaction_parser import abstract_reaction
from dgDynamic.utils.project_utils import LogMixin, ProjectTypeHints


class DynamicSimulator(abc.ABC, LogMixin):

    def __init__(self, graph):
        self.graph = graph
        self.ignored = tuple()
        self.symbols = tuple(vertex.graph.name for vertex in self.graph.vertices)
        self.reaction_count = sum(1 for _ in self.graph.edges)
        self.species_count = sum(1 for _ in self.graph.vertices)

    def parse_abstract_reaction(self, reaction: str) -> Union[object, Tuple[object, object]]:
        return abstract_reaction(self, reaction)

    def __call__(self, plugins, *args, **kwargs):
        return self.get_plugin(plugins, *args, **kwargs)

    def unchanging_species(self, *species: Union[str, sp.Symbol, ProjectTypeHints.Countable_Sequence]):
        if len(self.ignored) < self.species_count:
            self.ignored = tuple((item, self.symbols.index(item)) for item in species if item in self.symbols)
        else:
            self.logger.warn("ignored species count exceeds the count of actual species")
        return self

    @abc.abstractmethod
    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_plugin(self, plugin_name, *args, **kwargs):
        pass

    def __repr__(self):
        return "<Abstract Simulator>"

