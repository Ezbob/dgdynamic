import sympy as sp
from dgDynamic.simulators.ode_simulator import ODESystem
from .converter_ode import DefaultFunctionSymbols, substitute
from ..convert_base import get_edge_rate_dict


class MatlabSymbols(DefaultFunctionSymbols):
    function_start = "@(t,y) ["
    equation_separator = ";"
    function_end = "]"
    pow = "^"


def _postprocessor(function_string: str):
    return function_string.replace('**', MatlabSymbols.pow)


def get_matlab_lambda(abstract_ode_system: ODESystem, parameter_substitutions=None):
    """
    Converts a sympy symbolic ODE system into a MatLab lambda function that can be integrated.
    :param abstract_ode_system: should be a legal AbstractOdeSystem instance
    :param parameter_substitutions: list/tuple of values that should be substituted
    :return: string, containing a anonymous MatLab function that can be integrated
    """
    parameter_map = get_edge_rate_dict(deviation_graph=abstract_ode_system.graph,
                                       user_parameters=parameter_substitutions,
                                       internal_parameters_map=abstract_ode_system.parameters)

    substitute_me = {sp.Symbol(value): sp.Symbol("y({})".format(key + 1))
                     for key, value in enumerate(abstract_ode_system.symbols)}

    return substitute(abstract_ode_system.generate_equations(), parameter_map, symbol_map=substitute_me,
                      extra_symbols=MatlabSymbols(), postprocessor=_postprocessor)
