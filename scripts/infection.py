"""
Infection model
This model, models the relationship between the
(I)fected, (R)ecovered and the (S)usceptible under the outbreak of some decease.
The recovered becomes immune to the infected once they recover,
and the model starts out with some infected.
"""
import mod

from dgDynamic.choices import SupportedSolvers
from dgDynamic.mod_dynamics import dgDynamicSim
from dgDynamic.plugins.scipy import ScipyOdeSolvers

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

scipy_ode = ode.get_ode_plugin(SupportedSolvers.Scipy)

scipy_ode.set_ode_solver(ScipyOdeSolvers.VODE)

scipy_ode.delta_t = 0.1

scipy_ode.set_integration_range(integration_range).set_initial_conditions(initial_conditions).set_parameters(parameters)

scipy_ode.solve().save(name).plot(figure_size=(40, 20))

matlab_solver = ode.get_ode_plugin(SupportedSolvers.Matlab)

matlab_solver.set_integration_range(integration_range).set_initial_conditions(initial_conditions)\
    .set_parameters(parameters)

matlab_solver.solve().save(name).plot(figure_size=(40, 20))
