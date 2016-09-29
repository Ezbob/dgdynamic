from src.mod_interface.ode_generator import AbstractOdeSystem
from src.plugins.ode_scipy.scipy import ScipyOde
from src.converters.scipy_converter import get_scipy_lambda
from src.utils.project_utils import set_logging
from src.plugins.ode_scipy.scipy import ScipyOdeSolvers
#from src.plugins.ode_matlab.matlab import MatlabOde # linking order is important so don't make this the first import
import random


set_logging(new_session=True)


aos = AbstractOdeSystem("""
A -> B + B
B -> A
B -> C
C -> D + D
D -> C
""")

name = "abstractReactions1"
init = [1.0] * aos.ode_count
parameters = [1.0] * aos.reaction_count
parameters[2] = 5
parameters[3] = 5
initial_conditions = {0: init}
integration_range = (0, 1)

#matlab_ode = MatlabOde(aos, initial_conditions=initial_conditions, integration_range=integration_range,
#                       parameters=parameters)

#matlab_ode.solve().save(name).plot()

scipy_ode = ScipyOde(aos, initial_condition=initial_conditions, integration_range=integration_range,
                     parameters=parameters)

scipy_ode.solve().save(name).plot()

