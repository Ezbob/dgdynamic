from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.simulators.stochastic_pi_simulator import StochasticPiSystem


def dgDynamicSim(graph, simulator_choice="ode"):
    if simulator_choice.strip().lower() == "ode":
        return ODESystem(graph=graph)
    elif simulator_choice.strip().lower() == "spim":
        return StochasticPiSystem(graph=graph)

