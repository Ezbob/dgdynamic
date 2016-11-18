from typing import Iterable
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


def _parse_mod_reaction(graph: "mod.mod_.DG", derivation: str) -> "mod.mod_.DGHyperEdge":
    sources, _, targets = derivation.partition(" -> ")

    edge = graph.findEdge(_get_side_vertices(graph, sources), _get_side_vertices(graph, targets))
    is_null = edge.isNull() if hasattr(edge, "isNull") else False

    if is_null or edge is None:
        raise ReactionParseError("No edge for reaction: {}".format(derivation))
    return edge


def _parse_reaction(derivation: str) -> tuple:
    sources, _, targets = derivation.partition(" -> ")

    parsed_sources = tuple(parsed for parsed in _parse_sides(sources))
    parsed_targets = tuple(parsed for parsed in _parse_sides(targets))

    if parsed_sources is None:
        raise ReactionParseError("Parsing of reaction {}, returned None for sources".format(derivation))
    if parsed_targets is None:
        raise ReactionParseError("Parsing of reaction {}, returned None for targets".format(derivation))
    return parsed_sources, parsed_targets


def abstract_parser(reaction: str):
    parse_result = namedtuple('parse_result', 'sources targets representation has_inverse')
    if reaction.find(" <=> ") != -1:
        first_reaction, second_reaction = _break_two_way_deviations(reaction)
        first_parsed = _parse_reaction(first_reaction)
        second_parsed = _parse_reaction(second_reaction)
        return parse_result(targets=(first_parsed[1], second_parsed[1]), sources=(first_parsed[0], second_parsed[0]),
                            has_inverse=True, representation=reaction)
    elif reaction.find(" -> ") != -1:
        parsed = _parse_reaction(reaction)
        return parse_result(targets=(parsed[1],), sources=(parsed[0],), has_inverse=False, representation=reaction)


@log_it
def abstract_mod_parser(deviation_graph: "DG", reaction: str) -> namedtuple:

    parse_result = namedtuple('parse_result', 'mod_edges representation has_inverse')
    if reaction.find(" <=> ") != -1:
        first_reaction, second_reaction = _break_two_way_deviations(reaction)
        mod_edges = (_parse_mod_reaction(deviation_graph, first_reaction),
                     _parse_mod_reaction(deviation_graph, second_reaction))
        return parse_result(mod_edges=mod_edges, representation=reaction, has_inverse=True)

    elif reaction.find(' -> ') != -1:
        return parse_result(mod_edges=(_parse_mod_reaction(deviation_graph, reaction),), representation=reaction,
                             has_inverse=False)
