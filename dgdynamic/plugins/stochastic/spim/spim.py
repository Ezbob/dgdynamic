import csv
import math
import os
import os.path
import subprocess
import tempfile
import dgdynamic.plugins.stochastic.spim.spim_converter as converters
import dgdynamic.utils.messages as messages
import numpy
from collections import OrderedDict
from dgdynamic.choices import SupportedStochasticPlugins
from dgdynamic.config.settings import config, logging_is_enabled
from dgdynamic.output import SimulationOutput
from dgdynamic.plugins.stochastic.stochastic_plugin import StochasticPlugin
from dgdynamic.utils.exceptions import SimulationError
from dgdynamic.plugins.sim_validation import simulation_parameter_validate

name = SupportedStochasticPlugins.SPiM


class SpimStochastic(StochasticPlugin):

    def __init__(self, simulator, timeout=None, resolution=1000, absolute_float_tolerance=1e-9,
                 relative_float_tolerance=0.0):
        super().__init__(simulator, timeout, resolution)
        self._spim_path = config['Simulation']['SPIM_PATH']
        if not self._spim_path:
            self._spim_path = os.path.join(os.path.dirname(__file__), "spim.ocaml")
        self._spim_path = os.path.abspath(self._spim_path)
        self._ocamlrun_path = os.path.abspath(config['Simulation']['OCAML_RUN'])
        self.relative_float_tolerance = relative_float_tolerance
        self.absolute_float_tolerance = absolute_float_tolerance

    def generate_code_file(self, writable_stream, simulation_range, initial_conditions, rate_parameters,
                           drain_parameters=None):
        fixed_point_precision = abs(config.getint('Simulation', 'FIXED_POINT_PRECISION', fallback=18))
        symbol_translate_dict = OrderedDict((sym, "SYM{}".format(index))
                                            for index, sym in enumerate(self._simulator.symbols))
        channels = self._simulator.generate_channels()
        writable_stream.write(converters.generate_preamble(sample_range=simulation_range,
                                                           symbols_dict=symbol_translate_dict,
                                                           species_count=self._simulator.species_count,
                                                           ignored=self._simulator.ignored,
                                                           float_precision=fixed_point_precision))
        writable_stream.write('\n')
        writable_stream.write(converters.generate_rates(derivation_graph=self._simulator.graph,
                                                        channel_dict=channels,
                                                        parameters=rate_parameters,
                                                        drain_parameters=drain_parameters,
                                                        internal_drains=self._simulator.internal_drain_dict,
                                                        float_precision=fixed_point_precision))
        writable_stream.write('\n')
        writable_stream.write(converters.generate_automata_code(channel_dict=channels,
                                                                symbols_dict=symbol_translate_dict,
                                                                internal_drains=self._simulator.internal_drain_dict))
        writable_stream.write('\n\n')
        writable_stream.write(converters.generate_initial_values(symbols_dict=symbol_translate_dict,
                                                                 initial_conditions=initial_conditions))

    def simulate(self, end_t, initial_conditions, rate_parameters, drain_parameters=None,
                 timeout=None, rel_tol=None, abs_tol=None):

        self._logger.info("Starting on SPiM simulation")
        self._logger.info("End_t: {} resolution: {}".format(end_t, self.resolution))
        self._logger.info("Initial conditions: {}".format(initial_conditions))
        self._logger.info("Rates: {}".format(rate_parameters))
        self._logger.info("Drains: {}".format(drain_parameters))

        simulation_parameter_validate(end_t=end_t, initial_conditions=initial_conditions,
                                      rates_params=rate_parameters, drain_params=drain_parameters)

        def collect_data(errors=None):
            errors = [] if errors is None else errors
            ignore_pad = [(i, initial_conditions[label]) for label, i in self._simulator.ignored]
            res_indep, res_dep = [], []
            with open(csv_file_path) as file:
                reader = csv.reader(file)
                next(reader)
                old_time = 0.0
                for line in reader:
                    new_time = float(line[0])
                    if new_time > old_time or math.isclose(new_time, old_time,
                                                           rel_tol=self.relative_float_tolerance,
                                                           abs_tol=self.absolute_float_tolerance):
                        res_indep.append(new_time)
                        dep = list(map(float, line[1:]))
                        for index, val in ignore_pad:
                            dep.insert(index, val)
                        res_dep.append(dep)
                        old_time = new_time
                    else:
                        errors.append(SimulationError("Simulation time regression detected"))

            return numpy.array(res_indep), numpy.array(res_dep)

        errors = list()
        self.timeout = timeout if timeout is not None else self.timeout
        self.relative_float_tolerance = rel_tol if rel_tol is not None else self.relative_float_tolerance
        self.absolute_float_tolerance = abs_tol if abs_tol is not None else self.absolute_float_tolerance

        with tempfile.TemporaryDirectory() as tmpdir:

            file_path_code = os.path.join(tmpdir, "spim.spi")
            csv_file_path = os.path.join(tmpdir, "spim.spi.csv")
            with open(file_path_code, mode="w") as script:
                self.generate_code_file(script, (end_t, self.resolution), initial_conditions,
                                        rate_parameters, drain_parameters)

            if logging_is_enabled():
                with open(file_path_code) as debug_file:
                    self._logger.info("SPiM simulation file:\n{}".format(debug_file.read()))

            run_parameters = [self._ocamlrun_path, self._spim_path, file_path_code]
            try:
                process = subprocess.Popen(run_parameters, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           universal_newlines=True)
                stdout, stderr = process.communicate(input="\n", timeout=self.timeout)

                self._logger.info("SPiM stdout:\n{}".format(stdout))
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                errors.append(SimulationError("Simulation time out"))
                messages.print_solver_done(name, was_failure=True)
                independent, dependent = collect_data(errors)
                return SimulationOutput(name, (0, end_t),
                                        symbols=self._simulator.symbols,
                                        ignore=self._simulator.ignored,
                                        independent=independent, dependent=dependent,
                                        errors=errors)

            if not os.path.isfile(csv_file_path):
                if logging_is_enabled():
                    self._logger.error("Missing SPiM output")
                errors.append(SimulationError("Missing SPiM output"))
                messages.print_solver_done(name, was_failure=True)
                return SimulationOutput(name, (0, end_t),
                                        symbols=self._simulator.symbols, errors=errors)

            independent, dependent = collect_data(errors)
            if errors:
                messages.print_solver_done(name, was_failure=True)
                return SimulationOutput(name, (0, end_t), symbols=self._simulator.symbols,
                                        independent=independent, dependent=dependent,
                                        ignore=self._simulator.ignored,
                                        errors=errors)
            else:
                messages.print_solver_done(name, was_failure=False)
                return SimulationOutput(name, (0, end_t), symbols=self._simulator.symbols,
                                        ignore=self._simulator.ignored,
                                        independent=independent, dependent=dependent)
