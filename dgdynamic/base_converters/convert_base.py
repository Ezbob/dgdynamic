from ..utils.exceptions import InitialValueError
from .reaction_parser import abstract_mod_parser
from ..utils.project_utils import log_it


@log_it
def get_edge_rate_dict(deviation_graph, user_parameters: dict,
                       internal_parameters_map=None):
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

    if not isinstance(user_parameters, dict):
        raise TypeError("Invalid data type for rate parameter specification. Expected {} got {}."
                        .format(dict, type(user_parameters)))

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
                if len(hyper_edges) != len(rate):
                    raise ValueError("Expected {} rates, got {} for parameter {}"
                                     .format(len(hyper_edges), len(rate), edges_representation))

                for index, edge in enumerate(hyper_edges):
                    if index == 0:
                        yield from add_to_result(edge.id, rate['->'])
                    elif index == 1:
                        yield from add_to_result(edge.id, rate['<-'])
            elif '->' in rate and len(hyper_edges) == 1:
                for edge in hyper_edges:
                    yield from add_to_result(edge.id, rate['->'])
            else:
                raise InitialValueError("Not enough initial conditions given for parameter: {}"
                                        .format(edges_representation))
        else:
            raise InitialValueError("Unsupported type {} of initial condition for parameter: {} "
                                    .format(type(rate), edges_representation))



@log_it
def get_drain_rate_dict(internal_drains, user_drain_rates):
    """
    Sanitize the user drain input with this function
    :param internal_drains: from the simulator maps species symbol to drain symbols that needs to replaced
    :param user_drain_rates: user information, what the user inputs
    :return:
    """
    number_of_values = len(tuple(internal_drains.values())[0])
    if not user_drain_rates:
        # UPDATE: there are now four values instead of two
        for drain_symbols in internal_drains.values():
            in_offset, in_factor, out_offset, out_factor = drain_symbols
            yield in_offset.replace('$', ''), 0.0
            yield in_factor.replace('$', ''), 0.0
            yield out_offset.replace('$', ''), 0.0
            yield out_factor.replace('$', ''), 0.0
    else:
        def add_to_result(key, values):
            # using collections instead
            for value in values:
                if not isinstance(value, (int, float)):
                    raise TypeError("Expected {} or {} got {} for key {}".format(int, float, type(value), key))

            if key in internal_drains:
                assert len(internal_drains[key]) == len(values)
                for symbol, value in zip(internal_drains[key], values):
                    yield symbol.replace('$', ''), value
            else:
                raise TypeError("Vertex key not found in deviation graph: {}".format(key))

        for external_vertex, drain_symbols in internal_drains.items():
            rate_entry = user_drain_rates[external_vertex] if external_vertex in user_drain_rates else 0.0
            if isinstance(rate_entry, (float, int)):
                # we get a single number from the user, this is a shorthand for setting all
                yield from add_to_result(external_vertex, (rate_entry,) * number_of_values)
            elif isinstance(rate_entry, (tuple, set, list)):
                # we get a collection of numbers from the user
                yield from add_to_result(external_vertex, rate_entry)
            elif isinstance(rate_entry, dict):
                # we get a dictionary with members 'in' and 'out'
                if not ('in' in rate_entry or 'out' in rate_entry):
                    raise ValueError('Missing "in" or "out" keys for vertex key {}'.format(external_vertex))
                # put in default values
                values = [0.0] * number_of_values
                if 'in' in rate_entry:
                    assert isinstance(rate_entry['in'], dict), \
                        "Expected {} got {} for 'in' entry in drain parameter dictionary"\
                        .format(dict, type(rate_entry['in']))

                    values[0] = rate_entry['in']['constant'] if 'constant' in rate_entry['in'] else 0.0
                    values[1] = rate_entry['in']['factor'] if 'factor' in rate_entry['in'] else 0.0

                if 'out' in rate_entry:
                    assert isinstance(rate_entry['out'], dict), \
                        "Expected {} got {} for 'out' entry in drain parameter dictionary"\
                        .format(dict, type(rate_entry['out']))
                    values[2] = rate_entry['out']['constant'] if 'constant' in rate_entry['out'] else 0
                    values[3] = rate_entry['out']['factor'] if 'factor' in rate_entry['out'] else 0

                yield from add_to_result(external_vertex, values)


@log_it
def get_initial_values(initial_conditions, symbols):
    if isinstance(initial_conditions, (tuple, set, list)):
        return initial_conditions
    elif isinstance(initial_conditions, dict):
        translate_mapping = {val: index for index, val in enumerate(symbols)}
        results = [0] * len(translate_mapping)
        for key, value in initial_conditions.items():
            if key in translate_mapping:
                results[translate_mapping[key]] = value
        return results


def replacer(to_replace):
    if isinstance(to_replace, (list, tuple)):
        return tuple(item.replace('$', '') for item in to_replace)
    else:
        return to_replace.replace('$', '')
