"""
Here we numerically solve for the first-order autocatalytic cycles as described in the Ikegami et.al. paper
See Section: "The linear case: self-origanisation of first-order autocatalysis"
"""

import mod
import numpy

from dgDynamic.mod_dynamics import dgDynamicSim, HyperGraph, show_plots
from dgDynamic.choices import ScipyOdeSolvers

root_symbol = 'A'
species_limit = 10
max_concentration = 1.0
dimension_limit = species_limit // 2 + 1
epsilon = numpy.nextafter(0, 1)
theta = numpy.nextafter(max_concentration, 0)

integration_range = (0, 10000)

# this corresponds to setting the r_ij values
disabled_reactions = [
    (1, 1)
]

unchanging_species = (
    'A1',
)

k_s, k_d = 0.9, 0.9


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
    initial_conditions[symbol] = max_concentration - theta

initial_conditions['A1'] = theta

parameters = {}

# Here the <- direction of the edge means tweaking the decomposition rate
# And -> direction means the tweaking the rate of synthesis
# k_s and k_d marks the rate of synthesis and decomposition

for reaction in get_reactions():
    parameters[reaction] = {'<-': k_d, '->': k_s}

print("K = {}".format(theta * (k_s / k_d)))

dg = HyperGraph.from_abstract(reactions)

ode = dgDynamicSim(dg).unchanging_species(*unchanging_species)

solver = ode("scipy")

solver.integrator_mode = ScipyOdeSolvers.LSODA
solver.delta_t = 0.1

output = solver.simulate(integration_range, initial_conditions, parameters,)
output.save("reproduction1", unfiltered=True).plot(figure_size=(60, 30))
show_plots()
