from src.mod_interface.ode_generator import AbstractOdeSystem
from src.plugins.ode_scipy.scipy import ScipyOde
from src.converters.scipy_converter import get_scipy_lambda
from src.utils.project_utils import set_logging
from src.plugins.ode_scipy.scipy import ScipyOdeSolvers
#from src.plugins.ode_matlab.matlab import MatlabOde # linking order is important so don't make this the first import
import random


set_logging(new_session=True)


aos = AbstractOdeSystem("""
A + B -> A + A
C + D -> C + C
C -> E
""")

aos.ignore_species('A', 'D')

name = "abstractReactions1"
init = [random.random() for i in range(aos.species_count)]
parameters = [1.0] * aos.reaction_count
initial_conditions = {0: init}
integration_range = (0, 10)

#matlab_ode = MatlabOde(aos, initial_conditions=initial_conditions, integration_range=integration_range,
#                       parameters=parameters)

#matlab_ode.solve().save(name).plot()

scipy_ode = ScipyOde(aos, initial_condition=initial_conditions, integration_range=integration_range,
                     parameters=parameters)

scipy_ode.solve().save(name).plot()

