from src.mod_interface.ode_generator import AbstractOdeSystem
from src.plugins.ode_scipy.scipy import ScipyOdeSolvers, ScipyOde
from src.utils.project_utils import set_logging
from src.plugins.ode_matlab.matlab import MatlabOde, MatlabOdeSolvers
# linking order is important so don't make this the first import

set_logging(new_session=True)

aos = AbstractOdeSystem("""
F + B -> F + F
C + F -> C + C
B -> F
F -> C
C -> D
""")

# Set the species that you wish to remain unchanged in the integration process.
# Since these species don't contribute they don't get saved or plotted
aos.unchanging_species('B', 'D')

# Name of the data set
name = "abstractReactions1"

# Set the initial values for each species
initial_conditions = {
    'F': 0.5,
    'B': 1,
    'C': 0,
    'D': 0,
}

# Set the mass action parameters for each reaction
parameters = {
    'F + B -> F + F': 0.01,
    'C + F -> C + C': 0.005,
    'B -> F': 0.001,
    'F -> C': 0.001,
    'C -> D': 0.01,
}

# Set the integration range. This has to be a tuple of two numbers; a lower bound and a upper bound
integration_range = (0, 6000)

# Create Ode solver for the given abstract reaction system
scipy_ode = ScipyOde(aos)

# Set the solver method from one of the entries in the SciOdeSolvers enumeration
# If none are selected this default to the VODE method for Scipy
scipy_ode.set_ode_solver(ScipyOdeSolvers.VODE)

# Set the integration range
scipy_ode.set_integration_range(integration_range)

# Set the initial conditions
scipy_ode.set_initial_conditions(initial_conditions)

# Set the parameters
scipy_ode.set_parameters(parameters)

# Solve the ODE system to get the output object
output = scipy_ode.solve()

# Save the data to a file in the data folder using the output object
output.save(name)

# Plot the data using the MatPlotLib, also using the output object
output.plot()


# The following solver uses the matlab engine for python to compute the solutions to the ODEs
# matlab_ode = MatlabOde(aos, initial_conditions=initial_conditions, integration_range=integration_range,
#                       parameters=parameters, solver=MatlabOdeSolvers.ode45)

# matlab_ode.solve().save(name).plot() # solve the ODEs, save the output and plot it afterwards


