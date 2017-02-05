import abc
from ..plugin_base import PluginBase
from dgDynamic.output import SimulationOutput


class StochasticPlugin(PluginBase, abc.ABC):

    def __init__(self, simulator, timeout):
        self._simulator = simulator
        self.timeout = timeout

    @abc.abstractmethod
    def simulate(self, simulation_range, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs):
        pass

    def __call__(self, simulation_range, initial_conditions, rate_parameters, drain_parameters=None, *args, **kwargs):
        return self.simulate(simulation_range, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs)

