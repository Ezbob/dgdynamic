##
#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys
import matlab.engine


class MatlabOde:

    ode_solver = "ode45"
    integration_range = (0, 0)
    init_conditions = (0,)

    def __init__(self, eq_system):
        if isinstance(eq_system, str):
            self.diff = eq_system
        self.engine = matlab.engine.start_matlab()

    def set_integration_range(self, range_tuple):
        if isinstance(range_tuple, (tuple, list)):
            self.integration_range = range_tuple
        else:
            self.engine.exit()
            raise TypeError("Range not a tuple")

    def set_initial_conditions(self, conditions):
        if isinstance(conditions, (tuple, list)):
            self.integration_range = conditions
        else:
            self.engine.exit()
            raise TypeError("Range not a tuple")

    def set_ode_solver(self, name):
        if isinstance(name, str):
            self.ode_solver = name

    def solve(self):
        self.engine.workspace['y0'] = matlab.double(self.init_conditions)
        self.engine.workspace['tspan'] = matlab.double(self.integration_range)

        tres, yres = self.engine.eval(self.ode_solver + "(" + self.diff + ", tspan, y0)", nargout=2)
        self.engine.clear()
        return tres, yres

    def __del__(self):
        self.engine.exit()


if __name__ != "__main__":
    pass
else:
    print("Plugin not meant as standalone application", file=sys.stderr)