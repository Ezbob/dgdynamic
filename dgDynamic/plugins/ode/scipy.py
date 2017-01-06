import sys
import scipy.integrate
from dgDynamic.utils.exceptions import SimulationError
from dgDynamic.choices import ScipyOdeSolvers, SupportedOdePlugins
from dgDynamic.converters.ode.scipy_converter import get_scipy_lambda
from dgDynamic.converters.convert_base import get_initial_values
from dgDynamic.plugins.ode.ode_plugin import OdePlugin
from dgDynamic.utils.project_utils import LogMixin
from dgDynamic.output import SimulationOutput
from dgDynamic.config.settings import config
import dgDynamic.utils.messages as messages

name = SupportedOdePlugins.SciPy


class ScipyOde(OdePlugin, LogMixin):
    """
    Scipy ODE solver plugin
    """
    def __init__(self, simulator, solver_method=ScipyOdeSolvers.VODE, delta_t=0.1, initial_t=0):
        super().__init__(simulator, delta_t=delta_t, initial_t=initial_t, integrator_mode=solver_method)

    def simulate(self, simulation_range, initial_conditions, rate_parameters, drain_parameters=None, *args, **kwargs) \
            -> SimulationOutput:
        ode_function = get_scipy_lambda(self._simulator, rate_parameters, drain_parameters)

        if not ode_function:
            if config.getboolean('Logging', 'ENABLED_LOGGING'):
                self.logger.error("Scipy ode function was not generated")
            messages.print_solver_done(name, method_name=self.integrator_mode.name, was_failure=True)
            return SimulationOutput(name, simulation_range,
                                    errors=(SimulationError("Ode function could not be generated"),))

        try:
            ode_function = eval(ode_function)
        except SyntaxError:
            if config.getboolean('Logging', 'ENABLE_LOGGING'):
                self.logger.error("Scipy ode function was not generated; syntax error")
            messages.print_solver_done(name, method_name=self.integrator_mode.name, was_failure=True)
            return SimulationOutput(name, simulation_range, self._simulator.symbols,
                                    errors=(SimulationError("Internal syntax error encountered")))

        initial_y = get_initial_values(initial_conditions, self._simulator.symbols)

        self.logger.debug("Started solving using Scipy with method {}".format(self.integrator_mode.value))
        self.logger.debug("Initial conditions are {}, range: {} and dt: {} ".format(initial_conditions,
                                                                                    simulation_range, self.delta_t))

        y_solution = list()
        t_solution = list()
        solver = scipy.integrate.ode(ode_function).set_integrator(self.integrator_mode.value, **kwargs)
        solver.set_initial_value(y=initial_y, t=self.initial_t)
        solver.t = simulation_range[0]

        def fixed_step_integration():
            try:
                while solver.successful() and solver.t <= simulation_range[1]:
                    y_solution.append(solver.y)
                    t_solution.append(solver.t)
                    solver.integrate(solver.t + self.delta_t)
            except SystemError as integration_error:
                self.logger.exception("Integration process failed", integration_error)
                messages.print_solver_done(name, method_name=self.integrator_mode.name, was_failure=True)
                return SimulationOutput(name, simulation_range, self._simulator.symbols,
                                        dependent=y_solution, independent=t_solution,
                                        errors=(SimulationError("Integration failure"),))

            self.logger.debug("Solving finished using fixed step integration")
            messages.print_solver_done(name, method_name=self.integrator_mode.name)
            return SimulationOutput(name, user_sim_range=simulation_range,
                                    dependent=y_solution, independent=t_solution,
                                    symbols=self._simulator.symbols, ignore=self._simulator.ignored,
                                    solver_method=self.integrator_mode)

        def variable_step_integration():

            def solution_getter(t, y):
                y_solution.append(y.copy())
                t_solution.append(t)

            solver.set_solout(solout=solution_getter)

            try:
                while solver.successful() and solver.t < simulation_range[1]:
                    solver.integrate(simulation_range[1], step=True)
            except SystemError as integration_error:
                self.logger.exception("Integration process failed", integration_error)
                messages.print_solver_done(name, method_name=self.integrator_mode.name, was_failure=True)
                return SimulationOutput(name, simulation_range, self._simulator.symbols,
                                        dependent=y_solution, independent=t_solution,
                                        errors=(SimulationError("Integration failure"),))

            self.logger.debug("Solving finished using variable step integration")
            messages.print_solver_done(name, method_name=self.integrator_mode.name)
            return SimulationOutput(name, simulation_range, dependent=y_solution, independent=t_solution,
                                    symbols=self._simulator.symbols, ignore=self._simulator.ignored,
                                    solver_method=self.integrator_mode)

        if self.integrator_mode is ScipyOdeSolvers.DOP853 or self.integrator_mode is ScipyOdeSolvers.DOPRI5:
            return variable_step_integration()
        else:
            return fixed_step_integration()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
