from ..utils.exceptions import InitialValueError
from typing import Dict, Union
from collections import defaultdict
from ..utils.project_utils import log_it

# TODO make this independent of the parse, OR make the parser independent of this function OR bypass it by using a sub graph with edges and vertices in the hyper graph
@log_it
def get_edge_rate_dict(reaction_parser_function, user_parameters, internal_parameters_map=None) \
        -> Dict[int, Union[float, int]]:
    """
    Get a dictionary with edge.ids as keys and their associated rates as values
    :param reaction_parser_function:
    :param user_parameters:
    :param internal_parameters_map:
    :return:
    """
    result = defaultdict(lambda: 0)

    if not hasattr(reaction_parser_function, "__call__"):
        raise InitialValueError("Reaction parser function is not a callable")

    def add_to_result(key, value):
        if isinstance(value, (int, float)):
            if internal_parameters_map is not None:
                result[internal_parameters_map[key]] = value
            else:
                result[key] = value
        else:
            raise TypeError("Type error for key {}; expected float or int".format(key))

    if isinstance(user_parameters, dict):
        for key, rate in user_parameters.items():
            parsed_edges = reaction_parser_function(key)
            if isinstance(rate, (int, float)):
                # rhs is simply a number
                if isinstance(parsed_edges, tuple):
                    for parsed_edge in parsed_edges:
                        add_to_result(parsed_edge.id, rate)
                else:
                    add_to_result(parsed_edges.id, rate)
            elif isinstance(rate, (tuple, list, set)):
                # rhs is a iterable
                if isinstance(parsed_edges, tuple):
                    if len(rate) < len(parsed_edges):
                        raise InitialValueError("Not enough initial conditions given for reaction: {}".format(key))
                    for parsed_edge, rate_item in zip(parsed_edges, rate):
                        add_to_result(parsed_edge, rate_item)
                else:
                    raise InitialValueError("Multivalued initial condition given for reaction: {}"
                                            .format(key))
            elif isinstance(rate, dict):
                # right hand side is a dictionary of the form { '->': ..., '<-': ... } or { '<=>': ... }
                if isinstance(parsed_edges, tuple):
                    if '<=>' in rate:
                        for parsed_edge in parsed_edges:
                            add_to_result(parsed_edge.id, rate['<=>'])
                    elif '->' in rate and '<-' in rate:
                        add_to_result(parsed_edges[0].id, rate['->'])
                        add_to_result(parsed_edges[1].id, rate['<-'])
                    else:
                        raise InitialValueError("Not enough initial conditions given for reaction: {}"
                                                .format(key))
                else:
                    raise InitialValueError("Multivalued initial condition given for reaction: {}"
                                            .format(key))
            else:
                raise InitialValueError("Unsupported type {} of initial condition for reaction: {} "
                                        .format(type(rate), key))
    elif isinstance(user_parameters, (tuple, list, set)):
        # user parameters is just a iterable
        for index_rate, rate in enumerate(user_parameters):
            add_to_result(index_rate, rate)

    return result
