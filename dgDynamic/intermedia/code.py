import sympy as sp
import functools as ft
"""
Module that provides generation of different forms of intermediate code
"""


def generate_rate_laws(hyper_edges, rate_parameters: dict=None, internal_symbols: dict=None):

    translate_internal = internal_symbols if internal_symbols is not None else dict()
    translate_parameters = rate_parameters if rate_parameters is not None else dict()

    for edge in hyper_edges:
        sources = (sp.Symbol(translate_internal.get(vertex.graph.name, vertex.graph.name)) for vertex in edge.sources)
        reduced = ft.reduce(lambda a, b: a * b, sources)
        yield sp.Symbol(translate_parameters.get(edge.id, "r{}".format(edge.id))) * reduced


def generate_equations(hyper_vertices, hyper_edges, ignored, rate_parameters,
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
            rate_laws = generate_rate_laws(hyper_edges, rate_parameters, internal_symbol_dict)
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
