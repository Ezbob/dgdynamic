from dgDynamic.choices import SupportedStochasticPlugins
from .stochastic_plugin import StochasticPlugin
import dgDynamic.converters.stochastic.stochpy_converter as stochpy_converter
import dgDynamic.converters.convert_base as converter_base

name = SupportedStochasticPlugins.StochPy


class StochPyStochastic(StochasticPlugin):

    def __init__(self, simulator, timeout=None,):
        super().__init__()
        self._simulator = simulator

    def generate_psc_file(self, writable_stream, rate_law_dict, initial_conditions,
                          rate_parameters, drain_parameters=None, translate_dict=None):

        rates = dict(converter_base.get_edge_rate_dict(self._simulator.graph, rate_parameters,
                                                       self._simulator.parameters))
        writable_stream.write(stochpy_converter.generate_reactions(rate_law_dict, translate_dict))
        writable_stream.write("\n")
        writable_stream.write(stochpy_converter.generate_rates(rates))
        writable_stream.write("\n")
        initial_values = dict(zip((sym.replace('$', '') for sym in self._simulator.symbols_internal),
                                  converter_base.get_initial_values(initial_conditions, self._simulator.symbols)))
        writable_stream.write(stochpy_converter.generate_initial_conditions(initial_values))
        writable_stream.write("\n")

    def simulate(self, simulation_range, initial_conditions,
                 rate_parameters, drain_parameters, *args, **kwargs):
        pass