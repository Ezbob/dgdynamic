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

simple3 = """
B -> A
A + B -> A + A
A + A -> A + B
"""

dg = mod.dgAbstract(
    simple1
)

stochastic_sim = dgDynamicSim(dg, simulator_choice="spim")

print(generate_automata_code(stochastic_sim))
