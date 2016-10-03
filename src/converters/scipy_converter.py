import sympy as sp
from .converter import substitute, get_parameter_map
from ..mod_interface.ode_generator import AbstractOdeSystem


def _postprocessor(string_input: str):
    return eval(string_input)


def get_scipy_lambda(abstract_system: AbstractOdeSystem, parameter_substitutions=None):

    parameter_map = get_parameter_map(abstract_system, parameter_substitutions)

    substitute_me = {value: sp.Indexed('y', key) for key, value in enumerate(abstract_system.symbols.values())}

    return substitute(abstract_system.generate_equations(), parameter_map, substitute_me, postprocessor=_postprocessor)
