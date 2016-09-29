from .converter import DefaultFunctionSymbols, substitute


class MatlabSymbols(DefaultFunctionSymbols):
    function_start = "@(t,y) ["
    equation_separator = ";"
    function_end = "]"
    pow = "^"


def _postprocessor(function_string):
    return function_string.replace('**', MatlabSymbols.pow)


def get_matlab_lambda(abstract_ode_system, parameter_substitutions=None):
    """
    Converts a sympy symbolic ODE system into a MatLab lambda function that can be integrated.
    :param abstract_ode_system: should be a legal AbstractOdeSystem instance
    :param parameter_substitutions: list/tuple of values that should be substituted
    :return: string, containing a anonymous MatLab function that can be integrated
    """
    # Parameter (also Symbol) -> parameter id
    if parameter_substitutions is not None:
        assert len(parameter_substitutions) >= abstract_ode_system.reaction_count
        parameter_map = {k: v for k, v in zip(abstract_ode_system.parameters, parameter_substitutions)}
    else:
        parameter_map = None

    substitute_me = {value: "y({})".format(key + 1) for key, value in enumerate(abstract_ode_system.symbols.values())}

    return substitute(abstract_ode_system.generate_equations(), parameter_map, symbol_map=substitute_me,
                      extra_symbols=MatlabSymbols(), postprocessor=_postprocessor)