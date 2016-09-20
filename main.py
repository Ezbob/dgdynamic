from plugins.ode_matlab.matlab import MatlabOde
from plugins.ode_plugin import set_logging

set_logging()

#import matplotlib.pyplot as plt

matlab_ode = MatlabOde("@(y,t) y * 2 - 3", integration_range=(0, 5), init_conditions={0: 4})

ts, ys = matlab_ode.solve()

print(ts)
print(ys)
#plt.plot(ts, ys)
#plt.show()
