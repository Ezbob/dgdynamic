from typing import Iterable, Tuple, Union
from dgDynamic.utils.exceptions import ReactionParseError
from ..utils.project_utils import log_it
from collections import namedtuple


def _parse_sides(side: str) -> str:
    skip_next = False
    the_splitting = side.split()
    for index, atom in enumerate(the_splitting):
        if not skip_next:
            if str.isdigit(atom):
                skip_next = True
                multiplier = int(atom)
                try:
                    species = the_splitting[index + 1]
                except IndexError:
                    raise ReactionParseError("Index error in\
                      specification parsing; tried index {} but length is {} ".format(index + 1,
                                                                                      len(the_splitting)))
                for i in range(multiplier):
                    yield species
            elif '+' == atom:
                continue
            yield atom
        else:
            skip_next = False
            continue


def _get_side_vertices(graph: "mod.mod_.DG", side: str) -> "mod.mod_.DGVertex":
    for sym in _parse_sides(side):
        for vertex in graph.vertices:
            if vertex.graph.name == sym:
                yield vertex


def _break_two_way_deviations(two_way: str) -> Iterable[str]:
    yield " -> ".join(two_way.split(" <=> "))
    yield " -> ".join(reversed(two_way.split(" <=> ")))


def _parse_reaction(graph: "mod.mod_.DG", derivation: str) -> "mod.mod_.DGHyperEdge":
    sources, _, targets = derivation.partition(" -> ")

    edge = graph.findEdge(_get_side_vertices(graph, sources), _get_side_vertices(graph, targets))
    is_null = edge.isNull() if hasattr(edge, "isNull") else False

    if is_null or edge is None:
        raise ReactionParseError("No edge for reaction: {}".format(derivation))
    return edge


@log_it
def abstract_reaction_parser(deviation_graph: "DG", reaction: str) -> namedtuple:

    parse_results = namedtuple('parse_result', 'mod_edges representation has_inverse')
    if reaction.find(" <=> ") != -1:
        first_reaction, second_reaction = _break_two_way_deviations(reaction)
        mod_edges = (_parse_reaction(deviation_graph, first_reaction),
                     _parse_reaction(deviation_graph, second_reaction))
        return parse_results(mod_edges=mod_edges, representation=reaction, has_inverse=True)

    elif reaction.find(' -> ') != -1:
        return parse_results(mod_edges=(_parse_reaction(deviation_graph, reaction),), representation=reaction,
                             has_inverse=False)
