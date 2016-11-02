from dgDynamic.mod_dynamics import dgDynamicSim
from dgDynamic.config.settings import config
import mod


dg = mod.dgAbstract("""
B -> A + C
A + B <=> A + A
""")

print(config['Logging']['SAVE_LOGS'])

stochastic_sim = dgDynamicSim(dg, simulator_choice="spim")

stochastic_sim.generate_channels()

