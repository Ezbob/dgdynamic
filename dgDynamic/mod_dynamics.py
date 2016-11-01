from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.simulators.stochastic_pi_simulator import StochasticPiSystem
from typing import Union


def dgDynamicSim(graph, simulator_choice="ode") -> Union[ODESystem, StochasticPiSystem]:
    if simulator_choice.strip().lower() == "ode":
        return ODESystem(graph=graph)
    elif simulator_choice.strip().lower() == "spim":
        return StochasticPiSystem(graph=graph)

