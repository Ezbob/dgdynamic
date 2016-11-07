import os.path
import os
import shutil
import subprocess
import tempfile
from dgDynamic.config.settings import config
from .stochastic_plugin import StochasticPlugin, StochasticOutput
from ...converters.stochastic.spim_converter import generate_initial_values, generate_rates, generate_automata_code


class SpimStochastic(StochasticPlugin):

    def __init__(self, simulator, sample_range=None, parameters=None, initial_conditions=None,):
        super().__init__(sample_range=sample_range, parameters=parameters, initial_conditions=initial_conditions)
        self._spim_path = config['Simulation']['SPIM_PATH']
        if self._spim_path is None or not self._spim_path:
            self._spim_path = os.path.join(os.path.dirname(__file__), "spim.ocaml")
        self._spim_path = os.path.abspath(self._spim_path)
        self._simulator = simulator
        self._ocamlrun_path = os.path.abspath(config['Simulation']['OCAML_RUN'])

    def solve(self) -> StochasticOutput:

        if self.parameters is None or self.initial_conditions is None:
            raise ValueError("Missing parameters or initial values")

        with tempfile.TemporaryFile(mode='r+') as tf:
            channels = self._simulator.generate_channels()

            tf.write(generate_rates(self._simulator, channel_dict=channels, parameters=self.parameters))
            tf.write('\n')
            tf.write(generate_automata_code(channels, self._simulator.symbols))
            tf.write('\n\n')
            tf.write(generate_initial_values(self._simulator.symbols, self.initial_conditions))

            tf.seek(0)
            print(tf.read())
