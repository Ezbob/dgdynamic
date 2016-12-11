"""
Infection model
This model, models the relationship between the
(I)fected, (R)ecovered and the (S)usceptible under the outbreak of some decease.
The recovered becomes immune to the infected once they recover,
and the model starts out with some infected.
"""
from dgDynamic import dgDynamicSim, show_plots, HyperGraph
from dgDynamic.choices import MatlabOdeSolvers
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

integration_range = (0, 200)

ode = dgDynamicSim(dg, simulator_choice="ODE")
stochastic = dgDynamicSim(dg, simulator_choice="stochastic")

# Name of the data set
name = "infected"
# figure_size in centimetres
figure_size = (40, 20)

with stochastic("spim") as spim:
    simulation_range = (200, 1000)
    for i in range(3):
        spim(simulation_range, initial_conditions, parameters,).plot(figure_size=figure_size)

with ode.get_plugin("scipy") as scipy:
    # Let's generate some sample delta_ts
    for dt in numpy.linspace(0.1, 1, num=5):
        scipy.delta_t = dt
        scipy.simulate(integration_range, initial_conditions, parameters,).plot(figure_size=figure_size)

with ode.get_plugin("Matlab") as matlab:
    for supported in MatlabOdeSolvers:
        matlab.ode_method = supported
        matlab(integration_range, initial_conditions, parameters,).plot(figure_size=figure_size)

show_plots()
