##
#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys
import matlab.engine
import enum
from plugins.ode_plugin import OdePlugin, LogMixin, OdeOutput


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


class MatlabOde(OdePlugin, LogMixin):
    """
    Wrapper for working with odes using the MATLAB python engine.
    Meant for REAL numbers.
    """
    ode_solver = MatlabOdeSolvers.ode45

    def __init__(self, eq_system="", solver=MatlabOdeSolvers.ode45, integration_range=(0, 0), init_conditions=None):
        super().__init__(eq_system, integration_range=integration_range,  initial_conditions=init_conditions)
        if isinstance(solver, MatlabOdeSolvers):
            self.ode_solver = solver

        self.logger.debug("Starting MATLAB engine...")
        self.engine = matlab.engine.start_matlab()
        self.logger.debug("Started.")

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
        self.logger.debug("Solving ode using MATLAB")
        conditions = self.initial_conditions.values()
        if isinstance(conditions, (list, tuple)):
            self.engine.workspace['y0'] = matlab.double(conditions)
        else:
            # python 3 returns a view not a list of values
            self.engine.workspace['y0'] = matlab.double(list(conditions))

        self.engine.workspace['tspan'] = matlab.double(self.integration_range)

        if len(self.user_function) > 0:
            eval_str = "ode" + str(self.ode_solver.value) + "(" + self.user_function + ", tspan, y0)"
            tres, yres = self.engine.eval(eval_str, nargout=2)
            self.engine.clear(nargout=0)
            return OdeOutput(solvedby='matlab', dependend=yres, independed=tres)
        else:
            return None

    def close_engine(self):
        self.logger.debug("Closing MATLAB engine...")
        self.engine.exit()
        self.logger.debug("Closed")

    def __del__(self):
        self.engine.exit()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
