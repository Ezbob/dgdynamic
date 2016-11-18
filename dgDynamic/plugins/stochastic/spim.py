import os.path
import os
import array
import csv
import subprocess
import tempfile
import math
from dgDynamic.utils.exceptions import SimulationError
from dgDynamic.config.settings import config
from .stochastic_plugin import StochasticPlugin, SimulationOutput
from ...converters.stochastic.spim_converter import generate_initial_values, generate_rates, generate_automata_code, \
    generate_preamble
from dgDynamic.choices import SupportedStochasticPlugins
from collections import OrderedDict


class SpimStochastic(StochasticPlugin):

    def __init__(self, simulator, sample_range=None, parameters=None, initial_conditions=None,):
        sample_range = sample_range if sample_range is None else (float(sample_range[0]), sample_range[1])
        super().__init__(sample_range=sample_range, parameters=parameters, initial_conditions=initial_conditions)
        self._spim_path = config['Simulation']['SPIM_PATH']
        if self._spim_path is None or not self._spim_path:
            self._spim_path = os.path.join(os.path.dirname(__file__), "spim.ocaml")
        self._spim_path = os.path.abspath(self._spim_path)
        self._simulator = simulator
        self._ocamlrun_path = os.path.abspath(config['Simulation']['OCAML_RUN'])

    def solve(self, timeout=None, rel_tol=1e-09, abs_tol=0.0) -> SimulationOutput:
        def generate_code_file(file_path):
            with open(file_path, mode="w") as code_file:
                code_file.write(generate_preamble(sample_range=self.simulation_range,
                                                  symbols_dict=symbol_translate_dict,
                                                  species_count=self._simulator.species_count,
                                                  ignored=self._simulator.ignored))
                code_file.write('\n')
                code_file.write(generate_rates(derivation_graph=self._simulator.graph, channel_dict=channels,
                                               parameters=self.parameters))
                code_file.write('\n')
                code_file.write(generate_automata_code(channel_dict=channels,
                                                       symbols_dict=symbol_translate_dict,
                                                       species_count=self._simulator.species_count))
                code_file.write('\n\n')
                code_file.write(generate_initial_values(symbols_dict=symbol_translate_dict,
                                                        initial_conditions=self.initial_conditions))

        if self.parameters is None or self.initial_conditions is None:
            raise ValueError("Missing parameters or initial values")

        symbol_translate_dict = OrderedDict((sym, "_SYM{}".format(index))
                                            for index, sym in enumerate(self._simulator.symbols))
        channels = self._simulator.generate_channels()
        independent = array.array('d')
        dependent = list()
        errors = list()

        with tempfile.TemporaryDirectory() as tmpdir:

            file_path_code = os.path.join(tmpdir, "spim.spi")
            generate_code_file(file_path_code)

            if bool(config['Logging']['ENABLE_LOGGING']):
                with open(file_path_code) as debug_file:
                    self.logger.info("SPiM simulation file:\n{}".format(debug_file.read()))

            run_parameters = (self._ocamlrun_path, self._spim_path, file_path_code)
            try:
                stdout = subprocess.run(run_parameters, timeout=timeout, stdout=subprocess.PIPE).stdout
                self.logger.info("SPiM stdout:\n{}".format(stdout.decode()))
            except subprocess.TimeoutExpired:
                errors.append(SimulationError("Simulation time out"))

            csv_file_path = os.path.join(tmpdir, "spim.spi.csv")
            if not os.path.isfile(csv_file_path):
                self.logger.error("Missing SPiM output")
                errors.append(SimulationError("Missing SPiM output"))
                return SimulationOutput(SupportedStochasticPlugins.SPiM, errors=errors)

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
                        return SimulationOutput(SupportedStochasticPlugins.SPiM, dependent=dependent,
                                                independent=independent, abstract_system=self._simulator, errors=errors)

        return SimulationOutput(SupportedStochasticPlugins.SPiM, dependent=dependent, independent=independent,
                                abstract_system=self._simulator, errors=errors)
