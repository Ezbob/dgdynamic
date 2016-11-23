from dgDynamic.simulators.ode_simulator import ODESystem
from .converter_ode import substitute, join_parameter_maps
from ..convert_base import get_edge_rate_dict, get_drain_rate_dict


def get_scipy_lambda(simulator: ODESystem, parameter_substitutions, drain_substitutions):

    parameter_map = get_edge_rate_dict(deviation_graph=simulator.graph,
                                       user_parameters=parameter_substitutions,
                                       internal_parameters_map=simulator.parameters)

    rate_map = {value.replace('$', ''): 'y[{}]'.format(key)
                for key, value in enumerate(simulator.symbols_internal)}

    internal_mappings = simulator.internal_drain_dict
    drain = {}
    for key, val in get_drain_rate_dict(simulator.symbols, drain_substitutions).items():
        in_rate, out_rate = val
        in_sym, out_sym = internal_mappings[key]
        drain[in_sym.replace('$', '')], drain[out_sym.replace('$', '')] = in_rate, out_rate

    return substitute(simulator.generate_equations(),
                      substitution_map=join_parameter_maps(parameter_map.items(), rate_map.items(), drain.items()))
