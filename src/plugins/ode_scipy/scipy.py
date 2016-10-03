import sys
from enum import Enum
from typing import Union
from ...mod_interface.ode_generator import AbstractOdeSystem
from ..ode_plugin import OdePlugin, OdeOutput, sanity_check, get_initial_values
from scipy.integrate import ode
from ...converters.scipy_converter import get_scipy_lambda
from config import SupportedSolvers
from ...utils.project_utils import LogMixin
from array import array


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
    # the default method uses the real value solver VODE
    _solver_method = ScipyOdeSolvers.VODE

    def __init__(self, eq_system=None, integration_range=(0, 0), initial_condition=None, delta_t=0.05, parameters=None,
                 solver_method=ScipyOdeSolvers.VODE, initial_t=0):
        super().__init__(eq_system, integration_range, initial_condition, delta_t=delta_t, parameters=parameters,
                         initial_t=initial_t)

        self._solver_method = solver_method
        if isinstance(eq_system, AbstractOdeSystem):
            self._user_function = get_scipy_lambda(eq_system, parameters)
            self._symbols = eq_system.symbols
        else:
            self._symbols = None

    def solve(self) -> OdeOutput:
        if not self._user_function:
            return None
        if type(self._user_function) is str:
            self._user_function = eval(self._user_function)

        self.logger.debug("Checking scipy parameters...")
        initial_y = get_initial_values(self.initial_conditions, self._symbols)
        sanity_check(self, initial_y)

        self.logger.debug("Started solving using Scipy with method {}".format(self._solver_method.value))
        self.logger.debug("Initial conditions is {}, \
range: {} and dt: {} ".format(self.initial_conditions, self.integration_range, self.delta_t))

        y_solution = list()
        t_solution = list()
        solver = ode(self._user_function).set_integrator(self._solver_method.value.upper())
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

            if len(y_solution) > 0 and len(t_solution) > 0:
                return OdeOutput(SupportedSolvers.Scipy, y_solution, t_solution, self._ignored)
            return None

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

            if len(y_solution) > 0 and len(t_solution) > 0:
                return OdeOutput(SupportedSolvers.Scipy, y_solution, t_solution, self._ignored)
            return None

        if self._solver_method is ScipyOdeSolvers.DOP853 or self._solver_method is ScipyOdeSolvers.DOPRI5:
            self.logger.debug("Solving finished using variable step integration")
            return variable_step_integration()
        else:
            self.logger.debug("Solving finished using fixed step integration")
            return fixed_step_integration()

    def set_ode_solver(self, method: ScipyOdeSolvers):
        self._solver_method = method
        return self


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
