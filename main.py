from dgDynamic.mod_dynamics import dgDynamicSim
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

stochastic_sim.generate_channels()

