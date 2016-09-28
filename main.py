from src.mod_interface.ode_generator import AbstractOdeSystem
from src.converters import matlab_converter
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

initial_conditions = {0: range(1, len(aos.symbols) + 1)} # 1, 3, 5, 7
func = matlab_converter.get_malab_lambda(aos, list(range(1, len(aos.symbols) + 1)))
matlab_ode = MatlabOde(func, initial_conditions=initial_conditions, integration_range=(0, 10))
matlab_ode.solve().plot()

# matlab_ode = MatlabOde("@(t, y) y * 2 - 3", integration_range=(0, 5), initial_conditions={0: 4})
#
# output = matlab_ode.solve()
#
# output.save(name="firstordertest")
# output.plot()
# matlab_ode.set_ode_function("@(t,y) [ y(2); (1 - y(1) ^ 2) * y(2) - y(1) ]")\
#     .set_initial_conditions({0: [2, 3]}).set_integration_range((-10, 10))
#
# output = matlab_ode.solve()
# output.save(name="secondordertest")
# output.plot()
#
# scipy_ode = ScipyOde("lambda t, y: y * 2 - 3", integration_range=(0, 5), initial_condition={0: 4})
#
# output = scipy_ode.solve()
# output.save("firstordertest")
# print(output)
# output.plot()
#
#
# def f(t, y):
#     return [y[1], (1 - y[0] ** 2) * y[1] - y[0]]
#
# scipy_ode.set_ode_function(f).set_integration_range((-10, 10)).set_initial_conditions({0: [2, 3]})
#
# output = scipy_ode.solve()
# output.save("secondordertest")
# print(output)
# output.plot()
