import sys
from enum import Enum
from src.plugins.ode_plugin import OdePlugin, OdeOutput, sanity_check, get_initial_values
from scipy.integrate import ode
from src.converters.scipy_converter import get_scipy_lambda
from config import SupportedSolvers
from src.utils.project_utils import LogMixin


class ScipyOdeSolvers(Enum):
    """
    Enum representing different ode solver methods available to the Scipy solver
    """
    VODE = "vode"
    ZVODE = "zvode"
    LSODA = "lsoda"
    DOPRI5 = "dopri5"
    DOP853 = "dop853"


class ScipyOde(OdePlugin, LogMixin):
    """
    Scipy ODE solver plugin
    """

    def __init__(self, eq_system=None, integration_range=None, initial_condition=None, delta_t=0.05, parameters=None,
                 solver=ScipyOdeSolvers.VODE, initial_t=0):
        super().__init__(eq_system, integration_range, initial_condition, delta_t=delta_t, parameters=parameters,
                         initial_t=initial_t, solver_method=solver)

    def solve(self) -> OdeOutput:
        self._convert_to_function(get_scipy_lambda)

        if self._user_function is None:
            return None
        if type(self._user_function) is str:
            self._user_function = eval(self._user_function)

        self.logger.debug("Checking scipy parameters...")
        initial_y = get_initial_values(self.initial_conditions, self._symbols,
                                       fuzzy_match=self.initial_condition_prefix_match)
        sanity_check(self, initial_y)

        self.logger.debug("Started solving using Scipy with method {}".format(self._ode_solver.value))
        self.logger.debug("Initial conditions is {}, \
range: {} and dt: {} ".format(self.initial_conditions, self.integration_range, self.delta_t))

        y_solution = list()
        t_solution = list()
        solver = ode(self._user_function).set_integrator(self._ode_solver.value)
        solver.set_initial_value(y=initial_y, t=self.initial_t)
        solver.t = self.integration_range[0]

        def fixed_step_integration():
            try:
                while solver.successful() and solver.t <= self.integration_range[1]:
                    y_solution.append(solver.y)
                    t_solution.append(solver.t)
                    solver.integrate(solver.t + self.delta_t)
            except SystemError as integration_error:
                self.logger.exception("Integration process failed", integration_error)
                return None

            self.logger.debug("Solving finished using fixed step integration")
            return OdeOutput(SupportedSolvers.Scipy, y_solution, t_solution, self._ignored)

        def variable_step_integration():

            def solution_getter(t, y):
                y_solution.append(y.copy())
                t_solution.append(t)

            solver.set_solout(solout=solution_getter)

            try:
                while solver.successful() and solver.t < self.integration_range[1]:
                    solver.integrate(self.integration_range[1], step=True)
            except SystemError as integration_error:
                self.logger.exception("Integration process failed", integration_error)
                return None

            self.logger.debug("Solving finished using variable step integration")
            return OdeOutput(SupportedSolvers.Scipy, y_solution, t_solution, self._ignored)

        if self._ode_solver is ScipyOdeSolvers.DOP853 or self._ode_solver is ScipyOdeSolvers.DOPRI5:
            return variable_step_integration()
        else:
            return fixed_step_integration()


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
