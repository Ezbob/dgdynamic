from scipy.integrate import ode
from plugins.ode_plugin import OdePlugin
import sys


class Scipy(OdePlugin):

    def __init__(self, function, integration_range=(0, 0), initial_condition=None):
        super().__init__(function, integration_range, initial_condition)

    def solve(self):
        pass

    def set_integration_range(self, range_tuple):
        pass

    def set_ode_solver(self, name):
        pass

    def set_initial_conditions(self, conditions):
        pass


if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
