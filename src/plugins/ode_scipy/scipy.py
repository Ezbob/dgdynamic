import sys
from enum import Enum
from typing import Union
from ...mod_interface.ode_generator import AbstractOdeSystem
from ..ode_plugin import OdePlugin, OdeOutput, sanity_check
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
                 solver_method=ScipyOdeSolvers.VODE):
        super().__init__(eq_system, integration_range, initial_condition, delta_t=delta_t, parameters=parameters)

        self._solver_method = solver_method
        if isinstance(eq_system, AbstractOdeSystem):
            self._user_function = get_scipy_lambda(eq_system, parameters)

    def solve(self) -> OdeOutput:
        if not self._user_function:
            return None
        if type(self._user_function) is str:
            self._user_function = eval(self._user_function)

        initial_t, initial_y = self.initial_conditions.popitem()
        sanity_check(self, initial_y)

        self.logger.debug("Started solving using Scipy with method {}".format(self._solver_method.value))
        self.logger.debug("Initial conditions is {}, \
range: {} and dt: {} ".format(self.initial_conditions, self.integration_range, self.delta_t))

        def fixed_step_integration():
            self.logger.debug("Setting scipy parameters...")

            solver = ode(self._user_function).set_integrator(self._solver_method.value.upper())
            solver.set_initial_value(initial_y, initial_t)
            self.logger.debug("Set.")

            ys = list()
            ts = list()
            solver.t = self.integration_range[0]
            try:
                while solver.successful() and solver.t <= self.integration_range[1]:
                    ts.append(solver.t)
                    ys.append(solver.y)
                    solver.integrate(solver.t + self.delta_t)
            except SystemError:
                return None

            self.logger.debug("Solving finished")
            if len(ys) > 0 and len(ts) > 0:
                return OdeOutput(SupportedSolvers.Scipy, ys, ts, self._ignored)
            return None

        def variable_step_integration():

            y_solution = []
            t_solution = []

            def solution_getter(t, y):
                y_solution.append(y.copy())
                t_solution.append(t)

            solver = ode(self._user_function).set_integrator(self._solver_method.value)
            solver.set_solout(solout=solution_getter)
            solver.set_initial_value(y=initial_y, t=initial_t)
            solver.t = self.integration_range[0]

            while solver.successful() and solver.t < self.integration_range[1]:
                solver.integrate(self.integration_range[1], step=True)

            if len(y_solution) > 0 and len(t_solution) > 0:
                return OdeOutput(SupportedSolvers.Scipy, y_solution, t_solution, self._ignored)
            return None

        if self._solver_method is ScipyOdeSolvers.DOP853 or self._solver_method is ScipyOdeSolvers.DOPRI5:
            return variable_step_integration()
        else:
            return fixed_step_integration()

    def set_ode_solver(self, method: ScipyOdeSolvers):
        self._solver_method = method
        return self


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
