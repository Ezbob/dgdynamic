from io import StringIO
from dgDynamic.simulators.stochastic_pi_simulator import pretty_print_dict


def get_parameters(stochastic_system, parameter_substitutions=None):

    if isinstance(parameter_substitutions, dict):
        pass
    elif isinstance(parameter_substitutions, (tuple, list)):
        pass


def get_initial_values(stochastic_system, parameter_substitutions=None):
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
