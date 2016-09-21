from plugins.ode_matlab.matlab import MatlabOde
from plugins.ode_plugin import set_logging, plot
import subprocess

set_logging()

matlab_ode = MatlabOde("@(y,t) y * 2 - 3", integration_range=(0, 5), init_conditions={0: 4})

ts, ys = matlab_ode.solve()

#print(type(str(ts)))
#print(type(str(ys)))

plot(ys, ts)
