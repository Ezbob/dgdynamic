from ..config.settings import config
import enum

def _left_pad(string):
    string_stripped_size = len(string.strip())
    return "{:<{}}".format(string, string_stripped_size + 1 if string_stripped_size > 0 else 0)


def print_message(message, stream=None):
    if config.getboolean('Simulation', 'VERBOSE', fallback=False):
        print(message, file=stream)


def print_solver_start(plugin_name):
    print_message("{}simulation started".format(_left_pad(plugin_name)))


def print_solver_done(plugin_name, method_name='', was_failure=False):
    if isinstance(plugin_name, enum.Enum):
        plugin_name = plugin_name.name

    plugin_name, method_name = _left_pad(plugin_name), _left_pad(method_name)
    if was_failure:
        print_message("{}{}simulation finished with errors".format(plugin_name, method_name))
    else:
        print_message("{}{}simulation finished".format(plugin_name, method_name))
