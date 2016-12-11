from abc import abstractmethod, ABC
from ..plugin_base import PluginBase
import dgDynamic.utils.typehints as th
import typing as tp

# TODO fix parameter validation
# def parameter_validation(input_args, reaction_count, species_count):
#     def _count_parameters(parameters):
#         return sum(2 if "<=>" in reaction_string else 1 for reaction_string in parameters.keys())
#
#     if input_args.simulation_range is None:
#         raise ValueError("simulation range not set")
#     elif len(input_args.simulation_range) < 2:
#         raise ValueError("Integration range; tuple is not of length 2 or more")
#     elif input_args.simulation_range[0] > input_args.simulation_range[1]:
#         raise ValueError("First value exceeds second in integration range")
#     elif initial_values is None:
#         raise ValueError("No valid or no initial condition values where given")
#     elif plugin_instance.parameters is None:
#         raise ValueError("Parameters not set")
#     elif len(initial_values) - initial_values.count(None) < species_count:
#         raise ValueError("Not enough initial values given")
#     elif len(initial_values) - initial_values.count(None) > species_count:
#         raise ValueError("Too many initial values given")
#     elif reaction_count != _count_parameters(plugin_instance.parameters):
#         raise ValueError("Expected {} parameter values, have {}"
#                          .format(reaction_count, _count_parameters(plugin_instance.parameters)))


class OdePlugin(PluginBase, ABC):
    """
    Super class for all the ODE plugins. This class inherits the Abstract Base Class and functions as a
    interface for all the ODE plugins.
    """

    def simulate(self, simulation_range, initial_conditions, rate_parameters, drain_parameters):
        pass

    def __init__(self, simulator, delta_t: tp.Optional[float]=0.1, initial_t: th.Real=0,
                 ode_method: tp.Optional[tp.Union[str, th.Enum]]=None):
        super().__init__()
        self._simulator = simulator
        self.initial_t = initial_t
        self.ode_method = ode_method
        self.delta_t = delta_t
