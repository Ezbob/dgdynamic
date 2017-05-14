"""
Numerically solving non-linear case as described in the Ikegami et.al. paper
(Figure 2)
"""
import mod
from dgdynamic.mod_dynamics import dgDynamicSim, show_plots
from dgdynamic.choices import MatlabOdeSolvers, ScipyOdeSolvers

root_symbol = 'A'
species_limit = 60
dimension_limit = species_limit // 2 + 1

end_t = 600

# Exclude every A_3i species
banned_set = tuple(3 * i for i in range(1, species_limit + 1))

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

scipy = ode("scipy")
spim = sto('SPIM')
stochkit2 = sto('stochkit2')
matlab = ode('matlab')

scipy.method = ScipyOdeSolvers.LSODA
scipy.delta_t = 0.08

out = scipy.simulate(end_t, initial_conditions, parameters)
out.plot(filename="scipy_nonlinear.svg", axis_limits=((0, end_t), (0, 1.5)), figure_size=(60, 30))

matlab.method = MatlabOdeSolvers.ode45
out = matlab.simulate(end_t, initial_conditions, parameters)

out.plot(filename="matlab_nonlinear.svg", axis_limits=((0, end_t), (0, 1.5)), figure_size=(60, 30))

for species in initial_conditions.keys():
    initial_conditions[species] = int(initial_conditions[species] * 1e5)

end_t = end_t + 2400

out = spim.simulate(end_t, initial_conditions, parameters)
out.plot(filename="spim_nonlinear.svg", figure_size=(60, 30))

stochkit2.method = 'tauLeaping'
stochkit2.resolution = 7500

out = stochkit2.simulate(end_t, initial_conditions, parameters)
out.plot(filename="stochkit2_nonlinear.svg", figure_size=(60, 30), axis_limits=((0, end_t), (0, 100000)))

show_plots()
