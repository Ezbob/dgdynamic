from dgDynamic.choices import SupportedStochasticPlugins
from .stochastic_plugin import StochasticPlugin
import re

name = SupportedStochasticPlugins.StochPy


class StochPyStochastic(StochasticPlugin):

    def __init__(self, simulator, timeout=None,):
        super().__init__()
        self._simulator = simulator

    def generate_psc_file(self, writable_steam, rate_law_dict, translate_dict=None):
        print(writable_steam, rate_law_dict)

        def edge_to_psc_edge(reaction_string):
            seperator = " > "
            left, right = None, None
            if "->" in reaction_string:
                left, _, right = str.partition(reaction_string, '->')
            elif "<=>" in reaction_string:
                left, _, right = str.partition(reaction_string, '<=>')
                seperator = " = "
            else:
                raise ValueError("Not a reaction string")
            digit_matcher = re.compile("\d+")
            new_reaction = seperator.join((left, right))
            for match in digit_matcher.finditer(new_reaction):
                new_reaction = new_reaction.replace(match, '{' + match + '}')
            if translate_dict:
                return ' '.join((translate_dict[symbol] if symbol in translate_dict else symbol
                                 for symbol in new_reaction.split()))
            else:
                return new_reaction

        debug = tuple(rate_law_dict.keys())[0]
        print(debug)
        print(debug, edge_to_psc_edge(debug))

    def simulate(self, simulation_range, initial_conditions,
                 rate_parameters, drain_parameters, *args, **kwargs):
        pass