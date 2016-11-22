import abc
from ..plugin_base import PluginBase, SimulationOutput


class StochasticPlugin(PluginBase, abc.ABC):

    def __init__(self, sample_range=None, rate_parameters=None, initial_conditions=None, drain_parameters=None):
        super().__init__(simulation_range=sample_range, rate_parameters=rate_parameters,
                         initial_conditions=initial_conditions, drain_parameters=drain_parameters)

    @abc.abstractmethod
    def solve(self) -> SimulationOutput:
        pass

    def __call__(self, simulation_range, initial_conditions, rate_parameters, *args, diffusion_parameters=None,
                 **kwargs):
        self.simulation_range = simulation_range
        self.parameters = rate_parameters
        self.initial_conditions = initial_conditions
        self.diffusion_parameters = diffusion_parameters
        output = self.solve(*args, **kwargs)
        if output is None:
            raise ValueError("Stochastic simulation output was None; check your parameters")
        return output
