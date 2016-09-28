from src.mod_interface.ode_generator import AbstractOdeSystem
from src.plugins.ode_scipy.scipy import ScipyOde
from src.plugins.ode_matlab.matlab import MatlabOde # linking order is important so don't make this the first import
from src.utils.project_utils import set_logging

set_logging(new_session=True)

aos = AbstractOdeSystem("""
A + B -> C + C
A + C -> D
C -> E + F
F + F -> B
""")

name = "abstractReactions1"
initial_conditions = {0: range(1, len(aos.symbols) + 1)}
integration_range = (0, 10)
parameters = range(1, len(aos.symbols) + 1)

matlab_ode = MatlabOde(aos, initial_conditions=initial_conditions, integration_range=integration_range,
                       parameters=parameters)

matlab_ode.solve().save(name).plot()

scipy_ode = ScipyOde(aos, initial_condition=initial_conditions, integration_range=integration_range,
                     parameters=parameters)

scipy_ode.solve().save(name).plot()

matlab_ode.set_ode_function("@(t, y) y * 2 - 3").set_integration_range((0, 5))\
    .set_initial_conditions({0: 4})

output = matlab_ode.solve()

output.save(name="firstordertest")
output.plot()
matlab_ode.set_ode_function("@(t,y) [ y(2); (1 - y(1) ^ 2) * y(2) - y(1) ]")\
    .set_initial_conditions({0: [2, 3]}).set_integration_range((-10, 10))

output = matlab_ode.solve()
output.save(name="secondordertest")
output.plot()

scipy_ode.set_ode_function("lambda t, y: y * 2 - 3")\
    .set_integration_range((0, 5)).set_initial_conditions({0: 4})

output = scipy_ode.solve()
output.save("firstordertest")
print(output)
output.plot()


def f(t, y):
    return [y[1], (1 - y[0] ** 2) * y[1] - y[0]]

scipy_ode.set_ode_function(f).set_integration_range((-10, 10)).set_initial_conditions({0: [2, 3]})

output = scipy_ode.solve()
output.save("secondordertest")
print(output)
output.plot()
