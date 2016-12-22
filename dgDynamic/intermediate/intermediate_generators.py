import sympy as sp
import functools as ft
from collections import defaultdict
from .transition import TransitionChannel
from io import StringIO


def _hyper_edge_to_string(edge, newline_end=True):
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
        if newline_end:
            out.write("\n")
        return out.getvalue()


def generate_rate_laws(hyper_edges, rate_parameters: dict=None, internal_symbols: dict=None):

    translate_internal = internal_symbols if internal_symbols is not None else dict()
    translate_parameters = rate_parameters if rate_parameters is not None else dict()

    for edge in hyper_edges:
        sources = (sp.Symbol(translate_internal.get(vertex.graph.name, vertex.graph.name)) for vertex in edge.sources)
        reduced = ft.reduce(lambda a, b: a * b, sources)
        yield _hyper_edge_to_string(edge, False), sp.Symbol(translate_parameters.get(edge.id, "r{}".format(edge.id))) * reduced


def generate_equations(hyper_vertices, hyper_edges, ignored, rate_parameters: dict=None,
                       internal_symbols: dict=None, drain_translation: dict=None):
    """
    This function will attempt to create the symbolic ODEs using the rate laws.
    """

    drain_dict = drain_translation
    internal_symbol_dict = internal_symbols if internal_symbols is not None else dict()

    def drain():
        in_sym, out_sym = drain_dict[vertex.graph.name]
        vertex_sym = sp.Symbol(internal_symbol_dict.get(vertex.graph.name, vertex.graph.name))
        return sp.Symbol(in_sym) * vertex_sym, sp.Symbol(out_sym) * vertex_sym

    ignore_dict = dict(ignored)
    for vertex in hyper_vertices:
        if vertex.graph.name in ignore_dict:
            yield vertex.graph.name, 0
        else:
            # Since we use sympy, we can use the left hand expresses as mathematical expressions
            equation_result = 0
            rate_laws = (law_tuple[1] for law_tuple in generate_rate_laws(hyper_edges, rate_parameters,
                                                                          internal_symbol_dict))
            for reaction_edge, lhs in zip(hyper_edges, rate_laws):
                for source_vertex in reaction_edge.sources:
                    if vertex.id == source_vertex.id:
                        equation_result -= lhs
                for target_vertex in reaction_edge.targets:
                    if vertex.id == target_vertex.id:
                        equation_result += lhs

            if drain_translation is not None:
                in_drain, out_drain = drain()
                equation_result += in_drain
                equation_result -= out_drain

            yield vertex.graph.name, equation_result


def generate_channels(hyper_edges):
    result = defaultdict(tuple)
    decay_rates = tuple()

    def add_channel(vertex_key, channel):
        result[vertex_key] += (channel,)

    def homo_reaction_case(edge, edge_index):
        channel_results = tuple()
        first_vertex = ""
        for vertex_index, vertex in enumerate(edge.sources):
            if vertex_index == 0:
                first_vertex = vertex.graph.name
                new_input_channel = TransitionChannel(channel_edge=edge, rate_id=edge_index,
                                                      is_input=True, is_decay=False)\
                    .add_reagents(edge.targets)
                channel_results += (new_input_channel,)
            else:
                new_output_channel = TransitionChannel(channel_edge=edge, rate_id=edge_index, is_input=False,)
                channel_results += (new_output_channel,)
        for channel in channel_results:
            add_channel(vertex_key=first_vertex, channel=channel)

    def hetero_reaction_case(edge, edge_index):
        vertices = sorted(edge.sources, key=lambda instance: instance.graph.name)
        for vertex_index, vertex in enumerate(vertices):
            if vertex_index == 0:
                new_input_channel = TransitionChannel(channel_edge=edge, rate_id=edge_index, is_input=True)\
                    .add_reagents(edge.targets)
                add_channel(vertex_key=vertex.graph.name, channel=new_input_channel)
            else:
                new_output_channel = TransitionChannel(channel_edge=edge, rate_id=edge_index, is_input=False)
                add_channel(vertex_key=vertex.graph.name, channel=new_output_channel)

    def unary_reaction_case(edge, edge_index, decay_rates):
        for vertex in edge.sources:
            new_channel = TransitionChannel(channel_edge=edge, rate_id=edge_index, is_input=False, is_decay=True) \
                .add_reagents(edge.targets)
            decay_rates += ("r{}".format(edge_index),)
            add_channel(vertex_key=vertex.graph.name, channel=new_channel)

    for reaction_index, hyper_edge in enumerate(hyper_edges):
        if hyper_edge.numSources == 1:
            unary_reaction_case(hyper_edge, reaction_index, decay_rates)
        elif hyper_edge.numSources == 2:
            if ft.reduce(lambda a, b: a.graph.name == b.graph.name, hyper_edge.sources):
                homo_reaction_case(hyper_edge, reaction_index)
            else:
                hetero_reaction_case(hyper_edge, reaction_index)
        else:
            raise ValueError("For reaction: {}; reactions with 3 or more reactants are not support"
                             .format(_hyper_edge_to_string(hyper_edge)))
    return result, decay_rates
