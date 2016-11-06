import sympy as sp
from dgDynamic.simulators.ode_simulator import ODESystem
from .converter_ode import substitute
from ..convert_base import get_edge_rate_dict


def get_scipy_lambda(abstract_system: ODESystem, parameter_substitutions=None):

    parameter_map = get_edge_rate_dict(reaction_parser_function=abstract_system.parse_abstract_reaction,
                                       user_parameters=parameter_substitutions,
                                       internal_parameters_map=abstract_system.parameters)

    substitute_me = {value: sp.Indexed('y', key) for key, value in enumerate(abstract_system.symbols.values())}

    return substitute(abstract_system.generate_equations(), parameter_map, substitute_me)
