from dgDynamic.choices import SupportedStochasticPlugins, StochPyStochasticSolvers
from .stochastic_plugin import StochasticPlugin
import dgDynamic.converters.stochastic.stochpy_converter as stochpy_converter
import dgDynamic.converters.convert_base as converter_base
import tempfile
import io
import contextlib as cl
import time
import dgDynamic.output as o
import dgDynamic.utils.messages as messages

name = SupportedStochasticPlugins.StochPy


class StochPyStochastic(StochasticPlugin):

    def __init__(self, simulator, stochastic_method=StochPyStochasticSolvers.direct, timeout=None):
        super().__init__()
        self.stochastic_method = stochastic_method
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
                 rate_parameters, drain_parameters=None, *args, **kwargs):

        def choose_method_and_run(stochpy_module):

            if self.stochastic_method == StochPyStochasticSolvers.direct:
                stochpy_module.Method('Direct')
            elif self.stochastic_method == StochPyStochasticSolvers.tauLeaping:
                stochpy_module.Method('TauLeaping')

            self.logger.info("simulation method name: {}".format(stochpy_module.sim_method_name))
            stochpy_module.Endtime(simulation_range[1])
            self.logger.info("simulation end time: {}".format(stochpy_module.sim_end))

            self.logger.info("Running simulation...")
            start_time = time.time()
            stochpy_module.DoStochSim()
            end_time = time.time()
            self.logger.info("Simulation ended. Execution time: {} secs".format(end_time - start_time))
            data = stochpy_module.data_stochsim.getSpecies()
            return o.SimulationOutput(name, simulation_range, self._simulator.symbols,
                                      independent=data[:, :1], dependent=data[:, 1:])

        with tempfile.TemporaryDirectory() as tmp:
            stdout_str = io.StringIO()
            model_file_path = "{}/model.psc".format(tmp)
            with open(model_file_path, mode="w+") as file_stream:
                rate_law_dict = dict(zip(self._simulator.abstract_edges,
                                         self._simulator.generate_rate_laws()))
                self.generate_psc_file(file_stream, rate_law_dict, initial_conditions, rate_parameters,
                                       drain_parameters, self._simulator.internal_symbol_dict)
                file_stream.seek(0)
                self.logger.info("StochPy simulation file:\n{}".format("".join(file_stream.readlines())))

            with cl.redirect_stdout(stdout_str):
                import stochpy as sp
                stochpy_module = sp.SSA(dir=tmp, model_file="model.psc")

            output = choose_method_and_run(stochpy_module)

        messages.print_solver_done(name, method_name=self.stochastic_method.name)
        return output
