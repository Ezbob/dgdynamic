import sympy as sp
import functools as ft
"""
Module that provides generation of different forms of intermediate code
"""


def generate_rate_laws(hyper_edges, rate_parameters: dict=None, internal_symbols: dict=None):

    translate_internal = internal_symbols if internal_symbols else dict()
    translate_parameters = rate_parameters if rate_parameters else dict()

    for edge in hyper_edges:
        sources = (sp.Symbol(translate_internal.get(vertex.graph.name, vertex.graph.name)) for vertex in edge.sources)
        reduced = ft.reduce(lambda a, b: a * b, sources)
        yield sp.Symbol(translate_parameters.get(edge.id, "r{}".format(edge.id))) * reduced
