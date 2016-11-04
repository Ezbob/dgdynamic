from dgDynamic.config.settings import config
import os.path


class StochasticSpim:
    def __init__(self):
        self._spim_path = config['Simulation']['SPIM_PATH']

        if self._spim_path is None or not self._spim_path:
            self._spim_path = os.path.abspath()  # TODO INCLUDE SPIM.OCAML IF CONFIG IS BLANK
        else:
            self._spim_path = os.path.abspath(self._spim_path)

        self._ocamlrun_path = os.path.abspath(config['Simulation']['OCAML_RUN'])

    def solve(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError
