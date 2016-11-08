import os
import os.path
import threading
import time
import multiprocessing as mp
import sympy as sp
from abc import abstractmethod, ABC
from enum import Enum
from typing import Union, Dict, Tuple, Callable
from ..plugin_base import PluginBase
from dgDynamic.config.settings import config
from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.utils.project_utils import make_directory, ProjectTypeHints as Types
from dgDynamic.utils.plotter import plot


def sanity_check(plugin_instance, initial_values):
    if plugin_instance.integration_range is None:
        raise ValueError("Integration range not set")
    elif len(plugin_instance.integration_range) != 2:
        raise ValueError("Integration range; tuple is not of length 2")
    elif plugin_instance.integration_range[0] > plugin_instance.integration_range[1]:
        raise ValueError("First value exceeds second in integration range")
    elif initial_values is None:
        raise ValueError("No valid or no initial condition values where given")
    elif len(initial_values) - initial_values.count(None) < plugin_instance.ode_count:
        raise ValueError("Not enough initial values given")
    elif len(initial_values) - initial_values.count(None) > plugin_instance.ode_count:
        raise ValueError("Too many initial values given")
    elif plugin_instance.parameters is None:
        raise ValueError("Parameters not set")
    elif plugin_instance._reaction_count != _count_parameters(plugin_instance.parameters):
        raise ValueError("Expected {} parameter values, have {}".format(plugin_instance._reaction_count,
                                                                        _count_parameters(plugin_instance.parameters)))


def _count_parameters(parameters):
    return sum(2 if "<=>" in reaction_string else 1 for reaction_string in parameters.keys())


class OdePlugin(PluginBase, ABC):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """

    def __init__(self, function: Union[object, Callable, str]=None, integration_range=(0, 0), initial_conditions=None,
                 delta_t=0.05, parameters=None, species_count=1, initial_t=0, converter_function=None,
                 ode_solver=None):
        super().__init__(parameters, initial_conditions)

        if type(function) is ODESystem:
            self.ode_count = function.species_count
            self._reaction_count = function.reaction_count
            self._symbols = function.symbols
            self._abstract_system = function
            self.ignored_count = len(function.ignored)
            self._ignored = function.ignored
            self._user_function = None
        else:
            self._ignored = ()
            self.ignored_count = 0
            self._reaction_count = None
            self.ode_count = species_count
            self._abstract_system = None
            self._symbols = None
            self._user_function = function

        self.initial_t = initial_t
        self._ode_solver = ode_solver
        self.delta_t = delta_t
        self.integration_range = integration_range
        self._convert_to_function(converter_function)

    def _convert_to_function(self, converter_function):
        if type(self._abstract_system) is ODESystem and callable(converter_function) and \
                        self.parameters is not None:
            self._user_function = converter_function(self._abstract_system, self.parameters)

    def __call__(self, ode_solver=None, simulation_range=None, initial_conditions=None, parameters=None, delta_t=None,
                 **kwargs):
        self.ode_solver = ode_solver
        self.integration_range = simulation_range
        self.initial_conditions = initial_conditions
        self.parameters = parameters
        self.delta_t = delta_t
        output = self.solve(**kwargs)
        if output is None:
            raise ValueError("Solve returned None; check the calling parameters")
        return output

    @abstractmethod
    def solve(self):
        pass

    @property
    def ode_solver(self):
        return self._ode_solver

    @ode_solver.setter
    def ode_solver(self, solver: Enum):
        self._ode_solver = solver

    def set_ode_solver(self, solver: Enum):
        self.ode_solver = solver
        return self

    def set_integration_range(self, *range_tuple: Tuple[int, int]):
        if isinstance(range_tuple, tuple):
            if type(range_tuple[0]) is tuple:
                self.integration_range = range_tuple[0]
            else:
                self.integration_range = range_tuple
        return self

    def set_parameters(self, parameters: Union[list, tuple, Dict[str, float]]):
        self.parameters = parameters
        return self

    def set_abstract_ode_system(self, system: ODESystem):
        self._abstract_system = system
        self.ode_count = system.species_count
        self.ignored_count = len(system.ignored)
        self._ignored = system.ignored
        self._symbols = system.symbols
        return self

    def set_initial_conditions(self, conditions: Dict[str, Types.Reals]):
        self.initial_conditions = conditions
        return self

    def set_ode_function(self, ode_function: Types.ODE_Function):
        self._user_function = ode_function
        return self
