import mod
from io import StringIO


class Channel:
    solutions = ()

    def __init__(self, rate_id, is_input, channel_edge=None, is_decay=False):
        self.channel_edge = channel_edge
        self.rate_id = rate_id
        self.is_input = is_input
        self.is_decay = is_decay

    def __repr__(self):
        if self.is_decay:
            return "<channel τ@r{};{}>".format(self.rate_id, self.solutions)
        elif self.is_input:
            return "<channel ?c{0}@r{0};{1}>".format(self.rate_id, self.solutions)
        else:
            return "<channel !c{0}@r{0};{1}>".format(self.rate_id, self.solutions)

    def add_reagents(self, reagents):
        for target in reagents:
            if isinstance(target, mod.mod_.DGVertex):
                self.solutions += (target.graph.name,)
            else:
                self.solutions += (target,)
        return self


def generate_automata_code(spi_system):
    channel_dict = spi_system.generate_channels()
    symbols = spi_system.symbols
    process_prefix = "_"

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
