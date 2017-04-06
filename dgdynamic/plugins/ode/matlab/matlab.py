#  Matlab ode solver plugin
#  This plugin uses the matlab python engine to approximate solutions to ODEs
##
import sys
import enum
import matlab.engine
import dgdynamic.utils.messages as messages
from dgdynamic.choices import MatlabOdeSolvers, SupportedOdePlugins
from dgdynamic.base_converters.convert_base import get_initial_values
from dgdynamic.output import SimulationOutput
from dgdynamic.plugins.ode.matlab.matlab_converter import get_matlab_lambda
from dgdynamic.plugins.ode.ode_plugin import OdePlugin
from dgdynamic.utils.exceptions import SimulationError
from dgdynamic.utils.project_utils import LogMixin
from dgdynamic.plugins.sim_validation import simulation_parameter_validate

name = SupportedOdePlugins.MATLAB


class MatlabOde(OdePlugin, LogMixin):
    """
    Wrapper for working with odes using the MATLAB python engine.
    """
    def __init__(self, simulator, method=MatlabOdeSolvers.ode45):
        super().__init__(simulator, method=method, delta_t=None)

        self._logger.debug("Starting MATLAB engine...")
        self.engine = matlab.engine.start_matlab()
        self._logger.debug("MATLAB engine started.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear_workspace()
        self.engine.exit()

    def simulate(self, end_t, initial_conditions, rate_parameters, drain_parameters=None, *args, **kwargs):
        simulation_parameter_validate(end_t=end_t, initial_conditions=initial_conditions,
                                      rates_params=rate_parameters, drain_params=drain_parameters)

        ode_function = get_matlab_lambda(simulator=self._simulator, parameter_substitutions=rate_parameters,
                                         drain_substitutions=drain_parameters)

        if ode_function is None or len(ode_function) == 0:
            self._logger.error("Matlab ode function was not generated")
            messages.print_solver_done(name, method_name=self.method.name, was_failure=True)
            return SimulationOutput(name, (self.initial_t, end_t), self._simulator.symbols,
                                    errors=(SimulationError("Ode function could not be generated"),))

        self._logger.debug("Solving ode using MATLAB")

        conditions = get_initial_values(initial_conditions, self._simulator.symbols)

        if isinstance(conditions, (list, tuple)):
            self.add_to_workspace('y0', matlab.double(conditions))
        else:
            # python 3 returns a view not a list of values
            self.add_to_workspace('y0', matlab.double(list(conditions)))

        self.add_to_workspace('tspan', matlab.double((self.initial_t, end_t)))

        eval_str = "ode" + str(self.method.value) + "(" + ode_function + ", tspan, y0)"
        self._logger.debug("evaluating matlab \
expression: {} with tspan: {} and y0: {}".format(eval_str, (self.initial_t, end_t), initial_conditions))

        t_result, y_result = self.engine.eval(eval_str, nargout=2)
        if len(t_result) >= 2:
            self.delta_t = t_result._data[1] - t_result._data[0]
        self.engine.clear(nargout=0)
        self._logger.debug("Successfully solved")

        # http://stackoverflow.com/questions/30013853/convert-matlab-double-array-to-python-array
        def convert_matrix(double_matrix):
            row_width = double_matrix.size[0]
            for x in range(row_width):
                yield double_matrix._data[x::row_width].tolist()

        # flat that list
        t_result = tuple(a for i in t_result for a in i)
        y_result = tuple(convert_matrix(y_result))

        self._logger.info("Return output object")
        messages.print_solver_done(name, method_name=self.method.name)
        return SimulationOutput(solved_by=name, user_sim_range=(self.initial_t, end_t),
                                symbols=self._simulator.symbols,
                                dependent=y_result, independent=t_result,
                                ignore=self._simulator.ignored, solver_method=self.method)

    def close_engine(self):
        self._logger.debug("Closing MATLAB engine...")
        self.engine.exit()
        self._logger.debug("Closed")

    def add_to_workspace(self, key, value):
        if isinstance(key, str):
            self.engine.workspace[key] = value
        return self

    def get_from_workspace(self, key):
        if isinstance(key, str):
            return self.engine.workspace[key]
        return self

    def clear_workspace(self):
        self.engine.clear(nargout=0)
        return self

    @property
    def method(self):
        if isinstance(self._method, enum.Enum):
            return self._method
        elif isinstance(self._method, str):
            for supported in MatlabOdeSolvers:
                name, value = supported.name.lower().strip(), supported.value.lower().strip()
                user_method = self._method.lower().strip()
                if user_method == name or user_method == value:
                    return supported

    @method.setter
    def method(self, value):
        self._method = value

    def __del__(self):
        if hasattr(self, "engine"):
            self.engine.exit()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
