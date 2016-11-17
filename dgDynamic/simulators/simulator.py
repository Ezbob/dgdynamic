import abc
import sympy as sp
from typing import Union, Tuple
from ..converters.reaction_parser import abstract_reaction_parser
from dgDynamic.utils.project_utils import LogMixin, ProjectTypeHints
from io import StringIO


class DynamicSimulator(abc.ABC, LogMixin):

    def __init__(self, graph):
        self.graph = graph
        self.ignored = tuple()
        self.symbols = tuple(vertex.graph.name for vertex in self.graph.vertices)
        self.reaction_count = sum(1 for _ in self.graph.edges)
        self.species_count = sum(1 for _ in self.graph.vertices)

    @property
    def abstract_edges(self):
        def _hyper_edge_to_string(edge):
            with StringIO() as out:
                for index, source_vertex in enumerate(edge.sources):
                    out.write(source_vertex.graph.name)
                    if index < edge.numSources - 1:
                        out.write(" + ")
                out.write(" -> ")

                for index, target_vertex in enumerate(edge.targets):
                    out.write(target_vertex.graph.name)
                    if index < edge.numTargets - 1:
                        out.write(" + ")
                out.write("\n")
                return out.getvalue()
        yield from (_hyper_edge_to_string(edge) for edge in self.graph.edges)

    def parse_abstract_reaction(self, reaction: str) -> Union[object, Tuple[object, object]]:
        return abstract_reaction_parser(self, reaction)

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

