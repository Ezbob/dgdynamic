import abc
from ..plugin_base import PluginBase, SimulationOutput


class StochasticPlugin(PluginBase, abc.ABC):

    def __init__(self, sample_range=None, parameters=None, initial_conditions=None, ignored=None):
        super().__init__(parameters=parameters, initial_conditions=initial_conditions)
        self.sample_range = sample_range

    @abc.abstractmethod
    def solve(self) -> SimulationOutput:
        pass

    def __call__(self, simulation_range=None, parameters=None, initial_conditions=None,):
        self.sample_range = simulation_range
        self.parameters = parameters
        self.initial_conditions = initial_conditions
        output = self.solve()
        if output is None:
            raise ValueError("Stochastic simulation output was None; check your parameters")
        return output
