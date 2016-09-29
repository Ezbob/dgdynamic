import sys
from enum import Enum
from typing import Union
from ...mod_interface.ode_generator import AbstractOdeSystem
from ..ode_plugin import OdePlugin, OdeOutput
from scipy.integrate import ode
from ...converters.scipy_converter import get_scipy_lambda
from config import SupportedSolvers
from ...utils.project_utils import LogMixin


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
    _ode_solver = None

    def __init__(self, eq_system=None, integration_range=(0, 0), initial_condition=None, delta_t=0.05, parameters=None):
        super().__init__(eq_system, integration_range, initial_condition, delta_t=delta_t, parameters=parameters)

        if isinstance(eq_system, AbstractOdeSystem):
            self._user_function = get_scipy_lambda(eq_system, parameters)

    def solve(self) -> OdeOutput:
        if not self._user_function:
            return None
        if type(self._user_function) is str:
            self._user_function = eval(self._user_function)

        self.logger.debug("Started solving using Scipy with method {}".format(self._solver_method.value))
        self.logger.debug("Initial conditions is {}, \
range: {} and dt: {} ".format(self.initial_conditions, self.integration_range, self.delta_t))

        self.logger.debug("Setting scipy parameters...")
        assert self.integration_range[0] <= self.integration_range[1]

        self._ode_solver = ode(self._user_function).set_integrator(self._solver_method.value.upper())
        initial_t, initial_y = self.initial_conditions.popitem()

        assert len(initial_y) == self.ode_count


        self._ode_solver.set_initial_value(initial_y, initial_t)
        self.logger.debug("Set.")

        ys = list()
        ts = list()
        self._ode_solver.t = self.integration_range[0]
        try:
            while self._ode_solver.successful() and self._ode_solver.t <= self.integration_range[1]:
                ts.append(self._ode_solver.t)
                ys.append(self._ode_solver.y)
                self._ode_solver.integrate(self._ode_solver.t + self.delta_t)
        except SystemError:
            return None

        self.logger.debug("Solving finished")
        if len(ys) > 0 and len(ts) > 0:
            return OdeOutput(SupportedSolvers.Scipy, ys, ts)
        else:
            return None

    def set_ode_method(self, method: ScipyOdeSolvers):
        self._solver_method = method
        return self


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
