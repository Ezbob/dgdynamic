from scipy.integrate import ode
from plugins.ode_plugin import OdePlugin, LogMixin, OdeOutput
from enum import Enum
import sys


class ScipyOdeSolvers(Enum):
    VODE = "vode"
    ZVODE = "zvode"
    ISODA = "isoda"
    DOPRI5 = "dopri5"
    DOP853 = "dop853"


class ScipyOde(OdePlugin, LogMixin):

    deltaT = 0.1
    solverMethod = ScipyOdeSolvers.VODE

    def __init__(self, function, integration_range=(0, 0), initial_condition=None):
        super().__init__(function, integration_range, initial_condition)
        self.logger.debug("Initializing SciPy module...")
        self._odesolver = ode(self.userFunction).set_integrator(str(self.solverMethod.value))
        initial_t, initial_y = self.initial_conditions.popitem()
        self._odesolver.set_initial_value(initial_y, initial_t)
        self.logger.debug("Initialized.")

    def solve(self):
        ys = list()
        ts = list()
        while self._odesolver.successful() and self._odesolver.t < self.integration_range[1]:
            self._odesolver.integrate(self._odesolver.t + self.deltaT)
            ts.append(self._odesolver.t)
            ys.append(list(self._odesolver.y))
        if len(ys) > 0 and len(ts) > 0:
            return OdeOutput("scipy", ys, ts)
        else:
            return None

    def set_integration_range(self, range_tuple):
        if isinstance(range_tuple, tuple):
            self.integration_range = range_tuple

    def set_ode_solver(self, function):
        self.userFunction = function

    def set_initial_conditions(self, conditions):
        if isinstance(conditions, dict):
            self.initial_conditions = conditions

if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
