from dgDynamic.choices import SupportedStochasticPlugins
from dgDynamic.intermediate.intermediate_generators import generate_channels
from .simulator import DynamicSimulator
from ..plugins.plugin_table import PLUGINS_TAB


class StochasticSystem(DynamicSimulator):

    def __init__(self, graph):
        super().__init__(graph=graph)
        self.decay_rates = tuple()

    def generate_channels(self):
        result, self.decay_rates = generate_channels(self.graph.edges)
        return result

    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        for enum_var, plugin_class in PLUGINS_TAB['stochastic'].items():
            if enum_var == enum_variable:
                return plugin_class(self, *args, **kwargs)

    def get_plugin(self, plugin_name, *args, **kwargs):
        if isinstance(plugin_name, str):
            for plugin_enum in SupportedStochasticPlugins:
                if plugin_enum.value in plugin_name.lower():
                    return self.get_plugin_from_enum(plugin_enum, *args, **kwargs)
        elif isinstance(plugin_name, SupportedStochasticPlugins):
            return self.get_plugin_from_enum(plugin_name, *args, **kwargs)

    def __repr__(self):
        return "<Abstract Stochastic Simulator>"
