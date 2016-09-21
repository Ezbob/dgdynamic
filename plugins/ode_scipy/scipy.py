from scipy.integrate import ode
from plugins.ode_plugin import OdePlugin, LogMixin
import sys


class ScipyOde(OdePlugin, LogMixin):

    def __init__(self, function, integration_range=(0, 0), initial_condition=None):
        super().__init__(function, integration_range, initial_condition)
        self.logger.debug("Initializing SciPy module")

    def solve(self):
        pass

    def set_integration_range(self, range_tuple):
        if isinstance(range_tuple, tuple):
            self.integration_range = range_tuple

    def set_ode_solver(self, function):
        self.odeFunction = function

    def set_initial_conditions(self, conditions):
        if isinstance(conditions, dict):
            self.initial_conditions = conditions

if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
