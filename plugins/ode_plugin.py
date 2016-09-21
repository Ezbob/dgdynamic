import logging
import subprocess


class LogMixin:
    @property
    def logger(self):
        name = ".".join([__name__, self.__class__.__name__])
        return logging.getLogger(name)


class OdePlugin:

    def __init__(self, function, integration_range=(0, 0), initial_conditions=None):
        self.odeFunction = function

        if isinstance(integration_range, (tuple, list)):
            self.integration_range = integration_range
        if initial_conditions is None:
            self.initial_conditions = {0: 0}
        elif isinstance(initial_conditions, dict):
            self.initial_conditions = initial_conditions

    def set_integration_range(self, range_tuple):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_ode_solver(self, name):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_initial_conditions(self, conditions):
        raise NotImplementedError("Subclass must implement abstract method")

    def solve(self):
        raise NotImplementedError("Subclass must implement abstract method")


class OdeOutput:

    def __init__(self, solvedby, dependend, independed):
        self.dependend = dependend
        self.independed = independed
        self.name = solvedby

    def __str__(self):
        return "{} \n {}".format(self.independed, self.dependend)

    def plot(self):
        subprocess.run(["python", "run_matplot.py", str(self.dependend), str(self.independed)])


def set_logging(filename="myapp.log", level=logging.DEBUG):
    logging.basicConfig(level=level, format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        filename=filename, filemode='w')


