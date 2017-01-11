import re
from io import StringIO
from dgDynamic.config.settings import config


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
        if translate_dict:
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
