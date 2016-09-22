from plugins.ode_scipy.scipy import ScipyOde
from plugins.ode_matlab.matlab import MatlabOde # linking order is important so don't make this the first import
from plugins.ode_plugin import set_logging

set_logging(new_session=True)

#matlab_ode = MatlabOde("@(y,t) y * 2 - 3", integration_range=(0, 5), init_conditions={0: 4})

#output = matlab_ode.solve()

#print(output)


#output.plot()

scipy_ode = ScipyOde(lambda y, t: y * 2 - 3, integration_range=(0, 5), initial_condition={0: 4})

output = scipy_ode.solve()
output.save()

#print(output)

#output.plot()
