import os.path
import os
import array
import csv
import subprocess
import tempfile
from dgDynamic.config.settings import config
from .stochastic_plugin import StochasticPlugin, SimulationOutput
from ...converters.stochastic.spim_converter import generate_initial_values, generate_rates, generate_automata_code, \
    generate_preamble
from dgDynamic.choices import SupportedStochasticPlugins


class SpimStochastic(StochasticPlugin):

    def __init__(self, simulator, sample_range=None, parameters=None, initial_conditions=None,):
        super().__init__(sample_range=sample_range, parameters=parameters, initial_conditions=initial_conditions)
        self._spim_path = config['Simulation']['SPIM_PATH']
        if self._spim_path is None or not self._spim_path:
            self._spim_path = os.path.join(os.path.dirname(__file__), "spim.ocaml")
        self._spim_path = os.path.abspath(self._spim_path)
        self._simulator = simulator
        self._ocamlrun_path = os.path.abspath(config['Simulation']['OCAML_RUN'])

    def solve(self) -> SimulationOutput:

        def generate_code_file(file_path):
            with open(file_path, mode="w") as file:
                file.write(generate_preamble(self.sample_range, symbols=self._simulator.symbols))
                file.write('\n')
                file.write(generate_rates(self._simulator, channel_dict=channels, parameters=self.parameters))
                file.write('\n')
                file.write(generate_automata_code(channels, self._simulator.symbols))
                file.write('\n\n')
                file.write(generate_initial_values(self._simulator.symbols, self.initial_conditions))

        if self.parameters is None or self.initial_conditions is None:
            raise ValueError("Missing parameters or initial values")

        with tempfile.TemporaryDirectory() as tmpdir:
            channels = self._simulator.generate_channels()

            file_path_code = os.path.join(tmpdir, "spim.spi")
            data_dir_path = os.path.join(os.path.abspath(os.path.curdir), "data/")
            generate_code_file(file_path_code)

            with open(os.devnull, 'w') as devnull:
                run_parameters = (self._ocamlrun_path, self._spim_path, file_path_code)
                subprocess.run(run_parameters, stdout=devnull)

            with open(os.path.join(tmpdir, "spim.spi.csv")) as file:
                reader = csv.reader(file)
                header = next(reader)
                independent = array.array('d')
                dependent = tuple(array.array('d') for _ in range(max(1, len(header) - 1)))
                for line in reader:
                    independent.append(float(line[0]))
                    for index, dependent_list in enumerate(dependent):
                        dependent_list.append(float(line[index + 1]))

        return SimulationOutput(SupportedStochasticPlugins.SPiM, dependent, independent,
                                abstract_system=self._simulator)
