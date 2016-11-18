from ..utils.exceptions import InitialValueError
from typing import Dict, Union
from .reaction_parser import abstract_mod_parser
from collections import defaultdict
from ..utils.project_utils import log_it


@log_it
def get_edge_rate_dict(deviation_graph, user_parameters, internal_parameters_map=None) \
        -> Dict[int, Union[float, int]]:
    """
    Get a dictionary with edge.ids as keys and their associated rates as values
    :param deviation_graph:
    :param user_parameters:
    :param internal_parameters_map:
    :return:
    """
    result = defaultdict(lambda: 0)

    def add_to_result(key, value):
        if isinstance(value, (int, float)):
            if internal_parameters_map is not None:
                result[internal_parameters_map[key]] = value
            else:
                result[key] = value
        else:
            raise TypeError("Type error for key {}; expected float or int".format(key))

    if isinstance(user_parameters, dict):
        for edges_representation, rate in user_parameters.items():
            hyper_edges = abstract_mod_parser(deviation_graph=deviation_graph, reaction=edges_representation).mod_edges
            if isinstance(rate, (int, float)):
                # rhs is a number and lhs is tuple of MØD edges
                for edge in hyper_edges:
                    add_to_result(edge.id, rate)
            elif isinstance(rate, (tuple, list, set)):
                # rhs is a iterable
                if len(rate) != len(hyper_edges):
                    raise ValueError("Expected {} rates, got {} for parameter {}"
                                     .format(len(edges_representation), len(rate), edges_representation))

                for edge, rate_val in zip(hyper_edges, rate):
                    add_to_result(edge.id, rate_val)

            elif isinstance(rate, dict):
                # right hand side is a dictionary of the form { '->': ..., '<-': ... } or { '<=>': ... }
                if '<=>' in rate:
                    for edge in hyper_edges:
                        add_to_result(edge.id, rate['<=>'])
                elif '->' in rate and '<-' in rate:
                    if len(rate) != len(hyper_edges):
                        raise ValueError("Expected {} rates, got {} for parameter {}"
                                         .format(len(edges_representation), len(rate), edges_representation))

                    for index, edge in enumerate(hyper_edges):
                        if index == 0:
                            add_to_result(edge.id, rate['->'])
                        elif index == 1:
                            add_to_result(edge.id, rate['<-'])
                else:
                    raise InitialValueError("Not enough initial conditions given for parameter: {}"
                                            .format(edges_representation))
            else:
                raise InitialValueError("Unsupported type {} of initial condition for parameter: {} "
                                        .format(type(rate), edges_representation))
    elif isinstance(user_parameters, (tuple, list, set)):
        # user parameters is just a iterable
        for index_rate, rate in enumerate(user_parameters):
            add_to_result(index_rate, rate)

    return result
