"""
Numerically solving non-linear case as described in the Ikegami et.al. paper
(Figure 2)
"""
import mod
import numpy

from dgdynamic.mod_dynamics import dgDynamicSim, show_plots
from dgdynamic.choices import MatlabOdeSolvers, ScipyOdeSolvers

root_symbol = 'A'
species_limit = 60
max_concentration = 1.0
dimension_limit = species_limit // 2 + 1
epsilon = numpy.nextafter(0, 1)
theta = numpy.nextafter(max_concentration, 0)

end_t = 600

# Exclude every A_3i species
banned_set = tuple(3 * i for i in range(species_limit))

k_s = k_d = 1


def get_symbols():
    yield from ('{}{}'.format(root_symbol, i) for i in range(1, species_limit + 1))


def get_reactions():
    for i in range(1, dimension_limit):
        for j in range(1, dimension_limit):
            is_banned = i in banned_set or j in banned_set or (i + j) in banned_set
            if i <= j and not is_banned and not (i == j == 1):
                yield "{0}{1} + {0}{2} <=> {0}{3}".format(root_symbol, i, j, i + j)

print("Is A1 + A1 <=> A2 in reaction set? {}".format("A1 + A1 <=> A2" in tuple(get_reactions())))

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

ode = dgDynamicSim(dg)
sto = dgDynamicSim(dg, 'stochastic')

solver = ode("scipy")
spim = sto('SPIM')
stochkit2 = sto('stochkit2')

solver.method = ScipyOdeSolvers.LSODA
solver.delta_t = 0.08

out = solver.simulate(end_t, initial_conditions, parameters)
out.plot(filename="scipy_nonlinear.svg", axis_limits=((0, end_t), (0, 1.5)), figure_size=(60, 30))

solver = ode('matlab')

solver.method = MatlabOdeSolvers.ode45
out = solver.simulate(end_t, initial_conditions, parameters)

out.plot(filename="matlab_nonlinear.svg", axis_limits=((0, end_t), (0, 1.5)), figure_size=(60, 30))

initial_conditions = {symbol: 1 for symbol in get_symbols()}
initial_conditions['A1'] = 10000000  # int(100 / 1e-5) * 100

out = spim.simulate(end_t + 2400, initial_conditions, parameters)
out.plot(filename="spim_nonlinear.svg", figure_size=(60, 30))

stochkit2.method = 'tauLeaping'
stochkit2.resolution = 7500

out = stochkit2.simulate(end_t + 2400, initial_conditions, parameters)
out.plot(filename="stochkit2_nonlinear.svg", figure_size=(60, 30))

show_plots()
