import abc
import sympy as sp
from typing import Union, Tuple
from ..converters.reaction_parser import parse
from dgDynamic.utils.project_utils import LogMixin, ProjectTypeHints


class DynamicSimulator(abc.ABC, LogMixin):

    def __init__(self, graph):
        self.graph = graph
        self.ignored = tuple()
        self.reaction_count = sum(1 for _ in self.graph.edges)
        self.species_count = self.graph.numVertices

    def parse_abstract_reaction(self, reaction: str) -> Union[object, Tuple[object, object]]:
        return parse(self, reaction)

    def __call__(self, plugins, *args, **kwargs):
        return self.get_plugin(plugins, *args, **kwargs)

    @abc.abstractmethod
    def unchanging_species(self, *species: Union[str, sp.Symbol, ProjectTypeHints.Countable_Sequence]):
        pass

    @abc.abstractmethod
    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_plugin(self, plugin_name, *args, **kwargs):
        pass

