from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.simulators.stochastic_pi_simulator import StochasticPiSystem
from typing import Union
import enum


def dgDynamicSim(graph, simulator_choice="ode") -> Union[ODESystem, StochasticPiSystem]:

    if isinstance(simulator_choice, str):
        if simulator_choice.strip().lower() == "ode":
            return ODESystem(graph=graph)
        elif simulator_choice.strip().lower() == "spim":
            return StochasticPiSystem(graph=graph)
    elif isinstance(simulator_choice, enum.Enum):
        if simulator_choice.name.lower() == "ode":
            return ODESystem(graph=graph)
        elif simulator_choice.name.lower() == "stochastic_pi":
            return StochasticPiSystem(graph=graph)
    else:
        return None
