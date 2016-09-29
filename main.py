from src.mod_interface.ode_generator import AbstractOdeSystem
from src.plugins.ode_scipy.scipy import ScipyOde
from src.utils.project_utils import set_logging
#from src.plugins.ode_matlab.matlab import MatlabOde # linking order is important so don't make this the first import
import random


set_logging(new_session=True)

aos = AbstractOdeSystem("""
R + R -> R + R + R
F + R -> F + F
F ->
""")

print(aos.generate_equations())

name = "abstractReactions1"
initial_conditions = {0: [random.random() for i in range(0, len(aos.symbols))]}
integration_range = (0, 100)
parameters = (1, 1, 0.01,)

#matlab_ode = MatlabOde(aos, initial_conditions=initial_conditions, integration_range=integration_range,
#                       parameters=parameters)

#matlab_ode.solve().save(name).plot()

scipy_ode = ScipyOde(aos, initial_condition=initial_conditions, integration_range=integration_range,
                     parameters=parameters)

scipy_ode.solve().save(name).plot(labels=("Rabbits", "Foxes eat Rabbits", "Foxes dies"))

