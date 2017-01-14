import re
from io import StringIO
from dgDynamic.config.settings import config
import dgDynamic.converters.convert_base as convert_base


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
            new_reaction = new_reaction.replace(match, '{' + match + '}')
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


def generate_drains(drain_value_map, internal_drain_dict, internal_symbol_dict):

    outgoing_drains = dict()
    ingoing_drains = dict()

    for original_symbol, drains in internal_drain_dict.items():
        internal_symbol = convert_base.replacer(internal_symbol_dict[original_symbol])
        ingoing_drains[convert_base.replacer(drains[0])] = internal_symbol
        outgoing_drains[convert_base.replacer(drains[1])] = internal_symbol

    with StringIO() as str_out:
        value_assignments = tuple()
        reactions = tuple()
        reaction_id = 0
        for drain_symbol, drain_value in drain_value_map.items():
            if drain_value > 0.0:
                value_assignments += ("{} = {}".format(drain_symbol, drain_value),)
                if drain_symbol in outgoing_drains:
                    species_symbol = outgoing_drains[drain_symbol]
                    reactions += ("D{}:\n\t{} > $pool\n\t{}*{}".format(reaction_id, species_symbol,
                                                                    drain_symbol, species_symbol),)
                elif drain_symbol in ingoing_drains:
                    species_symbol = ingoing_drains[drain_symbol]
                    reactions += ("D{}:\n\t$pool > {}\n\t{}*{}".format(reaction_id, species_symbol,
                                                                    drain_symbol, species_symbol),)
                reaction_id += 1

        for reaction in reactions:
            str_out.write(reaction)
            str_out.write('\n')

        str_out.write('\n')

        for item in value_assignments:
            str_out.write(item)
            str_out.write('\n')

        return str_out.getvalue()


def generate_fixed_species(ignored_species, internal_symbol_map):
    if len(ignored_species) > 0:
        with StringIO() as str_out:
            str_out.write('FIX: ')
            for symbol, _ in ignored_species:
                str_out.write('{} '.format(convert_base.replacer(internal_symbol_map[symbol])))
            str_out.write('\n')
            return str_out.getvalue()
