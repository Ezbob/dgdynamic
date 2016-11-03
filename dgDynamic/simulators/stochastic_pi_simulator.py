from .simulator import DynamicSimulator
from typing import Union
from dgDynamic.utils.project_utils import ProjectTypeHints
import functools as ft
from ..converters.CGF import Channel
from collections import defaultdict
from io import StringIO


def print_hyper_edge(edge):
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


def pretty_print_dict(channel_dict):
    for key, value in channel_dict.items():
        print(key)
        for inner_key, inner_value in value.items():
            print("\t{}: {}".format(inner_key, inner_value))


class StochasticPiSystem(DynamicSimulator):

    def __init__(self, graph):
        super().__init__(graph=graph)
        self.rate_names = tuple('r{}'.format(index) for index in range(self.reaction_count))
        self.symbols = tuple(vertex.graph.name for vertex in self.graph.vertices)

    def generate_channels(self):
        # our "matrix"
        result = defaultdict(lambda: defaultdict(tuple))

        def add_channel(vertex_key, channel, reaction_key):
            result[vertex_key][reaction_key] += (channel,)

        def homo_reaction_case(edge, edge_index):
            channel_results = tuple()
            first_vertex = ""
            for vertex_index, vertex in enumerate(edge.sources):
                if vertex_index == 0:
                    first_vertex = vertex.graph.name
                    new_input_channel = Channel(channel_name=edge_index,
                                                rate=self.rate_names[edge_index], is_input=True, is_decay=False)\
                        .add_reagents(edge.targets)
                    channel_results += (new_input_channel,)
                else:
                    new_output_channel = Channel(channel_name=edge_index,
                                                 rate=self.rate_names[edge_index], is_input=False,)
                    channel_results += (new_output_channel,)
            for channel in channel_results:
                add_channel(vertex_key=first_vertex, channel=channel, reaction_key=edge_index)

        def hetero_reaction_case(edge, edge_index):
            for vertex_index, vertex in enumerate(edge.sources):
                if vertex_index == 0:
                    new_input_channel = Channel(channel_name=edge_index,
                                                rate=self.rate_names[edge_index], is_input=True)\
                        .add_reagents(edge.targets)
                    add_channel(vertex_key=vertex.graph.name, channel=new_input_channel, reaction_key=edge_index)
                else:
                    new_output_channel = Channel(channel_name=edge_index,
                                                 rate=self.rate_names[edge_index], is_input=False)
                    add_channel(vertex_key=vertex.graph.name, channel=new_output_channel, reaction_key=edge_index)

        def unary_reaction_case(edge, edge_index):
            for vertex in edge.sources:
                new_channel = Channel(channel_name=edge_index,
                                      rate=self.rate_names[edge_index], is_input=False, is_decay=True) \
                    .add_reagents(edge.targets)

                add_channel(vertex_key=vertex.graph.name, channel=new_channel, reaction_key=edge_index)

        # debug = {value: key for key, value in self.symbols.items()}
        for reaction_index, hyper_edge in enumerate(self.graph.edges):
            if hyper_edge.numSources == 1:
                print("I am unary: ", print_hyper_edge(edge=hyper_edge))
                unary_reaction_case(hyper_edge, reaction_index)
            elif hyper_edge.numSources == 2:
                if ft.reduce(lambda a, b: a.graph.name == b.graph.name, hyper_edge.sources):
                    print("I am homo: ", print_hyper_edge(edge=hyper_edge))
                    homo_reaction_case(hyper_edge, reaction_index)
                else:
                    print("I am hetero: ", print_hyper_edge(edge=hyper_edge))
                    hetero_reaction_case(hyper_edge, reaction_index)

        pretty_print_dict(result)

    def unchanging_species(self, *species: Union[str, "Symbol", ProjectTypeHints.Countable_Sequence]):
        raise NotImplementedError
