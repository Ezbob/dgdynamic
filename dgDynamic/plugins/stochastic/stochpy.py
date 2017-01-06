from dgDynamic.choices import SupportedStochasticPlugins
from .stochastic_plugin import StochasticPlugin

name = SupportedStochasticPlugins.StochPy


class StochPyStochastic(StochasticPlugin):

    def __int__(self, simulator, timeout=None,):
        self._simulator = simulator

    def generate_code_file(self, writable_steam):
        pass

    def simulate(self, simulation_range, initial_conditions,
                 rate_parameters, drain_parameters, *args, **kwargs):
        pass