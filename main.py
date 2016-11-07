import mod

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
                 'A + B <=> A + A': {'->': 0.6, '<-': 0.4}}

initials1 = {
    'A': 100,
    'B': 200
}

dg = mod.dgAbstract(
    simple1
)

stochastic_sim = dgDynamicSim(dg, simulator_choice="stochastic")

spim = stochastic_sim('spim')

spim(sample_range=(20.0, 100), parameters=rates_simple1, initial_conditions=initials1,).plot()


