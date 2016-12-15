from collections import OrderedDict
from ..intermedia.code import generate_rate_laws, generate_equations
from typing import Union
from dgDynamic.choices import SupportedOdePlugins
from .simulator import DynamicSimulator
from ..utils.exceptions import SimulationError


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
        if enum_variable == SupportedOdePlugins.SciPy:
            from dgDynamic.plugins.ode.scipy import ScipyOde
            return ScipyOde(self, *args, **kwargs)
        elif enum_variable == SupportedOdePlugins.MATLAB:
            from dgDynamic.plugins.ode.matlab import MatlabOde
            return MatlabOde(self, *args, **kwargs)

    def get_plugin(self, plugin_name: Union[str, SupportedOdePlugins], *args, **kwargs):
        if isinstance(plugin_name, str):
            for plugin in SupportedOdePlugins:
                if plugin.value.strip().lower() == plugin_name.strip().lower():
                    return self.get_plugin_from_enum(plugin, *args, **kwargs)
            raise SimulationError("plugin name not recognized")
        elif isinstance(plugin_name, SupportedOdePlugins):
            return self.get_plugin_from_enum(plugin_name, *args, **kwargs)

    def generate_rate_laws(self):
        yield from generate_rate_laws(self.graph.edges, self.parameters, self.internal_symbol_dict)

    @property
    def rate_laws(self):
        return tuple(generate_rate_laws(self.graph.edges))

    def generate_equations(self):
        yield from generate_equations(self.graph.vertices, self.graph.edges, self.ignored, self.parameters,
                                      self.internal_symbol_dict, self.internal_drain_dict)

    @property
    def ode_equations(self):
        return dict(generate_equations(self.graph.vertices, self.graph.edges, self.ignored, self.parameters))

    def __repr__(self):
        return "<Abstract Ode Simulator>"

