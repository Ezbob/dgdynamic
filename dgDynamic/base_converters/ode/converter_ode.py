"""
This module contains stuff relevant for all converters
"""
from io import StringIO
from typing import Tuple
from string import Template
from dgDynamic.utils.project_utils import log_it
from itertools import chain


class DefaultFunctionSymbols:
    add = '+'
    mul = '*'
    pow = '**'
    equation_separator = ','
    function_start = 'lambda t,y: ['
    function_end = ']'


def join_parameter_maps(*maps):
    return dict(chain(*maps))


@log_it
def substitute(generated_equations: Tuple[Tuple], substitution_map,
               extra_symbols=DefaultFunctionSymbols(), postprocessor=None) -> str:
    """
    This function is tasked with generating a function string from the SymPy description
    """
    with StringIO() as eq_system_steam:

        eq_system_steam.write(extra_symbols.function_start)

        for vertex_id, equation in generated_equations:
            template = Template(str(equation))
            if type(equation) is not int:
                eq_system_steam.write(template.safe_substitute(substitution_map))
                eq_system_steam.write("{} ".format(extra_symbols.equation_separator))
            else:
                eq_system_steam.write(template.template)
                eq_system_steam.write("{} ".format(extra_symbols.equation_separator))

        eq_system_steam.write(extra_symbols.function_end)
        eq_system_string = eq_system_steam.getvalue()
        return eq_system_string if postprocessor is None else postprocessor(eq_system_string)
