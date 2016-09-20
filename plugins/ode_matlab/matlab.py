##
#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys
import matlab.engine
import enum
from plugins.ode_plugin import OdePlugin

use_log = True


def _log(message):
    global use_log
    if use_log:
        print(message)


class MatlabOdeSolvers(enum.Enum):
    """
    Choose your MATLAB ode solver from this enum.
    """
    ode45 = "45"
    ode23 = "23"
    ode113 = "113"
    ode15s = "15s"
    ode23s = "23s"
    ode23t = "23t"
    ode23tb = "23tb"
    ode15i = "15i"


class MatlabOde(OdePlugin):
    """
    Wrapper for working with odes using the MATLAB python engine.
    Meant for REAL numbers.
    """
    ode_solver = MatlabOdeSolvers.ode45
    integration_range = (0, 0)
    init_conditions = (0,)

    def __init__(self, eq_system="", solver=MatlabOdeSolvers.ode45, integration_range=(0, 0), init_conditions=(0,)):
        super().__init__(eq_system, integration_range, init_conditions)
        if isinstance(solver, MatlabOdeSolvers):
            self.ode_solver = solver

        _log("Starting MATLAB engine...")
        self.engine = matlab.engine.start_matlab()
        _log("Started.")

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
        _log("Solving ode using MATLAB")
        self.engine.workspace['y0'] = matlab.double(self.init_conditions)
        self.engine.workspace['tspan'] = matlab.double(self.integration_range)

        if len(self.diff) > 0:
            eval_str = "ode" + str(self.ode_solver.value) + "(" + self.diff + ", tspan, y0)"
            tres, yres = self.engine.eval(eval_str, nargout=2)
            self.engine.clear(nargout=0)
            return tres, yres
        else:
            return None

    def close_engine(self):
        _log("Closing MATLAB engine...")
        self.engine.exit()
        _log("Closed")

    def __del__(self):
        self.close_engine()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
