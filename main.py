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
""").unchanging_species('B', 'D')

name = "abstractReactions1"

initial_conditions = {
    'F': 0.5,
    'B': 1,
    'C': 0,
    'D': 0,
}
parameters = {
    'F + B -> F + F': 0.01,
    'C + F -> C + C': 0.005,
    'B -> F': 0.001,
    'F -> C': 0.001,
    'C -> D': 0.01,
}
integration_range = (0, 6000)

matlab_ode = MatlabOde(aos, initial_conditions=initial_conditions, integration_range=integration_range,
                       parameters=parameters)

matlab_ode.solve().save(name).plot()

scipy_ode = ScipyOde(aos, initial_condition=initial_conditions, integration_range=integration_range,
                     parameters=parameters).set_ode_solver(ScipyOdeSolvers.DOPRI5)

scipy_ode.solve().save(name).plot()

