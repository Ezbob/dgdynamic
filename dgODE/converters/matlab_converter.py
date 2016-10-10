from dgODE.ode_generator import dgODESystem
from .converter import DefaultFunctionSymbols, substitute, get_parameter_map
import sympy as sp


class MatlabSymbols(DefaultFunctionSymbols):
    function_start = "@(t,y) ["
    equation_separator = ";"
    function_end = "]"
    pow = "^"


def _postprocessor(function_string: str):
    return function_string.replace('**', MatlabSymbols.pow)


def get_matlab_lambda(abstract_ode_system: dgODESystem, parameter_substitutions=None):
    """
    Converts a sympy symbolic ODE system into a MatLab lambda function that can be integrated.
    :param abstract_ode_system: should be a legal AbstractOdeSystem instance
    :param parameter_substitutions: list/tuple of values that should be substituted
    :return: string, containing a anonymous MatLab function that can be integrated
    """
    parameter_map = get_parameter_map(abstract_ode_system, parameter_substitutions)

    substitute_me = {value: sp.Symbol("y({})".format(key + 1)) for key, value in enumerate(abstract_ode_system.symbols.values())}

    return substitute(abstract_ode_system.generate_equations(), parameter_map, symbol_map=substitute_me,
                      extra_symbols=MatlabSymbols(), postprocessor=_postprocessor)
