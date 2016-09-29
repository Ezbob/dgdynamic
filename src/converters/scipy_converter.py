import sympy as sp
from .converter import substitute


def _postprocessor(string_input):
    return eval(string_input)


def get_scipy_lambda(abstract_system, parameter_substitutions=None):

    if parameter_substitutions is not None:
        assert len(parameter_substitutions) >= abstract_system.reaction_count
        parameter_map = {k: v for k, v in zip(abstract_system.parameters, parameter_substitutions)}
    else:
        parameter_map = None

    substitute_me = {value: sp.Indexed('y', key) for key, value in enumerate(abstract_system.symbols.values())}

    return substitute(abstract_system.generate_equations(), parameter_map, substitute_me, postprocessor=_postprocessor)
