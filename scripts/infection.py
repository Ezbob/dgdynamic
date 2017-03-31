"""
Infection model
This model, models the relationship between the
(I)fected, (R)ecovered and the (S)usceptible under the outbreak of some decease.
The recovered becomes immune to the infected once they recover,
and the model starts out with some infected.
"""
from dgdynamic import dgDynamicSim, show_plots, HyperGraph
from dgdynamic.choices import MatlabOdeSolvers
import numpy

susceptible_infected = "S + I -> 2 I"
recovered = "I -> R"
infected_stays_infected = "2 I -> 2 I"
recovered_stays_recovered = "R + I -> R + I"

dg = HyperGraph.from_abstract(
    susceptible_infected,
    recovered,
    infected_stays_infected,
    recovered_stays_recovered
)

initial_conditions = {
    'S': 400,
    'I': 2,
}

parameters = {
    susceptible_infected: 0.001,
    infected_stays_infected: 0.001,
    recovered_stays_recovered: 0.001,
    recovered: 0.03,
}

ode = dgDynamicSim(dg, simulator_choice="ODE")
stochastic = dgDynamicSim(dg, simulator_choice="stochastic")

# Name of the data set
name = "infected"
# figure_size in centimetres
figure_size = (40, 20)
end_t = 200

with stochastic("spim") as spim:
    for i in range(3):
        spim(end_t, initial_conditions, parameters,).plot(figure_size=figure_size)

with stochastic("stochkit2") as stochkit2:
    stochkit2.trajectories = 3
    stochkit2.simulate(end_t, initial_conditions, parameters,).plot(figure_size=figure_size)

with ode.get_plugin("scipy") as scipy:
    # Let's generate some sample delta_ts
    for dt in numpy.linspace(0.1, 1, num=5):
        scipy.delta_t = dt
        scipy.simulate(end_t, initial_conditions, parameters,).plot(figure_size=figure_size)

with ode.get_plugin("Matlab") as matlab:
    for supported in MatlabOdeSolvers:
        matlab.method = supported
        matlab(end_t, initial_conditions, parameters,).plot(figure_size=figure_size)

show_plots()
