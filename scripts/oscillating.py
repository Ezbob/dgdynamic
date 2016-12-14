from dgDynamic.choices import SupportedOdePlugins, MatlabOdeSolvers, ScipyOdeSolvers, SupportedStochasticPlugins
from dgDynamic.mod_dynamics import dgDynamicSim, show_plots, HyperGraph


dg = HyperGraph.from_abstract(
    'F + B -> F + F',
    'C + F -> C + C',
    'B -> F',
    'F -> C',
)

ode = dgDynamicSim(dg)
stochastic = dgDynamicSim(dg, simulator_choice="stochastic")

# Set the species that you wish to remain unchanged in the integration process.
# Since these species don't contribute they don't get saved or plotted
ode.unchanging_species('B')
stochastic.unchanging_species('B')

# Name of the data set
name = "abstractReactions1"

# Specify the initial values for each species
initial_conditions = {
    'F': 1,
    'B': 1,
    'C': 0,
}

# Specify the mass action parameters for each reaction
parameters = {
   'F + B -> F + F': 0.01,
   'C + F -> C + C': 0.000001,
   'B -> F': 0.001,
   'F -> C': 0.001,
}

drain_para = {
    'C': {'in': 0, 'out': 0.01}
}

# Specify the integration range
integration_range = (0, 6000)

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
#    VODE   : Same method as the sundials method (default)
#    ZVODE  : A variant of the VODE solver that deals with complex numbers
#    LSODA  : Can automatically handle stiff and non-stiff problems
#    DOPRI5 : Has dense output and variable time step
#    DOP853 : Has dense output and variable time step
scipy_ode.ode_method = ScipyOdeSolvers.VODE

# Set the time step, default is 0.1
scipy_ode.delta_t = 0.1

# Set initial t value, default is 0
scipy_ode.initial_t = 0

# Solve the ODE system to get the output object
output = scipy_ode.simulate(integration_range, initial_conditions, parameters, drain_para)

# Save the data to a file in the data folder using the output object
output.save(name)

# Plot the data using the MatPlotLib, also using the output object
output.plot("plot.svg", figure_size=(60, 30))

# Using the stochastic pi machine for simulations
spim.simulate((40, 200), initial_conditions, parameters, drain_para)\
   .plot("plot2.svg", figure_size=(40, 20))

# The following solver uses the matlab engine for python to compute the solutions to the ODEs
matlab_ode = ode.get_plugin('matlab')

matlab_ode.simulate(integration_range, initial_conditions, parameters, drain_para).save(name).plot(figure_size=(40, 20))
# solve the ODEs, save the output and plot it afterwards

show_plots()
