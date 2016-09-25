from plugins.ode_scipy.scipy import ScipyOde
from plugins.ode_matlab.matlab import MatlabOde # linking order is important so don't make this the first import
from plugins.ode_plugin import set_logging

set_logging(new_session=True)

matlab_ode = MatlabOde("@(t, y) y * 2 - 3", integration_range=(0, 5), initial_conditions={0: 4})

output = matlab_ode.solve()

output.save(name="firstordertest")
output.plot()
matlab_ode.set_ode_function("@(t,y) [ y(2); (1 - y(1) ^ 2) * y(2) - y(1) ]")\
    .set_initial_conditions({0: [2, 3]}).set_integration_range((-10, 10))

output = matlab_ode.solve()
output.save(name="secondordertest")
output.plot()

scipy_ode = ScipyOde("lambda t, y: y * 2 - 3", integration_range=(0, 5), initial_condition={0: 4})

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
