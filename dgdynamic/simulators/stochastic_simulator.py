from dgdynamic.choices import SupportedStochasticPlugins
from dgdynamic.intermediate.intermediate_generators import generate_channels, generate_propensities
from .simulator import DynamicSimulator
from ..plugins.plugin_table import PLUGINS_TAB


class StochasticSystem(DynamicSimulator):

    def __init__(self, graph):
        super().__init__(graph=graph)
        self.decay_rates = tuple()

    def generate_channels(self):
        result, self.decay_rates = generate_channels(self.graph.edges)
        return result

    @property
    def channels(self):
        return dict(self.generate_channels())

    def generate_propensities(self):
        yield from (law_tuple[1] for law_tuple in generate_propensities(self.graph.edges, self.parameters,
                                                                        self.internal_symbol_dict))

    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        for enum_var, plugin_class in PLUGINS_TAB['stochastic'].items():
            if enum_var == enum_variable:
                return plugin_class(self, *args, **kwargs) if plugin_class is not None else None

    def get_plugin(self, plugin_name, *args, **kwargs):
        if isinstance(plugin_name, str):
            for plugin_enum in SupportedStochasticPlugins:
                if plugin_enum.value in plugin_name.lower():
                    return self.get_plugin_from_enum(plugin_enum, *args, **kwargs)
        elif isinstance(plugin_name, SupportedStochasticPlugins):
            return self.get_plugin_from_enum(plugin_name, *args, **kwargs)

    def __repr__(self):
        return "<Abstract Stochastic Simulator>"
