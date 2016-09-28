from io import StringIO


class MatlabSymbols:
    function_start = "@(t,y) ["
    equation_separator = ";"
    function_end = "]"
    pow = "^"


def _postprocessor(function_string):
    return function_string.replace('**', MatlabSymbols.pow)


def get_malab_lambda(abstract_ode_system, parameter_substitutions=None):
    """
    Converts a sympy symbolic ODE system into a MatLab lambda function that can be integrated.
    :param abstract_ode_system: should be a legal AbstractOdeSystem instance
    :param parameter_substitutions: list/tuple of values that should be substituted
    :return: string, containing a anonymous MatLab function that can be integrated
    """
    # Parameter (also Symbol) -> parameter id
    if parameter_substitutions is not None:
        parameter_map = {k: v for k, v in zip(abstract_ode_system.parameters, parameter_substitutions)}
    else:
        parameter_map = None

    substitute_me = {value: "y({})".format(key + 1) for key, value in enumerate(abstract_ode_system.symbols.values())}

    with StringIO() as matlab_string:

        matlab_string.write(MatlabSymbols.function_start)
        generated_functions = abstract_ode_system.generate_equations()

        if parameter_map is None:
            for vertex_id, equation in generated_functions:
                matlab_string.write(str(equation.subs(substitute_me)))
                matlab_string.write("{} ".format(MatlabSymbols.equation_separator))
        else:
            for vertex_id, equation in generated_functions:
                matlab_string.write(str(equation.subs(substitute_me).subs(parameter_map)))
                matlab_string.write("{} ".format(MatlabSymbols.equation_separator))

        matlab_string.write(MatlabSymbols.function_end)
        return _postprocessor(matlab_string.getvalue())
