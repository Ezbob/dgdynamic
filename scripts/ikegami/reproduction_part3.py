"""
Numerically solving non-linear case as described in the Ikegami et.al. paper
(Figure 2)
"""
import mod
import numpy

from dgDynamic.mod_dynamics import dgDynamicSim, show_plots
from dgDynamic.choices import MatlabOdeSolvers, ScipyOdeSolvers

root_symbol = 'A'
species_limit = 60
max_concentration = 1.0
dimension_limit = species_limit // 2 + 1
epsilon = numpy.nextafter(0, 1)
theta = numpy.nextafter(max_concentration, 0)

integration_range = (0, 200)

# Exclude every A_3i species
banned_set = tuple(3 * i for i in range(species_limit))

k_s = 1.0
k_d = 1200


def get_symbols():
    yield from ('{}{}'.format(root_symbol, i) for i in range(1, species_limit + 1))


def get_reactions():
    for i in range(1, dimension_limit):
        for j in range(1, dimension_limit):
            is_banned = i in banned_set or j in banned_set or (i + j) in banned_set
            if i <= j and not is_banned and not (i == j == 1):
                yield "{0}{1} + {0}{2} <=> {0}{3}".format(root_symbol, i, j, i + j)


print("Is A1 + A1 <=> A2 in reactions set? {}".format("A1 + A1 <=> A2" in tuple(get_reactions())))

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

drain_params = {}

for symbol in get_symbols():
    drain_params[symbol] = {
        'out': {
            'factor': 0.01
        }
    }

drain_params['A1'] = {
    'in': {
        'constant': 4000
    },
    'out': {
        'factor': 0.4
    }
}

dg = mod.dgAbstract(reactions)

ode = dgDynamicSim(dg)
sto = dgDynamicSim(dg, 'stochastic')

solver = ode.get_plugin("scipy")
spim = sto('SPIM')
stochpy = sto('stochpy')

solver.integrator_mode = ScipyOdeSolvers.LSODA
solver.delta_t = 0.08

out = solver.simulate(integration_range, initial_conditions, parameters, drain_params)
out.plot(filename="scipy3.svg", figure_size=(60, 30))

#
# solver = ode.get_plugin('matlab')
#
# solver.integrator_mode = MatlabOdeSolvers.ode45
# out = solver.simulate(integration_range, initial_conditions, parameters)
#
# out.plot(filename="matlab2.svg", axis_limits=(integration_range, (0, 1.5)), figure_size=(60, 30))
#
# initial_conditions = {symbol: 1 for symbol in get_symbols()}
#
# initial_conditions['A1'] = 100
#
# spim_sim_range = (10, 10000)
#
# out = spim.simulate(spim_sim_range, initial_conditions, parameters)
# out.plot(filename="spim.svg", axis_limits=((0, spim_sim_range[0]), (0, 14)), figure_size=(60, 30))
#

show_plots()
