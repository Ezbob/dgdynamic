from ..utils.exceptions import InitialValueError
from typing import Dict, Union
from collections import defaultdict
from ..utils.project_utils import log_it

# TODO make this independent of the parse, OR make the parser independent of this function OR bypass it by using a sub graph with edges and vertices in the hyper graph
@log_it
def get_edge_rate_dict(user_parameters, internal_parameters_map=None) \
        -> Dict[int, Union[float, int]]:
    """
    Get a dictionary with edge.ids as keys and their associated rates as values
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
        for mod_edges, rate in user_parameters.items():
            if isinstance(rate, (int, float)):
                # rhs is a number and lhs is tuple of MØD edges
                for edge in mod_edges:
                    add_to_result(edge.id, rate)
            elif isinstance(rate, (tuple, list, set)):
                # rhs is a iterable
                if len(rate) != len(mod_edges):
                    raise ValueError("Expected {} rates, got {} for parameter {}"
                                     .format(len(mod_edges), len(rate), mod_edges))

            elif isinstance(rate, dict):
                # right hand side is a dictionary of the form { '->': ..., '<-': ... } or { '<=>': ... }
                if '<=>' in rate:
                    for edge in mod_edges[-1]:
                        add_to_result(edge.id, rate['<=>'])
                elif '->' in rate and '<-' in rate:
                    for index, edge in enumerate(mod_edges):
                        if index == 0:
                            add_to_result(edge.id, rate['->'])
                        elif index == 1:
                            add_to_result(edge.id, rate['<-'])
                else:
                    raise InitialValueError("Not enough initial conditions given for parameter: {}"
                                            .format(mod_edges))
            else:
                raise InitialValueError("Unsupported type {} of initial condition for parameter: {} "
                                        .format(type(rate), mod_edges))
    elif isinstance(user_parameters, (tuple, list, set)):
        # user parameters is just a iterable
        for index_rate, rate in enumerate(user_parameters):
            add_to_result(index_rate, rate)

    return result
