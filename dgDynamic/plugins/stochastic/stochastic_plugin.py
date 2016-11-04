from ..plugin_base import PluginBase, OutputBase
import abc


class StochasticOutput(OutputBase):
    def plot(self):
        pass

    def save(self):
        pass


class StochasticPlugin(PluginBase, abc.ABC):

    def __init__(self, sample_range=None, parameters=None, initial_conditions=None,):
        super().__init__(parameters=parameters, initial_conditions=initial_conditions)
        self.sample_range = sample_range

    @abc.abstractmethod
    def solve(self) -> StochasticOutput:
        pass

    def __call__(self, sample_range=None, parameters=None, initial_conditions=None,):
        self.sample_range = sample_range
        self.parameters = parameters
        self.initial_conditions = initial_conditions
        output = self.solve()
        if output is None:
            raise ValueError("Stochastic simulation output was None; check your parameters")
        return output
