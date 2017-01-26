import re
from io import StringIO
from dgDynamic.config.settings import config
import dgDynamic.base_converters.convert_base as convert_base


def generate_reactions(rate_law_dict, translate_dict=None):

    def edge_to_psc_edge(reaction_string):
        separator = " > "
        if "->" in reaction_string:
            left, _, right = str.partition(reaction_string, '->')
        elif "<=>" in reaction_string:
            left, _, right = str.partition(reaction_string, '<=>')
            separator = " = "
        else:
            raise ValueError("Not a reaction string")
        digit_matcher = re.compile("\d+")
        new_reaction = separator.join((left, right))
        for match in digit_matcher.finditer(new_reaction):
            new_reaction = new_reaction.replace(str(match), '{' + str(match) + '}')
        if translate_dict is not None:
            return ' '.join((translate_dict[symbol].replace('$', '')
                             if symbol in translate_dict else symbol
                             for symbol in new_reaction.split()))
        else:
            return new_reaction

    with StringIO() as str_out:
        for index, key in enumerate(rate_law_dict.keys()):
            str_out.write("R{}:\n".format(index))
            str_out.write("\t{}\n".format(edge_to_psc_edge(key)))
            rate_equation = rate_law_dict[key].__repr__()
            str_out.write("\t{}\n".format(rate_equation.replace('$', '')))

        return str_out.getvalue()


def generate_rates(rate_parameter_map):
    fixed_float_precision = config.getint('Simulation', 'FIXED_POINT_PRECISION')
    with StringIO() as str_out:
        for key, value in rate_parameter_map.items():
            str_out.write("{} = {:.{}f}\n".format(key, value, fixed_float_precision))
        return str_out.getvalue()


def generate_initial_conditions(initial_values_map):
    with StringIO() as str_out:
        for key, value in initial_values_map.items():
            str_out.write("{} = {}\n".format(key, value))
        return str_out.getvalue()


def generate_drains(drain_value_map, internal_drain_dict, internal_symbol_dict, ignored):

    outgoing_drains = dict()
    ingoing_drains = dict()

    for original_symbol, drains in internal_drain_dict.items():
        internal_symbol = convert_base.replacer(internal_symbol_dict[original_symbol])
        r = convert_base.replacer
        ingoing_drains[internal_symbol] = drain_value_map[r(drains[0])], drain_value_map[r(drains[1])]
        outgoing_drains[internal_symbol] = drain_value_map[r(drains[2])], drain_value_map[r(drains[3])]

    with StringIO() as str_out:
        for external_symbol, internal_symbol in internal_symbol_dict.items():
            internal_symbol = internal_symbol.replace('$', '')
            reaction_number = 0
            outgoing_offset, outgoing_factor = outgoing_drains[internal_symbol]

            if int(outgoing_offset) != 0 or outgoing_factor != 0.0:
                str_out.write('D{0}:\n\t{1} > $pool\n\t{2} * {1} + {3}\n'
                              .format(reaction_number, internal_symbol, outgoing_factor, int(outgoing_offset)))
                reaction_number += 1

            ingoing_offset, ingoing_factor = ingoing_drains[internal_symbol]
            if int(ingoing_offset) != 0 or ingoing_factor != 0.0:
                str_out.write('D{0}:\n\t$pool > {1}\n\t{2} * {1} + {3}\n'
                              .format(reaction_number, internal_symbol, ingoing_factor, int(ingoing_offset)))
                reaction_number += 1

        result = str_out.getvalue()
        return result


def generate_fixed_species(ignored_species, internal_symbol_map):
    if len(ignored_species) > 0:
        with StringIO() as str_out:
            str_out.write('FIX: ')
            for symbol, _ in ignored_species:
                str_out.write('{} '.format(convert_base.replacer(internal_symbol_map[symbol])))
            str_out.write('\n')
            return str_out.getvalue()
    return ''
