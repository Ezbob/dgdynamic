import mod
import functools
from dgDynamic.mod_dynamics import dgDynamicSim

simple1 = """
B -> A
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
                 'A + B -> A + A': 0.4}

rates_simple1 = {'B -> A': 0.3,
                 'A + B <=> A + A': {'<-': 0.6, '->': 0.4}}

initials1 = {
    'A': 100,
    'B': 200
}

dg = mod.dgAbstract(
    simple1
)

stochastic_sim = dgDynamicSim(dg, simulator_choice="stochastic")
ode_sim = dgDynamicSim(dg, simulator_choice="ode")

with stochastic_sim('spim') as spim:
    spim_calling_parameters = ((20.0, 100), rates_simple1, initials1)
    for i in range(3):
        spim(*spim_calling_parameters).plot(title="spim {}".format(i))


with ode_sim('scipy') as scipy:
    scipy(simulation_range=(0, 20), parameters=rates_simple1, initial_conditions=initials1, ).plot()




