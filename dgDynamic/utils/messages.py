from ..config.settings import config


def print_message(message, stream=None):
    if config.getboolean('Simulation', 'VERBOSE', fallback=False):
        print(message, file=stream)


def print_solver_start(plugin_name):
    print_message("{}simulation started".format(plugin_name + ' '))


def print_solver_success(plugin_name):
    print_message("{}simulation finished".format(plugin_name + ' '))


def print_solver_failure(plugin_name):
    print_message("{}simulation finished with errors".format(plugin_name + ' '))
