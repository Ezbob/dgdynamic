
class OdePlugin:

    def __init__(self, function, integration_range=(0, 0), initial_conditions=(0,)):
        self.diff = function
        if isinstance(integration_range, (tuple, list)):
            self.integration_range = integration_range
        if isinstance(initial_conditions, (tuple, list)):
            self.initial_conditions = initial_conditions

    def set_integration_range(self, range_tuple):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_ode_solver(self, name):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_initial_conditions(self, conditions):
        raise NotImplementedError("Subclass must implement abstract method")

    def solve(self):
        raise NotImplementedError("Subclass must implement abstract method")
