import functools as ft
from .simulator import DynamicSimulator
from ..converters.definitions.cgf_channel import Channel
from collections import defaultdict
from ..plugins.stochastic.spim import SpimStochastic
from dgDynamic.choices import SupportedStochasticPlugins
from io import StringIO


def _hyper_edge_to_string(edge):
    with StringIO() as out:
        for index, source_vertex in enumerate(edge.sources):
            out.write(source_vertex.graph.name)
            if index < edge.numSources - 1:
                out.write(" + ")
        out.write(" -> ")

        for index, target_vertex in enumerate(edge.targets):
            out.write(target_vertex.graph.name)
            if index < edge.numTargets - 1:
                out.write(" + ")
        out.write("\n")
        return out.getvalue()


def _pretty_print_dict(channel_dict):
    for key, value in channel_dict.items():
        print(key, value)


class StochasticPiSystem(DynamicSimulator):

    def __init__(self, graph):
        super().__init__(graph=graph)
        self.rate_names = tuple('r{}'.format(index) for index in range(self.reaction_count))
        self.decay_rates = tuple()

    def generate_channels(self):
        # our "matrix"
        result = defaultdict(tuple)

        def add_channel(vertex_key, channel):
            result[vertex_key] += (channel,)

        def homo_reaction_case(edge, edge_index):
            channel_results = tuple()
            first_vertex = ""
            for vertex_index, vertex in enumerate(edge.sources):
                if vertex_index == 0:
                    first_vertex = vertex.graph.name
                    new_input_channel = Channel(channel_edge=edge, rate_id=edge_index, is_input=True, is_decay=False)\
                        .add_reagents(edge.targets)
                    channel_results += (new_input_channel,)
                else:
                    new_output_channel = Channel(channel_edge=edge, rate_id=edge_index, is_input=False, )
                    channel_results += (new_output_channel,)
            for channel in channel_results:
                add_channel(vertex_key=first_vertex, channel=channel)

        def hetero_reaction_case(edge, edge_index):
            vertices = sorted(edge.sources, key=lambda instance: instance.graph.name)
            for vertex_index, vertex in enumerate(vertices):
                if vertex_index == 0:
                    new_input_channel = Channel(channel_edge=edge,
                                                rate_id=edge_index, is_input=True)\
                        .add_reagents(edge.targets)
                    add_channel(vertex_key=vertex.graph.name, channel=new_input_channel)
                else:
                    new_output_channel = Channel(channel_edge=edge,
                                                 rate_id=edge_index, is_input=False)
                    add_channel(vertex_key=vertex.graph.name, channel=new_output_channel)

        def unary_reaction_case(edge, edge_index):
            for vertex in edge.sources:
                new_channel = Channel(channel_edge=edge,
                                      rate_id=edge_index, is_input=False, is_decay=True) \
                    .add_reagents(edge.targets)
                self.decay_rates += ("r{}".format(edge_index),)
                add_channel(vertex_key=vertex.graph.name, channel=new_channel)

        # debug = {value: key for key, value in self.symbols.items()}
        for reaction_index, hyper_edge in enumerate(self.graph.edges):
            if hyper_edge.numSources == 1:
                unary_reaction_case(hyper_edge, reaction_index)
            elif hyper_edge.numSources == 2:
                if ft.reduce(lambda a, b: a.graph.name == b.graph.name, hyper_edge.sources):
                    homo_reaction_case(hyper_edge, reaction_index)
                else:
                    hetero_reaction_case(hyper_edge, reaction_index)
            else:
                raise ValueError("For reaction: {}; reactions with 3 or more reactants are not support"
                                 .format(_hyper_edge_to_string(hyper_edge)))
        return result

    def get_plugin_from_enum(self, enum_variable, *args, **kwargs):
        if enum_variable == SupportedStochasticPlugins.SPiM:
            return SpimStochastic(self, *args, **kwargs)

    def get_plugin(self, plugin_name, *args, **kwargs):
        if isinstance(plugin_name, str):
            for plugin_enum in SupportedStochasticPlugins:
                if plugin_enum.value in plugin_name.lower():
                    return self.get_plugin_from_enum(plugin_enum, *args, **kwargs)
        elif isinstance(plugin_name, SupportedStochasticPlugins):
            return self.get_plugin_from_enum(plugin_name, *args, **kwargs)
