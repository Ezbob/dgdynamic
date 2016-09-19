##
#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys
import matlab.engine
from enum import Enum


class MatlabOdeSolvers(Enum):
    ode45 = "45"
    ode23 = "23"
    ode113 = "113"
    ode15s = "15s"
    ode23s = "23s"
    ode23t = "23t"
    ode23tb = "23tb"
    ode15i = "15i"


class MatlabOde:
    """
    Wrapper for working with odes using the MATLAB python engine.
    """
    ode_solver = MatlabOdeSolvers.ode45
    integration_range = (0, 0)
    init_conditions = (0,)

    def __init__(self, eq_system, solver=MatlabOdeSolvers.ode45, integration_range=(0, 0), init_conditions=(0,)):
        if isinstance(eq_system, str):
            self.diff = eq_system
        if isinstance(integration_range, (tuple, list)):
            self.integration_range = integration_range
        if isinstance(init_conditions, (tuple, list)):
            self.init_conditions = init_conditions
        if isinstance(solver, MatlabOdeSolvers):
            self.ode_solver = solver

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
        if isinstance(name, MatlabOdeSolvers):
            self.ode_solver = name

    def solve(self):
        self.engine.workspace['y0'] = matlab.double(self.init_conditions)
        self.engine.workspace['tspan'] = matlab.double(self.integration_range)

        eval_str = "ode" + str(self.ode_solver.value) + "(" + self.diff + ", tspan, y0)"
        tres, yres = self.engine.eval(eval_str, nargout=2)
        self.engine.clear()
        return tres, yres

    def __del__(self):
        self.engine.exit()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
