import abc
from ..plugin_base import PluginBase, SimulationOutput


class StochasticPlugin(PluginBase, abc.ABC):

    def __init__(self, sample_range=None, parameters=None, initial_conditions=None):
        super().__init__(simulation_range=sample_range, parameters=parameters, initial_conditions=initial_conditions)

    @abc.abstractmethod
    def solve(self) -> SimulationOutput:
        pass

    def __call__(self, simulation_range, initial_conditions, parameters, *args, **kwargs):
        self.simulation_range = simulation_range
        self.parameters = parameters
        self.initial_conditions = initial_conditions
        output = self.solve(*args, **kwargs)
        if output is None:
            raise ValueError("Stochastic simulation output was None; check your parameters")
        return output
