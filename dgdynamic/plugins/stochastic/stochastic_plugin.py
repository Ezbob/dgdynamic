import abc
from ..plugin_base import PluginBase


class StochasticPlugin(PluginBase, abc.ABC):

    def __init__(self, simulator, timeout, method=None):
        self._simulator = simulator
        self.timeout = timeout
        self._method = method

    @abc.abstractmethod
    def simulate(self, simulation_range, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs):
        pass

    def __call__(self, simulation_range, initial_conditions, rate_parameters, drain_parameters=None, *args, **kwargs):
        return self.simulate(simulation_range, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs)

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value
