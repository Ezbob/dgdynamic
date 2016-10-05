from src.mod_interface.ode_generator import AbstractOdeSystem
from src.plugins.ode_scipy.scipy import ScipyOdeSolvers, ScipyOde
from src.utils.project_utils import set_logging
from src.converters.converter import get_parameter_map
from src.plugins.ode_matlab.matlab import MatlabOde, MatlabOdeSolvers
# linking order is important so don't make this the first import

import mod

set_logging(new_session=True)

dg = mod.dgAbstract("""
F + B -> F + F
C + F -> C + C
B -> F
F -> C
C -> D
""")

aos = AbstractOdeSystem(dg).unchanging_species('B','D')


# Set the species that you wish to remain unchanged in the integration process.
# Since these species don't contribute they don't get saved or plotted
aos.unchanging_species('B', 'D')

# Name of the data set
name = "abstractReactions1"

# Specify the initial values for each species
initial_conditions = {
    'F': 0.5,
    'B': 1,
    'C': 0,
    'D': 0,
}

#Specify the mass action parameters for each reaction
parameters = {
   'F + B -> F + F': 0.01,
   'C + F -> C + C': 0.005,
   'B -> F': 0.001,
   'F -> C': 0.001,
   'C -> D': 0.01,
}

# parameters = (
#     0.01,
#     0.005,
#     0.001,
#     0.001,
#     0.01,
# )
#
# # Specify the integration range
# integration_range = (0, 6000)
#
# # Create Ode solver for the given abstract reaction system
# scipy_ode = ScipyOde()
#
# # Set the abstract ode system
# scipy_ode.set_abstract_ode_system(aos)
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
# output.plot()
#
#
# # The following solver uses the matlab engine for python to compute the solutions to the ODEs
# # matlab_ode = MatlabOde(aos, initial_conditions=initial_conditions, integration_range=integration_range,
# #                       parameters=parameters, solver=MatlabOdeSolvers.ode45)
#
# # matlab_ode.solve().save(name).plot() # solve the ODEs, save the output and plot it afterwards


