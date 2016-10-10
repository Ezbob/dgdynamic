import mod
import numpy

from dgODE.ode_generator import dgODESystem
from dgODE.plugins.scipy import ScipyOdeSolvers

root_symbol = 'A'
species_limit = 60
dimension_limit = species_limit // 2 + 1
epsilon = numpy.nextafter(0, 1)
theta = numpy.nextafter(1, 0)

integration_range = (0, 1500)

# this corresponds to setting the r_ij values
disabled_reactions = [
    (1, 1)
]

unchanging_species = (
    'A1',
)


def get_symbols():
    return ('A{}'.format(i) for i in range(1, species_limit + 1))


def get_reactions():
    for i in range(1, dimension_limit):
        for j in range(1, dimension_limit):
            in_disabled = (i == i_disabled and j == j_disabled for i_disabled, j_disabled in disabled_reactions)
            if i <= j and not any(in_disabled):
                yield "{0}{1} + {0}{2} <=> {0}{3}".format(root_symbol, i, j, i + j)

print("A1 + A1 <=> A2" in tuple(get_reactions()))

reactions = "\n".join(get_reactions())

initial_conditions = {}

for symbol in get_symbols():
    initial_conditions[symbol] = 1.0 - theta

initial_conditions['A1'] = theta

parameters = {}

# Here the <- direction of the edge means tweaking the decomposition rate
# And -> direction means the tweaking the rate of synthesis
# k_s and k_d marks the rate of synthesis and decomposition

for reaction in get_reactions():
    parameters[reaction] = 0.9


dg = mod.dgAbstract(reactions)

ode = dgODESystem(dg).unchanging_species(*unchanging_species)


solver = ode.get_ode_plugin("scipy")

solver.set_integration_range(integration_range)
solver.set_parameters(parameters)
solver.set_initial_conditions(initial_conditions)
solver.set_ode_solver(ScipyOdeSolvers.LSODA)

solver.delta_t = 0.1

solver.solve().save("reproduction1", unfiltered=True).plot(figure_size=(60, 30))
