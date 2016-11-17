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
        if internal_parameters_map is not None:
            result[internal_parameters_map[key]] = value
        else:
            result[key] = value

    if isinstance(user_parameters, dict):
        for reaction_string, rate in user_parameters.items():
            parsed_edges = reaction_parser_function(reaction_string)
            if isinstance(rate, (int, float)):
                if isinstance(parsed_edges, tuple):
                    for parsed_edge in parsed_edges:
                        add_to_result(parsed_edge.id, rate)
                else:
                    add_to_result(parsed_edges.id, rate)
            elif isinstance(rate, (tuple, list, set)):
                if isinstance(parsed_edges, tuple):
                    if len(rate) < len(parsed_edges):
                        raise InitialValueError("Not enough initial conditions given for reaction: {}"
                                                .format(reaction_string))
                    for parsed_edge, rate_item in zip(parsed_edges, rate):
                        add_to_result(parsed_edge, rate_item)
                else:
                    raise InitialValueError("Multivalued initial condition given for reaction: {}"
                                            .format(reaction_string))
            elif isinstance(rate, dict):
                if isinstance(parsed_edges, tuple):
                    if '<=>' in rate:
                        for parsed_edge in parsed_edges:
                            add_to_result(parsed_edge.id, rate['<=>'])
                    elif '->' in rate and '<-' in rate:
                        add_to_result(parsed_edges[0].id, rate['->'])
                        add_to_result(parsed_edges[1].id, rate['<-'])
                    else:
                        raise InitialValueError("Not enough initial conditions given for reaction: {}"
                                                .format(reaction_string))
                else:
                    raise InitialValueError("Multivalued initial condition given for reaction: {}"
                                            .format(reaction_string))
            else:
                raise InitialValueError("Unsupported type {} of initial condition for reaction: {} "
                                        .format(type(rate), reaction_string))
    elif isinstance(user_parameters, (tuple, list, set)):
        for index_rate, rate in enumerate(user_parameters):
            add_to_result(index_rate, rate)

    return result
