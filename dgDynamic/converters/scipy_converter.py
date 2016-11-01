import sympy as sp

from dgDynamic.simulators.ode_simulator import ODESystem
from .converter import substitute, get_parameter_map


def get_scipy_lambda(abstract_system: ODESystem, parameter_substitutions=None):

    parameter_map = get_parameter_map(abstract_system, parameter_substitutions)

    substitute_me = {value: sp.Indexed('y', key) for key, value in enumerate(abstract_system.symbols.values())}

    return substitute(abstract_system.generate_equations(), parameter_map, substitute_me)
