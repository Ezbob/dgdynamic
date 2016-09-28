import sys
from enum import Enum
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

    def __init__(self, eq_system=None, integration_range=(0, 0), initial_condition=None, delta_t=0.05, parameters=None):

        if isinstance(eq_system, str):
            eq_system = eval(eq_system)
        elif isinstance(eq_system, AbstractOdeSystem):
            eq_system = get_scipy_lambda(eq_system, parameters)

        super().__init__(eq_system, integration_range, initial_condition, delta_t=delta_t, parameters=parameters)

    def solve(self):
        if not self._user_function:
            return None
        if type(self._user_function) is str:
            self._user_function = eval(self._user_function)

        self.logger.debug("Started solving using Scipy with method {}".format(self._solverMethod.value))
        self.logger.debug("Functions is {}, \
range: {} and dt: {} ".format(self.initial_conditions, self.integration_range, self.delta_t))

        self.logger.debug("Setting scipy parameters...")
        assert self.integration_range[0] <= self.integration_range[1]

        self._odesolver = ode(self._user_function).set_integrator(str(self._solverMethod.value))
        initial_t, initial_y = self.initial_conditions.popitem()
        self._odesolver.set_initial_value(initial_y, initial_t)
        self.logger.debug("Set.")

        ys = list()
        ts = list()
        self._odesolver.t = self.integration_range[0]
        while self._odesolver.successful() and self._odesolver.t <= self.integration_range[1]:
            ts.append(self._odesolver.t)
            ys.append(self._odesolver.y)
            self._odesolver.integrate(self._odesolver.t + self.delta_t)

        self.logger.debug("Solving finished")
        if len(ys) > 0 and len(ts) > 0:
            return OdeOutput(SupportedSolvers.Scipy, ys, ts)
        else:
            return None

    def set_integration_range(self, range_tuple):
        if isinstance(range_tuple, tuple):
            self.integration_range = range_tuple
        return self

    def set_ode_method(self, function):
        self._user_function = function
        return self

    def set_parameters(self, parameters):
        if isinstance(self.parameters, (tuple, list)):
            self.parameters = parameters
        return self

    def from_abstract_ode_system(self, system, parameters=None):
        self._user_function = get_scipy_lambda(system)
        return self

    def set_initial_conditions(self, conditions):
        if isinstance(conditions, dict):
            self.initial_conditions = conditions
        return self

    def set_ode_function(self, ode_function):
        if isinstance(ode_function, str) or callable(ode_function):
            self._user_function = ode_function
        return self

if __name__ == "__main__":
    print("Plugin not meant as standalone application", file=sys.stderr)
