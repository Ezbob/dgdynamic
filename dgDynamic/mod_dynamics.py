from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.simulators.stochastic_pi_simulator import StochasticPiSystem
from typing import Union
from .structures import HyperGraph
from dgDynamic.plugins.plugin_base import SimulationOutput
import enum


def dgDynamicSim(derivation_graph, simulator_choice="ode", unchanging_species=()) -> Union[ODESystem, StochasticPiSystem]:
    deviation_graph = derivation_graph if isinstance(derivation_graph, HyperGraph) else HyperGraph(derivation_graph)
    if isinstance(simulator_choice, str):
        if simulator_choice.strip().lower() == "ode":
            return ODESystem(graph=deviation_graph).unchanging_species(*unchanging_species)
        elif simulator_choice.strip().lower() == "stochastic":
            return StochasticPiSystem(graph=deviation_graph).unchanging_species(*unchanging_species)
    elif isinstance(simulator_choice, enum.Enum):
        if simulator_choice.name.lower() == "ode":
            return ODESystem(graph=deviation_graph).unchanging_species(*unchanging_species)
        elif simulator_choice.name.lower() == "stochastic_pi":
            return StochasticPiSystem(graph=deviation_graph).unchanging_species(*unchanging_species)
    else:
        return None


def show_simulation_plots(*args, **kwargs):
    SimulationOutput.show(*args, **kwargs)
