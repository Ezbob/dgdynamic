"""
This module contains stuff relevant for all converters
"""
from io import StringIO
from typing import Dict, Tuple
from ..mod_interface.ode_generator import dgODESystem


class DefaultFunctionSymbols:
    add = '+'
    mul = '*'
    pow = '**'
    equation_separator = ','
    function_start = 'lambda t,y: ['
    function_end = ']'


def _handle_two_way_parameters(abstract_system, edge_tuple, parameter_value, reaction_string, result_dict):
    if not isinstance(parameter_value, (tuple, list, dict)):
        raise ValueError("Parameters for the two-way reaction {} was not a list or tuple or a "
                         "dictionary with '->' and '<-' as keys"
                         .format(reaction_string))
    if isinstance(parameter_value, (tuple, list)):
        for edge, parameter in zip(edge_tuple, parameter_value):
            result_dict[abstract_system.parameters[edge.id]] = parameter
    else:
        try:
            result_dict[abstract_system.parameters[edge_tuple[0].id]] = parameter_value['->']
            result_dict[abstract_system.parameters[edge_tuple[1].id]] = parameter_value['<-']
        except KeyError:
            raise KeyError("Two-way reactions keys not defined or understood")


def get_parameter_map(abstract_system: dgODESystem, parameter_substitutions=None):

    if parameter_substitutions is not None:

        if type(parameter_substitutions) is dict:
            # here the user uses a dictionary for parameter_subs with type: Dict[str, Union[Tuple[Real,Real], Real]]
            parameter_map = dict()
            for reaction_string, parameter_value in parameter_substitutions.items():
                edges = abstract_system.parse_abstract_reaction(reaction_string.strip())
                if type(edges) is tuple:
                    _handle_two_way_parameters(abstract_system=abstract_system, edge_tuple=edges,
                                               result_dict=parameter_map, reaction_string=reaction_string,
                                               parameter_value=parameter_value)
                else:
                    parameter_map[abstract_system.parameters[edges.id]] = parameter_value
        else:
            parameter_map = {k: v for k, v in zip(abstract_system.parameters.values(), parameter_substitutions)}
    else:
        parameter_map = None
    return parameter_map


def substitute(generated_equations: Tuple[Tuple], parameter_map: dict, symbol_map: dict,
               extra_symbols=DefaultFunctionSymbols(), postprocessor=None):
    """
    This function is tasked with generating a function string from the SymPy description
    :param generated_equations: equations from the AbstractOdeSystem
    :param parameter_map: what the different k-parameters should be substituted to
    :param symbol_map: new names for the symbols in the different equations
    :param extra_symbols: extra symbols for generating the functions from the equation(stuff such as function headers
     etc.)
    :param postprocessor: function to be called when the equations have been substituted and collected to a string
     ( f.x.: in the MatLab converter we use the processor function to replace the power operators from ** to ^ )
    :return:
    """
    with StringIO() as eq_system_steam:

        eq_system_steam.write(extra_symbols.function_start)

        if parameter_map is None:
            for vertex_id, equation in generated_equations:
                if type(equation) is not int:
                    eq_system_steam.write(str(equation.subs(symbol_map)))
                    eq_system_steam.write("{} ".format(extra_symbols.equation_separator))
                else:
                    eq_system_steam.write(str(equation))
                    eq_system_steam.write("{} ".format(extra_symbols.equation_separator))
        else:
            for vertex_id, equation in generated_equations:
                if type(equation) is not int:
                    eq_system_steam.write(str(equation.subs(symbol_map).subs(parameter_map)))
                    eq_system_steam.write("{} ".format(extra_symbols.equation_separator))
                else:
                    eq_system_steam.write(str(equation))
                    eq_system_steam.write("{} ".format(extra_symbols.equation_separator))

        eq_system_steam.write(extra_symbols.function_end)
        eq_system_string = eq_system_steam.getvalue()
        return eq_system_string if postprocessor is None else postprocessor(eq_system_string)
