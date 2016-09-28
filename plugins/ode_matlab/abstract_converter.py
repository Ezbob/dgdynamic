from mod_interface.ode_generator import *
from io import StringIO


class MatlabSymbols(DefaultFunctionSymbols):
    function_start = "@(t,y) ["
    equation_separator = ","
    function_end = "]"
    pow = ".^"


def get_malab_lambda(abstract_ode_system):

    # Symbol -> vertex.id
    symbol_map = {v: k for k, v in abstract_ode_system.symbols.items()}

    # Parameter (also Symbol) -> parameter id
    parameter_map = {v: k for k, v in enumerate(abstract_ode_system.parameters)}

    with StringIO as strout:
        strout.write(MatlabSymbols.function_start)
        for vertex_id, expr in abstract_ode_system.generate_equations():
            for item in sp.postorder_traversal(expr):
                if len(item.args) > 0:
                    # print("arg {} func {}".format(item.args, item.func))
                    for arg in item.args:
                        if arg.is_real:
                            strout.write(float(arg))
                        if arg.is_Symbol:
                            try:
                                strout.write("y({})".format(symbol_map[arg]))
                            except KeyError:
                                strout.write("k{}".format(parameter_map[arg]))
            strout.write(MatlabSymbols.equation_separator)
        strout.write(MatlabSymbols.function_end)
        return strout.getvalue()
