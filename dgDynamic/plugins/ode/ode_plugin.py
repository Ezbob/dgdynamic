from abc import abstractmethod, ABC
from enum import Enum
from typing import Union, Dict, Tuple
from ..plugin_base import PluginBase
from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.utils.project_utils import ProjectTypeHints as Types


def sanity_check(plugin_instance, initial_values):
    if plugin_instance.simulation_range is None:
        raise ValueError("simulation range not set")
    elif len(plugin_instance.simulation_range) != 2:
        raise ValueError("Integration range; tuple is not of length 2")
    elif plugin_instance.simulation_range[0] > plugin_instance.simulation_range[1]:
        raise ValueError("First value exceeds second in integration range")
    elif initial_values is None:
        raise ValueError("No valid or no initial condition values where given")
    elif len(initial_values) - initial_values.count(None) < plugin_instance._simulator.species_count:
        raise ValueError("Not enough initial values given")
    elif len(initial_values) - initial_values.count(None) > plugin_instance._simulator.species_count:
        raise ValueError("Too many initial values given")
    elif plugin_instance.parameters is None:
        raise ValueError("Parameters not set")
    elif plugin_instance._simulator.reaction_count != _count_parameters(plugin_instance.parameters):
        raise ValueError("Expected {} parameter values, have {}".format(plugin_instance._simulator.reaction_count,
                                                                        _count_parameters(plugin_instance.parameters)))


def _count_parameters(parameters):
    return sum(2 if "<=>" in reaction_string else 1 for reaction_string in parameters.keys())


class OdePlugin(PluginBase, ABC):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """

    def __init__(self, simulator, simulation_range=(0, 0), initial_conditions=None,
                 delta_t=0.05, rate_parameters=None, initial_t=0, ode_method=None):
        super().__init__(simulation_range=simulation_range, rate_parameters=rate_parameters,
                         initial_conditions=initial_conditions)
        self.simulation_range = simulation_range
        self._simulator = simulator
        self.initial_t = initial_t
        self._ode_method = ode_method
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

    @property
    def ode_method(self) -> Enum:
        return self._ode_method

    @ode_method.setter
    def ode_method(self, solver: Enum):
        self._ode_method = solver

    def set_ode_solver(self, solver: Enum):
        self._ode_method = solver
        return self

    def set_integration_range(self, *range_tuple: Tuple[int, int]):
        if isinstance(range_tuple, tuple):
            if type(range_tuple[0]) is tuple:
                self.simulation_range = range_tuple[0]
            else:
                self.simulation_range = range_tuple
        return self

    def set_parameters(self, parameters: Union[list, tuple, Dict[str, float]]):
        self.parameters = parameters
        return self

    def set_abstract_ode_system(self, system: ODESystem):
        self._simulator = system
        return self

    def set_initial_conditions(self, conditions: Dict[str, Types.Reals]):
        self.initial_conditions = conditions
        return self

