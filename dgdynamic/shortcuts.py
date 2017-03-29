import dgdynamic.choices as choices
from .mod_dynamics import dgDynamicSim, HyperGraph
import enum


def plugin_from_parameters(plugin_name, rate_parameters, *unchanging_species):

    if isinstance(plugin_name, str):
        if any(plugin_name.strip().lower() == member.name.lower() for member in choices.SupportedOdePlugins):
            sim_mode = choices.SimulatorModes.ODE
        elif any(plugin_name.strip().lower() == member.name.lower() for member in choices.SupportedStochasticPlugins):
            sim_mode = choices.SimulatorModes.Stochastic
        else:
            return
    elif isinstance(plugin_name, enum.Enum):
        if plugin_name in choices.SupportedOdePlugins:
            sim_mode = choices.SimulatorModes.ODE
        elif plugin_name in choices.SupportedStochasticPlugins:
            sim_mode = choices.SimulatorModes.Stochastic
        else:
            return

    hyper_g = HyperGraph.from_abstract(*rate_parameters.keys())
    sim = dgDynamicSim(hyper_g, simulator_choice=sim_mode, unchanging_species=unchanging_species)
    return sim.get_plugin(plugin_name)
