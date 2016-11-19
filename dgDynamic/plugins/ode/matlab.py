#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys
import matlab.engine
from dgDynamic.utils.exceptions import SimulationError
from dgDynamic.choices import MatlabOdeSolvers, SupportedOdePlugins
from dgDynamic.converters.ode.matlab_converter import get_matlab_lambda
from dgDynamic.converters.ode.converter_ode import get_initial_values
from dgDynamic.plugins.ode.ode_plugin import OdePlugin, sanity_check
from dgDynamic.plugins.plugin_base import SimulationOutput
from dgDynamic.utils.project_utils import LogMixin
import dgDynamic.utils.messages as messages

name = SupportedOdePlugins.MATLAB.name


class MatlabOde(OdePlugin, LogMixin):
    """
    Wrapper for working with odes using the MATLAB python engine.
    """
    def __init__(self, eq_system=None, solver=MatlabOdeSolvers.ode45, simulation_range=(0, 0), initial_conditions=None,
                 rate_parameters=None):

        super().__init__(eq_system, simulation_range=simulation_range, initial_conditions=initial_conditions,
                         rate_parameters=rate_parameters, ode_method=solver)

        self.logger.debug("Starting MATLAB engine...")
        self.engine = matlab.engine.start_matlab()
        self.logger.debug("MATLAB engine started.")

    def __call__(self, simulation_range, initial_conditions, rate_parameters, diffusion_parameters=None,
                 ode_solver=None, **kwargs):
        solver_choice = ode_solver if ode_solver is not None else MatlabOdeSolvers.ode45
        return super().__call__(simulation_range=simulation_range, initial_conditions=initial_conditions,
                                rate_parameters=rate_parameters, diffusion_parameters=diffusion_parameters,
                                ode_solver=solver_choice, **kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.clear(nargout=0)
        self.engine.exit()

    def solve(self, **kwargs) -> SimulationOutput:
        ode_function = get_matlab_lambda(abstract_ode_system=self._simulator,
                                         parameter_substitutions=self.parameters)

        if ode_function is None or len(ode_function) == 0:
            self.logger.error("Matlab ode function was not generated")
            messages.print_solver_done(name, method_name=self.ode_method.name, was_failure=True)
            return SimulationOutput(SupportedOdePlugins.MATLAB,
                                    errors=(SimulationError("Ode function could not be generated"),))

        self.logger.debug("Solving ode using MATLAB")

        conditions = get_initial_values(self.initial_conditions, self._simulator.symbols)
        sanity_check(self, list(conditions))

        if isinstance(conditions, (list, tuple)):
            self.add_to_workspace('y0', matlab.double(conditions))
        else:
            # python 3 returns a view not a list of values
            self.add_to_workspace('y0', matlab.double(list(conditions)))

        self.add_to_workspace('tspan', matlab.double(self.simulation_range))

        eval_str = "ode" + str(self._ode_method.value) + "(" + ode_function + ", tspan, y0)"
        self.logger.debug("evaluating matlab \
expression: {} with tspan: {} and y0: {}".format(eval_str, self.simulation_range, self.initial_conditions))

        t_result, y_result = self.engine.eval(eval_str, nargout=2)
        if len(t_result) >= 2:
            self.delta_t = t_result._data[1] - t_result._data[0]
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
        t_result = [a for i in t_result for a in i]
        y_result = convert_matrix(y_result)

        self.logger.info("Return output object")
        messages.print_solver_done(name, method_name=self.ode_method.name)
        return SimulationOutput(solved_by=SupportedOdePlugins.MATLAB, dependent=y_result, independent=t_result,
                                ignore=self._simulator.ignored, solver_method=self._ode_method,
                                abstract_system=self._simulator)

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
