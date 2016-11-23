from dgDynamic.simulators.ode_simulator import ODESystem
from .converter_ode import substitute, join_parameter_maps
from ..convert_base import get_edge_rate_dict


def get_scipy_lambda(abstract_system: ODESystem, parameter_substitutions=None):

    parameter_map = get_edge_rate_dict(deviation_graph=abstract_system.graph,
                                       user_parameters=parameter_substitutions,
                                       internal_parameters_map=abstract_system.parameters)

    rate_substitutes = {value.replace('$', ''): 'y[{}]'.format(key)
                        for key, value in enumerate(abstract_system.symbols_internal)}

    return substitute(abstract_system.generate_equations(),
                      substitution_map=join_parameter_maps(parameter_map.items(), rate_substitutes.items()))
