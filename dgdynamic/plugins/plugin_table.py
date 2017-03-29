from dgdynamic.choices import SupportedStochasticPlugins, SupportedOdePlugins
import importlib
import warnings


def tab_init(d):
    table = {}
    plugin_common_prefix = 'dgdynamic.plugins'
    for mode, plugin_dict in d.items():
        table[mode] = {}
        plugin_mode_prefix = plugin_common_prefix + '.' + mode
        for name_enum, path_name in plugin_dict.items():
            module_path, class_name = path_name
            full_path = plugin_mode_prefix + '.' + module_path
            try:
                module = importlib.import_module(full_path)
                clazz = getattr(module, class_name)
            except AttributeError:
                clazz = None
                warnings.warn("Failed to find class {} for module {}. Plugin {} disabled."
                              .format(class_name, full_path, name_enum.name))
            except ImportError:
                warnings.warn("Failed to import module {} from {}. Plugin {} disabled."
                              .format(name_enum.name, full_path, name_enum.name))
                clazz = None
            table[mode][name_enum] = clazz
    return table

PLUGINS_TAB = tab_init({
    'stochastic': {
        SupportedStochasticPlugins.StochKit2:
            ('stochkit2.stochkit2', 'StochKit2Stochastic'),
        SupportedStochasticPlugins.SPiM:
            ('spim.spim', 'SpimStochastic')
    },
    'ode': {
        SupportedOdePlugins.SciPy:
            ('scipy.scipy', 'ScipyOde'),
        SupportedOdePlugins.MATLAB:
            ('matlab.matlab', 'MatlabOde')
    }
})
