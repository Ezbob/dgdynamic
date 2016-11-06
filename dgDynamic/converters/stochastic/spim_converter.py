from io import StringIO
from dgDynamic.utils.exceptions import InitialValueError
from dgDynamic.simulators.stochastic_pi_simulator import pretty_print_dict
from collections import defaultdict


def get_preamble(sample_range, draw_automata=False) -> str:
    pass


def _get_edge_rate_dict(stochastic_system, parameters):
    result = dict()
    for reaction_string, rate in parameters.items():
        parsed_edges = stochastic_system.parse_abstract_reaction(reaction_string)
        if isinstance(rate, (int, float)):
            if isinstance(parsed_edges, tuple):
                for parsed_edge in parsed_edges:
                    result[parsed_edge.id] = rate
            else:
                result[parsed_edges.id] = rate
        elif isinstance(rate, (tuple, list, set)):
            if isinstance(parsed_edges, tuple):
                for parsed_edge, rate_item in zip(parsed_edges, rate):
                    result[parsed_edge.id] = rate_item
            else:
                raise InitialValueError("Multivalued initial condition given for reaction: {}".format(reaction_string))
        elif isinstance(rate, dict):
            if isinstance(parsed_edges, tuple):
                if '<=>' in rate:
                    for parsed_edge in parsed_edges:
                        result[parsed_edge.id] = rate['<=>']
                elif '->' in rate and '<-' in rate:
                    result[parsed_edges[0].id] = rate['->']
                    result[parsed_edges[1].id] = rate['<-']
                else:
                    raise InitialValueError("Not enough initial conditions given for reaction: {}"
                                            .format(reaction_string))
            else:
                raise InitialValueError("Multivalued initial condition given for reaction: {}".format(reaction_string))
        else:
            raise InitialValueError("Unsupported type of initial condition for reaction: {} ".format(reaction_string))
    return result


def get_parameters(stochastic_system, channel_dict, parameters=None) -> str:
    if isinstance(parameters, dict):
        edge_rate_dict = _get_edge_rate_dict(stochastic_system, parameters)
        print(edge_rate_dict)

        already_seen = dict()
        with StringIO() as str_out:
            for channel_tuple in channel_dict.values():
                for channel in channel_tuple:
                    rate = 0.0
                    if channel.channel_edge.id in edge_rate_dict:
                        rate = edge_rate_dict[channel.channel_edge.id]
                    if channel.rate_id not in already_seen:
                        if channel.is_decay:
                            str_out.write("val r{} = {}\n".format(channel.rate_id, rate))
                        else:
                            str_out.write("new chan{}@{} : chan()\n".format(channel.rate_id, rate))
                        already_seen[channel.rate_id] = True
            return str_out.getvalue()
    elif isinstance(parameters, (tuple, list)):
        pass


def get_initial_values(symbols, initial_conditions=None) -> str:
    if isinstance(initial_conditions, dict):
        pass
    elif isinstance(initial_conditions, (tuple, list)):
        pass


def generate_automata_code(channel_dict, symbols, process_prefix="_"):

    def generate_channel(stream, channel):

        def channel_solutions():
            if len(channel.solutions) > 1:
                stream.write("( ")
                for index_solution, solution in enumerate(channel.solutions):
                    stream.write("{}{}()".format(process_prefix, solution))
                    if index_solution < len(channel.solutions) - 1:
                        stream.write(' | ')
                stream.write(" )")
            elif len(channel.solutions) == 1:
                stream.write("{}{}()".format(process_prefix, channel.solutions[0]))
            else:
                stream.write("()")

        if channel.is_decay:
            stream.write('delay@r{}; '.format(channel.rate_id))
            channel_solutions()
        else:
            if channel.is_input:
                stream.write('?chan{}; '.format(channel.rate_id))
                channel_solutions()
            else:
                stream.write('!chan{}; '.format(channel.rate_id))
                channel_solutions()

    with StringIO() as str_result:
        str_result.write('let ')
        for symbol_index, symbol in enumerate(symbols):
            str_result.write("{}{}() = ".format(process_prefix, symbol))

            if symbol in channel_dict:
                current_channels = channel_dict[symbol]
                if len(current_channels) == 1:
                    generate_channel(str_result, current_channels[0])
                elif len(current_channels) > 1:
                    str_result.write('do ')
                    for channel_index, channel in enumerate(current_channels):
                        generate_channel(str_result, channel)
                        if len(current_channels) - 1 > channel_index:
                            str_result.write(' or ')
            else:
                str_result.write('()')

            if symbol_index < len(symbols) - 1:
                str_result.write('\nand ')
        return str_result.getvalue()
