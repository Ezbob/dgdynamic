#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys
import matlab.engine
import enum
from plugins.ode_plugin import OdePlugin, LogMixin, OdeOutput
from config import SupportedSolvers


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
        if isinstance(conditions, dict):
            self.initial_conditions = conditions
        else:
            self.engine.exit()
            raise TypeError("Initial conditions should be formulated as a dictionary t -> y")

    def set_ode_method(self, name):
        if isinstance(name, MatlabOdeSolvers):
            self.ode_solver = name

    def set_ode_function(self, ode_function):
        if isinstance(ode_function, (callable, str)):
            self.user_function = ode_function

    def add_to_workspace(self, key, value):
        if isinstance(key, str):
            self.engine.workspace[key] = value

    def get_from_workspace(self, key):
        if isinstance(key, str):
            return self.engine.workspace[key]

    def clear_workspace(self):
        self.engine.clear()

    def solve(self):
        if self.user_function is None:
            return None
        self.logger.debug("Solving ode using MATLAB")
        conditions = self.initial_conditions.values()
        if isinstance(conditions, (list, tuple)):
            self.add_to_workspace('y0', matlab.double(conditions))
        else:
            # python 3 returns a view not a list of values
            self.add_to_workspace('y0', matlab.double(list(conditions)))

        self.add_to_workspace('tspan', matlab.double(self.integration_range))

        if len(self.user_function) > 0:
            eval_str = "ode" + str(self.ode_solver.value) + "(" + self.user_function + ", tspan, y0)"
            self.logger.debug("evaluating matlab \
expression: {} with tspan: {} and y0: {}".format(eval_str, self.integration_range, self.initial_conditions))
            tres, yres = self.engine.eval(eval_str, nargout=2)
            if len(tres) >= 2:
                self.delta_t = tres._data[1] - tres._data[0]
            self.engine.clear(nargout=0)
            self.logger.debug("Successfully solved")

            # http://stackoverflow.com/questions/30013853/convert-matlab-double-array-to-python-array
            # plus some base case I figured out
            def convert_matrix(double_matrix):
                row_width = double_matrix.size[0]
                converts = []
                for x in range(row_width):
                    converts.append(double_matrix._data[x::row_width].tolist())
                return converts

            # flat that list
            tres = [a for i in convert_matrix(tres) for a in i]
            yres = convert_matrix(yres)

            return OdeOutput(solved_by=SupportedSolvers.Matlab, dependent=yres, independent=tres)
        else:
            self.logger.debug("Empty ode function. Aborting...")
            return None

    def close_engine(self):
        self.logger.debug("Closing MATLAB engine...")
        self.engine.exit()
        self.logger.debug("Closed")

    def __del__(self):
        self.engine.exit()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
