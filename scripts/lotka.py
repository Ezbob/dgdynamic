"""
A Lotka model with (F)oxes and (R)abbits (prey-predator model).
    Rabbits eat grass and multiples
    Foxes hunt and eat rabbits and multiples
    Foxes also dies of old age
"""
import mod

from dgDynamic.choices import SupportedOdePlugins
from dgDynamic.mod_dynamics import dgDynamicSim
from dgDynamic.plugins.ode.scipy import ScipyOdeSolvers


rabbit_multiples = "R -> 2 R\n"
foxes_hunts = "R + F -> F + F\n"
foxes_dies = "F -> D\n"

whole = rabbit_multiples + foxes_hunts + foxes_dies

dg = mod.dgAbstract(
    whole
)

initial_conditions = {
    'F': 250,
    'R': 250
}

parameters = {
    foxes_hunts: 0.004,
    rabbit_multiples: 0.7,
    foxes_dies: 0.5,
}

integration_range = (0, 100)

ode = dgDynamicSim(dg, simulator_choice='ode').unchanging_species('D')
stochastic = dgDynamicSim(dg, simulator_choice='stochastic').unchanging_species('D')

# Name of the data set
name = "foxesRabbits"
figure_size = (40, 20)

# scipy_ode = ode(SupportedOdePlugins.Scipy)

# scipy_ode.ode_solver = ScipyOdeSolvers.VODE

# scipy_ode.delta_t = 0.1

# scipy_ode.simulation_range = integration_range

# scipy_ode.initial_conditions = initial_conditions

# scipy_ode.parameters = parameters

# scipy_ode.solve().save(name).plot(figure_size=figure_size)

#with ode('matlab') as matlab:
#    matlab(integration_range, initial_conditions, parameters).plot(figure_size=figure_size)

spim_simulation_range = (100, 1000)
should_try = True
while should_try:
    with stochastic('spim') as spim:
        for i in range(10):
            output = spim(simulation_range=spim_simulation_range, initial_conditions=initial_conditions,
                          parameters=parameters, timeout=60)
            #if not output.is_empty:
            #    output.save(name).plot(figure_size=figure_size)
            print(i, output.has_errors)
            if output.has_errors and not output.is_empty:
                output.plot(figure_size=figure_size)
                print(output.errors)
                should_try = False

