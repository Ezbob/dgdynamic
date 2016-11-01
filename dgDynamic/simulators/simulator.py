import abc
from typing import Union, Tuple
import sympy as sp
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

    @abc.abstractmethod
    def unchanging_species(self, *species: Union[str, sp.Symbol, ProjectTypeHints.Countable_Sequence]):
        pass
