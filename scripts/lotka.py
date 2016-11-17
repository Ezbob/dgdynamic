"""
A Lotka model with (F)oxes and (R)abbits (prey-predator model).
    Rabbits eat grass and multiples
    Foxes hunt and eat rabbits and multiples
    Foxes also dies of old age
"""
import mod
from dgDynamic import dgDynamicSim
from dgDynamic.structures import AbstractReaction
from dgDynamic.choices import SupportedOdePlugins

rabbit_multiples = "R -> 2 R\n"
foxes_hunts = "R + F -> F + F\n"
foxes_dies = "F -> D\n"

whole = rabbit_multiples + foxes_hunts + foxes_dies

dg = mod.dgAbstract(
    whole
)

initial_conditions = {
    'F': 250,
    'R': 250
}

parameters = {
    AbstractReaction(dg, foxes_hunts): 0.005,
    AbstractReaction(dg, rabbit_multiples): 0.7,
    AbstractReaction(dg, foxes_dies): 0.5,
}

integration_range = (0, 100)

ode = dgDynamicSim(dg, simulator_choice='ode', unchanging_species='D')
stochastic = dgDynamicSim(dg, simulator_choice='stochastic', unchanging_species='D')

# Name of the data set
name = "foxesRabbits"
figure_size = (40, 20)

for ode_plugin_name in SupportedOdePlugins:
    output = ode(ode_plugin_name)(integration_range, initial_conditions, parameters).plot(figure_size=figure_size)

# spim_simulation_range = (100, 1000)
#
# with stochastic('spim') as spim:
#     for i in range(8):
#         spim(simulation_range=spim_simulation_range, initial_conditions=initial_conditions,
#              parameters=parameters, timeout=60).plot(figure_size=figure_size)

