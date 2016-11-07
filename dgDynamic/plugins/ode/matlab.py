#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys
import matlab.engine
from dgDynamic.choices import MatlabOdeSolvers, SupportedOdePlugins
from dgDynamic.converters.ode.matlab_converter import get_matlab_lambda
from dgDynamic.converters.ode.converter_ode import get_initial_values
from dgDynamic.plugins.ode.ode_plugin import OdePlugin, sanity_check
from dgDynamic.plugins.plugin_base import SimulationOutput
from dgDynamic.simulators.ode_simulator import ODESystem
from dgDynamic.utils.project_utils import LogMixin


class MatlabOde(OdePlugin, LogMixin):
    """
    Wrapper for working with odes using the MATLAB python engine.
    """
    def __init__(self, eq_system=None, solver=MatlabOdeSolvers.ode45, integration_range=None, initial_conditions=None,
                 parameters=None):

        super().__init__(eq_system, integration_range=integration_range, initial_conditions=initial_conditions,
                         parameters=parameters, ode_solver=solver, converter_function=get_matlab_lambda)

        self.logger.debug("Starting MATLAB engine...")
        self.engine = matlab.engine.start_matlab()
        self.logger.debug("MATLAB engine started.")

    def __call__(self, integration_range=None, initial_conditions=None, parameters=None, ode_solver=None, **kwargs):
        solver_choice = ode_solver if ode_solver is not None else MatlabOdeSolvers.ode45
        return super().__call__(solver_choice, integration_range, initial_conditions, parameters, **kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.clear(nargout=0)
        self.engine.exit()

    def solve(self, **kwargs) -> SimulationOutput:
        if type(self._abstract_system) is ODESystem:
            self._user_function = get_matlab_lambda(abstract_ode_system=self._abstract_system,
                                                    parameter_substitutions=self.parameters)
        if self._user_function is None:
            self.logger.error("User function was not generated")
            return None

        self.logger.debug("Solving ode using MATLAB")

        conditions = get_initial_values(self.initial_conditions, self._symbols)
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

            self.logger.info("Return output object")
            return SimulationOutput(solved_by=SupportedOdePlugins.Matlab, dependent=yres, independent=tres,
                                    ignore=self._ignored, solver_method=self._ode_solver,
                                    abstract_system=self._abstract_system)
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
        if hasattr(self, "engine"):
            self.engine.exit()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
