import mod

from dgDynamic.converters.stochastic.spim_converter import generate_automata_code, pretty_print_dict, get_parameters
from dgDynamic.mod_dynamics import dgDynamicSim

simple1 = """
B -> A + C
A + B <=> A + A
"""

simple2 = """
A + B -> C + C
A + C -> D
C -> E + F
F + F -> B
"""

simple3 = """
B -> A
A + B -> A + A
A + A -> A + B
"""

rates_simple3 = {'B -> A': 0.3,
                 'A + B -> A + A': 0.4,
                 'A + A -> A + B': 0.6}

dg = mod.dgAbstract(
    simple3
)

stochastic_sim = dgDynamicSim(dg, simulator_choice="stochastic")

stochastic_sim('spim')

#pretty_print_dict(stochastic_sim.generate_channels())
print(get_parameters(stochastic_sim, stochastic_sim.generate_channels(), rates_simple3))
print(generate_automata_code(stochastic_sim.generate_channels(), stochastic_sim.symbols))

