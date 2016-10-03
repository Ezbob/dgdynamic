"""
This module contains stuff relevant for all converters
"""
from io import StringIO
from typing import Dict, Tuple
from ..mod_interface.ode_generator import AbstractOdeSystem


class DefaultFunctionSymbols:
    add = '+'
    mul = '*'
    pow = '**'
    equation_separator = ','
    function_start = 'lambda t,y: ['
    function_end = ']'


def _get_parameter_mappings(abstract_system: AbstractOdeSystem):
    """
    Maps from strings of reactions (such as 'A + C -> D') to it's reaction index
    :return:
    """
    for edge_index, edge in enumerate(abstract_system.graph.edges):
        with StringIO() as out:
            for index, source in enumerate(edge.sources):
                out.write(str(source.graph.name))
                if index < edge.numSources - 1:
                    out.write(' + ')
            out.write(' -> ')
            for index, target in enumerate(edge.targets):
                out.write(str(target.graph.name))
                if index < edge.numTargets - 1:
                    out.write(' + ')
            reaction = out.getvalue()
        yield reaction, edge_index


def get_parameter_map(abstract_system, parameter_substitutions=None):
    if parameter_substitutions is not None:
        assert len(parameter_substitutions) >= abstract_system.reaction_count
        if type(parameter_substitutions) is dict:
            translate_dictionary = dict(_get_parameter_mappings(abstract_system))
            parameter_map = {abstract_system.parameters[translate_dictionary[key]]: value
                             for key, value in parameter_substitutions.items()}
        else:
            parameter_map = {k: v for k, v in zip(abstract_system.parameters, parameter_substitutions)}
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
