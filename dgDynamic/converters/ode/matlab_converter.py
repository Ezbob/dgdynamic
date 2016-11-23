from dgDynamic.simulators.ode_simulator import ODESystem
from .converter_ode import DefaultFunctionSymbols, substitute, join_parameter_maps
from ..convert_base import get_edge_rate_dict, get_drain_rate_dict


class MatlabSymbols(DefaultFunctionSymbols):
    function_start = "@(t,y) ["
    equation_separator = ";"
    function_end = "]"
    pow = "^"


def _postprocessor(function_string: str):
    return function_string.replace('**', MatlabSymbols.pow)


def get_matlab_lambda(simulator: ODESystem, parameter_substitutions=None, drain_substitutions=None):
    """
    Converts a sympy symbolic ODE system into a MatLab lambda function that can be integrated.
    """
    parameter_map = get_edge_rate_dict(deviation_graph=simulator.graph,
                                       user_parameters=parameter_substitutions,
                                       internal_parameters_map=simulator.parameters)

    rate_map = ((value.replace('$', ''), 'y({})'.format(index + 1))
                for index, value in enumerate(simulator.symbols_internal))

    drain = get_drain_rate_dict(simulator.internal_drain_dict, drain_substitutions)

    return substitute(simulator.generate_equations(),
                      substitution_map=join_parameter_maps(parameter_map, rate_map, drain),
                      extra_symbols=MatlabSymbols(), postprocessor=_postprocessor)
