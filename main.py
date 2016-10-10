import mod
import numpy

from dgODE.ode_generator import dgODESystem
from dgODE.plugins.scipy import ScipyOdeSolvers

root_symbol = 'A'
species_limit = 60
dimension_limit = species_limit // 2 + 1
epsilon = numpy.nextafter(0, 1)

integration_range = (0, 50)

disabled_reactions = [
    (1, 1)
]


def get_symbols():
    return ('A{}'.format(i) for i in range(1, species_limit + 1))


def get_reactions():
    for i in range(1, dimension_limit):
        for j in range(1, dimension_limit):
            it = (i == i_disabled and j == j_disabled for i_disabled, j_disabled in disabled_reactions)
            if i <= j and not any(it):
                yield "{0}{1} + {0}{2} <=> {0}{3}".format(root_symbol, i, j, i + j)

print("A1 + A1 <=> A2" in tuple(get_reactions()))

reactions = "\n".join(get_reactions())

initial_conditions = {}

for symbol in get_symbols():
    initial_conditions[symbol] = 0.0005

initial_conditions['A1'] = 0.9

parameters = {}

# Here the <- direction of the edge means tweaking the decomposition rate
# And -> direction means the tweaking the rate of synthesis
# k_s and k_d marks the rate of synthesis and decomposition

for reaction in get_reactions():
    parameters[reaction] = 0.5


dg = mod.dgAbstract(reactions)

ode = dgODESystem(dg)


solver = ode.get_ode_plugin("scipy")

solver.set_integration_range(integration_range)
solver.set_parameters(parameters)
solver.set_initial_conditions(initial_conditions)
solver.set_ode_solver(ScipyOdeSolvers.DOPRI5)

solver.solve().plot(figure_size=(60, 30))

#
# # Set the species that you wish to remain unchanged in the integration process.
# # Since these species don't contribute they don't get saved or plotted
# ode.unchanging_species('B', 'D')
#
# # Name of the data set
# name = "abstractReactions1"
#


#
# # Alternative syntax for specifying initial conditions
# # initial_conditions = (
# #     0.5,
# #     1,
# #     0,
# #     0,
# # )
#
# # Specify the mass action parameters for each reaction

#
# # Alternative specification of parameters
# # parameters = (
# #     0.01,
# #     0.005,
# #     0.001,
# #     0.001,
# #     0.01,
# # )
#
# # Specify the integration range
# integration_range = (0, 10000)
#
# # Get ODE solver plugin for the given abstract reaction system
# # input can be either a entry in the SupportedSolvers enum, or a string (such as "scipy" or "matlab")
# # that contains a recognized plugin name
# scipy_ode = ode.get_ode_plugin(SupportedSolvers.Scipy)
#
# # Set the abstract ode system, but this is already set when using the "get_ode_plugin" method
# # scipy_ode.set_abstract_ode_system(ode)
#
# # Set the solver method from one of the entries in the SciOdeSolvers enumeration
# # If none are selected this default to the VODE method for Scipy
# # The available solvers are (docs: http://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.ode.html):
# #    VODE   : Same method as the sundials method
# #    ZVODE  : A variant of the VODE solver that deals with complex numbers
# #    LSODA  : Can automatically handle stiff and non-stiff problems
# #    DOPRI5 : Has dense output and variable time step
# #    DOP853 : Has dense output and variable time step
# scipy_ode.set_ode_solver(ScipyOdeSolvers.VODE)
#
# # Set the time step, default is 0.05
# scipy_ode.delta_t = 0.1
#
# # Set initial t value, default is 0
# scipy_ode.initial_t = 0
#
# # Set the integration range. This has to be a tuple of two numbers; a lower bound and a upper bound
# scipy_ode.set_integration_range(integration_range)
#
# # Set the initial conditions
# scipy_ode.set_initial_conditions(initial_conditions)
#
# # Set the parameters
# scipy_ode.set_parameters(parameters)
#
# # Solve the ODE system to get the output object
# output = scipy_ode.solve()
#
# # Save the data to a file in the data folder using the output object
# output.save(name)
#
# # Plot the data using the MatPlotLib, also using the output object
# output.plot("plot.svg", figure_size=(40, 20), labels=('Cycle 1', 'Cycle 2'), axis_labels=('t','y'))
#
#
# # The following solver uses the matlab engine for python to compute the solutions to the ODEs
# # matlab_ode = ode.get_ode_plugin(SupportedSolvers.Matlab, initial_conditions=initial_conditions,
# #                    integration_range=integration_range, parameters=parameters, solver=MatlabOdeSolvers.ode45)
#
# # matlab_ode.solve().save(name).plot() # solve the ODEs, save the output and plot it afterwards
#
