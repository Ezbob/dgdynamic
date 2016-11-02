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


class StochasticPiSystem(DynamicSimulator):

    def __init__(self, graph):
        super().__init__(graph=graph)
        self.rate_names = tuple('r{}'.format(index) for index in range(self.reaction_count))
        self.symbols = tuple(vertex.graph.name for vertex in self.graph.vertices)

    def generate_channels(self):
        # our "matrix"
        result = defaultdict(lambda: defaultdict(tuple))

        def _add_channel(key, channel, reaction_index):
            result[key][reaction_index] += (channel,)

        # debug = {value: key for key, value in self.symbols.items()}
        for reaction_index, hyper_edge in enumerate(self.graph.edges):
            if hyper_edge.numSources == 1:
                print("I am unary: ", print_hyper_edge(edge=hyper_edge))
                for vertex in hyper_edge.sources:
                    new_channel = Channel(rate=self.rate_names[reaction_index], is_input=False, is_decay=True)\
                        .add_reagents(hyper_edge.targets)

                    _add_channel(key=vertex.graph.name, channel=new_channel, reaction_index=reaction_index)
            elif hyper_edge.numSources == 2:
                if ft.reduce(lambda a, b: a.graph.name == b.graph.name, hyper_edge.sources):
                    print("I am homo: ", print_hyper_edge(edge=hyper_edge))
                    channel_results = tuple()
                    for vertex_index, vertex in enumerate(hyper_edge.sources):
                        if vertex_index == 0:
                            new_input_channel = Channel(rate=self.rate_names[reaction_index], is_input=True,
                                                        is_decay=False).add_reagents(hyper_edge.targets)
                            channel_results += (new_input_channel,)
                        else:
                            pass
                else:
                    print("I am hetero: ", print_hyper_edge(edge=hyper_edge))

        print(result)

    def unchanging_species(self, *species: Union[str, "Symbol", ProjectTypeHints.Countable_Sequence]):
        pass
