from collections import OrderedDict
from ..intermediate.intermediate_generators import generate_rate_laws, generate_rate_equations
from dgdynamic.choices import SupportedOdePlugins
from .simulator import DynamicSimulator
from ..utils.exceptions import SimulationError
from ..plugins.plugin_table import PLUGINS_TAB


class ODESystem(DynamicSimulator):
    """
    This class is meant to create ODEs in SymPys abstract symbolic mathematical syntax, using deviation graphs
    from the MØD framework.
    """
    def __init__(self, graph):
        super().__init__(graph=graph)
        # the mass action law parameters. For mathematical reasons the symbol indices start at 1
        self.parameters = OrderedDict((edge.id, "$k{}".format(index + 1))
                                      for index, edge in enumerate(self.graph.edges))

    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        for enum_var, plugin_class in PLUGINS_TAB['ode'].items():
            if enum_var == enum_variable:
                return plugin_class(self, *args, **kwargs) if plugin_class is not None else None

    def get_plugin(self, plugin_name, *args, **kwargs):
        if isinstance(plugin_name, str):
            for plugin in SupportedOdePlugins:
                if plugin.value.strip().lower() == plugin_name.strip().lower():
                    return self.get_plugin_from_enum(plugin, *args, **kwargs)
            raise SimulationError("plugin name not recognized")
        elif isinstance(plugin_name, SupportedOdePlugins):
            return self.get_plugin_from_enum(plugin_name, *args, **kwargs)

    @property
    def rate_laws(self):
        return dict(generate_rate_laws(self.graph.edges))

    @property
    def rate_equations(self):
        return dict(generate_rate_equations(self.graph.vertices, self.graph.edges, self.ignored, ))

    def __repr__(self):
        return "<Abstract Ode Simulator>"
