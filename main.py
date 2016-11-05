import mod

from dgDynamic.converters.stochastic.spim_converter import generate_automata_code
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

dg = mod.dgAbstract(
    simple3
)

stochastic_sim = dgDynamicSim(dg, simulator_choice="stochastic")

stochastic_sim('spim')

print(generate_automata_code(stochastic_sim))
