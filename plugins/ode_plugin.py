import matplotlib.pyplot as plt
import logging
import os
import os.path
import shutil
import config


class LogMixin:
    @property
    def logger(self):
        name = ".".join([__name__, self.__class__.__name__])
        return logging.getLogger(name)


class OdePlugin:
    def __init__(self, function, integration_range=(0, 0), initial_conditions=None, delta_t=0.05):
        self.user_function = function
        self.delta_t = delta_t

        if isinstance(integration_range, (tuple, list)) and len(integration_range) >= 2:
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


class OdeOutput(LogMixin):
    def __init__(self, solved_by, dependent, independent):
        self.dependent = dependent
        self.independent = independent
        self.name = solved_by

    def __str__(self):
        return "independent variable: {}\ndependent variable: {}".format(self.independent, self.dependent)

    def plot(self):
        ys = list(self.dependent)
        ts = list(self.independent)
        plt.plot(ts, ys)
        plt.show()

    def save(self, filename="plotdata"):
        paired = list(zip(self.independent, self.dependent))
        self.logger.debug(paired)

        if os.path.exists(config.PLOT_DIRECTORY):
            shutil.rmtree(config.PLOT_DIRECTORY)
        os.mkdir(config.PLOT_DIRECTORY)
        count = 0
        if isinstance(self.dependent, list) and isinstance(self.dependent[0], list):
            count = len(self.dependent[0])
            self.logger.debug("Count is {}".format(count))

        absolute = os.path.abspath(config.PLOT_DIRECTORY)

        new_filename = os.path.join(absolute, "{}_{}.csv".format(self.name, filename))
        with open(new_filename, mode='a') as fout:
            fout.write("t,")
            for j in range(0, count - 1):
                fout.write("y{},".format(j))
            fout.write("y{}\n".format(count - 1))

            for i in range(0, len(paired)):
                fout.write("{},".format(self.independent[i]))
                for j in range(0, count):
                    if j < count - 1:
                        fout.write("{},".format(self.dependent[i][j]))
                    else:
                        fout.write("{}".format(self.dependent[i][j]))
                fout.write("\n")


def set_logging(filename="myapp.log", level=logging.DEBUG):
    logging.basicConfig(level=level, format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        filename=filename, filemode='w')
