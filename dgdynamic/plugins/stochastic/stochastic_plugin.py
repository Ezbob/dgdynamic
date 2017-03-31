import abc
from ..plugin_base import PluginBase


class StochasticPlugin(PluginBase, abc.ABC):

    def __init__(self, simulator, timeout, resolution, method=None):
        self._simulator = simulator
        self.timeout = timeout
        self._method = method
        self._resolution = resolution

    @abc.abstractmethod
    def simulate(self, end_t, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs):
        pass

    def __call__(self, end_t, initial_conditions, rate_parameters, drain_parameters=None, *args, **kwargs):
        return self.simulate(end_t, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs)

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, value):
        self._resolution = abs(int(value))
