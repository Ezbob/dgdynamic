import sys
from scipy.integrate import ode
from dgDynamic.utils.exceptions import SimulationError
from dgDynamic.choices import ScipyOdeSolvers, SupportedOdePlugins
from dgDynamic.converters.ode.scipy_converter import get_scipy_lambda
from dgDynamic.converters.convert_base import get_initial_values
from dgDynamic.plugins.ode.ode_plugin import OdePlugin, parameter_validation
from dgDynamic.utils.project_utils import LogMixin
from dgDynamic.plugins.plugin_base import SimulationOutput
from dgDynamic.config.settings import config
import dgDynamic.utils.messages as messages

name = SupportedOdePlugins.SciPy.name


class ScipyOde(OdePlugin, LogMixin):
    """
    Scipy ODE solver plugin
    """
    def __init__(self, simulator, simulation_range=(0, 0), initial_condition=None, rate_parameters=None,
                 drain_parameters=None, solver_method=ScipyOdeSolvers.VODE, delta_t=0.1, initial_t=0):
        super().__init__(simulator, simulation_range=simulation_range, initial_conditions=initial_condition,
                         drain_parameters=drain_parameters, delta_t=delta_t, rate_parameters=rate_parameters,
                         initial_t=initial_t, ode_method=solver_method)

    def __call__(self, simulation_range, initial_conditions, rate_parameters, drain_parameters=None, delta_t=0.1,
                 ode_solver=None, **kwargs):
        solver_choice = ode_solver if ode_solver is not None else ScipyOdeSolvers.VODE
        return super().__call__(simulation_range=simulation_range, initial_conditions=initial_conditions,
                                rate_parameters=rate_parameters, ode_solver=solver_choice,
                                drain_parameters=drain_parameters, delta_t=delta_t, **kwargs)

    def solve(self, **kwargs) -> SimulationOutput:
        ode_function = get_scipy_lambda(self._simulator, self.parameters, self.drain_parameters)

        if not ode_function:
            if config.getboolean('Logging', 'ENABLED_LOGGING'):
                self.logger.error("Scipy ode function was not generated")
            messages.print_solver_done(name, method_name=self.ode_method.name, was_failure=True)
            return SimulationOutput(SupportedOdePlugins.SciPy,
                                    errors=(SimulationError("Ode function could not be generated"),))

        try:
            ode_function = eval(ode_function)
        except SyntaxError:
            if config.getboolean('Logging', 'ENABLE_LOGGING'):
                self.logger.error("Scipy ode function was not generated; syntax error")
            messages.print_solver_done(name, method_name=self.ode_method.name, was_failure=True)
            return SimulationOutput(SupportedOdePlugins.SciPy,
                                    errors=(SimulationError("Internal syntax error encountered")))

        self.logger.debug("Checking scipy parameters...")
        initial_y = get_initial_values(self.initial_conditions, self._simulator.symbols)
        parameter_validation(self, initial_y, self._simulator.reaction_count, self._simulator.species_count)

        self.logger.debug("Started solving using Scipy with method {}".format(self.ode_method.value))
        self.logger.debug("Initial conditions are {}, range: {} and dt: {} ".format(self.initial_conditions,
                                                                                    self.simulation_range,
                                                                                    self.delta_t))

        y_solution = list()
        t_solution = list()
        solver = ode(ode_function).set_integrator(self.ode_method.value, **kwargs)
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
                messages.print_solver_done(name, method_name=self.ode_method.name, was_failure=True)
                return SimulationOutput(solved_by=SupportedOdePlugins.SciPy,
                                        dependent=y_solution, independent=t_solution,
                                        errors=(SimulationError("Integration failure"),))

            self.logger.debug("Solving finished using fixed step integration")
            messages.print_solver_done(name, method_name=self.ode_method.name)
            return SimulationOutput(solved_by=SupportedOdePlugins.SciPy, dependent=y_solution, independent=t_solution,
                                    abstract_system=self._simulator, ignore=self._simulator.ignored,
                                    solver_method=self.ode_method)

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
                messages.print_solver_done(name, method_name=self.ode_method.name, was_failure=True)
                return SimulationOutput(solved_by=SupportedOdePlugins.SciPy,
                                        dependent=y_solution, independent=t_solution,
                                        errors=(SimulationError("Integration failure"),))

            self.logger.debug("Solving finished using variable step integration")
            messages.print_solver_done(name, method_name=self.ode_method.name)
            return SimulationOutput(solved_by=SupportedOdePlugins.SciPy, dependent=y_solution, independent=t_solution,
                                    abstract_system=self._simulator, ignore=self._simulator.ignored,
                                    solver_method=self.ode_method)

        if self.ode_method is ScipyOdeSolvers.DOP853 or self.ode_method is ScipyOdeSolvers.DOPRI5:
            return variable_step_integration()
        else:
            return fixed_step_integration()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
