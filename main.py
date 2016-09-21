from plugins.ode_matlab.matlab import MatlabOde
from plugins.ode_plugin import set_logging

set_logging()

matlab_ode = MatlabOde("@(y,t) y * 2 - 3", integration_range=(0, 5), init_conditions={0: 4})

output = matlab_ode.solve()

print(output)
#print(type(str(ts)))
#print(type(str(ys)))

output.plot()
