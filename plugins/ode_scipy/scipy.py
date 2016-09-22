from scipy.integrate import ode
from plugins.ode_plugin import OdePlugin, LogMixin, OdeOutput
from enum import Enum
from config import SupportedSolvers
import sys
import inspect


class ScipyOdeSolvers(Enum):
    """
    Enum representing different ode solver methods available to the Scipy solver
    """
    VODE = "vode"
    ZVODE = "zvode"
    ISODA = "isoda"
    DOPRI5 = "dopri5"
    DOP853 = "dop853"


class ScipyOde(OdePlugin, LogMixin):
    """
    Scipy ODE solver plugin
    """
    # the default method uses the real value solver VODE
    _solverMethod = ScipyOdeSolvers.VODE
    _odesolver = None

    def __init__(self, function=None, integration_range=(0, 0), initial_condition=None, delta_t=0.05):
        if isinstance(function, str):
            super().__init__(eval(function), integration_range, initial_condition, delta_t)
        else:
            super().__init__(function, integration_range, initial_condition, delta_t)

    def solve(self):
        if self.user_function is None or (isinstance(self.user_function, str) and len(self.user_function) == 0):
            return None
        self.logger.debug("Started solving using Scipy with method {}".format(self._solverMethod.value))
        self.logger.debug("Functions is {}, \
initial condition: {} range: {} and dt: {} ".format(inspect.getsource(self.user_function),
                                                    self.initial_conditions, self.integration_range, self.delta_t))

        self.logger.debug("Setting scipy parameters...")
        assert self.integration_range[0] <= self.integration_range[1]

        self._odesolver = ode(self.user_function).set_integrator(str(self._solverMethod.value))
        initial_t, initial_y = self.initial_conditions.popitem()
        self._odesolver.set_initial_value(initial_y, initial_t)
        self.logger.debug("Set.")

        ys = list()
        ts = list()
        self._odesolver.t = self.integration_range[0]
        while self._odesolver.successful() and self._odesolver.t < self.integration_range[1]:
            ts.append(self._odesolver.t)
            ys.append(list(self._odesolver.y))
            self._odesolver.integrate(self._odesolver.t + self.delta_t)

        self.logger.debug("Solving finished")
        if len(ys) > 0 and len(ts) > 0:
            return OdeOutput(SupportedSolvers.Scipy, ys, ts)
        else:
            return None

    def set_integration_range(self, range_tuple):
        if isinstance(range_tuple, tuple):
            self.integration_range = range_tuple

    def set_ode_method(self, function):
        self.user_function = function

    def set_initial_conditions(self, conditions):
        if isinstance(conditions, dict):
            self.initial_conditions = conditions

    def set_ode_function(self, ode_function):
        if isinstance(ode_function, str) or callable(ode_function):
            self.user_function = ode_function

if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
