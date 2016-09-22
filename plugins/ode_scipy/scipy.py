from scipy.integrate import ode
from plugins.ode_plugin import OdePlugin, LogMixin, OdeOutput
from enum import Enum
from config import SupportedSolvers
import sys


class ScipyOdeSolvers(Enum):
    VODE = "vode"
    ZVODE = "zvode"
    ISODA = "isoda"
    DOPRI5 = "dopri5"
    DOP853 = "dop853"


class ScipyOde(OdePlugin, LogMixin):

    solverMethod = ScipyOdeSolvers.VODE

    def __init__(self, function, integration_range=(0, 0), initial_condition=None, delta_t=0.05):
        if isinstance(function, str):
            super().__init__(eval(function), integration_range, initial_condition, delta_t)
        else:
            super().__init__(function, integration_range, initial_condition, delta_t)
        self.logger.debug("Initializing SciPy module...")
        self._odesolver = ode(self.user_function).set_integrator(str(self.solverMethod.value))
        initial_t, initial_y = self.initial_conditions.popitem()
        self._odesolver.set_initial_value(initial_y, initial_t)
        self.logger.debug("Initialized SciPy.")

    def solve(self):
        self.logger.debug("Started solving using Scipy with method {}".format(self.solverMethod.value))
        ys = list()
        ts = list()
        while self._odesolver.successful() and self._odesolver.t < self.integration_range[1]:
            ts.append(self._odesolver.t)
            ys.append(list(self._odesolver.y))
            self._odesolver.integrate(self._odesolver.t + self.delta_t)

        self.logger.debug("Solving finished")
        if len(ys) > 0 and len(ts) > 0:
            return OdeOutput(SupportedSolvers.Scipy.value, ys, ts)
        else:
            return None

    def set_integration_range(self, range_tuple):
        if isinstance(range_tuple, tuple):
            self.integration_range = range_tuple

    def set_ode_solver(self, function):
        self.user_function = function

    def set_initial_conditions(self, conditions):
        if isinstance(conditions, dict):
            self.initial_conditions = conditions

if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
