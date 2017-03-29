from dgdynamic.simulators.ode_simulator import ODESystem
from dgdynamic.simulators.stochastic_simulator import StochasticSystem
from .structures import HyperGraph
from dgdynamic.output import SimulationOutput
import enum


class dgDynamicSim:
    def __new__(cls, derivation_graph, simulator_choice="ode", unchanging_species=()):
        deviation_graph = derivation_graph if isinstance(derivation_graph, HyperGraph) else HyperGraph(derivation_graph)
        if isinstance(simulator_choice, str):
            if simulator_choice.strip().lower() == "ode":
                return ODESystem(graph=deviation_graph).unchanging_species(*unchanging_species)
            elif simulator_choice.strip().lower() == "stochastic":
                return StochasticSystem(graph=deviation_graph).unchanging_species(*unchanging_species)
        elif isinstance(simulator_choice, enum.Enum):
            if simulator_choice.name.lower() == "ode":
                return ODESystem(graph=deviation_graph).unchanging_species(*unchanging_species)
            elif simulator_choice.name.lower() == "stochastic":
                return StochasticSystem(graph=deviation_graph).unchanging_species(*unchanging_species)
        else:
            return None


def show_plots(*args, **kwargs):
    SimulationOutput.show(block=True, *args, **kwargs)
