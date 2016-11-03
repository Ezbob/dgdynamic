"""
Infection model
This model, models the relationship between the
(I)fected, (R)ecovered and the (S)usceptible under the outbreak of some decease.
The recovered becomes immune to the infected once they recover,
and the model starts out with some infected.
"""
import mod
from dgDynamic.choices import SupportedOdePlugins, ScipyOdeSolvers, MatlabOdeSolvers
from dgDynamic.mod_dynamics import dgDynamicSim

susceptible_infected = "S + I -> 2 I\n"
recovered = "I -> R\n"
infected_stays_infected = "2 I -> 2 I\n"
recovered_stays_recovered = "R + I -> R + I\n"

whole_model = susceptible_infected + recovered + infected_stays_infected + recovered_stays_recovered

dg = mod.dgAbstract(
    whole_model
)

initial_conditions = {
    'S': 200,
    'I': 1,
}

parameters = {
    susceptible_infected: 0.001,
    infected_stays_infected: 0.001,
    recovered_stays_recovered: 0.001,
    recovered: 0.03,
}

integration_range = (0, 200)

ode = dgDynamicSim(dg)

# Name of the data set
name = "infected"

matlab_solver = ode(SupportedOdePlugins.Matlab)
scipy_ode = ode(SupportedOdePlugins.Scipy)

scipy_ode.delta_t = 0.1
figure_size = (40, 20)

output = scipy_ode(integration_range, initial_conditions, parameters)
output.plot(figure_size=figure_size)

output = matlab_solver(integration_range, initial_conditions, parameters)
output.plot(figure_size=figure_size)
