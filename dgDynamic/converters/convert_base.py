from ..utils.exceptions import InitialValueError
from typing import Union, Optional, Generator, Tuple
from .reaction_parser import abstract_mod_parser
from ..utils.project_utils import log_it
import dgDynamic.utils.typehints as th


@log_it
def get_edge_rate_dict(deviation_graph: th.MødDeviationGraph,
                       user_parameters: Union[tuple, set, dict, list],
                       internal_parameters_map: Optional[dict]=None):
    """
    Get a dictionary with edge.ids as keys and their associated rates as values
    :param deviation_graph:
    :param user_parameters:
    :param internal_parameters_map:
    :return:
    """

    def add_to_result(key, value):
        if isinstance(value, (int, float)):
            if internal_parameters_map is not None:
                param = internal_parameters_map[key].replace('$', '')
                yield param, value
            else:
                yield key, value
        else:
            raise TypeError("Type error for key {}; expected float or int".format(key))

    if isinstance(user_parameters, dict):
        for edges_representation, rate in user_parameters.items():
            hyper_edges = abstract_mod_parser(deviation_graph=deviation_graph, reaction=edges_representation).mod_edges
            if isinstance(rate, (int, float)):
                # rhs is a number and lhs is tuple of MØD edges
                for edge in hyper_edges:
                    yield from add_to_result(edge.id, rate)
            elif isinstance(rate, (tuple, list, set)):
                # rhs is a iterable
                if len(rate) != len(hyper_edges):
                    raise ValueError("Expected {} rates, got {} for parameter {}"
                                     .format(len(edges_representation), len(rate), edges_representation))

                for edge, rate_val in zip(hyper_edges, rate):
                    yield from add_to_result(edge.id, rate_val)

            elif isinstance(rate, dict):
                # right hand side is a dictionary of the form { '->': ..., '<-': ... } or { '<=>': ... }
                if '<=>' in rate:
                    for edge in hyper_edges:
                        yield from add_to_result(edge.id, rate['<=>'])
                elif '->' in rate and '<-' in rate:
                    if len(rate) != len(hyper_edges):
                        raise ValueError("Expected {} rates, got {} for parameter {}"
                                         .format(len(edges_representation), len(rate), edges_representation))

                    for index, edge in enumerate(hyper_edges):
                        if index == 0:
                            yield from add_to_result(edge.id, rate['->'])
                        elif index == 1:
                            yield from add_to_result(edge.id, rate['<-'])
                else:
                    raise InitialValueError("Not enough initial conditions given for parameter: {}"
                                            .format(edges_representation))
            else:
                raise InitialValueError("Unsupported type {} of initial condition for parameter: {} "
                                        .format(type(rate), edges_representation))
    elif isinstance(user_parameters, (tuple, list, set)):
        # user parameters is just a iterable
        for index_rate, rate in enumerate(user_parameters):
            yield from add_to_result(index_rate, rate)


@log_it
def get_drain_rate_dict(internal_drains: dict, user_drain_rates: dict):

    if not user_drain_rates:
        for drain_symbols in internal_drains.values():
            in_symbol, out_symbol = drain_symbols
            yield in_symbol.replace('$', ''), 0
            yield out_symbol.replace('$', ''), 0
    else:
        def add_to_result(key, in_value, out_value):
            if isinstance(in_value, (int, float)) and isinstance(out_value, (int, float)):
                if key in internal_drains:
                    in_sym, out_sym = internal_drains[key]
                    yield in_sym.replace('$', ''), in_value
                    yield out_sym.replace('$', ''), out_value
                else:
                    raise TypeError("Vertex key not found in deviation graph: {}".format(key))
            else:
                raise TypeError("Type error for values mapped to key {}; expected float or int value".format(key))

        for vertex, rate in user_drain_rates.items():
            if isinstance(rate, (float, int)):
                yield from add_to_result(vertex, rate, rate)
            elif isinstance(rate, (tuple, set, list)):
                if len(rate) < 2:
                    raise ValueError('Not enough diffusion rates given for key: {}'.format(vertex))
                in_val, out_val = rate[:2]
                yield from add_to_result(vertex, in_val, out_val)
            elif isinstance(rate, dict):
                if 'in' in rate and 'out' in rate:
                    yield from add_to_result(vertex, rate['in'], rate['out'])
                else:
                    raise ValueError('Missing "in" and "out" keys for vertex key {}'.format(vertex))


@log_it
def get_initial_values(initial_conditions, symbols) -> Union[set, tuple, list]:
    if isinstance(initial_conditions, (tuple, set, list)):
        return initial_conditions
    elif isinstance(initial_conditions, dict):
        translate_mapping = {val: index for index, val in enumerate(symbols)}
        results = [0] * len(translate_mapping)
        for key, value in initial_conditions.items():
            if key in translate_mapping:
                results[translate_mapping[key]] = value
        return results
