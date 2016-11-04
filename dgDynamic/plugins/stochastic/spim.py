from dgDynamic.config.settings import config
import os.path


class StochasticSpim:
    def __init__(self):
        self._spim_path = config['Simulation']['SPIM_PATH']

        if self._spim_path is None or not self._spim_path:
            self._spim_path = os.path.abspath()

        self._ocaml_path = config['Simulation']['OCAML_PATH']

