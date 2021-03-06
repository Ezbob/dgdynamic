from dgdynamic.choices import SupportedOdePlugins, MatlabOdeSolvers, ScipyOdeSolvers, SupportedStochasticPlugins
from dgdynamic.mod_dynamics import dgDynamicSim, show_plots, HyperGraph

# Enable logging when uncommented
# set_logging(new_session=True)

dg = HyperGraph.from_abstract(
    'F + B -> F + F',
    'C + F -> C + C',
    'B -> F',
    'F -> C',
    'C -> B',
)

ode = dgDynamicSim(dg)
stochastic = dgDynamicSim(dg, simulator_choice="stochastic")

# Set the species that you wish to remain unchanged in the integration process.
# Since these species don't contribute they don't get saved or plotted
#ode.unchanging_species('B')
#stochastic.unchanging_species('B', 'D')

# Name of the data set
name = "abstractReactions1"

# Specify the initial values for each species
initial_conditions = {
    'F': 0.5,
    'B': 100,
    'C': 0,
}
#
# spim_initial_conditions = {
#     'F': 1,
#     'B': 1,
#     'C': 0,
#     'D': 0,
# }

# Alternative syntax for specifying initial conditions
# initial_conditions = (
#     0.5,
#     1,
#     0,
#     0,
# )

# Specify the mass action parameters for each reaction
parameters = {
   'F + B -> F + F': 0.01,
   'C + F -> C + C': 0.005,
   'B -> F': 0.001,
   'F -> C': 0.001,
   'C -> B': 0.01,
}

drain_par = {}

# Alternative specification of parameters
# parameters = (
#     0.01,
#     0.005,
#     0.001,
#     0.001,
#     0.01,
# )

# Specify the end_t
end_t = 400

# Get ODE solver plugin for the given abstract reaction system
# input can be either a entry in the SupportedSolvers enum, or a string (such as "scipy" or "matlab")
# that contains a recognized plugin name
scipy_ode = ode.get_plugin(SupportedOdePlugins.SciPy)

spim = stochastic.get_plugin(SupportedStochasticPlugins.SPiM)

# Set the abstract ode system, but this is already set when using the "get_ode_plugin" method
# scipy_ode.set_abstract_ode_system(ode)

# Set the solver method from one of the entries in the SciOdeSolvers enumeration
# If none are selected this default to the VODE method for Scipy
# The available solvers are (docs: http://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.ode.html):
#    VODE   : Same method as the sundials method
#    ZVODE  : A variant of the VODE solver that deals with complex numbers
#    LSODA  : Can automatically handle stiff and non-stiff problems
#    DOPRI5 : Has dense output and variable time step
#    DOP853 : Has dense output and variable time step
scipy_ode.ode_method = ScipyOdeSolvers.VODE

# Set the time step, default is 0.05
scipy_ode.delta_t = 0.1

# Set initial t value, default is 0
scipy_ode.initial_t = 0

# Set the initial conditions
scipy_ode.initial_conditions = initial_conditions

# Set the parameters
scipy_ode.parameters = parameters

scipy_ode.drain_parameters = drain_par

# Solve the ODE system to get the output object
output = scipy_ode.simulate(end_t, initial_conditions, parameters)

# Save the data to a file in the data folder using the output object
output.save(name)

# Plot the data using the MatPlotLib, also using the output object
output.plot("plot.svg", figure_size=(60, 30))

#spim(end_t, parameters=parameters, initial_conditions=spim_initial_conditions)\
#    .plot("plot2.svg", figure_size=(40, 20))

show_plots()

# The following solver uses the matlab engine for python to compute the solutions to the ODEs
# matlab_ode = ode.get_ode_plugin(SupportedSolvers.Matlab, initial_conditions=initial_conditions,
#                    integration_range=integration_range, parameters=parameters, solver=MatlabOdeSolvers.ode45)

# matlab_ode.solve().save(name).plot() # solve the ODEs, save the output and plot it afterwards


