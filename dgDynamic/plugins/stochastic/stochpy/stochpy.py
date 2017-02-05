import contextlib as cl
import enum
import io
import tempfile
import time
import warnings
import dgDynamic.base_converters.convert_base as converter_base
import dgDynamic.output as o
import dgDynamic.plugins.stochastic.stochpy.stochpy_converter as stochpy_converter
import dgDynamic.utils.messages as messages
from dgDynamic.choices import SupportedStochasticPlugins, StochPyStochasticSolvers
from dgDynamic.plugins.stochastic.stochastic_plugin import StochasticPlugin
import multiprocessing as mp
import queue

name = SupportedStochasticPlugins.StochPy


class StochPyStochastic(StochasticPlugin):

    def __init__(self, simulator, stochastic_method=StochPyStochasticSolvers.direct, timeout=None):
        super().__init__(simulator, timeout)
        self._method = stochastic_method
        self.startup_interval = 1
        self._simulator = simulator

    def generate_psc_file(self, writable_stream, rate_law_dict, initial_conditions,
                          rate_parameters, drain_parameters=None, translate_dict=None):

        internal_symbols = self._simulator.internal_symbol_dict
        internal_drains = self._simulator.internal_drain_dict

        ignoreds = tuple(item[0] for item in self._simulator.ignored)
        rates = dict(converter_base.get_edge_rate_dict(self._simulator.graph, rate_parameters,
                                                       self._simulator.parameters))
        for sym in self._simulator.parameters.values():
            # adding in any missing parameter values
            new_sym = sym.replace('$', '')
            if new_sym not in rates:
                rates[new_sym] = 0

        writable_stream.write(stochpy_converter.generate_fixed_species(self._simulator.ignored, internal_symbols))

        writable_stream.write(stochpy_converter.generate_reactions(rate_law_dict, translate_dict))

        drain_values = dict(converter_base.get_drain_rate_dict(internal_drains, drain_parameters))

        writable_stream.write(stochpy_converter.generate_drains(drain_values, internal_drains, internal_symbols, ignoreds))

        writable_stream.write('\n')
        writable_stream.write(stochpy_converter.generate_rates(rates))
        writable_stream.write("\n")
        initial_values = dict(zip((sym.replace('$', '') for sym in self._simulator.symbols_internal),
                                  converter_base.get_initial_values(initial_conditions, self._simulator.symbols)))
        writable_stream.write(stochpy_converter.generate_initial_conditions(initial_values))
        writable_stream.write("\n")

    @property
    def method(self):
        if isinstance(self._method, enum.Enum):
            return self._method
        elif isinstance(self._method, str):
            for supported in StochPyStochasticSolvers:
                name, value = supported.name.lower().strip(), supported.value.lower().strip()
                user_method = self._method.lower().strip()
                if user_method == name or user_method == value:
                    return supported

    @method.setter
    def method(self, value):
        self._method = value

    def simulate(self, simulation_range, initial_conditions,
                 rate_parameters, drain_parameters=None, *args, **kwargs):

        def choose_method_and_run(tmp_dir, model_name):

            self.logger.info("simulation method name: {}".format(self.method.name))
            self.logger.info("simulation end time: {}".format(simulation_range[1]))

            with cl.redirect_stdout(None):
                import stochpy

            def do_it(queue):
                import os
                import random

                random.seed(os.urandom(32))
                settings = queue.get()  # get the actual config for this instance
                queue.get()  # consume our start up token

                module = stochpy.SSA(model_file=settings['model'],
                                     dir=settings['directory'], )

                if settings['method'] == StochPyStochasticSolvers.direct:
                    module.Method('Direct')
                elif settings['method'] == StochPyStochasticSolvers.tauLeaping:
                    module.Method('TauLeaping')

                module.Endtime(settings['end_time'])

                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore')
                        stdout_str = io.StringIO()
                        with cl.redirect_stdout(stdout_str):
                            module.DoStochSim()
                except BaseException as exception:
                    queue.put({
                        "success": False,
                        "output": exception
                    })
                    module.Reload()
                    return
                finally:
                    stdout_str.close()
                queue.put({
                    "success": True,
                    "output": module.data_stochsim.getSpecies(lbls=True)
                })
                module.Reload()

            q = mp.Queue()
            q.put({
                "method": self.method,
                "end_time": simulation_range[1],
                "directory": tmp_dir,
                "model": model_name
            })
            q.put(0)

            process = mp.Process(target=do_it, args=(q,))
            #do_it(q)
            self.logger.info("Running simulation...")
            start_time = time.time()
            process.start()

            while q.qsize() == 2:  # because the subprocess needs time to consume the input we wait
                process.join(timeout=self.startup_interval)

            self.logger.info("Started subprocess")
            try:
                self.logger.info("Timeout: {}".format(self.timeout))
                out = q.get(timeout=self.timeout, block=True)
                end_time = time.time()
                self.logger.info("Simulation ended. Execution time: {} secs".format(end_time - start_time))
                self.logger.info("Got back: {}".format(repr(out)))
                if out['success']:
                    data, labels = out['output']
                    # now we have to compute an inverse mapping from internal symbols to external since stochpy does
                    # not maintain the order of the dependent data columns
                    inverse_symbol_translator = {val.replace('$', ''): key
                                                 for key, val in self._simulator.internal_symbol_dict.items()}
                    new_symbol_order = (inverse_symbol_translator[symbol] for symbol in labels[1:])
                    messages.print_solver_done(name, method_name=self.method.name)
                    return o.SimulationOutput(name, simulation_range, new_symbol_order,
                                              independent=data[:, :1], dependent=data[:, 1:])
                else:
                    messages.print_solver_done(name, method_name=self.method.name, was_failure=True)
                    return o.SimulationOutput(name, simulation_range, self._simulator.symbols,
                                              solver_method=self.method, errors=(out['output'],))
            except queue.Empty:
                messages.print_solver_done(name, method_name=self.method.name, was_failure=True)
                return o.SimulationOutput(name, simulation_range, self._simulator.symbols,
                                          solver_method=self.method, errors=(
                                            Exception('Internal process error'),))
            finally:
                if process.is_alive():  # if process is still alive(that is computing) then terminate it
                    self.logger.info("Terminating process")
                    process.terminate()
                    process.join()
        with tempfile.TemporaryDirectory() as tmp:
            model_file_path = "{}/model.psc".format(tmp)
            with open(model_file_path, mode="w+") as file_stream:
                rate_law_dict = dict(zip(self._simulator.abstract_edges,
                                         self._simulator.generate_propensities()))
                self.generate_psc_file(file_stream, rate_law_dict, initial_conditions, rate_parameters,
                                       drain_parameters, self._simulator.internal_symbol_dict)
                file_stream.seek(0)
                self.logger.info("StochPy simulation file:\n{}".format("".join(file_stream.readlines())))

                output = choose_method_and_run(tmp, "model.psc")

        return output
