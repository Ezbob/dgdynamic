"""
Numerically solving non-linear case as described in the Ikegami et.al. paper
(Figure 3)
"""
import mod
import numpy

from dgODE.ode_generator import dgODESystem
from dgODE.plugins.scipy import ScipyOdeSolvers
from dgODE.plugins.matlab import MatlabOdeSolvers

root_symbol = 'A'
species_limit = 60
max_concentration = 1.0
dimension_limit = species_limit // 2 + 1
epsilon = numpy.nextafter(0, 1)
theta = numpy.nextafter(max_concentration, 0)

integration_range = (0, 4)

# Exclude every A_3i species
banned_set = (3 * i for i in range(species_limit))

unchanging_species = (
    'A1',
)

k_s = k_d = 1


def get_symbols():
    yield from ('{}{}'.format(root_symbol, i) for i in range(1, species_limit + 1))


def get_reactions():
    yield "FIN -> {}{}".format(root_symbol, 1)

    for i in range(2, species_limit + 2):
        yield "{}{} -> FOUT{}".format(root_symbol, i, i)

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

for index, reaction in enumerate(get_reactions()):
    if reaction == "FIN -> A1":
        parameters[reaction] = 0.4 * 10000
    elif reaction == "A{0} -> FOUT{0}".format(index):
        parameters[reaction] = -0.01
    else:
        parameters[reaction] = {'<-': k_d, '->': k_s}

dg = mod.dgAbstract(reactions)

print(parameters)

ode = dgODESystem(dg).unchanging_species("FIN", *tuple("FOUT{0}".format(index) for index in range(2, len(parameters))))

solver = ode.get_ode_plugin("scipy")

solver.set_integration_range(integration_range)
solver.set_parameters(parameters)
solver.set_initial_conditions(initial_conditions)
solver.set_ode_solver(ScipyOdeSolvers.LSODA)

solver.delta_t = 0.08

solver.solve().plot(figure_size=(60, 30))

solver = ode.get_ode_plugin('matlab')

solver.set_integration_range(integration_range)\
    .set_parameters(parameters)\
    .set_initial_conditions(initial_conditions)
solver.set_ode_solver(MatlabOdeSolvers.ode45)

solver.solve().plot(figure_size=(60, 30))
