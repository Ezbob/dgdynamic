from dgDynamic.simulators.ode_simulator import ODESystem
from .converter_ode import substitute, join_parameter_maps
from ..convert_base import get_edge_rate_dict, get_drain_rate_dict


def get_scipy_lambda(simulator: ODESystem, parameter_substitutions, drain_substitutions):

    parameter_map = get_edge_rate_dict(deviation_graph=simulator.graph, user_parameters=parameter_substitutions,
                                       internal_parameters_map=simulator.parameters)

    rate_map = ((value.replace('$', ''), 'y[{}]'.format(index)) for index, value in enumerate(simulator.symbols_internal))

    drain = get_drain_rate_dict(simulator.internal_drain_dict, drain_substitutions)

    return substitute(simulator.generate_equations(),
                      substitution_map=join_parameter_maps(parameter_map, rate_map, drain))
