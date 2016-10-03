#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import enum
import sys

import matlab.engine
from ..ode_plugin import OdePlugin, OdeOutput, sanity_check
from ...converters.matlab_converter import get_matlab_lambda
from ...mod_interface.ode_generator import AbstractOdeSystem
from config import SupportedSolvers
from ...utils.project_utils import LogMixin


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
    _ode_solver = MatlabOdeSolvers.ode45

    def __init__(self, eq_system=None, solver=MatlabOdeSolvers.ode45, integration_range=(0, 0), initial_conditions=None,
                 parameters=None):

        super().__init__(eq_system, integration_range=integration_range,  initial_conditions=initial_conditions,
                         parameters=parameters)

        if type(eq_system) is AbstractOdeSystem:
            self._user_function = get_matlab_lambda(eq_system, parameter_substitutions=parameters)

        if isinstance(solver, MatlabOdeSolvers):
            self._ode_solver = solver

        self.logger.debug("Starting MATLAB engine...")
        self.engine = matlab.engine.start_matlab()
        self.logger.debug("Started.")

    def set_ode_solver(self, name: MatlabOdeSolvers):
        if isinstance(name, MatlabOdeSolvers):
            self._ode_solver = name
        return self

    def solve(self) -> OdeOutput:
        if self._user_function is None:
            return None
        self.logger.debug("Solving ode using MATLAB")
        conditions = self.initial_conditions.values()
        sanity_check(self, list(conditions))
        if isinstance(conditions, (list, tuple)):
            self.add_to_workspace('y0', matlab.double(conditions))
        else:
            # python 3 returns a view not a list of values
            self.add_to_workspace('y0', matlab.double(list(conditions)))

        self.add_to_workspace('tspan', matlab.double(self.integration_range))

        if len(self._user_function) > 0:
            eval_str = "ode" + str(self._ode_solver.value) + "(" + self._user_function + ", tspan, y0)"
            self.logger.debug("evaluating matlab \
expression: {} with tspan: {} and y0: {}".format(eval_str, self.integration_range, self.initial_conditions))

            tres, yres = self.engine.eval(eval_str, nargout=2)
            if len(tres) >= 2:
                self.delta_t = tres._data[1] - tres._data[0]
            self.engine.clear(nargout=0)
            self.logger.debug("Successfully solved")

            # http://stackoverflow.com/questions/30013853/convert-matlab-double-array-to-python-array
            def convert_matrix(double_matrix):
                row_width = double_matrix.size[0]
                converts = []
                for x in range(row_width):
                    converts.append(double_matrix._data[x::row_width].tolist())
                return converts

            # flat that list
            tres = [a for i in tres for a in i]
            yres = convert_matrix(yres)

            return OdeOutput(solved_by=SupportedSolvers.Matlab, dependent=yres, independent=tres, ignore=self._ignored)
        else:
            self.logger.debug("Empty ode function. Aborting...")
            return None

    def close_engine(self):
        self.logger.debug("Closing MATLAB engine...")
        self.engine.exit()
        self.logger.debug("Closed")

    def add_to_workspace(self, key, value):
        if isinstance(key, str):
            self.engine.workspace[key] = value
        return self

    def get_from_workspace(self, key):
        if isinstance(key, str):
            return self.engine.workspace[key]
        return self

    def clear_workspace(self):
        self.engine.clear()
        return self

    def __del__(self):
        self.engine.exit()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
