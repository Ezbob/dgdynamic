from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.simulators.stochastic_pi_simulator import StochasticPiSystem
import typing as tp
from .structures import HyperGraph
from dgDynamic.output import SimulationOutput
import enum
import mod


class dgDynamicSim:
    def __new__(cls, derivation_graph: mod.DG, simulator_choice: tp.Union[str, enum.Enum]="ode", unchanging_species:
                tp.Union[str, tuple]=()) -> tp.Optional[tp.Union[ODESystem, StochasticPiSystem]]:
        deviation_graph = derivation_graph if isinstance(derivation_graph, HyperGraph) else HyperGraph(derivation_graph)
        if isinstance(simulator_choice, str):
            if simulator_choice.strip().lower() == "ode":
                return ODESystem(graph=deviation_graph).unchanging_species(*unchanging_species)
            elif simulator_choice.strip().lower() == "stochastic":
                return StochasticPiSystem(graph=deviation_graph).unchanging_species(*unchanging_species)
        elif isinstance(simulator_choice, enum.Enum):
            if simulator_choice.name.lower() == "ode":
                return ODESystem(graph=deviation_graph).unchanging_species(*unchanging_species)
            elif simulator_choice.name.lower() == "stochastic":
                return StochasticPiSystem(graph=deviation_graph).unchanging_species(*unchanging_species)
        else:
            return None


def show_plots(*args, **kwargs):
    SimulationOutput.show(*args, **kwargs)
