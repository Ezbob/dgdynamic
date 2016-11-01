from dgDynamic.mod_dynamics import dgDynamicSim
import dgDynamic.converters.CGF as CGF
import mod

dg = mod.dgAbstract("""
B -> A
A + B <=> A + A
""")

stochastic_sim = dgDynamicSim(dg, simulator_choice="spim")


g = CGF.CGF()

print(g.reagents)



