"""
This module contains stuff relevant for all converters
"""
import sympy as sp
from io import StringIO
from typing import Tuple
from dgDynamic.utils.project_utils import log_it


class DefaultFunctionSymbols:
    add = '+'
    mul = '*'
    pow = '**'
    equation_separator = ','
    function_start = 'lambda t,y: ['
    function_end = ']'


def get_initial_values(initial_conditions, symbols):
    if isinstance(initial_conditions, (tuple, list)):
        return initial_conditions
    elif isinstance(initial_conditions, dict):
        translate_mapping = {val: index for index, val in enumerate(symbols)}
        results = [0] * len(translate_mapping)
        for key, value in initial_conditions.items():
            if key in translate_mapping:
                results[translate_mapping[key]] = value
        return results


@log_it
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
                    eq_system_steam.write(str(equation.xreplace(symbol_map)))
                    eq_system_steam.write("{} ".format(extra_symbols.equation_separator))
                else:
                    eq_system_steam.write(str(equation))
                    eq_system_steam.write("{} ".format(extra_symbols.equation_separator))
        else:
            for vertex_id, equation in generated_equations:
                if type(equation) is not int:
                    eq_system_steam.write(str(equation.xreplace(symbol_map).xreplace(parameter_map)))
                    eq_system_steam.write("{} ".format(extra_symbols.equation_separator))
                else:
                    eq_system_steam.write(str(equation))
                    eq_system_steam.write("{} ".format(extra_symbols.equation_separator))

        eq_system_steam.write(extra_symbols.function_end)
        eq_system_string = eq_system_steam.getvalue()
        return eq_system_string if postprocessor is None else postprocessor(eq_system_string)