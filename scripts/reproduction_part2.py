"""
Numerically solving non-linear case as described in the Ikegami et.al. paper
(Figure 2)
"""
import mod
import numpy

from dgDynamic.generators.ode_generator import ODESystem
from dgDynamic.plugins.matlab import MatlabOdeSolvers
from dgDynamic.plugins.scipy import ScipyOdeSolvers

root_symbol = 'A'
species_limit = 60
max_concentration = 1.0
dimension_limit = species_limit // 2 + 1
epsilon = numpy.nextafter(0, 1)
theta = numpy.nextafter(max_concentration, 0)

integration_range = (0, 10)

# Exclude every A_3i species
banned_set = (3 * i for i in range(species_limit))

k_s = k_d = 1


def get_symbols():
    yield from ('{}{}'.format(root_symbol, i) for i in range(1, species_limit + 1))


def get_reactions():
    for i in range(1, dimension_limit):
        for j in range(1, dimension_limit):
            is_banned = i in banned_set or j in banned_set or (i + j) in banned_set
            if i <= j and not is_banned and not (i == j == 1):
                yield "{0}{1} + {0}{2} <=> {0}{3}".format(root_symbol, i, j, i + j)

print("A1 + A1 <=> A2" in tuple(get_reactions()))

reactions = "\n".join(get_reactions())

initial_conditions = {}

for symbol in get_symbols():
    initial_conditions[symbol] = 1e-5

initial_conditions['A1'] = 100

parameters = {}

# Here the <- direction of the edge means tweaking the decomposition rate
# And -> direction means the tweaking the rate of synthesis
# k_s and k_d marks the rate of synthesis and decomposition

for reaction in get_reactions():
    parameters[reaction] = {'<-': k_d, '->': k_s}

dg = mod.dgAbstract(reactions)

ode = ODESystem(dg)

solver = ode.get_ode_plugin("scipy")

solver.set_integration_range(integration_range)
solver.set_parameters(parameters)
solver.set_initial_conditions(initial_conditions)
solver.set_ode_solver(ScipyOdeSolvers.LSODA)

solver.delta_t = 0.08

solver.solve().plot(filename="scipy2.svg", axis_limits=(integration_range, (0, 1.5)), figure_size=(60, 30))

solver = ode.get_ode_plugin('matlab')

solver.set_integration_range(integration_range)\
    .set_parameters(parameters)\
    .set_initial_conditions(initial_conditions)
solver.set_ode_solver(MatlabOdeSolvers.ode45)

solver.solve().plot(filename="matlab2.svg", axis_limits=(integration_range, (0, 1.5)), figure_size=(60, 30))
