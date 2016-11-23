from dgDynamic.simulators.ode_simulator import ODESystem
from .converter_ode import DefaultFunctionSymbols, substitute, join_parameter_maps
from ..convert_base import get_edge_rate_dict
from itertools import chain


class MatlabSymbols(DefaultFunctionSymbols):
    function_start = "@(t,y) ["
    equation_separator = ";"
    function_end = "]"
    pow = "^"


def _postprocessor(function_string: str):
    return function_string.replace('**', MatlabSymbols.pow)


def get_matlab_lambda(abstract_system: ODESystem, parameter_substitutions=None):
    """
    Converts a sympy symbolic ODE system into a MatLab lambda function that can be integrated.
    :param abstract_system: should be a legal AbstractOdeSystem instance
    :param parameter_substitutions: list/tuple of values that should be substituted
    :return: string, containing a anonymous MatLab function that can be integrated
    """
    parameter_map = get_edge_rate_dict(deviation_graph=abstract_system.graph,
                                       user_parameters=parameter_substitutions,
                                       internal_parameters_map=abstract_system.parameters)

    rate_substitutes = {value.replace('$', ''): "y({})".format(key + 1)
                        for key, value in enumerate(abstract_system.symbols_internal)}

    return substitute(abstract_system.generate_equations(),
                      substitution_map=join_parameter_maps(parameter_map.items(), rate_substitutes.items()),
                      extra_symbols=MatlabSymbols(), postprocessor=_postprocessor)
