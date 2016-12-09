import dgDynamic.choices as choices
from .mod_dynamics import dgDynamicSim, HyperGraph
import typing as tp
import enum


def plugin_from_parameters(plugin_name: tp.Union[enum.Enum, str], rate_parameters: dict, *unchanging_species):

    if isinstance(plugin_name, str):
        if any(plugin_name.strip().lower() == member for member in choices.SupportedOdePlugins):
            sim_mode = choices.SimulatorModes.ODE
        elif any(plugin_name.strip().lower() == member for member in choices.SupportedOdePlugins):
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
    plugin = sim.get_plugin(plugin_name)
    plugin.parameters = rate_parameters
    return plugin
