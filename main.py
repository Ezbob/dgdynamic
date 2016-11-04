from dgDynamic.mod_dynamics import dgDynamicSim
from dgDynamic.converters.spim_converter import generate_automata_code
import mod

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

dg = mod.dgAbstract(
    simple2
)

stochastic_sim = dgDynamicSim(dg, simulator_choice="spim")

print(generate_automata_code(stochastic_sim))
