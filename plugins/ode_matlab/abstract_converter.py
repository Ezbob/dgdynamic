from mod_interface.ode_generator import *


class MatlabSymbols(DefaultFunctionSymbols):
    function_start = "@(t,y) ["
    function_end = "]"


def get_malab_lambda(abstract_ode_system):

    # Symbol -> vertex.id
    symbol_map = {v: k for k, v in abstract_ode_system.symbols.items()}

    # Parameter (also Symbol) -> parameter id
    parameter_map = {v: k for k, v in enumerate(abstract_ode_system.parameters)}

    for vertex_id, expr in abstract_ode_system.generate_equations():
        for item in sp.postorder_traversal(expr):
            if len(item.args) > 0:
                # print("arg {} func {}".format(item.args, item.func))
                for arg in item.args:
                    if arg.is_real:
                        pass
                        # print(float(arg))
                    if arg.is_Symbol:
                        try:
                            print("I came from rev {} ".format(rev[arg]))
                        except KeyError:
                            print("I came from rev1 {} ".format(rev1[arg]))
