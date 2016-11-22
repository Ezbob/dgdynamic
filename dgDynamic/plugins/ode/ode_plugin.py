from abc import abstractmethod, ABC
from enum import Enum
from typing import Union, Dict, Tuple
from ..plugin_base import PluginBase
from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.utils.project_utils import ProjectTypeHints as Types


def parameter_validation(plugin_instance, initial_values, reaction_count, species_count):
    def _count_parameters(parameters):
        return sum(2 if "<=>" in reaction_string else 1 for reaction_string in parameters.keys())

    if plugin_instance.simulation_range is None:
        raise ValueError("simulation range not set")
    elif len(plugin_instance.simulation_range) < 2:
        raise ValueError("Integration range; tuple is not of length 2 or more")
    elif plugin_instance.simulation_range[0] > plugin_instance.simulation_range[1]:
        raise ValueError("First value exceeds second in integration range")
    elif initial_values is None:
        raise ValueError("No valid or no initial condition values where given")
    elif plugin_instance.parameters is None:
        raise ValueError("Parameters not set")
    elif len(initial_values) - initial_values.count(None) < species_count:
        raise ValueError("Not enough initial values given")
    elif len(initial_values) - initial_values.count(None) > species_count:
        raise ValueError("Too many initial values given")
    elif reaction_count != _count_parameters(plugin_instance.parameters):
        raise ValueError("Expected {} parameter values, have {}"
                         .format(reaction_count, _count_parameters(plugin_instance.parameters)))


class OdePlugin(PluginBase, ABC):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """

    def __init__(self, simulator, simulation_range=(0, 0), initial_conditions=None,
                 rate_parameters=None, drain_parameters=None, delta_t=0.1, initial_t=0, ode_method=None):
        super().__init__(simulation_range=simulation_range, rate_parameters=rate_parameters,
                         initial_conditions=initial_conditions, drain_parameters=drain_parameters)
        self.simulation_range = simulation_range
        self._simulator = simulator
        self.initial_t = initial_t
        self.ode_method = ode_method
        self.delta_t = delta_t

    def __call__(self, simulation_range, initial_conditions, rate_parameters, diffusion_parameters=None,
                 ode_solver=None, delta_t=None, **kwargs):
        self.ode_method = ode_solver
        self.simulation_range = simulation_range
        self.initial_conditions = initial_conditions
        self.parameters = rate_parameters
        self.delta_t = delta_t
        output = self.solve(**kwargs)
        if output is None:
            raise ValueError("Solve returned None; check the calling parameters")
        return output

    @abstractmethod
    def solve(self):
        pass
