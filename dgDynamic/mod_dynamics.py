from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.simulators.stochastic_pi_simulator import StochasticPiSystem
from typing import Union
import enum


class SupportedSolvers(enum.Enum):
    """
    Here we list the different solvers available in our system as key-value pairs.
    The value is the internal system name for the solver and is used when saving the data files etc.
    """
    Scipy = "scipy"
    Matlab = "matlab"


def dgDynamicSim(graph, simulator_choice="ode") -> Union[ODESystem, StochasticPiSystem]:
    if simulator_choice.strip().lower() == "ode":
        return ODESystem(graph=graph)
    elif simulator_choice.strip().lower() == "spim":
        return StochasticPiSystem(graph=graph)

