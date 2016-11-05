import os.path
from dgDynamic.config.settings import config
from .stochastic_plugin import StochasticPlugin, StochasticOutput


class SpimStochastic(StochasticPlugin):

    def solve(self) -> StochasticOutput:
        pass

    def __init__(self, simulator, sample_range=None, parameters=None, initial_conditions=None,):
        super().__init__(sample_range=sample_range, parameters=parameters, initial_conditions=initial_conditions)
        self._spim_path = config['Simulation']['SPIM_PATH']
        if self._spim_path is None or not self._spim_path:
            self._spim_path = os.path.join(os.path.dirname(__file__), "spim.ocaml")
        self._spim_path = os.path.abspath(self._spim_path)
        self.simulator = simulator

        print(self._spim_path)

        self._ocamlrun_path = os.path.abspath(config['Simulation']['OCAML_RUN'])

