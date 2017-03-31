from abc import ABC
from ..plugin_base import PluginBase


class OdePlugin(PluginBase, ABC):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """

    def simulate(self, simulation_range, initial_conditions, rate_parameters, drain_parameters, *args, **kwargs):
        pass

    def __init__(self, simulator, delta_t=0.1, initial_t=0, method=None):
        super().__init__()
        self._simulator = simulator
        self.initial_t = initial_t
        self.delta_t = delta_t
        self._method = method

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value
