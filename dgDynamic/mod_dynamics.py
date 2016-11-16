from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.simulators.stochastic_pi_simulator import StochasticPiSystem
from typing import Union
from dgDynamic.simulators.simulator import HyperGraph
import enum


def dgDynamicSim(graph, simulator_choice="ode", unchanging_species=()) -> Union[ODESystem, StochasticPiSystem]:

    if isinstance(simulator_choice, str):
        if simulator_choice.strip().lower() == "ode":
            return ODESystem(graph=HyperGraph(graph)).unchanging_species(*unchanging_species)
        elif simulator_choice.strip().lower() == "stochastic":
            return StochasticPiSystem(graph=HyperGraph(graph)).unchanging_species(*unchanging_species)
    elif isinstance(simulator_choice, enum.Enum):
        if simulator_choice.name.lower() == "ode":
            return ODESystem(graph=HyperGraph(graph)).unchanging_species(*unchanging_species)
        elif simulator_choice.name.lower() == "stochastic_pi":
            return StochasticPiSystem(graph=HyperGraph(graph)).unchanging_species(*unchanging_species)
    else:
        return None
