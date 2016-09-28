from io import StringIO
import sympy as sp
from .converter import substitutioner


def get_scipy_lambda(abstract_system, parameter_substitutions=None):

    if parameter_substitutions is not None:
        assert len(parameter_substitutions) >= len(abstract_system.symbols)
        parameter_map = {k: v for k, v in zip(abstract_system.parameters, parameter_substitutions)}
    else:
        parameter_map = None

    substitute_me = {value: sp.Indexed('y', key) for key, value in enumerate(abstract_system.symbols.values())}

    return substitutioner(abstract_system.generate_equations(), parameter_map, substitute_me)
