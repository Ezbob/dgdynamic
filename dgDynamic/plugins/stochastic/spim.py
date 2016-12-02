from dgDynamic.utils.exceptions import SimulationError
from dgDynamic.config.settings import config
from .stochastic_plugin import StochasticPlugin
from dgDynamic.output import SimulationOutput
import dgDynamic.converters.stochastic.spim_converter as converters
from dgDynamic.choices import SupportedStochasticPlugins
from collections import OrderedDict
import dgDynamic.utils.messages as messages
import os.path
import os
import array
import csv
import subprocess
import tempfile
import math


name = SupportedStochasticPlugins.SPiM


class SpimStochastic(StochasticPlugin):

    def __init__(self, simulator, sample_range=None, rate_parameters=None, initial_conditions=None,
                 drain_parameters=None):
        sample_range = sample_range if sample_range is None else (float(sample_range[0]), sample_range[1])

        super().__init__(sample_range=sample_range, rate_parameters=rate_parameters,
                         initial_conditions=initial_conditions, drain_parameters=drain_parameters)
        self._spim_path = config['Simulation']['SPIM_PATH']
        if not self._spim_path:
            self._spim_path = os.path.join(os.path.dirname(__file__), "spim.ocaml")
        self._spim_path = os.path.abspath(self._spim_path)
        self._simulator = simulator
        self._ocamlrun_path = os.path.abspath(config['Simulation']['OCAML_RUN'])

    def generate_code_file(self, writable_stream):
        fixed_point_precision = abs(config.getint('Simulation', 'FIXED_POINT_PRECISION', fallback=18))
        symbol_translate_dict = OrderedDict((sym, "SYM{}".format(index))
                                            for index, sym in enumerate(self._simulator.symbols))
        channels = self._simulator.generate_channels()
        writable_stream.write(converters.generate_preamble(sample_range=self.simulation_range,
                                                           symbols_dict=symbol_translate_dict,
                                                           species_count=self._simulator.species_count,
                                                           ignored=self._simulator.ignored,
                                                           float_precision=fixed_point_precision))
        writable_stream.write('\n')
        writable_stream.write(converters.generate_rates(derivation_graph=self._simulator.graph,
                                                        channel_dict=channels,
                                                        parameters=self.rate_parameters,
                                                        drain_parameters=self.drain_parameters,
                                                        internal_drains=self._simulator.internal_drain_dict,
                                                        float_precision=fixed_point_precision))
        writable_stream.write('\n')
        writable_stream.write(converters.generate_automata_code(channel_dict=channels,
                                                                symbols_dict=symbol_translate_dict,
                                                                internal_drains=self._simulator.internal_drain_dict,))
        writable_stream.write('\n\n')
        writable_stream.write(converters.generate_initial_values(symbols_dict=symbol_translate_dict,
                                                                 initial_conditions=self.initial_conditions, ))

    def solve(self, timeout=None, rel_tol=1e-09, abs_tol=0.0) -> SimulationOutput:

        if self.rate_parameters is None or self.initial_conditions is None:
            raise ValueError("Missing parameters or initial values")

        def collect_data(errors=None):
            errors = [] if errors is None else errors
            with open(csv_file_path) as file:
                reader = csv.reader(file)
                next(reader)
                old_time = 0.0
                for line in reader:
                    new_time = float(line[0])
                    if new_time > old_time or math.isclose(new_time, old_time, rel_tol=rel_tol, abs_tol=abs_tol):
                        independent.append(new_time)
                        dependent.append(array.array('d', map(float, line[1:])))
                        old_time = new_time
                    else:
                        errors.append(SimulationError("Simulation time regression detected"))
            return independent, dependent

        independent = array.array('d')
        dependent = list()
        errors = list()

        with tempfile.TemporaryDirectory() as tmpdir:

            file_path_code = os.path.join(tmpdir, "spim.spi")
            csv_file_path = os.path.join(tmpdir, "spim.spi.csv")
            with open(file_path_code, mode="w") as script:
                self.generate_code_file(script)

            if config.getboolean('Logging', 'ENABLE_LOGGING', fallback=False):
                with open(file_path_code) as debug_file:
                    self.logger.info("SPiM simulation file:\n{}".format(debug_file.read()))

            run_parameters = [self._ocamlrun_path, self._spim_path, file_path_code]
            try:
                process = subprocess.Popen(run_parameters, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           universal_newlines=True)
                stdout, stderr = process.communicate(input="\n", timeout=timeout)

                self.logger.info("SPiM stdout:\n{}".format(stdout))
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                errors.append(SimulationError("Simulation time out"))
                messages.print_solver_done(name, was_failure=True)
                independent, dependent = collect_data(errors)
                return SimulationOutput(name, abstract_system=self._simulator,
                                        independent=independent, dependent=dependent,
                                        errors=errors)

            if not os.path.isfile(csv_file_path):
                if config.getboolean('Logging', 'ENABLE_LOGGING', fallback=False):
                    self.logger.error("Missing SPiM output")
                errors.append(SimulationError("Missing SPiM output"))
                messages.print_solver_done(name, was_failure=True)
                return SimulationOutput(name, abstract_system=self._simulator, errors=errors)

            independent, dependent = collect_data(errors)
            if errors:
                messages.print_solver_done(name, was_failure=True)
                return SimulationOutput(name, abstract_system=self._simulator,
                                        independent=independent, dependent=dependent,
                                        errors=errors)
            else:
                messages.print_solver_done(name, was_failure=False)
                return SimulationOutput(name, abstract_system=self._simulator,
                                        independent=independent, dependent=dependent)