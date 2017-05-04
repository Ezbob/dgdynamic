import abc
from ..base_converters.reaction_parser import abstract_mod_parser, hyper_edge_to_string
from dgdynamic.utils.project_utils import LogMixin
from ..intermediate.intermediate_generators import generate_rate_laws, generate_rate_equations
from collections import OrderedDict


class DynamicSimulator(abc.ABC, LogMixin):

    def __init__(self, graph):
        self.graph = graph
        self.ignored = tuple()
        self.reaction_count = sum(1 for _ in self.graph.edges)
        self.species_count = sum(1 for _ in self.graph.vertices)
        self.parameters = OrderedDict((edge.id, "$k{}".format(index + 1))
                                      for index, edge in enumerate(self.graph.edges))

    @property
    def symbols(self):
        yield from (vertex.graph.name for vertex in self.graph.vertices)

    @property
    def abstract_edges(self):
        yield from (hyper_edge_to_string(edge) for edge in self.graph.edges)

    @property
    def symbols_internal(self):
        yield from ("$SYM{}".format(index) for index, vertex in enumerate(self.graph.vertices))

    @property
    def drain_symbols(self):
        yield from (("$INOFF{}".format(index), "$INFAC{}".format(index),
                     "$OUTOFF{}".format(index), "$OUTFAC{}".format(index))
                    for index, vertex in enumerate(self.graph.vertices))

    @property
    def internal_symbol_dict(self):
        return OrderedDict(zip(self.symbols, self.symbols_internal))

    @property
    def internal_drain_dict(self):
        return OrderedDict(zip(self.symbols, self.drain_symbols))

    @staticmethod
    def edge_stoichiometrics(hyper_edge):
        source_stoiciometrics, target_stoichiometrics = dict(), dict()
        sources, targets = tuple(hyper_edge.sources), tuple(hyper_edge.targets)
        for v in sources:
            if v.graph.name in source_stoiciometrics:
                continue
            source_stoiciometrics[v.graph.name] = sources.count(v)
        for v in targets:
            if v.graph.name in target_stoichiometrics:
                continue
            target_stoichiometrics[v.graph.name] = targets.count(v)
        return source_stoiciometrics, target_stoichiometrics

    def parse_abstract_reaction(self, reaction):
        return abstract_mod_parser(self, reaction)

    def __call__(self, plugins, *args, **kwargs):
        return self.get_plugin(plugins, *args, **kwargs)

    def unchanging_species(self, *species):
        if len(self.ignored) < self.species_count:
            for item in species:
                for symbol_index, symbol in enumerate(self.symbols):
                    if item == symbol:
                        self.ignored += ((item, symbol_index),)
        else:
            self._logger.warn("ignored species count exceeds the count of actual species")
        return self

    def generate_rate_laws(self):
        yield from (law_tuple[1] for law_tuple in generate_rate_laws(self.graph.edges, self.parameters,
                                                                     self.internal_symbol_dict))

    def generate_rate_equations(self):
        yield from generate_rate_equations(self.graph.vertices, self.graph.edges, self.ignored, self.parameters,
                                           self.internal_symbol_dict, self.internal_drain_dict)

    @abc.abstractmethod
    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_plugin(self, plugin_name, *args, **kwargs):
        pass

    def __repr__(self):
        return "<Abstract Simulator>"

