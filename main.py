from dgDynamic.mod_dynamics import dgDynamicSim
import mod

dg = mod.dgAbstract("""
B -> A + C
A + B <=> A + A
""")

stochastic_sim = dgDynamicSim(dg, simulator_choice="spim")

stochastic_sim.generate_channels()

