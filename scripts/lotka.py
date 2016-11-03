"""
A Lotka model with (F)oxes and (R)abbits (prey-predator model).
    Rabbits eat grass and multiples
    Foxes hunt and eat rabbits and multiples
    Foxes also dies of old age
"""
import mod

from dgDynamic.choices import SupportedOdePlugins
from dgDynamic.mod_dynamics import dgDynamicSim
from dgDynamic.plugins.scipy import ScipyOdeSolvers


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
    foxes_hunts: 0.004,
    rabbit_multiples: 0.7,
    foxes_dies: 0.5,
}

integration_range = (0, 100)

ode = dgDynamicSim(dg).unchanging_species('D')

# Name of the data set
name = "foxesRabbits"

scipy_ode = ode(SupportedOdePlugins.Scipy)

scipy_ode.ode_solver = ScipyOdeSolvers.VODE

scipy_ode.delta_t = 0.1

scipy_ode.integration_range = integration_range

scipy_ode.initial_conditions = initial_conditions

scipy_ode.parameters = parameters

scipy_ode.solve().save(name).plot(figure_size=(40, 20))

