import sys
from scipy.integrate import ode
from dgDynamic.utils.exceptions import SimulationError
from dgDynamic.choices import ScipyOdeSolvers, SupportedOdePlugins
from dgDynamic.converters.ode.scipy_converter import get_scipy_lambda
from dgDynamic.converters.ode.converter_ode import get_initial_values
from dgDynamic.plugins.ode.ode_plugin import OdePlugin, sanity_check
from dgDynamic.utils.project_utils import LogMixin
from dgDynamic.plugins.plugin_base import SimulationOutput
import dgDynamic.utils.messages as messages

name = SupportedOdePlugins.SciPy.name


class ScipyOde(OdePlugin, LogMixin):
    """
    Scipy ODE solver plugin
    """

    def __init__(self, simulator=None, simulation_range=(0, 0), initial_condition=None, delta_t=0.1, parameters=None,
                 solver=ScipyOdeSolvers.VODE, initial_t=0):
        super().__init__(simulator, simulation_range, initial_condition, delta_t=delta_t, parameters=parameters,
                         initial_t=initial_t, ode_method=solver)

    def __call__(self, simulation_range, initial_conditions, parameters, delta_t=0.1, ode_solver=None,
                 **kwargs):
        solver_choice = ode_solver if ode_solver is not None else ScipyOdeSolvers.VODE
        return super().__call__(simulation_range, initial_conditions, parameters, solver_choice, delta_t, **kwargs)

    def solve(self, **kwargs) -> SimulationOutput:
        name_method = "{} {}".format(name, self.ode_method.name)
        ode_function = get_scipy_lambda(self._simulator, self.parameters)

        if ode_function is None or len(ode_function) == 0:
            self.logger.error("Scipy ode function was not generated")
            messages.print_solver_failure(name_method)
            return SimulationOutput(SupportedOdePlugins.SciPy,
                                    errors=(SimulationError("Ode function could not be generated"),))

        ode_function = eval(ode_function)

        self.logger.debug("Checking scipy parameters...")
        initial_y = get_initial_values(self.initial_conditions, self._simulator.symbols)
        sanity_check(self, initial_y)

        self.logger.debug("Started solving using Scipy with method {}".format(self._ode_method.value))
        self.logger.debug("Initial conditions are {}, \
range: {} and dt: {} ".format(self.initial_conditions, self.simulation_range, self.delta_t))

        y_solution = list()
        t_solution = list()
        solver = ode(ode_function).set_integrator(self._ode_method.value, **kwargs)
        solver.set_initial_value(y=initial_y, t=self.initial_t)
        solver.t = self.simulation_range[0]

        def fixed_step_integration():
            try:
                while solver.successful() and solver.t <= self.simulation_range[1]:
                    y_solution.append(solver.y)
                    t_solution.append(solver.t)
                    solver.integrate(solver.t + self.delta_t)
            except SystemError as integration_error:
                self.logger.exception("Integration process failed", integration_error)
                messages.print_solver_failure(name_method)
                return SimulationOutput(solved_by=SupportedOdePlugins.SciPy,
                                        dependent=y_solution, independent=t_solution,
                                        errors=(SimulationError("Integration failure"),))

            self.logger.debug("Solving finished using fixed step integration")
            messages.print_solver_success(name_method)
            return SimulationOutput(solved_by=SupportedOdePlugins.SciPy, dependent=y_solution, independent=t_solution,
                                    abstract_system=self._simulator, ignore=self._simulator.ignored,
                                    solver_method=self._ode_method)

        def variable_step_integration():

            def solution_getter(t, y):
                y_solution.append(y.copy())
                t_solution.append(t)

            solver.set_solout(solout=solution_getter)

            try:
                while solver.successful() and solver.t < self.simulation_range[1]:
                    solver.integrate(self.simulation_range[1], step=True)
            except SystemError as integration_error:
                self.logger.exception("Integration process failed", integration_error)
                messages.print_solver_failure(name_method)
                return SimulationOutput(solved_by=SupportedOdePlugins.SciPy,
                                        dependent=y_solution, independent=t_solution,
                                        errors=(SimulationError("Integration failure"),))

            self.logger.debug("Solving finished using variable step integration")
            messages.print_solver_success(name_method)
            return SimulationOutput(solved_by=SupportedOdePlugins.SciPy, dependent=y_solution, independent=t_solution,
                                    abstract_system=self._simulator, ignore=self._simulator.ignored,
                                    solver_method=self._ode_method)

        if self._ode_method is ScipyOdeSolvers.DOP853 or self._ode_method is ScipyOdeSolvers.DOPRI5:
            return variable_step_integration()
        else:
            return fixed_step_integration()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
