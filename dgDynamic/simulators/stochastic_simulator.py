from dgDynamic.choices import SupportedStochasticPlugins
from dgDynamic.intermediate.intermediate_generators import generate_channels
from .simulator import DynamicSimulator
from ..plugins.stochastic.spim import SpimStochastic
from ..plugins.stochastic.stochpy import StochPyStochastic


class StochasticSystem(DynamicSimulator):

    def __init__(self, graph):
        super().__init__(graph=graph)
        self.decay_rates = tuple()

    def generate_channels(self):
        result, self.decay_rates = generate_channels(self.graph.edges)
        return result

    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        if enum_variable == SupportedStochasticPlugins.SPiM:
            return SpimStochastic(self, *args, **kwargs)
        elif enum_variable == SupportedStochasticPlugins.StochPy:
            return StochPyStochastic(self, *args, **kwargs)

    def get_plugin(self, plugin_name, *args, **kwargs):
        if isinstance(plugin_name, str):
            for plugin_enum in SupportedStochasticPlugins:
                if plugin_enum.value in plugin_name.lower():
                    return self.get_plugin_from_enum(plugin_enum, *args, **kwargs)
        elif isinstance(plugin_name, SupportedStochasticPlugins):
            return self.get_plugin_from_enum(plugin_name, *args, **kwargs)

    def __repr__(self):
        return "<Abstract Stochastic Simulator>"
