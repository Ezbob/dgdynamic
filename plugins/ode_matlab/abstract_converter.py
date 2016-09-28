from mod_interface.ode_generator import *
from io import StringIO


class MatlabSymbols:
    function_start = "@(t,y) ["
    equation_separator = ","
    function_end = "]"
    pow = ".^"


def get_malab_lambda(abstract_ode_system):

    # Parameter (also Symbol) -> parameter id
    parameter_map = {v: k for k, v in enumerate(abstract_ode_system.parameters)}

    substitute_me = {value: "y({})".format(key) for key, value in abstract_ode_system.symbols.items()}

    with StringIO() as matlab_string:
        matlab_string.write(MatlabSymbols.function_start)
        generated_functions = abstract_ode_system.generate_equations()

        for vertex_id, equation in generated_functions:
            matlab_string.write(str(equation.subs(substitute_me)))

            if vertex_id < len(generated_functions) - 1:
                matlab_string.write("{} ".format(MatlabSymbols.equation_separator))

        matlab_string.write(MatlabSymbols.function_end)
        return matlab_string.getvalue()

